#!/usr/bin/env python3
"""Build or verify the local AIPM source-release archive."""
from __future__ import annotations

import argparse
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "Core-Engine"))

from aipm_core.release import ReleaseError, build_release, verify_release  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(prog="New-Release-Package")
    parser.add_argument("command", choices=("build", "verify"))
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--output", type=Path, default=ROOT / "Releases")
    parser.add_argument("--archive", type=Path)
    parser.add_argument("--checksum", type=Path)
    args = parser.parse_args()
    try:
        if args.command == "build":
            result = build_release(args.root, args.output)
        else:
            if args.archive is None:
                parser.error("verify requires --archive")
            result = verify_release(args.root, args.archive, args.checksum)
    except ReleaseError as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1
    print(f"{result['status']}: {result['version']} ({result['file_count']} files)")
    if "archive" in result:
        print(result["archive"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
