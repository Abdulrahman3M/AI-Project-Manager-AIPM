"""Import-safe JSON command-line interface for AIPM."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Sequence

from aipm_core.domain import CommandEnvelope, CoreEngine
from aipm_core.host_adapters import load_capability_matrix
from aipm_core.storage import ManagedProject, STATE_ROOT_NAME, _canonical


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="aipm")
    parser.add_argument("command", choices=["health", "list", "inspect", "state-read", "host-capabilities"])
    parser.add_argument("--registry")
    parser.add_argument("--project-id")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.command == "host-capabilities":
        try:
            result = {"schema_version": "1.0", "status": "PASS", "matrix": load_capability_matrix(Path(__file__).resolve().parents[1])}
        except ValueError:
            result = {"schema_version": "1.0", "status": "BLOCKED", "reason": "INVALID_CAPABILITY_MATRIX"}
    elif args.command == "health":
        result = {"schema_version": "1.0", "status": "PASS", "service": "aipm-core", "command": "health"}
    else:
        try:
            data = json.loads(Path(args.registry).read_text(encoding="utf-8"))
            if not isinstance(data, dict) or data.get("schema_version") != "1.0" or not isinstance(data.get("projects"), list):
                raise ValueError("Invalid Registry")
            ids = set()
            for entry in data["projects"]:
                if not isinstance(entry, dict) or any(not isinstance(entry.get(key), str) or not entry[key].strip() for key in ("project_id", "root_path", "alias")) or entry["project_id"] in ids:
                    raise ValueError("Invalid Registry Entry")
                ids.add(entry["project_id"])
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
