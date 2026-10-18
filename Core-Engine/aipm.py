"""Import-safe JSON command-line interface for AIPM."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Sequence

from aipm_core.domain import CommandEnvelope, CoreEngine
from aipm_core.host_adapters import load_capability_matrix
from aipm_core.storage import ManagedProject, ProjectRegistry, STATE_ROOT_NAME, StateError, _canonical, _protect_platform_path, default_registry_path, initialize_project_state


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="aipm")
    parser.add_argument("command", choices=["health", "list", "inspect", "state-read", "host-capabilities", "dashboard", "catalog", "registry-init", "registry-register", "registry-unregister", "registry-backup", "registry-restore"])
    parser.add_argument("--registry")
    parser.add_argument("--project-id")
    parser.add_argument("--project-root")
    parser.add_argument("--alias")
    parser.add_argument("--destination")
    parser.add_argument("--source")
    return parser


def _read_registered_projects(registry_path: Path) -> list[dict[str, str]]:
    data = json.loads(registry_path.read_text(encoding="utf-8"))
    if not isinstance(data, dict) or data.get("schema_version") != "1.0" or not isinstance(data.get("projects"), list):
        raise ValueError("Invalid Registry")
    projects: list[dict[str, str]] = []
    ids: set[str] = set()
    for entry in data["projects"]:
        if not isinstance(entry, dict) or any(not isinstance(entry.get(key), str) or not entry[key].strip() for key in ("project_id", "root_path", "alias")) or entry["project_id"] in ids:
            raise ValueError("Invalid Registry Entry")
        ids.add(entry["project_id"])
        projects.append({key: entry[key] for key in ("project_id", "root_path", "alias")})
    return projects


def _dashboard(registry_path: Path) -> dict:
    try:
        registry = ProjectRegistry(registry_path)
        if not registry.path.exists():
            return {"schema_version": "1.0", "status": "PASS", "registry_status": "NOT_REGISTERED", "projects": []}
        data = registry.read()
        entries = data["projects"]
    except StateError as error:
        if str(error).startswith("AIPM_PLATFORM_PROTECTED"):
            return {"schema_version": "1.0", "status": "BLOCKED", "reason": "AIPM_PLATFORM_PROTECTED"}
        if not registry_path.exists():
            return {"schema_version": "1.0", "status": "PASS", "registry_status": "NOT_REGISTERED", "projects": []}
        return {"schema_version": "1.0", "status": "BLOCKED", "reason": "INVALID_REGISTRY"}
    except (OSError, ValueError, TypeError):
        if not registry_path.exists():
            return {"schema_version": "1.0", "status": "PASS", "registry_status": "NOT_REGISTERED", "projects": []}
        return {"schema_version": "1.0", "status": "BLOCKED", "reason": "INVALID_REGISTRY"}

    projects = []
    for entry in entries:
        try:
            root = _canonical(Path(entry["root_path"]))
            project = ManagedProject(entry["project_id"], entry["alias"], root, _canonical(root / STATE_ROOT_NAME))
            state_result = CoreEngine({project.project_id: project}).execute(
                CommandEnvelope("aipm-dashboard", "state.read", "aipm-dashboard", project.project_id, 0, None, {})
            )
        except (OSError, ValueError, TypeError):
            state_result = {"status": "BLOCKED", "reason": "INVALID_STATE"}
        state_status = "PASS" if state_result.get("status") == "PASS" else "UNVERIFIED"
        projects.append({
            "project_id": entry["project_id"],
            "alias": entry["alias"],
            "state_status": state_status,
            "state": state_result.get("state") if state_status == "PASS" else None,
            "reason": None if state_status == "PASS" else state_result.get("reason", "INVALID_STATE"),
        })
    return {"schema_version": "1.0", "status": "PASS", "registry_status": "REGISTERED", "projects": projects}


def _catalog(root: Path) -> dict:
    try:
        registry = json.loads((root / "Capability-Library" / "Registry.json").read_text(encoding="utf-8"))
        first_party = json.loads((root / "Capability-Library" / "First-Party-Skills.json").read_text(encoding="utf-8"))
        if not isinstance(registry, dict) or registry.get("schema_version") != "1.0" or not isinstance(registry.get("skills"), list):
            raise ValueError("Invalid Capability Registry")
        if not isinstance(first_party, dict) or first_party.get("schema_version") != "1.0" or not isinstance(first_party.get("skills"), list):
            raise ValueError("Invalid First-Party Registry")
        skills = []
        for item in registry["skills"]:
            if not isinstance(item, dict) or any(not isinstance(item.get(key), str) for key in ("slug", "version", "description")):
                raise ValueError("Invalid Skill Entry")
            license_record = item.get("license")
            if not isinstance(license_record, dict):
                raise ValueError("Invalid Skill License")
            skills.append({
                "slug": item["slug"],
                "version": item["version"],
                "description": item["description"],
                "source_license": license_record.get("source_license", "UNVERIFIED"),
                "aipm_apache_applies": license_record.get("aipm_apache_applies") is True,
            })
        first_party_slugs = sorted(
            item["slug"] for item in first_party["skills"]
            if isinstance(item, dict) and isinstance(item.get("slug"), str)
        )
        sample_root = root / "Plugins" / "aipm-project-agent-bridge"
        version_path = sample_root / "VERSION"
        sample_version = version_path.read_text(encoding="utf-8").strip() if version_path.is_file() else None
        manifests = [name for name in ("plugin.json", ".codex-plugin/plugin.json", ".claude-plugin/plugin.json", "gemini-extension.json") if (sample_root / name).is_file()]
    except (OSError, UnicodeError, ValueError, TypeError, json.JSONDecodeError):
        return {"schema_version": "1.0", "status": "BLOCKED", "reason": "INVALID_CAPABILITY_CATALOG"}
    return {
        "schema_version": "1.0",
        "status": "PASS",
        "catalog": {
            "platform_version": registry.get("platform_version", "UNVERIFIED"),
            "integrity_status": "UNVERIFIED",
            "skill_count": len(skills),
            "skills": skills,
            "first_party_skills": first_party_slugs,
            "plugin_sample": {
                "version": sample_version,
                "status": "PACKAGE_SAMPLE_ONLY",
                "installation": "UNVERIFIED",
                "publication": "UNVERIFIED",
                "manifests": manifests,
            },
        },
    }


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    registry_path = Path(args.registry) if args.registry else default_registry_path()
    if args.command.startswith("registry-"):
        try:
            registry = ProjectRegistry(registry_path)
            if args.command == "registry-init":
                data = registry.initialize()
                result = {"schema_version": "1.0", "status": "PASS", "registry_status": "READY", "registry_path": str(registry.path), "project_count": len(data["projects"])}
            elif args.command == "registry-register":
                if not args.project_root or not args.project_id or not args.alias:
                    raise StateError("REGISTRY_REGISTER_ARGUMENTS_REQUIRED")
                root = _protect_platform_path(Path(args.project_root), operation="project registration")
                registry.initialize()
                state_root = _canonical(root / STATE_ROOT_NAME)
                if state_root.exists():
                    manifest = json.loads((state_root / "Project-Manifest.json").read_text(encoding="utf-8"))
                    if not isinstance(manifest, dict):
                        raise StateError("INVALID_PROJECT_STATE")
                    if manifest.get("project_id") != args.project_id or manifest.get("state_root_name") != STATE_ROOT_NAME:
                        raise StateError("PROJECT_STATE_IDENTITY_CONFLICT")
                    project = ManagedProject(args.project_id, args.alias.strip(), _canonical(root), state_root)
                else:
                    project = initialize_project_state(root, args.project_id, args.alias)
                entry = registry.register(project)
                result = {"schema_version": "1.0", "status": "PASS", "registered": entry}
            elif args.command == "registry-unregister":
                if not args.project_id:
                    raise StateError("PROJECT_ID_REQUIRED")
                entry = registry.unregister(args.project_id)
                result = {"schema_version": "1.0", "status": "PASS", "unregistered": entry, "project_state_deleted": False}
            elif args.command == "registry-backup":
                if not args.destination:
                    raise StateError("BACKUP_DESTINATION_REQUIRED")
                backup = registry.backup(Path(args.destination))
                result = {"schema_version": "1.0", "status": "PASS", "backup": str(backup), "sha256": str(backup.with_suffix(backup.suffix + ".sha256"))}
            else:
                if not args.source:
                    raise StateError("RESTORE_SOURCE_REQUIRED")
                safety_copy = registry.restore(Path(args.source))
                result = {"schema_version": "1.0", "status": "PASS", "restored": str(Path(args.source).resolve()), "pre_restore_backup": str(safety_copy) if safety_copy else None}
        except (OSError, ValueError, TypeError, AttributeError, json.JSONDecodeError) as error:
            reason = str(error) if isinstance(error, StateError) else "REGISTRY_OPERATION_FAILED"
            if reason.startswith("AIPM_PLATFORM_PROTECTED"):
                reason = "AIPM_PLATFORM_PROTECTED"
            result = {"schema_version": "1.0", "status": "BLOCKED", "reason": reason}
        print(json.dumps(result))
        return 0 if result["status"] == "PASS" else 1
    if args.command == "dashboard":
        result = _dashboard(registry_path)
    elif args.command == "catalog":
        result = _catalog(Path(__file__).resolve().parents[1])
    elif args.command == "host-capabilities":
        try:
            result = {"schema_version": "1.0", "status": "PASS", "matrix": load_capability_matrix(Path(__file__).resolve().parents[1])}
        except ValueError:
            result = {"schema_version": "1.0", "status": "BLOCKED", "reason": "INVALID_CAPABILITY_MATRIX"}
    elif args.command == "health":
        result = {"schema_version": "1.0", "status": "PASS", "service": "aipm-core", "command": "health"}
    else:
        try:
            data = ProjectRegistry(registry_path).read()
            if not isinstance(data, dict) or data.get("schema_version") != "1.0" or not isinstance(data.get("projects"), list):
                raise ValueError("Invalid Registry")
            ids = set()
            for entry in data["projects"]:
                if not isinstance(entry, dict) or any(not isinstance(entry.get(key), str) or not entry[key].strip() for key in ("project_id", "root_path", "alias")) or entry["project_id"] in ids:
                    raise ValueError("Invalid Registry Entry")
                ids.add(entry["project_id"])
        except StateError as error:
            reason = "AIPM_PLATFORM_PROTECTED" if str(error).startswith("AIPM_PLATFORM_PROTECTED") else str(error)
            result = {"schema_version": "1.0", "status": "BLOCKED", "reason": reason}
        except (OSError, ValueError, TypeError):
            result = {"schema_version": "1.0", "status": "BLOCKED", "reason": "INVALID_REGISTRY"}
        else:
            if args.command == "list":
                result = {"schema_version": "1.0", "status": "PASS", "projects": data["projects"]}
            else:
                entry = next((item for item in data["projects"] if item["project_id"] == args.project_id), None)
                if entry is None:
                    result = {"schema_version": "1.0", "status": "BLOCKED", "reason": "PROJECT_NOT_REGISTERED"}
                elif args.command == "inspect":
                    result = {"schema_version": "1.0", "status": "PASS", "project": entry}
                else:
                    try:
                        root = _canonical(Path(entry["root_path"]))
                        project = ManagedProject(entry["project_id"], entry["alias"], root, _canonical(root / STATE_ROOT_NAME))
                        result = CoreEngine({project.project_id: project}).execute(CommandEnvelope("cli-read", "state.read", "aipm-cli", project.project_id, 0, None, {}))
                    except (OSError, ValueError):
                        result = {"schema_version": "1.0", "status": "BLOCKED", "reason": "INVALID_STATE"}
    print(json.dumps(result))
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
