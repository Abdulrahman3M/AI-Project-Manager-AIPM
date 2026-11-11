"""Behavioral contract for the instruction-level Project Manager bootstrap."""

import importlib.util
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MODULE = ROOT / "01-Skills-General/project-manager/scripts/bootstrap.py"


class BootstrapContractTests(unittest.TestCase):
    def test_lifecycle_bootstrap_and_revision(self):
        self.assertTrue(MODULE.is_file(), "Project Manager bootstrap is missing")
        spec = importlib.util.spec_from_file_location("aipm_bootstrap", MODULE)
        bootstrap = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(bootstrap)
        for event in ("NEW", "ACTIVE", "RESUME", "REVISE", "REOPEN", "FIX", "RECHECK"):
            with self.subTest(event=event):
                result = bootstrap.bootstrap(event, "task-1", "scope-v1", "scope-v1")
                self.assertEqual(result["sequence"], ["project-manager", "task-scope-contract", "resource-optimization"])
                self.assertEqual(result["task_key"], "task-1")
                self.assertFalse(result["scope_changed"])
                self.assertEqual(result["enforcement"], "INSTRUCTION_ONLY")
        revised = bootstrap.bootstrap("REVISE", "task-1", "scope-v1", "scope-v2")
        self.assertTrue(revised["scope_changed"])
        self.assertEqual(revised["task_key"], "task-1")
        with self.assertRaises(ValueError):
            bootstrap.bootstrap("UNKNOWN", "task-1", "scope-v1", "scope-v1")
        with self.assertRaises(ValueError):
            bootstrap.bootstrap("NEW", "", "", "scope-v1")

    def test_repeated_bootstrap_is_deterministic_and_missing_revision_fails(self):
        self.assertTrue(MODULE.is_file(), "Project Manager bootstrap is missing")
        spec = importlib.util.spec_from_file_location("aipm_bootstrap_repeat", MODULE)
        bootstrap = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(bootstrap)
        args = ("FIX", "existing-task", "revision-1", "revision-1")
        self.assertEqual(bootstrap.bootstrap(*args), bootstrap.bootstrap(*args))
        with self.assertRaises(ValueError):
            bootstrap.bootstrap("NEW", "task-1", "", "")

    def test_policy_is_instruction_only_and_links_retained_material(self):
        skill = ROOT / "01-Skills-General/project-manager/SKILL.md"
        self.assertTrue(skill.is_file())
        text = skill.read_text(encoding="utf-8")
        for policy in ("task-scope-contract", "resource-optimization", "INSTRUCTION_ONLY"):
            self.assertIn(policy, text)
        for relative in ("references/Governance-Rules.md", "references/Skill-Routing.md",
                         "references/Quality-Supervision.md", "scripts/bootstrap.py"):
            self.assertTrue((skill.parent / relative).is_file(), relative)
        self.assertIn("only on explicit owner request", text)

    def test_missing_or_reordered_entry_is_rejected(self):
        self.assertTrue(MODULE.is_file(), "Project Manager bootstrap is missing")
        spec = importlib.util.spec_from_file_location("aipm_bootstrap_entry", MODULE)
        bootstrap = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(bootstrap)
        self.assertTrue(hasattr(bootstrap, "valid_entry"), "Entry validation is missing")
        self.assertFalse(bootstrap.valid_entry(["task-scope-contract", "resource-optimization"]))
        self.assertFalse(bootstrap.valid_entry(["task-scope-contract", "project-manager", "resource-optimization"]))
        self.assertFalse(bootstrap.valid_entry(["project-manager", "task-scope-contract"]))
        self.assertTrue(bootstrap.valid_entry(["project-manager", "task-scope-contract", "resource-optimization"]))

    def test_orchestration_brief_retains_management_fields_without_auto_state(self):
        path = ROOT / "01-Skills-General/project-manager/templates/Orchestration-Brief.md"
        self.assertTrue(path.is_file(), "Orchestration brief template is missing")
        text = path.read_text(encoding="utf-8")
        for term in ("Objective", "Must Preserve", "Capability Map", "Team Map", "Phase Plan",
                     "Supervisor Gates", "Risk", "Recovery Checkpoint", "explicit owner request"):
            self.assertIn(term, text)


if __name__ == "__main__":
    unittest.main()
