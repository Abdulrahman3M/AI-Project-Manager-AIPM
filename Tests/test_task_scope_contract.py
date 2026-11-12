"""Evidence and decision checks for the instruction-level scope contract."""

import importlib.util
import inspect
import tempfile
import unittest
import os
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
        self.assertEqual(check([passed], ["test-a"]), "REPORTED_PASS")
        forged = {**passed, "evidence": "invented test output"}
        self.assertNotEqual(check([forged], ["test-a"]), "PASS")
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

    def test_filesystem_preflight_is_provisional_and_rejects_links(self):
        check = self.checker.edit_preflight
        self.assertEqual(check(None, "src/file.py", ["src/file.py"]), "UNVERIFIED")
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            source = root / "src"
            source.mkdir()
            (source / "file.py").write_text("fixture", encoding="utf-8")
            self.assertEqual(check(root, "src/file.py", ["src/file.py"]), "PROVISIONAL_MATCH")
            self.assertEqual(check(root, "src/missing.py", ["src/missing.py"]), "UNVERIFIED")
            self.assertEqual(check(root, "src/%2e%2e/file.py", ["src/%2e%2e/file.py"]), "DENY")
            for alias in ("src/file.py.", "src/file.py ", "src/CON", "src/NUL.txt"):
                with self.subTest(alias=alias):
                    self.assertEqual(check(root, alias, [alias]), "DENY")
            self.assertEqual(check(root, "../outside.py", ["../outside.py"]), "DENY")
            outside = root / "outside"
            outside.mkdir()
            (outside / "file.py").write_text("outside", encoding="utf-8")
            link = source / "link"
            try:
                link.symlink_to(outside, target_is_directory=True)
            except OSError as exc:
                self.skipTest(f"Symlink creation unavailable: {exc}")
            self.assertEqual(check(root, "src/link/file.py", ["src/link/file.py"]), "DENY")

    @unittest.skipUnless(os.name == "nt", "Windows short-name semantics")
    def test_filesystem_preflight_rejects_short_name_alias(self):
        import ctypes
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            file = root / "long canonical filename.txt"
            file.write_text("fixture", encoding="utf-8")
            short = ctypes.create_unicode_buffer(32768)
            if not ctypes.windll.kernel32.GetShortPathNameW(str(file), short, len(short)):
                self.skipTest("Windows short names unavailable")
            alias = Path(short.value).name
            if alias.casefold() == file.name.casefold():
                self.skipTest("Windows short names not enabled on this volume")
            self.assertEqual(self.checker.edit_preflight(root, alias, [alias]), "DENY")


if __name__ == "__main__":
    unittest.main()
