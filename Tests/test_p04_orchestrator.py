from __future__ import annotations
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "Core-Engine"))
from aipm_core.orchestrator import Acceptance, Phase, TaskPlan, VerificationError


class OrchestratorTests(unittest.TestCase):
    def test_progress_uses_verified_weighted_acceptance_only(self) -> None:
        plan = TaskPlan("Task-2026-10-15-Demo", [Phase("P01", (), [Acceptance("A", 2, "PASS")]), Phase("P02", ("P01",), [Acceptance("B", 3, "UNVERIFIED")])])
        self.assertEqual(plan.progress(), 40)
        self.assertFalse(plan.can_complete("P02"))

    def test_complete_requires_dependencies_pass_and_report(self) -> None:
        plan = TaskPlan("Task-2026-10-15-Demo", [Phase("P01", (), [Acceptance("A", 1, "PASS")], report=True), Phase("P02", ("P01",), [Acceptance("B", 1, "PASS")])])
        self.assertFalse(plan.can_complete("P02"))
        plan.phases[1].report = True
        self.assertTrue(plan.can_complete("P02"))

    def test_rejects_fake_pass_and_unknown_dependency(self) -> None:
        with self.assertRaises(VerificationError):
            Phase("P01", (), [Acceptance("A", 1, "UNKNOWN")])
        with self.assertRaises(VerificationError):
            TaskPlan("Task-2026-10-15-Demo", [Phase("P02", ("P01",), [Acceptance("A", 1, "PASS")])])


if __name__ == "__main__": unittest.main()
