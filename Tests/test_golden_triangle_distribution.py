"""Distribution entry guidance must describe the policy without claiming hooks."""

import importlib.util
import os
import shutil
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
from test_support import CORE_ROOT
sys.path.insert(0, str(CORE_ROOT))
from aipm_core import capabilities


class DistributionEntryTests(unittest.TestCase):
    def test_bridge_requires_manager_then_both_policies(self):
        text = capabilities._agent_bridge_document()
        positions = [text.index(name) if name in text else -1 for name in (
            "project-manager", "task-scope-contract", "resource-optimization")]
        self.assertTrue(all(index >= 0 for index in positions), "Triangle entry guidance is missing")
        self.assertEqual(positions, sorted(positions))
        self.assertIn("INSTRUCTION_ONLY", text)
        self.assertIn("explicit owner request", text)

    def test_existing_bridge_is_recognized_for_safe_upgrade(self):
        old = ROOT / "Plugins/aipm-project-agent-bridge"
        result = capabilities._validate_upgradeable_embedded_plugin(ROOT, old)
        self.assertEqual(result["plugin_name"], capabilities.PLUGIN_SLUG)

    def test_legacy_guidance_is_accepted_for_pre_manager_inventory(self):
        catalog = capabilities.scan_library(ROOT)
        catalog["skills"] = [item for item in catalog["skills"] if item["slug"] != "project-manager"]
        with tempfile.TemporaryDirectory(dir=ROOT / "Shared-Project-State-Manager/Test-Workspace") as temporary:
            old = Path(temporary) / "bridge"
            old.mkdir()
            capabilities._materialize_plugin(ROOT, old, catalog, "1.2.4", previous_version=None, previous_changelog=None)
            (old / "AIPM-Agent-Bridge.md").write_text(capabilities._legacy_agent_bridge_document(), encoding="utf-8", newline="\n")
            result = capabilities._validate_upgradeable_embedded_plugin(ROOT, old)
            self.assertNotIn("project-manager", {item["slug"] for item in result["skills"]})

    def test_unrecognized_bridge_changes_cannot_be_upgraded(self):
        source = ROOT / "Plugins/aipm-project-agent-bridge"
        with tempfile.TemporaryDirectory(dir=ROOT / "Shared-Project-State-Manager/Test-Workspace") as temporary:
            target = Path(temporary) / "bridge"
            shutil.copytree(source, target)
            with (target / "AIPM-Agent-Bridge.md").open("a", encoding="utf-8") as stream:
                stream.write("\nUnexpected modification\n")
            with self.assertRaises(capabilities.CapabilityError):
                capabilities._validate_upgradeable_embedded_plugin(ROOT, target)

    def test_new_inventory_cannot_be_downgraded_to_legacy_guidance(self):
        source = ROOT / "Plugins/aipm-project-agent-bridge"
        with tempfile.TemporaryDirectory(dir=ROOT / "Shared-Project-State-Manager/Test-Workspace") as temporary:
            target = Path(temporary) / "bridge"
            shutil.copytree(source, target)
            (target / "AIPM-Agent-Bridge.md").write_text(capabilities._legacy_agent_bridge_document(), encoding="utf-8", newline="\n")
            with self.assertRaises(capabilities.CapabilityError):
                capabilities._validate_upgradeable_embedded_plugin(ROOT, target)

    def test_all_host_staging_readmes_describe_entry_limits(self):
        path = ROOT / "Plugins/Build-System/build_plugins.py"
        spec = importlib.util.spec_from_file_location("triangle_builder", path)
        builder = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(builder)
        catalog = capabilities.scan_library(ROOT)
        profiles = builder.load_profiles(ROOT)
        with tempfile.TemporaryDirectory(dir=ROOT / "Shared-Project-State-Manager/Test-Workspace") as temporary:
            for profile in profiles:
                stage = Path(temporary) / profile["id"]
                stage.mkdir()
                builder._materialize(ROOT, stage, profile, catalog)
                text = (stage / "README.md").read_text(encoding="utf-8")
                for term in ("project-manager", "task-scope-contract", "resource-optimization", "INSTRUCTION_ONLY"):
                    self.assertIn(term, text, profile["id"])

    def test_staging_override_must_be_existing_and_inside_project(self):
        workspace = ROOT / "Shared-Project-State-Manager/Test-Workspace"
        self.assertTrue(hasattr(capabilities, "plugin_workspace"), "Safe workspace selection is missing")
        with mock.patch.dict(os.environ, {"AIPM_BUILD_WORKSPACE": str(workspace)}):
            self.assertEqual(capabilities.plugin_workspace(ROOT), workspace.resolve())
        with mock.patch.dict(os.environ, {"AIPM_BUILD_WORKSPACE": str(ROOT.parent)}):
            with self.assertRaises(capabilities.CapabilityError):
                capabilities.plugin_workspace(ROOT)
        with mock.patch.dict(os.environ, {"AIPM_BUILD_WORKSPACE": str(workspace)}):
            original = capabilities._has_reparse_point
            with mock.patch.object(capabilities, "_has_reparse_point", side_effect=lambda p: p == workspace.parent or original(p)):
                with self.assertRaises(capabilities.CapabilityError):
                    capabilities.plugin_workspace(ROOT)


if __name__ == "__main__":
    unittest.main()
