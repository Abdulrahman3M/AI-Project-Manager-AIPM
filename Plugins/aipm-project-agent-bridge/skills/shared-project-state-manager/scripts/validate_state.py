#!/usr/bin/env python3
from __future__ import annotations
import argparse, json
from pathlib import Path

REQUIRED_ROOT = [
    "README.md","State-Manifest.json","Current-State.md","Next-Agent-Handoff.md",
    "Root-Exceptions.md","File-Operations-Policy.md"
]
ALLOWED_TASK = {"NOT-STARTED","IN-PROGRESS","BLOCKED","READY-FOR-VERIFY","COMPLETE"}
ALLOWED_HEALTH = {"CONSISTENT","STATE-DIVERGED","RECOVERY-IN-PROGRESS","BLOCKED"}

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--project-root", default=".")
    ap.add_argument("--strict", action="store_true")
    args = ap.parse_args()
    root = Path(args.project_root).expanduser().resolve()
    state = root / "Shared-Project-State"
    errors, warnings = [], []
    if not state.is_dir():
        errors.append(f"Missing state root: {state}")
    else:
        for name in REQUIRED_ROOT:
            if not (state / name).exists():
                errors.append(f"Missing root file: {name}")
        mf = state / "State-Manifest.json"
        if mf.exists():
            try:
                data = json.loads(mf.read_text(encoding="utf-8"))
            except Exception as exc:
                errors.append(f"Invalid State-Manifest.json: {exc}")
                data = {}
            for key in ["schema_version","task_id","task_title","task_status","active_phase","updated_by","updated_at","state_health","next_action","file_operations_policy"]:
                if key not in data:
                    errors.append(f"Manifest missing key: {key}")
            if data.get("task_status") not in ALLOWED_TASK:
                errors.append(f"Invalid task_status: {data.get('task_status')}")
            if data.get("state_health") not in ALLOWED_HEALTH:
                errors.append(f"Invalid state_health: {data.get('state_health')}")
            if data.get("file_operations_policy") != "QUARANTINE-FIRST":
                errors.append(f"Invalid file_operations_policy: {data.get('file_operations_policy')}")
            task_id = data.get("task_id")
            if task_id:
                task = state / "Tasks" / str(task_id)
                if not task.is_dir():
                    errors.append(f"Missing task directory: Tasks/{task_id}")
                else:
                    for name in ["Task-Plan.md","Decision-Log.md","File-Change-Map.md","Test-Status.md","Blockers.md"]:
                        if not (task / name).exists():
                            errors.append(f"Missing task file: Tasks/{task_id}/{name}")
                    for name in ["Checkpoints","Phase-Reports","Test-Reports","Agent-Sessions"]:
                        if not (task / name).is_dir():
                            warnings.append(f"Missing task directory: Tasks/{task_id}/{name}")
    passed = not errors and not (args.strict and warnings)
    print(json.dumps({"status":"PASS" if passed else "FAIL","errors":errors,"warnings":warnings}, indent=2))
    return 0 if passed else 1

if __name__ == "__main__":
    raise SystemExit(main())
