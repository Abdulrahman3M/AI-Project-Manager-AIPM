"""Evidence and decision checks for the instruction-level scope contract."""

import importlib.util
import inspect
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODULE = ROOT / "01-Skills-General/task-scope-contract/scripts/scope_check.py"


class ScopeContractTests(unittest.TestCase):
    def setUp(self):
        self.assertTrue(MODULE.is_file(), "Scope contract checker is missing")
        spec = importlib.util.spec_from_file_location("scope_check", MODULE)
        self.checker = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(self.checker)

    def test_read_tracking_requires_reason_and_identity(self):
        check = self.checker.read_decision
        self.assertEqual(check("", "v1", None), "DENY")
        self.assertEqual(check("dependency", "", None), "UNVERIFIED")
        self.assertEqual(check("dependency", "v1", "v1"), "REDUNDANT")
        self.assertEqual(check("dependency", "v2", "v1"), "ALLOW")
        self.assertGreaterEqual(len(inspect.signature(check).parameters), 5, "Read ranges must be tracked")
        self.assertEqual(check("dependency", "v1", "v1", (20, 30), (1, 10)), "ALLOW")
        self.assertEqual(check("dependency", "v1", "v1", (3, 5), (1, 10)), "REDUNDANT")
        self.assertEqual(check("dependency", "v1", "v1", None, (1, 10)), "ALLOW")

    def test_retry_requires_new_evidence_and_budget(self):
        check = self.checker.retry_decision
        self.assertFalse(check("", 1, 3, "old"))
        self.assertFalse(check("new hypothesis", 3, 3, "old"))
        self.assertTrue(check("new hypothesis", 1, 3, "old"))
        self.assertFalse(check("new hypothesis", 1, 3, None))
        self.assertGreaterEqual(len(inspect.signature(check).parameters), 4, "Prior hypothesis must be compared")
        self.assertFalse(check("same", 1, 3, "same"))
        self.assertTrue(check("changed", 1, 3, "same"))
        self.assertGreaterEqual(len(inspect.signature(check).parameters), 6, "Changed evidence must be comparable")
        self.assertTrue(check("same", 1, 3, "same", "prior result", "new result"))
        self.assertFalse(check("same", 1, 3, "same", "same result", "same result"))

    def test_quality_gate_never_passes_without_required_evidence(self):
        check = self.checker.quality_gate
        self.assertEqual(len(inspect.signature(check).parameters), 2, "Required checks must be explicit")
        passed = {"id": "test-a", "status": "PASS", "evidence": "test output", "supported": True}
        self.assertEqual(check([passed], ["test-a", "test-b"]), "UNVERIFIED")
        self.assertEqual(check([{**passed, "evidence": ""}], ["test-a"]), "UNVERIFIED")
        self.assertEqual(check([{**passed, "status": "FAIL"}], ["test-a"]), "FAIL")
        self.assertEqual(check([{**passed, "supported": False}], ["test-a"]), "UNVERIFIED")
        self.assertEqual(check([passed], ["test-a"]), "PASS")
        self.assertEqual(check([passed, passed], ["test-a"]), "UNVERIFIED")
        self.assertEqual(check([], ["test-a"]), "UNVERIFIED")

    def test_edit_scope_is_distinct_and_no_file_count_cap(self):
        self.assertTrue(hasattr(self.checker, "edit_decision"), "Edit scope checker is missing")
        check = self.checker.edit_decision
        permitted = [f"src/dependency-{i}.py" for i in range(12)]
        for path in permitted:
            self.assertTrue(check(path, permitted))
        self.assertFalse(check("src/unrelated.py", permitted))
        self.assertFalse(check("../outside.py", ["../outside.py"]))
        self.assertFalse(check("C:/outside.py", ["C:/outside.py"]))
        self.assertFalse(check("src/../outside.py", ["src/../outside.py"]))


if __name__ == "__main__":
    unittest.main()
