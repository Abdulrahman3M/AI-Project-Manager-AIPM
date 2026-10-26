"""Turn the portable token template into a CSS custom-property layer."""
from __future__ import annotations

import json
from pathlib import Path
import re
import sys

SAFE_NAME = re.compile(r"^[a-zA-Z0-9][a-zA-Z0-9_-]*$")


def flatten(value: object, prefix: str = "") -> list[tuple[str, str]]:
    if not isinstance(value, dict):
        raise ValueError("token groups must be JSON objects")
    rows: list[tuple[str, str]] = []
    for key, child in value.items():
        if not isinstance(key, str) or not SAFE_NAME.fullmatch(key):
            raise ValueError(f"unsafe token name: {key!r}")
        name = f"{prefix}-{key}" if prefix else key
        if isinstance(child, dict):
            rows.extend(flatten(child, name))
        elif isinstance(child, str) and child.strip():
            rows.append((name, child))
        else:
            raise ValueError(f"token {name} must be a non-empty string or object")
    return rows


def main(argv: list[str]) -> int:
    if len(argv) != 3:
        print("usage: build_token_css.py TOKENS.json OUTPUT.css", file=sys.stderr)
        return 2
    try:
        data = json.loads(Path(argv[1]).read_text(encoding="utf-8"))
        if not isinstance(data, dict) or "schema_version" not in data:
            raise ValueError("tokens must include schema_version")
        rows = flatten({key: value for key, value in data.items() if key != "schema_version"})
        css = ":root {\n" + "".join(f"  --wd-{name}: {value};\n" for name, value in rows) + "}\n"
        Path(argv[2]).write_text(css, encoding="utf-8")
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"cannot build tokens: {exc}", file=sys.stderr)
        return 1
    print(f"Wrote {len(rows)} tokens to {argv[2]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
