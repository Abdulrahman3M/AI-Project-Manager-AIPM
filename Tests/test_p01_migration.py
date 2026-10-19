from __future__ import annotations

import hashlib
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
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
    def test_root_license_is_the_project_personal_use_license(self) -> None:
        text = (ROOT / "LICENSE").read_text(encoding="utf-8")
        self.assertIn("AI Project Manager — Personal Use License", text)
        self.assertIn("Copyright (c) 2026 Abdulrahman Elbatrah", text)
        self.assertIn("your own personal, non-commercial use", text)

    def test_approved_skill_subset_is_installed_and_verified(self) -> None:
        self.assertTrue(TARGET.is_dir(), "approved Skills directory is not installed")
        installed = {path.name for path in TARGET.iterdir() if path.is_dir()}
        registry = json.loads((ROOT / "Capability-Library" / "Registry.json").read_text(encoding="utf-8"))
        approved = {item["slug"] for item in registry["skills"]}
        first_party = json.loads((ROOT / "Capability-Library" / "First-Party-Skills.json").read_text(encoding="utf-8"))
        declared_first_party = {item["slug"] for item in first_party["skills"]}
        self.assertEqual(
            {"browser-environment-manager", "powershell-tui-app-designer", "tui-intelligence"},
            declared_first_party,
        )
        self.assertEqual(approved, installed)
        self.assertEqual(12, len(installed))
        self.assertTrue(declared_first_party <= installed)
        self.assertFalse(installed & EXCLUDED)
        self.assertFalse((ROOT / "02-Skills-Personal").exists())

        orchestrator_text = "\n".join(
            path.read_text(encoding="utf-8")
            for path in (TARGET / "project-orchestrator").rglob("*.md")
        )
        self.assertFalse(any(marker in orchestrator_text for marker in PERSONAL_MARKERS))

        record = json.loads((ROOT / "docs/project" / "Provenance" / "Skill-Migration-Record.json").read_text(encoding="utf-8"))
        # This record is an immutable historical baseline, not the current inventory:
        # the owner subsequently removed several skills from the project.
        self.assertEqual(record["migrated_skill_count"], 17)
        self.assertEqual(sorted(record["excluded_skills"]), sorted(EXCLUDED))


if __name__ == "__main__":
    unittest.main()
