from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from test_support import CORE_ROOT, CORE_SCRIPT, RUNTIME_ROOT, TEST_WORKSPACE
sys.path.insert(0, str(CORE_ROOT))
from aipm_core.domain import CommandEnvelope, CoreEngine
from aipm_core.storage import ManagedProject, ProjectRegistry, StateError, initialize_project_state


class RegistryAdminTests(unittest.TestCase):
    def cli(self, *arguments: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run([sys.executable, str(CORE_SCRIPT), *arguments], cwd=RUNTIME_ROOT, capture_output=True, text=True)

    def test_core_rejects_managed_state_that_overlaps_its_own_installation(self) -> None:
        project = ManagedProject("aipm-self", "AIPM", RUNTIME_ROOT, RUNTIME_ROOT / "Shared-Project-State-Manager")
        engine = CoreEngine({project.project_id: project})
        for command in ("state.read", "state.set-next-action"):
            payload = {"next_action": "Must Not Write"} if command != "state.read" else {}
            result = engine.execute(CommandEnvelope("read", command, "test", project.project_id, 0, None, payload))
            self.assertEqual((result["status"], result["reason"]), ("BLOCKED", "AIPM_PLATFORM_PROTECTED"))
        self.assertFalse(project.state_root.exists())

    def test_project_registration_rejects_the_aipm_installation_before_writing(self) -> None:
        with self.assertRaisesRegex(StateError, "AIPM_PLATFORM_PROTECTED"):
            initialize_project_state(RUNTIME_ROOT / "TUI", "self-project", "AIPM")
        self.assertFalse((RUNTIME_ROOT / "TUI" / "Shared-Project-State-Manager").exists())

    def test_registry_storage_is_forbidden_inside_the_aipm_installation(self) -> None:
        with self.assertRaisesRegex(StateError, "AIPM_PLATFORM_PROTECTED"):
            ProjectRegistry(RUNTIME_ROOT / "registry.json")
        self.assertFalse((RUNTIME_ROOT / "registry.json").exists())

    def test_dashboard_and_registry_backups_reject_paths_overlapping_the_installation(self) -> None:
        protected_registry = RUNTIME_ROOT / "private" / "registry.json"
        result = self.cli("dashboard", "--registry", str(protected_registry))
        self.assertEqual(result.returncode, 1)
        self.assertEqual(json.loads(result.stdout)["reason"], "AIPM_PLATFORM_PROTECTED")
        with tempfile.TemporaryDirectory(dir=TEST_WORKSPACE) as temporary:
            base = Path(temporary)
            outside_registry = base / "registry.json"
            manager = ProjectRegistry(outside_registry)
            manager.initialize()
            backup = self.cli("registry-backup", "--registry", str(outside_registry), "--destination", str(RUNTIME_ROOT / "backup.json"))
            self.assertEqual(backup.returncode, 1)
            self.assertEqual(json.loads(backup.stdout)["reason"], "AIPM_PLATFORM_PROTECTED")
            self.assertFalse((RUNTIME_ROOT / "backup.json").exists())

    def test_cli_initializes_registers_and_unregisters_without_deleting_project_state(self) -> None:
        with tempfile.TemporaryDirectory(dir=TEST_WORKSPACE) as temporary:
            base = Path(temporary)
            registry = base / "User-Data" / "registry.json"
            project_root = base / "Client-Project"
            initialized = self.cli("registry-init", "--registry", str(registry))
            self.assertEqual(initialized.returncode, 0, initialized.stderr)
            self.assertEqual(json.loads(initialized.stdout)["registry_status"], "READY")

            registered = self.cli("registry-register", "--registry", str(registry), "--project-root", str(project_root), "--project-id", "client-project", "--alias", "Client Project")
            self.assertEqual(registered.returncode, 0, registered.stderr)
            self.assertTrue((project_root / "Shared-Project-State-Manager" / "State-Manifest.json").is_file())
            self.assertEqual(json.loads(registry.read_text(encoding="utf-8"))["projects"][0]["root_path"], str(project_root.resolve()))

            removed = self.cli("registry-unregister", "--registry", str(registry), "--project-id", "client-project")
            self.assertEqual(removed.returncode, 0, removed.stderr)
            self.assertEqual(json.loads(registry.read_text(encoding="utf-8"))["projects"], [])
            self.assertTrue((project_root / "Shared-Project-State-Manager" / "State-Manifest.json").is_file())

    def test_registry_backup_restore_validates_and_keeps_a_pre_restore_backup(self) -> None:
        with tempfile.TemporaryDirectory(dir=TEST_WORKSPACE) as temporary:
            base = Path(temporary)
            registry = base / "registry.json"
            project_one = initialize_project_state(base / "Project-One", "project-one", "Project One")
            project_two = initialize_project_state(base / "Project-Two", "project-two", "Project Two")
            manager = ProjectRegistry(registry)
            manager.initialize()
            manager.register(project_one)
            backup = base / "registry-backup.json"
            created = self.cli("registry-backup", "--registry", str(registry), "--destination", str(backup))
            self.assertEqual(created.returncode, 0, created.stderr)
            self.assertTrue(backup.is_file())
            sidecar = backup.with_suffix(".json.sha256")
            self.assertTrue(sidecar.is_file())
            import hashlib
            self.assertEqual(sidecar.read_text(encoding="ascii").split()[0], hashlib.sha256(backup.read_bytes()).hexdigest())

            manager.register(project_two)
            restored = self.cli("registry-restore", "--registry", str(registry), "--source", str(backup))
            self.assertEqual(restored.returncode, 0, restored.stderr)
            self.assertEqual([item["project_id"] for item in json.loads(registry.read_text(encoding="utf-8"))["projects"]], ["project-one"])
            self.assertEqual(len(list(base.glob("registry.pre-restore-*.json"))), 1)

    def test_restore_refuses_a_changed_checksum_without_modifying_registry(self) -> None:
        with tempfile.TemporaryDirectory(dir=TEST_WORKSPACE) as temporary:
            base = Path(temporary)
            project = initialize_project_state(base / "Project", "project-one", "Project One")
            registry_path = base / "registry.json"
            manager = ProjectRegistry(registry_path)
            manager.initialize()
            manager.register(project)
            backup = manager.backup(base / "backup.json")
            before = registry_path.read_bytes()
            backup.write_bytes(backup.read_bytes() + b" ")
            result = self.cli("registry-restore", "--registry", str(registry_path), "--source", str(backup))
            self.assertEqual(result.returncode, 1)
            self.assertEqual(json.loads(result.stdout)["reason"], "BACKUP_CHECKSUM_MISMATCH")
            self.assertEqual(registry_path.read_bytes(), before)
            self.assertEqual(list(base.glob("registry.pre-restore-*.json")), [])

    def test_cli_rejects_registration_of_its_own_installation_without_side_effects(self) -> None:
        with tempfile.TemporaryDirectory(dir=TEST_WORKSPACE) as temporary:
            registry = Path(temporary) / "registry.json"
            self.assertEqual(self.cli("registry-init", "--registry", str(registry)).returncode, 0)
            result = self.cli("registry-register", "--registry", str(registry), "--project-root", str(RUNTIME_ROOT), "--project-id", "aipm-self", "--alias", "AIPM")
            self.assertEqual(result.returncode, 1)
            self.assertEqual(json.loads(result.stdout)["reason"], "AIPM_PLATFORM_PROTECTED")
            self.assertEqual(json.loads(registry.read_text(encoding="utf-8"))["projects"], [])
            self.assertFalse((RUNTIME_ROOT / "Shared-Project-State-Manager").exists())


if __name__ == "__main__":
    unittest.main()
