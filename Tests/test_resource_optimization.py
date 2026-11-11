"""Tests for resource reporting and delegation decision records."""

import importlib.util
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODULE = ROOT / "01-Skills-General/resource-optimization/scripts/resource_policy.py"


class ResourcePolicyTests(unittest.TestCase):
    def setUp(self):
        self.assertTrue(MODULE.is_file(), "Resource policy checker is missing")
        spec = importlib.util.spec_from_file_location("resource_policy", MODULE)
        self.policy = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(self.policy)

    def test_delegation_requires_huge_approved_scoped_plan(self):
        gate = self.policy.delegation_decision
        plan = {"reason": "independent work", "roles": ["review"], "boundaries": ["tests/"],
                "collision_avoidance": "separate files", "overhead": "extra context",
                "serial_alternative": "sequential", "count": 1, "verification": "review results"}
        self.assertEqual(gate("SMALL", True, plan), "DENY")
        self.assertEqual(gate("MEDIUM", True, plan), "SERIAL")
        self.assertEqual(gate("HUGE", None, plan), "SERIAL")
        self.assertEqual(gate("HUGE", False, plan), "SERIAL")
        self.assertEqual(gate("HUGE", True, {}), "DENY")
        self.assertEqual(gate("HUGE", True, plan), "ALLOW_PLAN")
        overlap = {**plan, "count": 2, "roles": ["one", "two"],
                   "boundaries": ["src/", "src/components/"]}
        self.assertEqual(gate("HUGE", True, overlap), "DENY")

    def test_missing_quota_is_not_measured_and_required_tests_remain_required(self):
        self.assertEqual(self.policy.telemetry(None), {"status": "NOT_MEASURED", "value": None})
        self.assertEqual(self.policy.telemetry(42), {"status": "NOT_MEASURED", "value": None})
        self.assertEqual(self.policy.telemetry(42, verified=True), {"status": "MEASURED", "value": 42})
        self.assertEqual(self.policy.telemetry(float("nan")), {"status": "NOT_MEASURED", "value": None})
        self.assertEqual(self.policy.telemetry(True), {"status": "NOT_MEASURED", "value": None})
        self.assertTrue(self.policy.required_checks_continue(budget_exhausted=True))

    def test_revision_preserves_required_checks_and_measurements(self):
        self.assertTrue(hasattr(self.policy, "revise_budget"), "Budget reconciliation is missing")
        original = {"revision": "v1", "target_calls": 5, "required_checks": ["unit", "security"],
                    "observed_calls": 3, "quota": "NOT_MEASURED"}
        revised = self.policy.revise_budget(original, {"revision": "v2", "target_calls": 8})
        self.assertEqual(revised["required_checks"], ["unit", "security"])
        self.assertEqual(revised["observed_calls"], 3)
        self.assertEqual(revised["quota"], "NOT_MEASURED")
        self.assertEqual(revised["target_calls"], 8)
        self.assertEqual(original["target_calls"], 5)
        with self.assertRaises(ValueError):
            self.policy.revise_budget(original, {"required_checks": []})


if __name__ == "__main__":
    unittest.main()
