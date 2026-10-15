import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "safe_file_ops.py"

class SafeFileOpsTests(unittest.TestCase):
    def run_tool(self, *args):
        return subprocess.run([sys.executable, str(SCRIPT), *map(str,args)], text=True, capture_output=True)

    def test_quarantine_and_restore(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            target = root / "temp-work"
            target.mkdir()
            (target / "data.txt").write_text("x", encoding="utf-8")
            r = self.run_tool("quarantine", target, "--project-root", root)
            self.assertEqual(r.returncode, 0, r.stderr)
            payload = json.loads(r.stdout)
            record = Path(payload["record"])
            self.assertFalse(target.exists())
            self.assertTrue(record.exists())
            r = self.run_tool("restore", record, "--project-root", root)
            self.assertEqual(r.returncode, 0, r.stderr)
            self.assertTrue((target / "data.txt").exists())

    def test_path_escape_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td) / "project"
            root.mkdir()
            outside = root.parent / "outside"
            outside.mkdir()
            r = self.run_tool("diagnose", outside, "--project-root", root)
            self.assertNotEqual(r.returncode, 0)
            self.assertIn("escapes project root", r.stderr)

if __name__ == "__main__":
    unittest.main()
