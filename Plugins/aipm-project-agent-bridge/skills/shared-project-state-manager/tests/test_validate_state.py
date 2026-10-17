import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "validate_state.py"

class ValidateStateTests(unittest.TestCase):
    def run_tool(self, root):
        return subprocess.run([sys.executable, str(SCRIPT), "--project-root", str(root)], text=True, capture_output=True)

    def test_missing_state_fails(self):
        with tempfile.TemporaryDirectory() as td:
            r = self.run_tool(Path(td))
            self.assertNotEqual(r.returncode, 0)
            self.assertIn('"status": "FAIL"', r.stdout)

    def test_minimal_valid_state_passes(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            shared = root / "Shared-Project-State"
            task_id = "Task-Test"
            task = shared / "Tasks" / task_id
            for d in [task/"Checkpoints", task/"Phase-Reports", task/"Test-Reports", task/"Agent-Sessions"]:
                d.mkdir(parents=True, exist_ok=True)
            for name in ["README.md","Current-State.md","Next-Agent-Handoff.md","Root-Exceptions.md","File-Operations-Policy.md"]:
                (shared/name).write_text("x\n", encoding="utf-8")
            for name in ["Task-Plan.md","Decision-Log.md","File-Change-Map.md","Test-Status.md","Blockers.md"]:
                (task/name).write_text("x\n", encoding="utf-8")
            manifest = {
                "schema_version":"2.0","task_id":task_id,"task_title":"Test","task_status":"IN-PROGRESS",
                "active_phase":"P01","updated_by":"Test","updated_at":"2026-10-08T12:00:00Z",
                "state_health":"CONSISTENT","next_action":"Continue","file_operations_policy":"QUARANTINE-FIRST"
            }
            (shared/"State-Manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
            r = self.run_tool(root)
            self.assertEqual(r.returncode, 0, r.stdout+r.stderr)
            self.assertIn('"status": "PASS"', r.stdout)

if __name__ == "__main__":
    unittest.main()
