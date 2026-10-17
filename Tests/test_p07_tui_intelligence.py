from __future__ import annotations

import json
from pathlib import Path
import re
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "Core-Engine"))

from aipm_core.capabilities import scan_library, validate_plugin, validate_registry  # noqa: E402

SKILL = ROOT / "01-Skills-General" / "tui-intelligence"


class TuiIntelligenceContractTests(unittest.TestCase):
    def test_first_party_skill_has_separate_semver_and_companion_prompt(self) -> None:
        document = (SKILL / "SKILL.md").read_text(encoding="utf-8")
        prompt = (SKILL / "PROMPT.md").read_text(encoding="utf-8")
        version = (SKILL / "VERSION").read_text(encoding="utf-8").strip()
        changelog = (SKILL / "CHANGELOG.md").read_text(encoding="utf-8")
        self.assertRegex(document, r"(?s)\A---\nname: tui-intelligence\ndescription: .+?\n---")
        self.assertRegex(version, r"^\d+\.\d+\.\d+$")
        self.assertIn(f"## [{version}]", changelog)
        self.assertIn("Type: Companion", prompt)
        self.assertIn("powershell-tui-app-designer", document)

    def test_skill_covers_intelligent_tui_visual_navigation_and_rendering_invariants(self) -> None:
        text = "\n".join(path.read_text(encoding="utf-8") for path in SKILL.rglob("*.md"))
        required = (
            "Task Dashboard", "Command Palette", "Assistant Console", "Title Case",
            "#101923", "#172635", "#203447", "#F0F5FA", "#AAB9C9", "#8ED3FF",
            "#46C89A", "#F2B45C", "#F16F7B", "Unknown", "Differential Rendering",
            "Clear-Host", "NO_COLOR", "ChatGPT", "Tui-Screen-Contract.json",
        )
        for phrase in required:
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, text)

    def test_screen_contract_contains_theme_actions_explanations_modes_and_safe_unknowns(self) -> None:
        contract = json.loads((SKILL / "references" / "Tui-Screen-Contract.json").read_text(encoding="utf-8"))
        self.assertEqual(contract["schema_version"], "1.0")
        self.assertEqual(contract["default_mode"], "Task Dashboard")
        self.assertEqual(contract["modes"], ["Task Dashboard", "Command Palette", "Assistant Console"])
        self.assertEqual(contract["theme"]["selected"], "#203447")
        self.assertIn("UP", contract["keyboard"])
        self.assertIn("1-9", contract["keyboard"])
        self.assertGreaterEqual(len(contract["actions"]), 5)
        self.assertTrue(all(action["label"] and action["description"] for action in contract["actions"]))
        self.assertEqual(contract["progress"]["unknown_progress"], "Unknown")
        self.assertEqual(contract["physical_no_flicker_status"], "UNVERIFIED")

    def test_qa_evaluations_and_screenshot_manifest_do_not_claim_unrun_visual_tests(self) -> None:
        qa = (SKILL / "references" / "Tui-QA-Report.md").read_text(encoding="utf-8")
        handoff = (SKILL / "references" / "Tui-Design-Handoff.md").read_text(encoding="utf-8")
        manifest = json.loads((SKILL / "references" / "Screenshot-Manifest.json").read_text(encoding="utf-8"))
        evaluations = json.loads((SKILL / "evals" / "evals.json").read_text(encoding="utf-8"))
        self.assertIn("UNVERIFIED", qa)
        self.assertIn("13", handoff)
        self.assertEqual(manifest["status"], "REFERENCE_MOCKUP_ONLY")
        self.assertGreaterEqual(len(evaluations["cases"]), 3)
        self.assertEqual(evaluations["execution_status"], "UNVERIFIED_MODEL_EVALS_NOT_RUN")

    def test_catalog_registers_the_owner_approved_skill_inventory_under_the_project_license(self) -> None:
        catalog = scan_library(ROOT)
        skills = {item["slug"]: item for item in catalog["skills"]}
        self.assertEqual(len(skills), 12)
        self.assertEqual(skills["tui-intelligence"]["license"]["source_license"], "AI Project Manager Personal Use License")
        self.assertTrue(skills["tui-intelligence"]["license"]["aipm_personal_license_applies"])
        self.assertTrue(skills["audio-timing-author"]["license"]["aipm_personal_license_applies"])
        self.assertEqual(validate_registry(ROOT)["skill_count"], 12)
        self.assertEqual(validate_plugin(ROOT, ROOT / "Plugins" / "aipm-project-agent-bridge")["skill_count"], 12)
        self.assertFalse((ROOT / "01-Skills-General" / "import-memory").exists())
        self.assertFalse((ROOT / "01-Skills-General" / "morning").exists())

    def test_new_human_facing_skill_headings_use_title_case(self) -> None:
        headings = [line[2:].strip() for line in (SKILL / "SKILL.md").read_text(encoding="utf-8").splitlines() if line.startswith("## ")]
        self.assertTrue(headings)
        self.assertTrue(all(not heading.isupper() for heading in headings))

    def test_generated_sample_has_official_host_package_manifests_and_scoped_licenses(self) -> None:
        package = ROOT / "Plugins" / "aipm-project-agent-bridge"
        portable = json.loads((package / "plugin.json").read_text(encoding="utf-8"))
        claude = json.loads((package / ".claude-plugin" / "plugin.json").read_text(encoding="utf-8"))
        gemini = json.loads((package / "gemini-extension.json").read_text(encoding="utf-8"))
        self.assertEqual(portable["version"], "1.0.0")
        self.assertEqual(claude["version"], "1.0.0")
        self.assertEqual(gemini["version"], "1.0.0")
        self.assertFalse(any("license" in manifest for manifest in (portable, claude, gemini)))
        self.assertEqual((package / "licenses" / "AI-Project-Manager-Personal-Use-License.txt").read_bytes(), (ROOT / "LICENSE").read_bytes())


if __name__ == "__main__":
    unittest.main()
