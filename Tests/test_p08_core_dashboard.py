from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
WORKSPACE = ROOT / ".test-workspace"
sys.path.insert(0, str(ROOT / "Core-Engine"))

from aipm_core.domain import CommandEnvelope, CoreEngine  # noqa: E402
from aipm_core.storage import ProjectRegistry, initialize_project_state  # noqa: E402


class CoreDashboardCliTests(unittest.TestCase):
    def setUp(self) -> None:
        WORKSPACE.mkdir(exist_ok=True)
        self.temp = tempfile.TemporaryDirectory(prefix="p08-dashboard-", dir=WORKSPACE)
        self.root = Path(self.temp.name)
        self.registry = self.root / "registry.json"

    def tearDown(self) -> None:
        self.temp.cleanup()

    def _project(self, project_id: str, alias: str):
        project = initialize_project_state(self.root / project_id, project_id, alias)
        ProjectRegistry(self.registry).register(project)
        return project

    def _cli(self, command: str, *arguments: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(ROOT / "Core-Engine" / "aipm.py"), command, *arguments],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        )

    def test_dashboard_returns_verified_core_state_without_project_paths(self) -> None:
        project = self._project("P08-Dashboard", "Dashboard Fixture")
        engine = CoreEngine({project.project_id: project})
        created = engine.execute(CommandEnvelope(
            "create-task", "task.create", "test", project.project_id, 0, "create-task",
            {"task_id": "Task-P08", "title": "Verify Dashboard", "scope": "Core Projection"},
        ))
        verified = engine.execute(CommandEnvelope(
            "verify-task", "task.verify", "test", project.project_id, 1, "verify-task",
            {"task_id": "Task-P08", "result": "PASS", "evidence": "Unit test passed."},
        ))
        self.assertEqual((created["status"], verified["status"]), ("PASS", "PASS"))

        result = self._cli("dashboard", "--registry", str(self.registry))

        self.assertEqual(result.returncode, 0, result.stderr)
        response = json.loads(result.stdout)
        self.assertEqual(response["status"], "PASS")
        self.assertEqual(response["registry_status"], "REGISTERED")
        self.assertEqual(len(response["projects"]), 1)
        item = response["projects"][0]
        self.assertEqual((item["project_id"], item["alias"], item["state_status"]), ("P08-Dashboard", "Dashboard Fixture", "PASS"))
        self.assertEqual(item["state"]["tasks"]["Task-P08"]["verification"]["result"], "PASS")
        self.assertNotIn(str(project.root), result.stdout)
        self.assertNotIn("state_root", item)

    def test_dashboard_distinguishes_unregistered_registry_from_verified_zero_progress(self) -> None:
        missing = self.root / "not-created.json"

        result = self._cli("dashboard", "--registry", str(missing))

        self.assertEqual(result.returncode, 0, result.stderr)
        response = json.loads(result.stdout)
        self.assertEqual((response["status"], response["registry_status"], response["projects"]), ("PASS", "NOT_REGISTERED", []))
        self.assertNotIn("progress", result.stdout.lower())

    def test_dashboard_isolates_invalid_project_state_and_keeps_valid_projects(self) -> None:
        invalid = self._project("P08-Broken", "Broken Fixture")
        valid = self._project("P08-Healthy", "Healthy Fixture")
        (invalid.state_root / "State-Manifest.json").write_text("{broken", encoding="utf-8")

        result = self._cli("dashboard", "--registry", str(self.registry))

        self.assertEqual(result.returncode, 0, result.stderr)
        response = json.loads(result.stdout)
        by_id = {item["project_id"]: item for item in response["projects"]}
        self.assertEqual(set(by_id), {"P08-Broken", "P08-Healthy"})
        self.assertEqual((by_id["P08-Broken"]["state_status"], by_id["P08-Broken"]["state"]), ("UNVERIFIED", None))
        self.assertEqual(by_id["P08-Healthy"]["state_status"], "PASS")

    def test_dashboard_rejects_malformed_registry_without_writing_it(self) -> None:
        self.registry.write_text(json.dumps({"schema_version": "9.9", "projects": []}), encoding="utf-8")
        before = self.registry.read_bytes()

        result = self._cli("dashboard", "--registry", str(self.registry))

        self.assertEqual(result.returncode, 1)
        self.assertEqual(json.loads(result.stdout), {"schema_version": "1.0", "status": "BLOCKED", "reason": "INVALID_REGISTRY"})
        self.assertEqual(self.registry.read_bytes(), before)

    def test_catalog_reports_registered_skills_and_uninstalled_local_sample_read_only(self) -> None:
        registry = ROOT / "Capability-Library" / "Registry.json"
        before = registry.read_bytes()

        result = self._cli("catalog")

        self.assertEqual(result.returncode, 0, result.stderr)
        response = json.loads(result.stdout)
        self.assertEqual(response["status"], "PASS")
        self.assertEqual(response["catalog"]["skill_count"], 12)
        self.assertEqual(response["catalog"]["integrity_status"], "UNVERIFIED")
        self.assertEqual(response["catalog"]["first_party_skills"], ["tui-intelligence"])
        self.assertEqual(response["catalog"]["plugin_sample"]["status"], "PACKAGE_SAMPLE_ONLY")
        self.assertEqual(response["catalog"]["plugin_sample"]["installation"], "UNVERIFIED")
        self.assertEqual(response["catalog"]["plugin_sample"]["publication"], "UNVERIFIED")
        self.assertEqual(registry.read_bytes(), before)


if __name__ == "__main__":
    unittest.main()
