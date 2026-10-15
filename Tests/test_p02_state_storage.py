from __future__ import annotations

import json
import csv
from contextlib import contextmanager
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

TEST_WORKSPACE = Path(__file__).resolve().parents[1] / ".test-workspace"
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "Core-Engine"))
from aipm_core.storage import ProjectRegistry, StateError, default_registry_path, initialize_project_state


class StateStorageTests(unittest.TestCase):
    @contextmanager
    def _junction(self, link: Path, target: Path) -> None:
        result = subprocess.run(["cmd", "/c", "mklink", "/J", str(link), str(target)], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, f"UNVERIFIED: Windows junction creation failed: {result.stdout} {result.stderr}")
        try:
            yield
        finally:
            link.rmdir()

    @contextmanager
    def _deny_file_creation(self, directory: Path) -> None:
        identity = subprocess.run(["whoami", "/user", "/fo", "csv", "/nh"], capture_output=True, text=True, check=True)
        sid = next(csv.reader(identity.stdout.splitlines()))[1]
        denial = subprocess.run(["icacls", str(directory), "/deny", f"*{sid}:(OI)(CI)(WD)"], capture_output=True, text=True)
        try:
            self.assertEqual(denial.returncode, 0, f"UNVERIFIED: Windows ACL denial failed: {denial.stdout} {denial.stderr}")
            with self.assertRaises(PermissionError, msg="UNVERIFIED: ACL did not deny real file creation"):
                (directory / "Denied-Probe.txt").write_text("Denied", encoding="utf-8")
            yield
        finally:
            restore = subprocess.run(["icacls", str(directory), "/remove:d", f"*{sid}", "/t", "/c"], capture_output=True, text=True)
            self.assertEqual(restore.returncode, 0, f"ACL restoration failed: {restore.stdout} {restore.stderr}")

    def test_acl_denial_leaves_no_partial_state_tree(self) -> None:
        TEST_WORKSPACE.mkdir(exist_ok=True)
        with tempfile.TemporaryDirectory(dir=TEST_WORKSPACE) as temporary:
            project = Path(temporary) / "Project"
            project.mkdir()
            with self._deny_file_creation(project):
                try:
                    with self.assertRaisesRegex(StateError, "access denied"):
                        initialize_project_state(project, "project", "Project")
                finally:
                    self.assertFalse((project / "Shared-Project-State-Manager").exists())
                    self.assertEqual(list(project.glob(".aipm-*")), [])

    def test_inherited_directory_acl_denial_leaves_no_partial_state_tree(self) -> None:
        TEST_WORKSPACE.mkdir(exist_ok=True)
        with tempfile.TemporaryDirectory(dir=TEST_WORKSPACE) as temporary:
            project = Path(temporary) / "Project"
            project.mkdir()
            access_check = project / "Access-Check"
            access_check.mkdir()
            identity = subprocess.run(["whoami", "/user", "/fo", "csv", "/nh"], capture_output=True, text=True, check=True)
            sid = next(csv.reader(identity.stdout.splitlines()))[1]
            denial = subprocess.run(["icacls", str(project), "/deny", f"*{sid}:(CI)(IO)(AD)"], capture_output=True, text=True)
            try:
                self.assertEqual(denial.returncode, 0, f"UNVERIFIED: Windows ACL denial failed: {denial.stdout} {denial.stderr}")
                permitted_file = access_check / "Permitted.txt"
                permitted_file.write_text("File Creation Is Allowed", encoding="utf-8")
                permitted_file.unlink()
                with self.assertRaises(PermissionError, msg="UNVERIFIED: ACL did not deny real child-directory creation"):
                    (access_check / "Denied-Directory").mkdir()
                try:
                    with self.assertRaisesRegex(StateError, "access denied"):
                        initialize_project_state(project, "project", "Project")
                finally:
                    self.assertFalse((project / "Shared-Project-State-Manager").exists())
                    self.assertEqual(set(project.iterdir()), {access_check})
            finally:
                restore = subprocess.run(["icacls", str(project), "/remove:d", f"*{sid}", "/t", "/c"], capture_output=True, text=True)
                self.assertEqual(restore.returncode, 0, f"ACL restoration failed: {restore.stdout} {restore.stderr}")

    def test_registry_acl_denial_preserves_existing_registry(self) -> None:
        TEST_WORKSPACE.mkdir(exist_ok=True)
        with tempfile.TemporaryDirectory(dir=TEST_WORKSPACE) as temporary:
            base = Path(temporary)
            registry = ProjectRegistry(base / "User-Data" / "registry.json")
            first = initialize_project_state(base / "Project-One", "project-one", "Project One")
            second = initialize_project_state(base / "Project-Two", "project-two", "Project Two")
            registry.register(first)
            original = registry.path.read_bytes()
            with self._deny_file_creation(registry.path.parent):
                try:
                    with self.assertRaisesRegex(StateError, "access denied"):
                        registry.register(second)
                finally:
                    self.assertEqual(registry.path.read_bytes(), original)
                    self.assertEqual(list(registry.path.parent.glob(".aipm-*")), [])

    def test_rejects_junction_in_project_root_path(self) -> None:
        TEST_WORKSPACE.mkdir(exist_ok=True)
        with tempfile.TemporaryDirectory(dir=TEST_WORKSPACE) as temporary:
            base = Path(temporary)
            target = base / "Target"
            target.mkdir()
            link = base / "Junction"
            with self._junction(link, target):
                with self.assertRaises(StateError):
                    initialize_project_state(link / "Project", "project", "Project")
                self.assertFalse((target / "Project" / "Shared-Project-State-Manager").exists())

    def test_rejects_junction_in_existing_state_path(self) -> None:
        TEST_WORKSPACE.mkdir(exist_ok=True)
        with tempfile.TemporaryDirectory(dir=TEST_WORKSPACE) as temporary:
            base = Path(temporary)
            project = base / "Project"
            project.mkdir()
            target = base / "Target"
            target.mkdir()
            link = project / "Shared-Project-State-Manager"
            with self._junction(link, target):
                with self.assertRaisesRegex(StateError, "reparse"):
                    initialize_project_state(project, "project", "Project")
                self.assertEqual(list(target.iterdir()), [])

    def test_new_state_manifest_uses_schema_1_1_fields(self) -> None:
        TEST_WORKSPACE.mkdir(exist_ok=True)
        with tempfile.TemporaryDirectory(dir=TEST_WORKSPACE) as temporary:
            project = initialize_project_state(Path(temporary) / "Project", "project", "Project")
            state = json.loads((project.state_root / "State-Manifest.json").read_text())
            self.assertEqual(state["schema_version"], "1.1")
            self.assertEqual(state["tasks"], {})
            self.assertIsNone(state["diff_fingerprint"])
            manifest = json.loads((project.state_root / "Project-Manifest.json").read_text())
            self.assertEqual(manifest["schema_version"], "1.0")
            self.assertEqual(list(Path(temporary).rglob(".aipm-*")), [])

    def test_default_registry_is_outside_platform_root(self) -> None:
        path = default_registry_path()
        self.assertEqual(path.name, "registry.json")
        self.assertIn("AI-Project-Manager", str(path.parent))
    def test_initializes_two_distinct_external_projects_and_registry_has_pointers_only(self) -> None:
        TEST_WORKSPACE.mkdir(exist_ok=True)
        with tempfile.TemporaryDirectory(dir=TEST_WORKSPACE) as temporary:
            base = Path(temporary)
            registry = ProjectRegistry(base / "User-Data" / "registry.json")
            first = initialize_project_state(base / "Project-One", "project-one", "Project One")
            second = initialize_project_state(base / "Project-Two", "project-two", "Project Two")
            registry.register(first)
            registry.register(second)
            data = json.loads((base / "User-Data" / "registry.json").read_text())
            self.assertEqual([item["project_id"] for item in data["projects"]], ["project-one", "project-two"])
            self.assertNotIn("tasks", data)
            self.assertTrue((first.state_root / "Project-Manifest.json").exists())
            self.assertTrue((second.state_root / "State-Manifest.json").exists())

    def test_rejects_state_root_inside_platform_and_legacy_collision(self) -> None:
        TEST_WORKSPACE.mkdir(exist_ok=True)
        with tempfile.TemporaryDirectory(dir=TEST_WORKSPACE) as temporary:
            base = Path(temporary)
            with self.assertRaises(StateError):
                initialize_project_state(base / "Platform", "platform", "Platform", platform_root=base)
            project = base / "Legacy"
            (project / "Shared-Project-State").mkdir(parents=True)
            with self.assertRaises(StateError):
                initialize_project_state(project, "legacy", "Legacy")

    def test_refuses_existing_state_root_and_traversal_alias(self) -> None:
        TEST_WORKSPACE.mkdir(exist_ok=True)
        with tempfile.TemporaryDirectory(dir=TEST_WORKSPACE) as temporary:
            base = Path(temporary)
            project = base / "Project"
            initialize_project_state(project, "project", "Project")
            with self.assertRaises(StateError):
                initialize_project_state(project, "project", "Project")
            with self.assertRaises(StateError):
                initialize_project_state(base / "nested" / ".." / "Project", "project-two", "Project Two")


if __name__ == "__main__":
    unittest.main()
