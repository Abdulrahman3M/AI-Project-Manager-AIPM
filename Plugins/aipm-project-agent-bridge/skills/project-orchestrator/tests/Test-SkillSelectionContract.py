"""Validate AIPM's maintained Skill-routing table and key selection rules."""

import json
import re
import unittest
from pathlib import Path


SKILL_DIR = Path(__file__).resolve().parents[1]
REPO_ROOT = SKILL_DIR.parents[1]
REGISTRY_PATH = REPO_ROOT / "Capability-Library" / "Registry.json"
SKILL_PATH = SKILL_DIR / "SKILL.md"
PROTOCOL_PATH = SKILL_DIR / "references" / "Skill-Selection-Protocol.md"


class SkillSelectionContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.registry = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
        cls.skill = SKILL_PATH.read_text(encoding="utf-8")
        cls.protocol = PROTOCOL_PATH.read_text(encoding="utf-8")

    def test_catalog_matches_active_registry_slugs_and_versions(self):
        catalog = {}
        in_catalog = False
        for line in self.skill.splitlines():
            if "Current Skill Catalog" in line:
                in_catalog = True
                continue
            if in_catalog:
                if line.startswith("### "):
                    break
                match = re.match(r"\| `([^`]+)` \| `([^`]+)` \|", line)
                if match:
                    catalog[match.group(1)] = match.group(2)
        expected = {item["slug"]: item["version"] for item in self.registry["skills"]}
        self.assertEqual(expected, catalog)

    def test_agent_handoff_output_intent_routes_to_handoff_skill(self):
        self.assertIn("create-strict-implementation-handoff", self.protocol)
        self.assertRegex(self.protocol, r"(?is)markdown.*(?:another|next).*AI agent")
        self.assertRegex(self.protocol, r"(?is)handoff.*(?:lead|implement(?:ation)?-handoff)")
        self.assertIn("generic Markdown", self.protocol)
        self.assertRegex(self.protocol, r"(?is)generic README.*not enough|generic README.*does not trigger|not.*a handoff merely because")

    def test_missing_skill_has_online_and_offline_fallbacks(self):
        self.assertRegex(self.protocol, r"(?is)online.*search|search.*online")
        self.assertRegex(self.protocol, r"(?is)network.*unavailable|unavailable.*network")
        self.assertRegex(self.protocol, r"(?is)native capabilities|base agent")
        self.assertRegex(self.protocol, r"(?is)install.*approval|approval.*install")


if __name__ == "__main__":
    unittest.main(verbosity=2)
