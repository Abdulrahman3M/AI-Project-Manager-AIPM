#!/usr/bin/env python3
"""Migrate the owner-approved P01 AIPM Skill subset without writing the source."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import shutil
import tempfile

EXCLUDED = {"import-memory", "morning"}
PERSONAL_MARKERS = ("02-Skills-Personal", "msg-ar", "msg-eg", "msg-en", "msg-ru", "msg-tg", "msg-uz")
DERIVATIVE = "project-orchestrator"


def digest(path: Path) -> str:
    hasher = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


def inventory(root: Path) -> dict[str, str]:
    if root.is_symlink():
        raise ValueError(f"symlink is not permitted: {root}")
    result: dict[str, str] = {}
    folded: set[str] = set()
    for path in sorted(root.rglob("*")):
        if path.is_symlink():
            raise ValueError(f"symlink is not permitted: {path}")
        if path.is_file():
            relative = path.relative_to(root).as_posix()
            if relative.casefold() in folded:
                raise ValueError(f"case collision: {relative}")
            folded.add(relative.casefold())
            result[relative] = digest(path)
    return result


def remove_personal_catalog_references(skill_root: Path) -> list[str]:
    changed: list[str] = []
    for path in skill_root.rglob("*.md"):
        original = path.read_text(encoding="utf-8")
        filtered = "\n".join(line for line in original.splitlines() if not any(marker in line for marker in PERSONAL_MARKERS))
        if filtered != original:
            path.write_text(filtered + ("\n" if original.endswith("\n") else ""), encoding="utf-8", newline="")
            changed.append(path.relative_to(skill_root).as_posix())
    return changed


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", required=True, type=Path)
    parser.add_argument("--target", required=True, type=Path)
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    source = args.source.resolve()
    target = args.target.resolve()
    if not source.is_dir() or not target.is_dir():
        raise SystemExit("source and target must be existing directories")
    source_skills = {path.name for path in source.iterdir() if path.is_dir()}
    if len(source_skills) != 19 or not EXCLUDED <= source_skills:
        raise SystemExit("source must contain the original 19-Skill baseline and approved exclusions")
    selected = sorted(source_skills - EXCLUDED)
    destination = target / "01-Skills-General"
    if destination.exists() and any(destination.iterdir()):
        raise SystemExit("destination exists and is not empty; overwrite is forbidden")
    if not args.apply:
        print(json.dumps({"selected_skill_count": len(selected), "excluded_skills": sorted(EXCLUDED), "destination": str(destination)}, indent=2))
        return 0
    # The execution sandbox permits writes only below the new repository. The
    # ignored staging parent is still isolated from the destination subtree.
    staging_parent = target / ".migration-staging"
    staging_parent.mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="AipmP01-", dir=staging_parent) as temporary:
        staged = Path(temporary) / "01-Skills-General"
        staged.mkdir()
        for name in selected:
            shutil.copytree(source / name, staged / name, copy_function=shutil.copy2)
        changed = remove_personal_catalog_references(staged / DERIVATIVE)
        if not changed:
            raise SystemExit("expected Personal Skill catalog references were not found")
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(staged), str(destination))
    source_hashes = {name: inventory(source / name) for name in selected if name != DERIVATIVE}
    target_hashes = {name: inventory(destination / name) for name in selected if name != DERIVATIVE}
    mismatched = [name for name in source_hashes if source_hashes[name] != target_hashes[name]]
    if mismatched:
        raise SystemExit(f"byte-preserved Skills differ: {mismatched}")
    derivative_text = "\n".join(path.read_text(encoding="utf-8") for path in (destination / DERIVATIVE).rglob("*.md"))
    if any(marker in derivative_text for marker in PERSONAL_MARKERS):
        raise SystemExit("Personal Skill reference remains in derivative")
    record = {
        "migration_mode": "Owner-Approved Controlled Exception",
        "source": str(source),
        "migrated_skill_count": len(selected),
        "excluded_skills": sorted(EXCLUDED),
        "byte_preserved_skills": sorted(source_hashes),
        "derivative_skill": DERIVATIVE,
        "derivative_changed_markdown_files": changed,
        "source_hashes": source_hashes,
        "target_hashes": target_hashes,
        "source_written": False,
        "personal_skills_imported": False,
    }
    record_path = target / "docs/project" / "Provenance" / "Skill-Migration-Record.json"
    record_path.parent.mkdir(parents=True, exist_ok=True)
    record_path.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": "COPIED_AND_VERIFIED", "migrated_skill_count": len(selected), "derivative_files": changed}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
