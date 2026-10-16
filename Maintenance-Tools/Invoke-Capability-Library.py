"""Validate and build the P06 capability library without import-time effects."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Sequence

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "Core-Engine"))

from aipm_core.capabilities import (  # noqa: E402
    CapabilityError,
    build_plugin,
    initialize_registry,
    refresh_registry,
    validate_plugin,
    validate_registry,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="Invoke-Capability-Library")
    parser.add_argument("command", choices=("validate", "initialize-baseline", "refresh-baseline", "build-plugin", "validate-plugin"))
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--output", type=Path, default=Path("Plugins/aipm-general-skills"))
    parser.add_argument("--confirm-initial-baseline", action="store_true")
    parser.add_argument("--confirm-integrity-baseline-update", action="store_true")
    parser.add_argument("--reason")
    parser.add_argument("--replace-generated", action="store_true")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    root = args.root.resolve()
    output = args.output if args.output.is_absolute() else root / args.output
    try:
        if args.command == "validate":
            result = validate_registry(root)
        elif args.command == "initialize-baseline":
            if not args.confirm_initial_baseline:
                raise CapabilityError("Pass --confirm-initial-baseline to create the initial protected records")
            result = initialize_registry(root)
        elif args.command == "refresh-baseline":
            result = refresh_registry(root, confirmed=args.confirm_integrity_baseline_update, reason=args.reason or "")
        elif args.command == "build-plugin":
            result = build_plugin(root, output, replace_generated=args.replace_generated)
        else:
            result = validate_plugin(root, output)
    except CapabilityError as exc:
        result = {"status": "FAIL", "reason": str(exc)}
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 0 if result["status"] in {"PASS", "UNCHANGED"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
