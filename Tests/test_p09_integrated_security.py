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

from aipm_core.domain import CoreEngine  # noqa: E402
from aipm_core.host_adapters import (  # noqa: E402
    HostAdapter,
    accept_manual_handoff,
    create_manual_handoff,
)
from aipm_core.storage import ProjectRegistry, StateError, initialize_project_state  # noqa: E402


class IntegratedSecurityAndCrossSessionTests(unittest.TestCase):
    def setUp(self) -> None:
        WORKSPACE.mkdir(exist_ok=True)
        self.temp = tempfile.TemporaryDirectory(prefix="p09-integration-", dir=WORKSPACE)
        self.root = Path(self.temp.name)
        self.alpha = initialize_project_state(self.root / "Project-Alpha", "P09-Alpha", "Project Alpha")
        self.beta = initialize_project_state(self.root / "Project-Beta", "P09-Beta", "Project Beta")
        self.registry_path = self.root / "registry.json"
        registry = ProjectRegistry(self.registry_path)
        registry.register(self.alpha)
        registry.register(self.beta)
        self.engine = CoreEngine({self.alpha.project_id: self.alpha, self.beta.project_id: self.beta})

    def tearDown(self) -> None:
        self.temp.cleanup()

    def _adapter(self, project_id: str, *, allow_mutations: bool = False) -> HostAdapter:
        return HostAdapter(self.engine, project_id, "local-cli", root=ROOT, allow_mutations=allow_mutations)

    def _cli_dashboard(self) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [
                sys.executable,
                str(ROOT / "Core-Engine" / "aipm.py"),
                "dashboard",
                "--registry",
                str(self.registry_path),
            ],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        )

    def _cli_state_read(self, project_id: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [
                sys.executable,
                str(ROOT / "Core-Engine" / "aipm.py"),
                "state-read",
                "--registry",
                str(self.registry_path),
                "--project-id",
                project_id,
            ],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        )

    def test_agent_core_dashboard_and_fresh_session_preserve_project_boundary(self) -> None:
        agent = self._adapter(self.alpha.project_id, allow_mutations=True)
        commands = [
            ("task.create", 0, "create", {"task_id": "Task-P09-Alpha", "title": "Alpha Private Task", "scope": "Validate exact handoff boundary"}),
            ("task.plan", 1, "plan", {"task_id": "Task-P09-Alpha", "text": "Read current state before continuation."}),
            ("task.verify", 2, "verify", {"task_id": "Task-P09-Alpha", "result": "PASS", "evidence": "P09 integration assertions passed."}),
            ("task.report", 3, "report", {"task_id": "Task-P09-Alpha", "text": "Task lifecycle reached verified completion."}),
        ]
        for command, revision, key, payload in commands:
            with self.subTest(command=command):
                result = agent.execute(command, payload, expected_revision=revision, idempotency_key=f"p09-{key}")
                self.assertEqual(result["status"], "PASS", result)

        dashboard = self._cli_dashboard()
        self.assertEqual(dashboard.returncode, 0, dashboard.stderr)
        projection = json.loads(dashboard.stdout)
        projects = {item["project_id"]: item for item in projection["projects"]}
        self.assertEqual(set(projects), {"P09-Alpha", "P09-Beta"})
        self.assertEqual(projects["P09-Alpha"]["state"]["tasks"]["Task-P09-Alpha"]["verification"]["result"], "PASS")
        self.assertEqual(projects["P09-Alpha"]["state"]["task_status"], "COMPLETE")
        self.assertEqual(projects["P09-Beta"]["state"]["tasks"], {})
        self.assertNotIn(str(self.alpha.root), dashboard.stdout)
        self.assertNotIn(str(self.beta.root), dashboard.stdout)

        outgoing = create_manual_handoff(agent.execute("state.read"), project_alias="Project Alpha")
        self.assertEqual(outgoing["status"], "UNVERIFIED")
        self.assertEqual(outgoing["handoff"]["state_snapshot"]["revision"], 4)
        self.assertNotIn(str(self.alpha.root), json.dumps(outgoing))

        receiving_agent = HostAdapter(
            CoreEngine({self.alpha.project_id: self.alpha, self.beta.project_id: self.beta}),
            self.alpha.project_id,
            "local-cli",
            root=ROOT,
        )
        refused = accept_manual_handoff(receiving_agent, outgoing)
        self.assertEqual(refused["reason"], "MANUAL_HANDOFF_REQUIRES_LOCAL_REVALIDATION")
        fresh = receiving_agent.execute("state.read")
        self.assertEqual((fresh["status"], fresh["revision"]), ("PASS", 4))
        self.assertEqual(fresh["state"]["tasks"]["Task-P09-Alpha"]["report"], "Task lifecycle reached verified completion.")
        fresh_process = self._cli_state_read(self.alpha.project_id)
        self.assertEqual(fresh_process.returncode, 0, fresh_process.stderr)
        process_state = json.loads(fresh_process.stdout)
        self.assertEqual((process_state["status"], process_state["revision"]), ("PASS", 4))
        self.assertNotIn(str(self.alpha.root), fresh_process.stdout)
        cross_project_read = self._adapter(self.beta.project_id).execute("task.read", {"task_id": "Task-P09-Alpha"})
        self.assertEqual((cross_project_read["status"], cross_project_read["reason"]), ("BLOCKED", "TASK_NOT_FOUND"))

    def test_unapproved_receiver_cannot_write_and_stale_revision_is_rejected(self) -> None:
        receiver = self._adapter(self.alpha.project_id)
        blocked = receiver.execute(
            "task.create",
            {"task_id": "Task-P09-Denied", "title": "Denied Write", "scope": "No Explicit Grant"},
            expected_revision=0,
            idempotency_key="p09-denied",
        )
        self.assertEqual((blocked["status"], blocked["reason"]), ("BLOCKED", "WRITE_NOT_AUTHORIZED"))

        writer = self._adapter(self.alpha.project_id, allow_mutations=True)
        created = writer.execute(
            "task.create",
            {"task_id": "Task-P09-Revision", "title": "Revision Guard", "scope": "Reject stale writes"},
            expected_revision=0,
            idempotency_key="p09-revision-create",
        )
        self.assertEqual(created["status"], "PASS")
        stale = writer.execute(
            "task.create",
            {"task_id": "Task-P09-Stale", "title": "Stale Write", "scope": "Must not commit"},
            expected_revision=0,
            idempotency_key="p09-stale-create",
        )
        self.assertEqual((stale["status"], stale["reason"], stale["revision"]), ("BLOCKED", "STATE_CONFLICT", 1))

        state = writer.execute("state.read")
        self.assertEqual(set(state["state"]["tasks"]), {"Task-P09-Revision"})
        self.assertEqual(self._adapter(self.beta.project_id).execute("state.read")["state"]["tasks"], {})

    def test_synthetic_platform_boundary_accepts_sibling_projects_and_rejects_nested_project(self) -> None:
        """Exercise the external-root invariant without writing outside AIPM."""
        synthetic_platform = self.root / "Synthetic-Platform"
        synthetic_platform.mkdir()
        project_a = initialize_project_state(
            self.root / "External-Project-A",
            "P09-Synthetic-A",
            "Synthetic External Project A",
            platform_root=synthetic_platform,
        )
        project_b = initialize_project_state(
            self.root / "External-Project-B",
            "P09-Synthetic-B",
            "Synthetic External Project B",
            platform_root=synthetic_platform,
        )
        self.assertFalse(project_a.root.is_relative_to(synthetic_platform))
        self.assertFalse(project_b.root.is_relative_to(synthetic_platform))
        self.assertNotEqual(project_a.state_root, project_b.state_root)
        with self.assertRaises(StateError):
            initialize_project_state(
                synthetic_platform / "Nested-Project",
                "P09-Nested",
                "Nested Project",
                platform_root=synthetic_platform,
            )


if __name__ == "__main__":
    unittest.main()
