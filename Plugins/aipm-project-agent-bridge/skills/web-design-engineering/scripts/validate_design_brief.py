"""Validate a portable web-design brief JSON document using only the standard library."""
from __future__ import annotations

import json
from pathlib import Path
import sys

REQUIRED = {"thesis", "audience", "primary_job", "hierarchy", "tokens", "verification"}


def validate(value: object) -> list[str]:
    if not isinstance(value, dict):
        return ["brief must be a JSON object"]
    missing = sorted(key for key in REQUIRED if not isinstance(value.get(key), str if key != "tokens" and key != "verification" else dict))
    errors = [f"missing or invalid {key}" for key in missing]
    for key in ("thesis", "audience", "primary_job", "hierarchy"):
        if isinstance(value.get(key), str) and not value[key].strip():
            errors.append(f"{key} must not be blank")
    if isinstance(value.get("tokens"), dict) and not {"color", "type", "space"}.issubset(value["tokens"]):
        errors.append("tokens must include color, type, and space")
    if isinstance(value.get("verification"), dict) and not {"viewports", "states"}.issubset(value["verification"]):
        errors.append("verification must include viewports and states")
    return errors


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print("usage: validate_design_brief.py BRIEF.json", file=sys.stderr)
        return 2
    try:
        errors = validate(json.loads(Path(argv[1]).read_text(encoding="utf-8")))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"invalid brief: {exc}", file=sys.stderr)
        return 2
    if errors:
        print("FAIL\n" + "\n".join(f"- {error}" for error in errors))
        return 1
    print("PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
