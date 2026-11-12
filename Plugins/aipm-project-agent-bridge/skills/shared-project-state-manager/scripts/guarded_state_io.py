#!/usr/bin/env python3
"""Handle-bound state I/O for the PowerShell-invoked state CLI."""
from __future__ import annotations

import base64
import hashlib
import json
from pathlib import Path
import sys
import uuid
from contextlib import ExitStack

import safe_file_ops
import safe_move


def main() -> int:
    locks = ExitStack()
    try:
        request = json.load(sys.stdin)
        if not isinstance(request, dict):
            raise ValueError("Invalid request")
        root = safe_file_ops.resolve_project_root(request["project_root"])
        inspected = root.lstat()
        locks.enter_context(safe_move.locked_directories(root))
        current = root.lstat()
        identity = [str(current.st_dev & 0xffffffff), str(current.st_ino)]
        if (not inspected.st_ino or (inspected.st_dev, inspected.st_ino) != (current.st_dev, current.st_ino)
                or (request.get("root_identity") is not None and request["root_identity"] != identity)):
            raise ValueError("Project root identity changed since it was selected")
        target = safe_file_ops.resolve_scoped(root, request["path"], must_exist=False)
        state = root / safe_file_ops.STATE_ROOT
        try:
            relative = target.relative_to(state)
        except ValueError as error:
            raise ValueError("Target is outside the state root") from error
        action = request.get("action")
        if action == "mkdir":
            safe_move.ensure_directory(target)
            result = {"status": "PASS"}
        elif not relative.parts:
            raise ValueError("A state root cannot be used as a file")
        elif action == "read":
            with safe_move.locked_record(target, read_only=True) as locked:
                raw = locked.read()
                result = {"status": "PASS", "data": base64.b64encode(raw).decode("ascii"),
                          "sha256": hashlib.sha256(raw).hexdigest(), "identity": locked.identity}
        elif action in ("create", "update"):
            raw = base64.b64decode(request["data"], validate=True)
            safe_move.ensure_directory(target.parent)
            try:
                with safe_move.locked_record(target, create=action == "create") as locked:
                    if action == "update":
                        previous = locked.read()
                        if (request.get("sha256") != hashlib.sha256(previous).hexdigest()
                                or request.get("identity") != locked.identity):
                            raise ValueError("State file changed since it was read")
                        backup = target.with_name(f"{target.name}.before-update-{uuid.uuid4().hex}.bak")
                        with safe_move.locked_record(backup, create=True) as saved:
                            saved.write(previous)
                    locked.write(raw)
            except FileExistsError:
                if action != "create":
                    raise
                result = {"status": "EXISTS"}
            else:
                result = {"status": "PASS"}
        elif action == "list":
            with safe_move.locked_directories(target):
                result = {"status": "PASS", "names": sorted(item.name for item in target.iterdir())}
        else:
            raise ValueError("Unsupported state operation")
        print(json.dumps(result))
        return 0
    except (Exception, SystemExit) as error:
        print(json.dumps({"status": "ERROR", "reason": str(error)}))
        return 1
    finally:
        locks.close()


if __name__ == "__main__":
    raise SystemExit(main())
