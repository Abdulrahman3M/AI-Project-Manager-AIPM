"""Check the separate local state tool is not implicitly requested."""

import importlib.util
import re
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "01-Skills-General/shared-project-state-manager"


class SharedStateOptInTests(unittest.TestCase):
    def test_entry_documents_require_explicit_powershell_invocation(self):
        for name in ("SKILL.md", "PROMPT.md", "README.md"):
            with self.subTest(name=name):
                text = (SKILL / name).read_text(encoding="utf-8").lower()
                self.assertIn("explicit owner request", text)
                self.assertIn("powershell", text)
                self.assertIn("do not automatically", text)

    def test_resume_does_not_implicitly_activate_state_tool(self):
        text = (ROOT / "01-Skills-General/resume-task/SKILL.md").read_text(encoding="utf-8").lower()
        self.assertIn("explicit owner request", text)
        self.assertIn("do not automatically", text)

    def test_host_guidance_does_not_claim_runtime_enforcement(self):
        text = (ROOT / "Plugins/Adapters/Host-Adapter-Contract.md").read_text(encoding="utf-8")
        for term in ("project-manager", "task-scope-contract", "resource-optimization", "INSTRUCTION_ONLY"):
            self.assertIn(term, text)

    def test_active_guides_use_powershell_entry_points(self):
        paths = [SKILL / "README.md", *(SKILL / "references").glob("*.md"), *(SKILL / "examples").glob("*.md")]
        direct = re.compile(r"(?im)^\s*(?:node\s+[^\n]*sps\.mjs|python\s+[^\n]*(?:safe_file_ops|validate_state|route_transient_state)\.py)")
        for path in paths:
            self.assertIsNone(direct.search(path.read_text(encoding="utf-8")), str(path))

    @unittest.skipUnless(shutil.which("pwsh") and shutil.which("node"), "PowerShell or Node unavailable")
    def test_bootstrap_records_do_not_initialize_but_explicit_powershell_does(self):
        workspace = ROOT / "Shared-Project-State-Manager/Test-Workspace"
        script = ROOT / "01-Skills-General/project-manager/scripts/bootstrap.py"
        spec = importlib.util.spec_from_file_location("bootstrap_opt_in", script)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        with tempfile.TemporaryDirectory(dir=workspace) as temporary:
            project = Path(temporary)
            before = list(project.iterdir())
            for event in ("NEW", "ACTIVE", "RESUME", "REVISE", "REOPEN", "FIX"):
                module.bootstrap(event, "test-task", "v1", "v1")
            self.assertEqual(before, list(project.iterdir()))
            result = subprocess.run(
                [shutil.which("pwsh"), "-NoProfile", "-File", str(SKILL / "scripts/sps.ps1"),
                 "init", "--project-root", str(project), "--task-id", "test-task",
                 "--title", "Test", "--agent", "Test"],
                capture_output=True, text=True, timeout=45,
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertTrue((project / "Shared-Project-State").is_dir())
            validator = SKILL / "scripts/Validate-State.ps1"
            self.assertTrue(validator.is_file(), "PowerShell validation entry is missing")
            checked = subprocess.run(
                [shutil.which("pwsh"), "-NoProfile", "-File", str(validator), "--project-root", str(project)],
                capture_output=True, text=True, timeout=45,
            )
            self.assertEqual(checked.returncode, 0, checked.stdout + checked.stderr)


if __name__ == "__main__":
    unittest.main()
