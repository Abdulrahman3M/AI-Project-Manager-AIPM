"""Capability-declared host routing into the AIPM Core Engine."""
from __future__ import annotations

import base64
import binascii
from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Any
from uuid import uuid4

from .domain import CommandEnvelope, CoreEngine
from .storage import StateError
from .task_ops import MAX_TASK_ARTIFACT_BYTES, TaskOperations


MATRIX_PATH = Path("Plugins/Adapters/Host-Capability-Matrix.json")
MUTATING_COMMANDS = {
    "task.create", "task.plan", "task.blocker.add", "task.blocker.clear",
    "task.verify", "task.report", "task.checkpoint", "task.artifact.write",
    "state.set-next-action", "state.record-git-observation",
}
TASK_ARTIFACT_COMMANDS = {"task.artifact.list", "task.artifact.read", "task.artifact.write"}


def load_capability_matrix(root: str | Path) -> dict[str, Any]:
    """Load and minimally validate the checked-in host capability contract."""
    root_path = Path(root).resolve()
    try:
        matrix = json.loads((root_path / MATRIX_PATH).read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise ValueError("Host capability matrix is missing or invalid") from exc
    if not isinstance(matrix, dict) or matrix.get("schema_version") != "1.0" or not isinstance(matrix.get("hosts"), list):
        raise ValueError("Host capability matrix has an invalid envelope")
    ids: set[str] = set()
    required = {"id", "display_name", "runtime_status", "local_project_access", "core_commands", "mutating_commands", "package_format_status"}
    for host in matrix["hosts"]:
        if not isinstance(host, dict) or not required.issubset(host) or not isinstance(host.get("id"), str) or host["id"] in ids:
            raise ValueError("Host capability matrix contains an invalid or duplicate host")
        if not isinstance(host["core_commands"], list) or not isinstance(host["mutating_commands"], list) or not set(host["mutating_commands"]).issubset(host["core_commands"]):
            raise ValueError("Host capability matrix contains invalid commands")
        if (set(host["core_commands"]) & MUTATING_COMMANDS) - set(host["mutating_commands"]):
            raise ValueError("Host capability matrix misclassifies a mutating Core command")
        ids.add(host["id"])
    return matrix


class HostAdapter:
    """Enforce a host's declared command list before delegating to CoreEngine.

    The adapter has no filesystem API and never accepts a project path. A caller
    must construct it with a registered project ID and separately grant writes.
    """

    def __init__(
        self,
        engine: CoreEngine,
        project_id: str,
        host_id: str,
        *,
        root: str | Path,
        allow_mutations: bool = False,
    ) -> None:
        self.engine = engine
        self.project_id = project_id
        self.host_id = host_id
        self.allow_mutations = allow_mutations is True
        hosts = {host["id"]: host for host in load_capability_matrix(root)["hosts"]}
        self.profile = hosts.get(host_id)

    def execute(
        self,
        command: str,
        payload: dict[str, Any] | None = None,
        *,
        expected_revision: int = 0,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        """Dispatch an allowlisted Core command or return a stable fail-closed result."""
        profile = self.profile
        if profile is None:
            return {"schema_version": "1.0", "status": "BLOCKED", "reason": "UNSUPPORTED_HOST"}
        if profile["local_project_access"] == "UNAVAILABLE":
            return {"schema_version": "1.0", "status": "BLOCKED", "reason": "HOST_NO_LOCAL_BRIDGE"}
        if profile["runtime_status"] != "IMPLEMENTED_TESTED":
            return {"schema_version": "1.0", "status": "BLOCKED", "reason": "HOST_RUNTIME_UNVERIFIED"}
        if command not in profile["core_commands"]:
            return {"schema_version": "1.0", "status": "BLOCKED", "reason": "UNSUPPORTED_CAPABILITY"}
        if not isinstance(payload, dict) and payload is not None:
            return {"schema_version": "1.0", "status": "BLOCKED", "reason": "INVALID_INPUT"}
        payload = payload or {}
        mutation = command in MUTATING_COMMANDS or command in profile["mutating_commands"]
        if mutation and not self.allow_mutations:
            return {"schema_version": "1.0", "status": "BLOCKED", "reason": "WRITE_NOT_AUTHORIZED"}
        if type(expected_revision) is not int or expected_revision < 0 or (mutation and (not isinstance(idempotency_key, str) or not idempotency_key.strip())):
            return {"schema_version": "1.0", "status": "BLOCKED", "reason": "INVALID_INPUT"}
        if command in TASK_ARTIFACT_COMMANDS:
            return self._execute_task_artifact(command, payload, expected_revision=expected_revision)
        request_id = uuid4().hex
        envelope = CommandEnvelope(
            request_id=request_id,
            command=command,
            actor=f"aipm-host:{self.host_id}",
            project_id=self.project_id,
            expected_revision=expected_revision,
            idempotency_key=idempotency_key if mutation else None,
            input=payload,
        )
        return self.engine.execute(envelope)

    def _execute_task_artifact(self, command: str, payload: dict[str, Any], *, expected_revision: int) -> dict[str, Any]:
        task_id = payload.get('task_id')
        required = {'task_id', 'path', 'content_base64'} if command == 'task.artifact.write' else {'task_id', 'path'} if command == 'task.artifact.read' else {'task_id'}
        allowed = required | ({'expected_sha256'} if command == 'task.artifact.write' else set())
        if not required.issubset(payload) or set(payload) - allowed or not isinstance(task_id, str):
            return {"schema_version": "1.0", "status": "BLOCKED", "reason": "INVALID_INPUT"}
        project = self.engine.projects.get(self.project_id)
        if project is None:
            return {"schema_version": "1.0", "status": "BLOCKED", "reason": "PROJECT_NOT_REGISTERED"}
        state = self.engine.execute(CommandEnvelope(uuid4().hex, 'state.read', f'aipm-host:{self.host_id}', self.project_id, 0, None, {}))
        if state.get('status') != 'PASS':
            return state
        revision = state['revision']
        if command == 'task.artifact.write' and expected_revision != revision:
            return {"schema_version": "1.0", "status": "BLOCKED", "reason": "STATE_CONFLICT", "revision": revision}
        operations = TaskOperations(self.engine, project)
        task = project.state_root / 'Tasks' / task_id
        try:
            if command == 'task.artifact.list':
                return {"schema_version": "1.0", "status": "PASS", "revision": revision, "artifacts": operations.list_artifacts(task)}
            if command == 'task.artifact.read':
                content = operations.read_artifact(task, payload['path'])
                return {"schema_version": "1.0", "status": "PASS", "revision": revision, "content_base64": base64.b64encode(content).decode('ascii')}
            encoded = payload.get('content_base64')
            if not isinstance(encoded, str) or len(encoded) > ((MAX_TASK_ARTIFACT_BYTES + 2) // 3) * 4:
                return {"schema_version": "1.0", "status": "BLOCKED", "reason": "INVALID_INPUT"}
            try:
                content = base64.b64decode(encoded, validate=True)
            except (ValueError, binascii.Error):
                return {"schema_version": "1.0", "status": "BLOCKED", "reason": "INVALID_INPUT"}
            metadata = operations.write_artifact(task, payload['path'], content, expected_sha256=payload.get('expected_sha256'))
            return {"schema_version": "1.0", "status": "PASS", "revision": revision, "artifact": metadata, "replayed": metadata['replayed']}
        except (StateError, OSError, TypeError):
            return {"schema_version": "1.0", "status": "BLOCKED", "reason": "TASK_ARTIFACT_OPERATION_BLOCKED", "revision": revision}


def create_manual_handoff(state_response: dict[str, Any], *, project_alias: str) -> dict[str, Any]:
    """Create a path-free, immutable-by-convention handoff that is never trusted."""
    if not isinstance(state_response, dict) or state_response.get("status") != "PASS" or not isinstance(state_response.get("state"), dict):
        return {"schema_version": "1.0", "status": "BLOCKED", "reason": "CORE_STATE_REQUIRED"}
    state = state_response["state"]
    if not isinstance(project_alias, str) or not project_alias.strip() or type(state.get("revision")) is not int:
        return {"schema_version": "1.0", "status": "BLOCKED", "reason": "INVALID_HANDOFF_SOURCE"}
    fields = ("project_id", "revision", "task_id", "task_status", "active_phase", "next_action", "branch", "head_sha", "state_health", "updated_at", "updated_by")
    snapshot = {key: state[key] for key in fields if key in state}
    snapshot["observed_at"] = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    return {
        "schema_version": "1.0",
        "status": "UNVERIFIED",
        "handoff": {
            "project_alias": project_alias.strip(),
            "verification": "UNVERIFIED",
            "transport": "MANUAL_COPY_OR_PASTE",
            "read_only": True,
            "state_snapshot": snapshot,
            "warning": "Re-read the registered project through AIPM Core before acting on this snapshot.",
        },
    }


def accept_manual_handoff(adapter: HostAdapter, handoff: dict[str, Any]) -> dict[str, Any]:
    """Refuse to import a pasted snapshot as authoritative project state."""
    del adapter, handoff
    return {
        "schema_version": "1.0",
        "status": "BLOCKED",
        "reason": "MANUAL_HANDOFF_REQUIRES_LOCAL_REVALIDATION",
        "next_action": "Use the local AIPM Core adapter to read current registered project state.",
    }
