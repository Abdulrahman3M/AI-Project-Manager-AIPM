#!/usr/bin/env python3
"""Synchronize product compatibility versions from Versioning/VERSION."""
from __future__ import annotations

from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[1]
SEMVER = re.compile(r"(?:0|[1-9]\d*)\.(?:0|[1-9]\d*)\.(?:0|[1-9]\d*)\Z")


def main() -> int:
    version = (ROOT / "Versioning" / "VERSION").read_text(encoding="utf-8").strip()
    if not SEMVER.fullmatch(version):
        raise SystemExit(f"Invalid product SemVer: {version!r}")
    entry = (ROOT / "Versioning" / "CHANGELOG.md").read_text(encoding="utf-8")
    if not re.search(rf"^## \[{re.escape(version)}\]", entry, re.MULTILINE):
        raise SystemExit(f"Versioning/CHANGELOG.md lacks [{version}] entry")
    _, _, tail = entry.partition(f"## [{version}]")
    section = f"## [{version}]" + tail.split("\n## ", 1)[0]
    mirrors = ("VERSION", "TUI/AI-Project-Manager/VERSION", "Plugins/VERSION", "Plugins/aipm-project-agent-bridge/VERSION")
    for relative in mirrors:
        (ROOT / relative).write_text(version + "\n", encoding="utf-8", newline="\n")
    changelogs = ("CHANGELOG.md", "TUI/AI-Project-Manager/CHANGELOG.md", "Plugins/CHANGELOG.md")
    for relative in changelogs:
        path = ROOT / relative
        text = path.read_text(encoding="utf-8")
        pattern = re.compile(rf"^## \[{re.escape(version)}\].*?(?=^## |\Z)", re.MULTILINE | re.DOTALL)
        text = pattern.sub("", text).rstrip()
        first_heading = re.search(r"^## ", text, re.MULTILINE)
        if first_heading:
            text = text[:first_heading.start()] + section.rstrip() + "\n\n" + text[first_heading.start():]
        else:
            text = text.rstrip() + "\n\n" + section.rstrip()
        path.write_text(text.rstrip() + "\n", encoding="utf-8", newline="\n")
    notes = ROOT / "Versioning" / "Release-Notes" / f"v{version}.md"
    if notes.is_file():
        (ROOT / "docs" / "project" / "Release-Notes" / f"Release-Notes-v{version}.md").write_bytes(notes.read_bytes())
    print(f"Synchronized product version {version} to {len(mirrors)} compatibility files and {len(changelogs)} component changelogs")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
