import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

SKILL = Path(__file__).resolve().parents[1]
POWERSHELL = shutil.which("pwsh")


@unittest.skipUnless(POWERSHELL and shutil.which("node"), "PowerShell or Node unavailable")
class PowerShellStateToolTests(unittest.TestCase):
    def test_explicit_init_and_copied_router_in_disposable_project(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            wrapper = SKILL / "scripts" / "sps.ps1"
            result = subprocess.run([POWERSHELL, "-NoProfile", "-File", str(wrapper), "init",
                                     "--project-root", str(root), "--task-id", "Task-Test",
                                     "--title", "Test", "--agent", "Test"],
                                    text=True, capture_output=True, timeout=90)
            self.assertEqual(result.returncode, 0, result.stderr)
            state = root / "Shared-Project-State"
            self.assertTrue((state / "State-Manifest.json").is_file())
            self.assertTrue((state / "safe_move.py").is_file())
            router = state / "Route-Transient-State.ps1"
            checked = subprocess.run([POWERSHELL, "-NoProfile", "-File", str(router),
                                      "-ProjectRoot", str(root), "-Status"],
                                     text=True, capture_output=True, timeout=45)
            self.assertEqual(checked.returncode, 0, checked.stderr)
            self.assertFalse((root / "Shared-Project-State-Manager").exists())
