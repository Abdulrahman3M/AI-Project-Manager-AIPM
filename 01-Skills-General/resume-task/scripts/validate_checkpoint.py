#!/usr/bin/env python3
"""Read-only portable Resume Task checkpoint validator; Python 3.8+."""
import argparse
import json
from pathlib import Path
import sys

STATUSES = {"VERIFIED", "IN_PROGRESS", "UNVERIFIED", "FAILED", "BLOCKED"}

def validate(data):
    errors = []
    if not isinstance(data, dict):
        return ["Checkpoint must be a JSON object."]
    if data.get("schema_version") != 1:
        errors.append("schema_version must be 1.")
    for key in ("objective", "source", "next_action"):
        if not isinstance(data.get(key), str) or not data[key].strip():
            errors.append(f"{key} must be a non-empty string.")
    for key in ("requirements", "constraints", "final_checks", "blockers"):
        if not isinstance(data.get(key), list) or not all(isinstance(x, str) for x in data[key]):
            errors.append(f"{key} must be a list of strings.")
    steps = data.get("steps")
    if not isinstance(steps, list) or not steps:
        errors.append("steps must be a non-empty list.")
        return errors
    seen = set()
    for idx, step in enumerate(steps):
        label = f"steps[{idx}]"
        if not isinstance(step, dict):
            errors.append(f"{label} must be an object.")
            continue
        sid = step.get("id")
        if not isinstance(sid, str) or not sid.strip() or sid in seen:
            errors.append(f"{label}.id must be unique and non-empty.")
        else:
            seen.add(sid)
        if step.get("status") not in STATUSES:
            errors.append(f"{label}.status is invalid.")
        if not isinstance(step.get("acceptance"), str) or not step["acceptance"].strip():
            errors.append(f"{label}.acceptance must be non-empty.")
        ev = step.get("evidence")
        if not isinstance(ev, list) or not all(isinstance(x, str) for x in ev):
            errors.append(f"{label}.evidence must be a list of strings.")
        elif step.get("status") == "VERIFIED" and not any(s.strip() for s in ev):
            errors.append(f"{label} is VERIFIED but has no evidence.")
    last = data.get("last_verified_step")
    if last is not None and not any(isinstance(s, dict) and s.get("id") == last and s.get("status") == "VERIFIED" for s in steps):
        errors.append("last_verified_step must reference a VERIFIED step or be null.")
    current = data.get("current_step")
    if current is not None and current not in seen:
        errors.append("current_step must reference an existing step or be null.")
    return errors

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("checkpoint", type=Path)
    parser.add_argument("--next", action="store_true", help="Print the next safe action.")
    args = parser.parse_args()
    try:
        data = json.loads(args.checkpoint.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        print(f"INVALID: {exc}", file=sys.stderr)
        return 1
    errors = validate(data)
    if errors:
        for error in errors:
            print(f"INVALID: {error}", file=sys.stderr)
        return 1
    print(f"VALID: {len(data['steps'])} steps")
    if args.next:
        print(data["next_action"])
    return 0

if __name__ == "__main__":
    sys.exit(main())
