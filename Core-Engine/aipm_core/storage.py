"""P02 external project registration and safe state-root initialization."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import json
from pathlib import Path
import re
import tempfile
import os

STATE_ROOT_NAME = "Shared-Project-State-Manager"
LEGACY_ROOT_NAME = "Shared-Project-State"
PROJECT_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_-]{2,63}$")


class StateError(ValueError):
    """Raised when a state operation would violate AIPM isolation rules."""


def default_registry_path() -> Path:
    """Return the pointer-only per-user registry location, never a repo path."""
    base = Path(os.environ.get("LOCALAPPDATA", Path.home() / ".local"))
    return base / "AI-Project-Manager" / "registry.json"


@dataclass(frozen=True)
class ManagedProject:
    project_id: str
    alias: str
    root: Path
    state_root: Path


def _canonical(path: Path) -> Path:
    if path.is_symlink():
        raise StateError(f"symlink root is not allowed: {path}")
    return path.resolve(strict=False)


def _inside(child: Path, parent: Path) -> bool:
    try:
        child.relative_to(parent)
        return True
    except ValueError:
        return False


def _timestamp() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _atomic_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", dir=path.parent, delete=False, prefix=".aipm-", suffix=".tmp") as stream:
        json.dump(data, stream, indent=2, sort_keys=True)
        stream.write("\n")
        stream.flush()
        temporary = Path(stream.name)
    temporary.replace(path)


def initialize_project_state(project_root: Path, project_id: str, alias: str, *, platform_root: Path | None = None) -> ManagedProject:
    if not PROJECT_ID.fullmatch(project_id):
        raise StateError("project_id must use 3-64 ASCII letters, digits, underscores, or hyphens")
    if not alias.strip():
        raise StateError("project alias is required")
    root = _canonical(project_root)
    platform = _canonical(platform_root) if platform_root is not None else None
    if platform is not None and _inside(root, platform):
        raise StateError("managed project root cannot be inside the AIPM platform repository")
    legacy = root / LEGACY_ROOT_NAME
    state_root = root / STATE_ROOT_NAME
    if legacy.exists():
        raise StateError("legacy Shared-Project-State detected; use a read-only compatibility workflow")
    if state_root.exists():
        raise StateError("managed state root already exists; initialization never overwrites")
    root.mkdir(parents=True, exist_ok=True)
    state_root.mkdir()
    for relative in ("Tasks", "Tool-State", "Temporary-Files", "Cache", "Test-Workspace", "Logs", "Quarantine/Items", "Quarantine/Records", "History/Snapshots", "History/Events", "Locks", "Archive"):
        (state_root / relative).mkdir(parents=True, exist_ok=True)
    now = _timestamp()
    _atomic_json(state_root / "Project-Manifest.json", {"schema_version": "1.0", "project_id": project_id, "project_alias": alias, "state_root_name": STATE_ROOT_NAME, "created_at": now, "source_root_fingerprint": None, "active_task_id": None})
    _atomic_json(state_root / "State-Manifest.json", {"schema_version": "1.0", "revision": 0, "project_id": project_id, "task_id": None, "task_status": "NOT-STARTED", "active_phase": None, "state_health": "CONSISTENT", "last_verified_action": "P02 initialization", "next_action": None, "branch": None, "head_sha": None, "updated_at": now, "updated_by": "aipm-core"})
    (state_root / "README.md").write_text("# Shared Project State Manager\n\nManaged operational state for this project.\n", encoding="utf-8")
    return ManagedProject(project_id, alias, root, state_root)


class ProjectRegistry:
    """Pointer-only registry stored outside the platform source tree."""

    def __init__(self, path: Path) -> None:
        self.path = _canonical(path)
        if self.path.name != "registry.json":
            raise StateError("registry must be named registry.json")

    def register(self, project: ManagedProject) -> None:
        data = {"schema_version": "1.0", "projects": [], "preferences": {}}
        if self.path.exists():
            data = json.loads(self.path.read_text(encoding="utf-8"))
        projects = [entry for entry in data["projects"] if entry["project_id"] != project.project_id]
        projects.append({"project_id": project.project_id, "root_path": str(project.root), "alias": project.alias})
        data["projects"] = projects
        _atomic_json(self.path, data)
