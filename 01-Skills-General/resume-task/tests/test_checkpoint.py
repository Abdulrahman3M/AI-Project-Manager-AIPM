"""Tests for the portable checkpoint validator."""
import importlib.util
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("checkpoint_validator", ROOT / "scripts" / "validate_checkpoint.py")
module = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(module)

class ResumeCheckpointTests(unittest.TestCase):
    def setUp(self):
        self.doc = json.loads((ROOT / "examples" / "Task-Checkpoint.json").read_text(encoding="utf-8"))

    def test_valid_example(self):
        self.assertEqual(module.validate(self.doc), [])

    def test_unverified_last_step(self):
        self.doc["last_verified_step"] = "step-2"
        self.assertTrue(any("last_verified_step" in e for e in module.validate(self.doc)))

    def test_verified_without_evidence(self):
        self.doc["steps"][0]["evidence"] = []
        self.assertTrue(any("no evidence" in e for e in module.validate(self.doc)))

    def test_duplicate_step(self):
        self.doc["steps"][1]["id"] = "step-1"
        self.assertTrue(any("unique" in e for e in module.validate(self.doc)))

if __name__ == "__main__":
    unittest.main()
