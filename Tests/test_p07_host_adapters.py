from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "Core-Engine"))

from aipm_core.domain import CoreEngine  # noqa: E402
from aipm_core.host_adapters import (  # noqa: E402
    HostAdapter,
    accept_manual_handoff,
    create_manual_handoff,
    load_capability_matrix,
)
from aipm_core.storage import initialize_project_state  # noqa: E402


class HostAdapterContractTests(unittest.TestCase):
    def setUp(self) -> None:
        workspace = ROOT / ".test-workspace"
        workspace.mkdir(exist_ok=True)
        self.temp = tempfile.TemporaryDirectory(prefix="p07-host-", dir=workspace)
        self.project = initialize_project_state(Path(self.temp.name) / "Managed-Project", "P07-Fixture", "P07 Fixture")
        self.engine = CoreEngine({self.project.project_id: self.project})

    def tearDown(self) -> None:
        self.temp.cleanup()

    def test_capability_matrix_declares_supported_and_unsupported_hosts(self) -> None:
        matrix = load_capability_matrix(ROOT)
        hosts = {item["id"]: item for item in matrix["hosts"]}
        self.assertEqual(matrix["schema_version"], "1.0")
        self.assertIn("state.read", hosts["local-cli"]["core_commands"])
        self.assertEqual(hosts["chatgpt-text"]["local_project_access"], "UNAVAILABLE")
        self.assertEqual(hosts["chatgpt-text"]["core_commands"], [])
        self.assertEqual(hosts["codex-plugin"]["package_format_status"], "FORMAT_VERIFIED")
        self.assertEqual(hosts["claude-code-plugin"]["package_format_status"], "FORMAT_VERIFIED")
        self.assertEqual(hosts["gemini-cli-extension"]["runtime_status"], "UNVERIFIED")

    def test_cli_exposes_matrix_as_read_only_json(self) -> None:
        result = subprocess.run([sys.executable, str(ROOT / "Core-Engine" / "aipm.py"), "host-capabilities"], cwd=ROOT, capture_output=True, text=True, check=False)
        self.assertEqual(result.returncode, 0, result.stderr)
        response = json.loads(result.stdout)
        self.assertEqual(response["status"], "PASS")
        self.assertIn("local-cli", {host["id"] for host in response["matrix"]["hosts"]})

    def test_local_adapter_delegates_read_to_core_without_exposing_project_path(self) -> None:
        adapter = HostAdapter(self.engine, self.project.project_id, "local-cli", root=ROOT)
        result = adapter.execute("state.read")
        self.assertEqual(result["status"], "PASS")
        self.assertEqual(result["state"]["project_id"], self.project.project_id)
        self.assertNotIn("root", result)
        self.assertNotIn("state_root", result)

    def test_read_only_mode_blocks_mutations_before_core_dispatch(self) -> None:
        adapter = HostAdapter(self.engine, self.project.project_id, "local-cli", root=ROOT)
        with mock.patch.object(self.engine, "execute", wraps=self.engine.execute) as dispatch:
            result = adapter.execute("task.create", {"task_id": "Task-P07", "title": "Adapter", "scope": "Contract"}, expected_revision=0, idempotency_key="key")
        self.assertEqual((result["status"], result["reason"]), ("BLOCKED", "WRITE_NOT_AUTHORIZED"))
        dispatch.assert_not_called()
        state = adapter.execute("state.read")
        self.assertEqual(state["state"]["tasks"], {})

    def test_explicit_write_grant_delegates_mutation_through_core_revision_and_idempotency(self) -> None:
        adapter = HostAdapter(self.engine, self.project.project_id, "local-cli", root=ROOT, allow_mutations=True)
        result = adapter.execute("task.create", {"task_id": "Task-P07", "title": "Adapter Contract", "scope": "Core Engine"}, expected_revision=0, idempotency_key="p07-task-create")
        self.assertEqual(result["status"], "PASS")
        state = adapter.execute("state.read")
        self.assertEqual(state["state"]["tasks"]["Task-P07"]["title"], "Adapter Contract")
        self.assertEqual(state["revision"], 1)

    def test_mutation_requires_idempotency_and_stale_revision_is_rejected(self) -> None:
        adapter = HostAdapter(self.engine, self.project.project_id, "local-cli", root=ROOT, allow_mutations=True)
        missing_key = adapter.execute("task.create", {"task_id": "Task-P07", "title": "Adapter", "scope": "Contract"}, expected_revision=0)
        self.assertEqual((missing_key["status"], missing_key["reason"]), ("BLOCKED", "INVALID_INPUT"))
        accepted = adapter.execute("task.create", {"task_id": "Task-P07", "title": "Adapter", "scope": "Contract"}, expected_revision=0, idempotency_key="create-1")
        stale = adapter.execute("task.create", {"task_id": "Task-P07-2", "title": "Second", "scope": "Conflict"}, expected_revision=0, idempotency_key="create-2")
        self.assertEqual(accepted["status"], "PASS")
        self.assertEqual((stale["status"], stale["reason"], stale["revision"]), ("BLOCKED", "STATE_CONFLICT", 1))

    def test_unsupported_host_and_command_fail_closed_without_dispatch(self) -> None:
        adapter = HostAdapter(self.engine, self.project.project_id, "chatgpt-text", root=ROOT, allow_mutations=True)
        with mock.patch.object(self.engine, "execute", wraps=self.engine.execute) as dispatch:
            unsupported_host = adapter.execute("state.read")
            unsupported_command = HostAdapter(self.engine, self.project.project_id, "local-cli", root=ROOT).execute("filesystem.delete", {"path": "anywhere"})
        self.assertEqual((unsupported_host["status"], unsupported_host["reason"]), ("BLOCKED", "HOST_NO_LOCAL_BRIDGE"))
        self.assertEqual((unsupported_command["status"], unsupported_command["reason"]), ("BLOCKED", "UNSUPPORTED_CAPABILITY"))
        dispatch.assert_not_called()

    def test_unregistered_project_is_rejected_by_core_without_cross_project_access(self) -> None:
        adapter = HostAdapter(self.engine, "Other-Project", "local-cli", root=ROOT)
        result = adapter.execute("state.read")
        self.assertEqual((result["status"], result["reason"]), ("BLOCKED", "PROJECT_NOT_REGISTERED"))

    def test_manual_handoff_is_read_only_unverified_and_cannot_be_imported_as_state(self) -> None:
        adapter = HostAdapter(self.engine, self.project.project_id, "local-cli", root=ROOT)
        handoff = create_manual_handoff(adapter.execute("state.read"), project_alias="P07 Fixture")
        self.assertEqual(handoff["status"], "UNVERIFIED")
        self.assertEqual(handoff["handoff"]["verification"], "UNVERIFIED")
        serialized = json.dumps(handoff)
        self.assertNotIn(str(self.project.root), serialized)
        self.assertEqual(accept_manual_handoff(adapter, handoff)["reason"], "MANUAL_HANDOFF_REQUIRES_LOCAL_REVALIDATION")
        self.assertEqual(adapter.execute("state.read")["revision"], 0)


if __name__ == "__main__":
    unittest.main()
