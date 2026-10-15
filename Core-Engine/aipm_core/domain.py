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

    def execute(self, command: CommandEnvelope) -> dict[str, Any]:
        project = self.projects.get(command.project_id)
        if project is None:
            return {"schema_version": "1.0", "status": "BLOCKED", "reason": "PROJECT_NOT_REGISTERED"}
        manifest_path = project.state_root / "State-Manifest.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        if command.command == "state.read":
            return {"schema_version": "1.0", "status": "PASS", "state": manifest, "revision": manifest["revision"]}
        if command.command != "state.set-next-action":
            return {"schema_version": "1.0", "status": "BLOCKED", "reason": "COMMAND_UNSUPPORTED"}
        events = project.state_root / "History" / "Events"
        if command.idempotency_key:
            for event_path in events.glob("*.json"):
                if json.loads(event_path.read_text(encoding="utf-8")).get("idempotency_key") == command.idempotency_key:
                    return {"schema_version": "1.0", "status": "PASS", "revision": manifest["revision"], "replayed": True}
        if command.expected_revision != manifest["revision"]:
            return {"schema_version": "1.0", "status": "BLOCKED", "reason": "STATE_CONFLICT", "revision": manifest["revision"]}
        next_action = command.input.get("next_action")
        if not isinstance(next_action, str) or not next_action.strip():
            return {"schema_version": "1.0", "status": "BLOCKED", "reason": "INVALID_INPUT"}
        manifest["revision"] += 1
        manifest["next_action"] = next_action
        manifest["updated_by"] = command.actor
        manifest["updated_at"] = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        _atomic_json(manifest_path, manifest)
        event = {"schema_version": "1.0", "request_id": command.request_id, "command": command.command, "actor": command.actor, "project_id": command.project_id, "revision": manifest["revision"], "idempotency_key": command.idempotency_key, "input": command.input}
        _atomic_json(events / f"{manifest['revision']:020d}-{command.request_id}.json", event)
        return {"schema_version": "1.0", "status": "PASS", "revision": manifest["revision"], "replayed": False}
