#!/usr/bin/env python3
"""Validate that every normative v5 requirement has a complete example."""
from __future__ import annotations
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
PATH = ROOT / "examples" / "EXAMPLE_COVERAGE.json"

def main() -> int:
    data = json.loads(PATH.read_text(encoding="utf-8"))
    requirements = data.get("requirements", [])
    examples = data.get("examples", [])
    req_ids = [r.get("id") for r in requirements]
    if len(req_ids) != len(set(req_ids)):
        print("FAIL: duplicate requirement IDs")
        return 1
    by_req = {}
    errors = []
    for ex in examples:
        eid = ex.get("id")
        rid = ex.get("requirement_id")
        for field in ("id","requirement_id","scenario","correct","incorrect","acceptance"):
            if not ex.get(field):
                errors.append(f"{eid or '<missing-id>'}: missing {field}")
        by_req.setdefault(rid, []).append(eid)
    for req in requirements:
        rid=req.get("id")
        for field in ("id","capability","rule","reference"):
            if not req.get(field):
                errors.append(f"{rid or '<missing-id>'}: missing {field}")
        if not by_req.get(rid):
            errors.append(f"{rid}: no mapped example")
    orphan=[rid for rid in by_req if rid not in set(req_ids)]
    errors.extend(f"orphan example target: {rid}" for rid in orphan)
    coverage = 0 if not requirements else (sum(1 for r in req_ids if by_req.get(r)) / len(requirements) * 100)
    print(f"Requirements: {len(requirements)}")
    print(f"Examples: {len(examples)}")
    print(f"Coverage: {coverage:.1f}%")
    if errors:
        for e in errors: print("FAIL:", e)
        return 1
    if coverage != 100:
        print("FAIL: coverage must be 100%")
        return 1
    print("PASS: every normative requirement has a complete example")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
