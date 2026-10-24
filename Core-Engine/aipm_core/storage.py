"""P02 external project registration and safe state-root initialization."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import json
import hashlib
from pathlib import Path
import re
import shutil
import stat
import tempfile
import os
from uuid import uuid4

STATE_ROOT_NAME = "Shared-Project-State-Manager"
LEGACY_ROOT_NAME = "Shared-Project-State"
PROJECT_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_-]{2,63}$")


class StateError(ValueError):
    """Raised when a state operation would violate AIPM isolation rules."""


def platform_root() -> Path:
    """Resolve the installed AIPM source root from this Core package."""
    return Path(__file__).resolve().parents[2]


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
    # Inspect the lexical components before resolve() can erase a redirect.
    absolute = path.absolute()
    for component in (*reversed(absolute.parents), absolute):
        try:
            attributes = component.lstat()
        except FileNotFoundError:
            continue
        except PermissionError as error:
            raise StateError(f"access denied: {component}") from error
        if stat.S_ISLNK(attributes.st_mode) or getattr(attributes, "st_file_attributes", 0) & stat.FILE_ATTRIBUTE_REPARSE_POINT:
            raise StateError(f"reparse point is not allowed: {component}")
    return path.resolve(strict=False)


def _inside(child: Path, parent: Path) -> bool:
    try:
        child.relative_to(parent)
        return True
    except ValueError:
        return False


def _overlaps(left: Path, right: Path) -> bool:
    """Return true when either path is equal to, inside, or contains the other."""
    return _inside(left, right) or _inside(right, left)


def _protect_platform_path(path: Path, *, operation: str, additional_root: Path | None = None) -> Path:
    canonical = _canonical(path)
    roots = [platform_root()]
    if additional_root is not None:
        roots.append(_canonical(additional_root))
    if any(_overlaps(canonical, _canonical(root)) for root in roots):
        raise StateError(f"AIPM_PLATFORM_PROTECTED: {operation}")
    return canonical


def validate_managed_project(project: ManagedProject) -> None:
    """Validate both the external project root and its exact owned state location."""
    root = _protect_platform_path(project.root, operation="managed project writes")
    expected_state = _canonical(root / STATE_ROOT_NAME)
    supplied_state = _canonical(project.state_root)
    if supplied_state != expected_state or supplied_state == root or not _inside(supplied_state, root):
        raise StateError("INVALID_MANAGED_STATE_ROOT")


def _timestamp() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _atomic_json(path: Path, data: dict) -> None:
    temporary = None
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        _probe_access(path.parent)
        with tempfile.NamedTemporaryFile("w", encoding="utf-8", dir=path.parent, delete=False, prefix=".aipm-", suffix=".tmp") as stream:
            temporary = Path(stream.name)
            json.dump(data, stream, indent=2, sort_keys=True)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        temporary.replace(path)
    except PermissionError as error:
        raise StateError(f"access denied: {path}") from error
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


def _probe_access(directory: Path) -> None:
    """Exercise effective file access, including delete-on-close cleanup."""
    probe = directory / f".aipm-probe-{uuid4().hex}.tmp"
    descriptor = None
    permission_error = None
    try:
        # Avoid tempfile.NamedTemporaryFile here. On Windows, the stdlib retries
        # PermissionError when os.access() mistakenly reports a denied directory
        # as writable, turning a fast ACL rejection into thousands of retries.
        descriptor = os.open(
            probe,
            os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_BINARY", 0),
            0o600,
        )
        os.write(descriptor, b"AIPM Access Probe\n")
    except PermissionError as error:
        permission_error = error
    finally:
        if descriptor is not None:
            try:
                os.close(descriptor)
            except PermissionError as error:
                permission_error = permission_error or error
        try:
            probe.unlink(missing_ok=True)
        except PermissionError as error:
            permission_error = permission_error or error
    if permission_error is not None:
        raise StateError(f"access denied: {directory}") from permission_error


def initialize_project_state(project_root: Path, project_id: str, alias: str, *, platform_root: Path | None = None) -> ManagedProject:
    if not PROJECT_ID.fullmatch(project_id):
        raise StateError("project_id must use 3-64 ASCII letters, digits, underscores, or hyphens")
    if not alias.strip():
        raise StateError("project alias is required")
    root = _protect_platform_path(project_root, operation="project registration", additional_root=platform_root)
    legacy = _canonical(root / LEGACY_ROOT_NAME)
    state_root = _canonical(root / STATE_ROOT_NAME)
    if legacy.exists():
        raise StateError("legacy Shared-Project-State detected; use a read-only compatibility workflow")
    if state_root.exists():
        raise StateError("managed state root already exists; initialization never overwrites")
    try:
        root.mkdir(parents=True, exist_ok=True)
    except PermissionError as error:
        raise StateError(f"access denied: {root}") from error
    _probe_access(root)
    staging = None
    try:
        # Exercise inherited permissions while building a complete, owned tree.
        # The public state path is published only after every operation succeeds.
        # Default mkdir permissions preserve the project's inherited Windows ACL.
        # tempfile.mkdtemp uses mode 0700, which installs a private Windows ACL.
        candidate = root / f".aipm-init-{uuid4().hex}"
        candidate.mkdir()
        staging = candidate
        _probe_access(staging)
        for relative in ("Tasks", "Tool-State", "Temporary-Files", "Cache", "Test-Workspace", "Logs", "Quarantine/Items", "Quarantine/Records", "History/Snapshots", "History/Events", "Locks", "Archive"):
            (staging / relative).mkdir(parents=True, exist_ok=True)
        now = _timestamp()
        _atomic_json(staging / "Project-Manifest.json", {"schema_version": "1.0", "project_id": project_id, "project_alias": alias, "state_root_name": STATE_ROOT_NAME, "created_at": now, "source_root_fingerprint": None, "active_task_id": None})
        _atomic_json(staging / "State-Manifest.json", {"schema_version": "1.1", "tasks": {}, "diff_fingerprint": None, "revision": 0, "project_id": project_id, "task_id": None, "task_status": "NOT-STARTED", "active_phase": None, "state_health": "CONSISTENT", "last_verified_action": "P02 initialization", "next_action": None, "branch": None, "head_sha": None, "updated_at": now, "updated_by": "aipm-core"})
        (staging / "README.md").write_text("# Shared Project State Manager\n\nManaged operational state for this project.\n", encoding="utf-8")
        if state_root.exists():
            raise StateError("managed state root already exists; initialization never overwrites")
        staging.rename(state_root)
        staging = None
    except PermissionError as error:
        raise StateError(f"access denied: {root}") from error
    except OSError as error:
        raise StateError(f"state initialization failed: {root}") from error
    finally:
        if staging is not None:
            try:
                shutil.rmtree(staging)
            except PermissionError as error:
                raise StateError(f"access denied during initialization cleanup: {staging}") from error
    project = ManagedProject(project_id, alias, root, state_root)
    validate_managed_project(project)
    return project


class ProjectRegistry:
    """Pointer-only registry stored outside the platform source tree."""

    def __init__(self, path: Path) -> None:
        self.path = _protect_platform_path(path, operation="registry storage")
        if self.path.suffix.lower() != ".json":
            raise StateError("registry file must end in .json")

    @staticmethod
    def _validate_data(data: object) -> dict:
        if not isinstance(data, dict) or data.get("schema_version") != "1.0" or not isinstance(data.get("projects"), list):
            raise StateError("INVALID_REGISTRY")
        preferences = data.get("preferences", {})
        if not isinstance(preferences, dict):
            raise StateError("INVALID_REGISTRY")
        projects: list[dict[str, str]] = []
        ids: set[str] = set()
        roots: set[str] = set()
        for entry in data["projects"]:
            if not isinstance(entry, dict) or any(not isinstance(entry.get(key), str) or not entry[key].strip() for key in ("project_id", "root_path", "alias")):
                raise StateError("INVALID_REGISTRY_ENTRY")
            project_id, root_text = entry["project_id"], entry["root_path"]
            if not PROJECT_ID.fullmatch(project_id) or project_id in ids or not Path(root_text).is_absolute():
                raise StateError("INVALID_REGISTRY_ENTRY")
            root = _protect_platform_path(Path(root_text), operation="registered project pointer")
            normalized_root = os.path.normcase(str(root))
            if normalized_root in roots:
                raise StateError("INVALID_REGISTRY_ENTRY")
            ids.add(project_id)
            roots.add(normalized_root)
            projects.append({"project_id": project_id, "root_path": str(root), "alias": entry["alias"].strip()})
        return {"schema_version": "1.0", "projects": projects, "preferences": preferences}

    def read(self) -> dict:
        if not self.path.exists():
            return {"schema_version": "1.0", "projects": [], "preferences": {}}
        try:
            data = json.loads(self.path.read_text(encoding="utf-8"))
        except (OSError, UnicodeError, json.JSONDecodeError) as error:
            raise StateError("INVALID_REGISTRY") from error
        return self._validate_data(data)

    def initialize(self) -> dict:
        if self.path.exists():
            return self.read()
        data = {"schema_version": "1.0", "projects": [], "preferences": {}}
        _atomic_json(self.path, data)
        return data

    def update_preferences(self, preferences: dict) -> dict:
        if not isinstance(preferences, dict):
            raise StateError("INVALID_REGISTRY_PREFERENCES")
        data = self.read()
        updated = {**data, "preferences": preferences}
        _atomic_json(self.path, updated)
        return updated

    def register(self, project: ManagedProject) -> dict[str, str]:
        validate_managed_project(project)
        if not project.root.is_dir():
            raise StateError("PROJECT_ROOT_NOT_FOUND")
        manifest_path = project.state_root / "Project-Manifest.json"
        try:
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        except (OSError, UnicodeError, json.JSONDecodeError) as error:
            raise StateError("INVALID_PROJECT_STATE") from error
        if manifest.get("project_id") != project.project_id or manifest.get("state_root_name") != STATE_ROOT_NAME:
            raise StateError("INVALID_PROJECT_STATE")
        data = self.read()
        new_entry = {"project_id": project.project_id, "root_path": str(project.root), "alias": project.alias.strip()}
        for entry in data["projects"]:
            if entry["project_id"] == project.project_id and entry["root_path"] != new_entry["root_path"]:
                raise StateError("PROJECT_ID_CONFLICT")
            if entry["root_path"] == new_entry["root_path"] and entry["project_id"] != project.project_id:
                raise StateError("PROJECT_ALREADY_REGISTERED")
        projects = [entry for entry in data["projects"] if entry["project_id"] != project.project_id]
        projects.append(new_entry)
        updated = {**data, "projects": projects}
        _atomic_json(self.path, updated)
        return new_entry

    def unregister(self, project_id: str) -> dict[str, str]:
        data = self.read()
        matches = [entry for entry in data["projects"] if entry["project_id"] == project_id]
        if not matches:
            raise StateError("PROJECT_NOT_REGISTERED")
        updated = {**data, "projects": [entry for entry in data["projects"] if entry["project_id"] != project_id]}
        _atomic_json(self.path, updated)
        return matches[0]

    def backup(self, destination: Path) -> Path:
        target = _protect_platform_path(destination, operation="registry backup")
        if target == self.path or target.exists():
            raise StateError("BACKUP_DESTINATION_EXISTS")
        if target.suffix.casefold() != ".json":
            raise StateError("BACKUP_FILE_MUST_BE_JSON")
        payload = self.path.read_bytes()
        # Reject a malformed source before preserving it as a recovery artifact.
        self._validate_data(json.loads(payload.decode("utf-8")))
        checksum_path = target.with_suffix(target.suffix + ".sha256")
        if checksum_path.exists():
            raise StateError("BACKUP_DESTINATION_EXISTS")
        target.parent.mkdir(parents=True, exist_ok=True)
        _write_exclusive(target, payload)
        checksum = hashlib.sha256(payload).hexdigest()
        try:
            _write_exclusive(checksum_path, f"{checksum}  {target.name}\n".encode("ascii"))
        except StateError:
            target.unlink(missing_ok=True)
            raise
        return target

    def restore(self, source: Path) -> Path | None:
        backup = _protect_platform_path(source, operation="registry restore source")
        if not backup.is_file() or backup == self.path:
            raise StateError("RESTORE_SOURCE_NOT_FOUND")
        try:
            payload = backup.read_bytes()
            sidecar = backup.with_suffix(backup.suffix + ".sha256")
            if sidecar.exists():
                expected = sidecar.read_text(encoding="ascii").split()[0]
                if hashlib.sha256(payload).hexdigest() != expected:
                    raise StateError("BACKUP_CHECKSUM_MISMATCH")
            restored = self._validate_data(json.loads(payload.decode("utf-8")))
        except (OSError, UnicodeError, json.JSONDecodeError, IndexError) as error:
            raise StateError("INVALID_RESTORE_SOURCE") from error
        safety_copy = None
        if self.path.exists():
            stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
            safety_copy = self.path.with_name(f"registry.pre-restore-{stamp}-{uuid4().hex[:8]}.json")
            self.backup(safety_copy)
        _atomic_json(self.path, restored)
        return safety_copy


def _write_exclusive(path: Path, payload: bytes) -> None:
    descriptor = None
    created = False
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        created = True
        with os.fdopen(descriptor, "wb") as stream:
            descriptor = None
            stream.write(payload)
            stream.flush()
            os.fsync(stream.fileno())
    except FileExistsError as error:
        raise StateError("BACKUP_DESTINATION_EXISTS") from error
    except OSError as error:
        if created:
            path.unlink(missing_ok=True)
        raise StateError("BACKUP_WRITE_FAILED") from error
    finally:
        if descriptor is not None:
            os.close(descriptor)
