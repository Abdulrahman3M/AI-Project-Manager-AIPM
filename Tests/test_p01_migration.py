from __future__ import annotations

import hashlib
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
SOURCE = Path(r"D:\Test\02 │ Assistance Projects\AI Project Manager (AIPM) │ Archive\AI-Project-Manager-AIPM-V2\Source-Skills\01-Skills-General")
TARGET = ROOT / "01-Skills-General"
EXCLUDED = {"import-memory", "morning"}
PERSONAL_MARKERS = ("02-Skills-Personal", "msg-ar", "msg-eg", "msg-en", "msg-ru", "msg-tg", "msg-uz")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


class P01MigrationTests(unittest.TestCase):
    def test_root_license_is_the_complete_apache_2_text(self) -> None:
        text = (ROOT / "LICENSE").read_text(encoding="utf-8")
        self.assertIn("Apache License\n                           Version 2.0, January 2004", text)
        self.assertIn("3. Grant of Patent License.", text)
        self.assertIn("END OF TERMS AND CONDITIONS", text)

    def test_approved_skill_subset_is_installed_and_verified(self) -> None:
        self.assertTrue(TARGET.is_dir(), "approved Skills directory is not installed")
        source_skills = {path.name for path in SOURCE.iterdir() if path.is_dir()}
        expected = source_skills - EXCLUDED
        installed = {path.name for path in TARGET.iterdir() if path.is_dir()}

        # tui-intelligence is AIPM-authored, not a migrated Universal AI ToolKit Skill.
        # Keep the byte-preservation comparison scoped to imported source material.
        first_party = json.loads((ROOT / "Capability-Library" / "First-Party-Skills.json").read_text(encoding="utf-8"))
        declared_first_party = {item["slug"] for item in first_party["skills"]}
        self.assertEqual({"tui-intelligence"}, declared_first_party)
        self.assertEqual(expected | declared_first_party, installed)
        self.assertFalse((ROOT / "02-Skills-Personal").exists())

        for skill in sorted(expected - {"project-orchestrator"}):
            source_files = {path.relative_to(SOURCE / skill): sha256(path) for path in (SOURCE / skill).rglob("*") if path.is_file()}
            target_files = {path.relative_to(TARGET / skill): sha256(path) for path in (TARGET / skill).rglob("*") if path.is_file()}
            self.assertEqual(source_files, target_files, skill)

        orchestrator_text = "\n".join(
            path.read_text(encoding="utf-8")
            for path in (TARGET / "project-orchestrator").rglob("*.md")
        )
        self.assertFalse(any(marker in orchestrator_text for marker in PERSONAL_MARKERS))

        record = json.loads((ROOT / "Project-Documentation" / "Provenance" / "Skill-Migration-Record.json").read_text(encoding="utf-8"))
        self.assertEqual(record["migrated_skill_count"], 17)
        self.assertEqual(sorted(record["excluded_skills"]), sorted(EXCLUDED))


if __name__ == "__main__":
    unittest.main()
