from __future__ import annotations

import json
from pathlib import Path
import sys
import tempfile
import unittest

TEST_WORKSPACE = Path(__file__).resolve().parents[1] / ".test-workspace"
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "Core-Engine"))
from aipm_core.storage import ProjectRegistry, StateError, default_registry_path, initialize_project_state


class StateStorageTests(unittest.TestCase):
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
