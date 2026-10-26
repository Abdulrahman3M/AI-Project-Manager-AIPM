from pathlib import Path
import unittest


SKILL_DIR = Path(__file__).resolve().parents[1]


class EvidenceModeContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.skill = (SKILL_DIR / "SKILL.md").read_text(encoding="utf-8")
        cls.modes = (SKILL_DIR / "references" / "Evidence-Modes.md").read_text(
            encoding="utf-8"
        )

    def test_browser_inspection_requires_explicit_opt_in(self):
        self.assertIn("Use **screenshot-only mode by default**", self.skill)
        self.assertIn("**Browser inspection is optional and requires opt-in", self.skill)
        self.assertIn(
            "Would you like to use an approved agent-connected browser/extension? "
            "It can improve pixel fidelity by reading the page you are authorized "
            "to view (DOM, computed styles, layout geometry, loaded assets, and "
            "visible states). Screenshot-only reconstruction remains available.",
            self.skill,
        )

    def test_browser_inspection_has_page_and_data_boundaries(self):
        for rule in (
            "Never attach to the user's personal browser",
            "Do not enter credentials",
            "backend source",
            "continue with screenshot-only mode",
        ):
            self.assertIn(rule, self.skill)
        self.assertIn("A supplied URL alone does not authorize navigation.", self.modes)

    def test_screenshot_only_examples_cover_required_uncertainties(self):
        for scenario in (
            "One desktop image, unknown CSS scale",
            "Desktop and mobile images",
            "Arabic with a mixed-direction identifier",
            "Custom font missing",
            "A dynamic control appears in one state",
            "Screenshot ends partway down a page",
        ):
            self.assertIn(scenario, self.modes)

    def test_evidence_modes_do_not_claim_unrun_browser_scenarios(self):
        self.assertIn("NOT_RUN", self.modes)
        self.assertIn("live reference page is not a local implementation render", self.skill)


if __name__ == "__main__":
    unittest.main()
