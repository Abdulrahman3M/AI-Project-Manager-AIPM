import base64
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "guarded_state_io.py"


class GuardedStateIOTests(unittest.TestCase):
    def call(self, root, action, target, data=None, baseline=None):
        request = {"project_root": str(root), "action": action, "path": str(target)}
        if data is not None:
            request["data"] = base64.b64encode(data).decode("ascii")
        if baseline:
            request.update(sha256=baseline["sha256"], identity=baseline["identity"])
        result = subprocess.run([sys.executable, str(SCRIPT)], input=json.dumps(request),
                                text=True, capture_output=True)
        return result, json.loads(result.stdout)

    def test_create_read_update_and_concurrent_change(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            state = root / "Shared-Project-State"
            result, reply = self.call(root, "mkdir", state)
            self.assertEqual((result.returncode, reply["status"]), (0, "PASS"))
            target = state / "State-Manifest.json"
            result, reply = self.call(root, "create", target, b"original")
            self.assertEqual((result.returncode, reply["status"]), (0, "PASS"))
            result, baseline = self.call(root, "read", target)
            self.assertEqual(result.returncode, 0, result.stderr)
            result, reply = self.call(root, "update", target, b"updated", baseline)
            self.assertEqual((result.returncode, reply["status"]), (0, "PASS"))
            self.assertEqual(target.read_bytes(), b"updated")
            backups = list(state.glob("State-Manifest.json.before-update-*.bak"))
            self.assertEqual(len(backups), 1)
            self.assertEqual(backups[0].read_bytes(), b"original")
            result, reply = self.call(root, "update", target, b"stale", baseline)
            self.assertNotEqual(result.returncode, 0)
            self.assertEqual(target.read_bytes(), b"updated")
            result, reply = self.call(root, "create", target, b"overwrite")
            self.assertEqual(reply["status"], "EXISTS")
            self.assertEqual(target.read_bytes(), b"updated")

    def test_target_outside_state_is_refused(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            target = root / "source.txt"
            target.write_bytes(b"source canary")
            result, _ = self.call(root, "create", target, b"other")
            self.assertNotEqual(result.returncode, 0)
            self.assertEqual(target.read_bytes(), b"source canary")

    def test_changed_project_identity_is_rejected_before_state_creation(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            target = root / "Shared-Project-State"
            request = {"project_root": str(root), "root_identity": ["0", "0"],
                       "action": "mkdir", "path": str(target)}
            result = subprocess.run([sys.executable, str(SCRIPT)], input=json.dumps(request),
                                    text=True, capture_output=True)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("identity changed", json.loads(result.stdout)["reason"])
            self.assertFalse(target.exists())


if __name__ == "__main__":
    unittest.main()
