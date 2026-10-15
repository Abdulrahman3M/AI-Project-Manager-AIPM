"""Versioned commands, results, and immutable event records for AIPM."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Any

from .storage import ManagedProject, StateError, _atomic_json


@dataclass(frozen=True)
class CommandEnvelope:
    request_id: str
    command: str
    actor: str
    project_id: str
    expected_revision: int
    idempotency_key: str | None
    input: dict[str, Any]


class CoreEngine:
    """The only P03 writer for registered managed-project state."""

    def __init__(self, projects: dict[str, ManagedProject]) -> None:
        self.projects = projects

    @staticmethod
    def _recover(project: ManagedProject) -> None:
        """Finish a durable intent before exposing state or accepting a mutation."""
        pending = project.state_root / "History" / "Pending-Commit.json"
        if not pending.exists():
            return
        transaction = json.loads(pending.read_text(encoding="utf-8"))
        manifest = transaction["manifest"]
        event = transaction["event"]
        revision = manifest["revision"]
        if type(revision) is not int or revision < 1 or event["revision"] != revision or manifest["project_id"] != project.project_id or event["project_id"] != project.project_id:
            raise StateError("Invalid Pending Commit")
        manifest_path = project.state_root / "State-Manifest.json"
        current = json.loads(manifest_path.read_text(encoding="utf-8"))
        if current["revision"] not in (revision - 1, revision) or (current["revision"] == revision and current != manifest):
            raise StateError("Pending Commit Conflicts With State")
        event_path = project.state_root / "History" / "Events" / f"{revision:020d}.json"
        if event_path.exists():
            if json.loads(event_path.read_text(encoding="utf-8")) != event:
                raise StateError("Pending Commit Conflicts With Event")
        else:
            _atomic_json(event_path, event)
        if current != manifest:
            _atomic_json(manifest_path, manifest)
        pending.unlink()

    def _commit(self, project: ManagedProject, manifest: dict[str, Any], event: dict[str, Any]) -> None:
        pending = project.state_root / "History" / "Pending-Commit.json"
        _atomic_json(pending, {"schema_version": "1.0", "manifest": manifest, "event": event})
        self._recover(project)

    def execute(self, command: CommandEnvelope) -> dict[str, Any]:
        project = self.projects.get(command.project_id)
        if project is None:
            return {"schema_version": "1.0", "status": "BLOCKED", "reason": "PROJECT_NOT_REGISTERED"}
        manifest_path = project.state_root / "State-Manifest.json"
        try:
            self._recover(project)
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            if not isinstance(manifest, dict) or manifest.get("schema_version") not in {"1.0", "1.1"} or type(manifest.get("revision")) is not int or manifest["revision"] < 0 or manifest.get("project_id") != project.project_id:
                raise StateError("Invalid State Manifest")
            manifest.setdefault("tasks", {})
            manifest.setdefault("diff_fingerprint", None)
            if not isinstance(manifest["tasks"], dict):
                raise StateError("Invalid Task State")
        except (OSError, ValueError, KeyError, TypeError):
            return {"schema_version": "1.0", "status": "BLOCKED", "reason": "INVALID_STATE"}
        if command.command == "state.read":
            return {"schema_version": "1.0", "status": "PASS", "state": manifest, "revision": manifest["revision"]}
        if command.command not in {"state.set-next-action", "state.record-git-observation"}:
            return {"schema_version": "1.0", "status": "BLOCKED", "reason": "COMMAND_UNSUPPORTED"}
        events = project.state_root / "History" / "Events"
        if command.idempotency_key:
            for event_path in events.glob("*.json"):
                if json.loads(event_path.read_text(encoding="utf-8")).get("idempotency_key") == command.idempotency_key:
                    return {"schema_version": "1.0", "status": "PASS", "revision": manifest["revision"], "replayed": True}
        if command.expected_revision != manifest["revision"]:
            return {"schema_version": "1.0", "status": "BLOCKED", "reason": "STATE_CONFLICT", "revision": manifest["revision"]}
        if command.command == "state.set-next-action":
            next_action = command.input.get("next_action")
            if not isinstance(next_action, str) or not next_action.strip():
                return {"schema_version": "1.0", "status": "BLOCKED", "reason": "INVALID_INPUT"}
            manifest["next_action"] = next_action
        else:
            keys = ("branch", "head_sha", "diff_fingerprint")
            if any(key not in command.input or (command.input[key] is not None and (not isinstance(command.input[key], str) or not command.input[key].strip())) for key in keys):
                return {"schema_version": "1.0", "status": "BLOCKED", "reason": "INVALID_INPUT"}
            manifest.update({key: command.input[key] for key in keys})
        manifest["revision"] += 1
        manifest["schema_version"] = "1.1"
        manifest["updated_by"] = command.actor
        manifest["updated_at"] = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        event = {"schema_version": "1.0", "request_id": command.request_id, "command": command.command, "actor": command.actor, "project_id": command.project_id, "revision": manifest["revision"], "idempotency_key": command.idempotency_key, "input": command.input}
        try:
            self._commit(project, manifest, event)
        except (OSError, ValueError, KeyError, TypeError):
            return {"schema_version": "1.0", "status": "BLOCKED", "reason": "STATE_COMMIT_FAILED"}
        return {"schema_version": "1.0", "status": "PASS", "revision": manifest["revision"], "replayed": False}
