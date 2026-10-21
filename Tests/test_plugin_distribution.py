"""Tests for AIPM multi-host Plugin archive distribution."""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest import mock
import zipfile


ROOT = Path(__file__).resolve().parents[1]
BUILDER_PATH = ROOT / "Plugins" / "Build-System" / "build_plugins.py"


def load_builder():
    spec = importlib.util.spec_from_file_location("aipm_plugin_builder", BUILDER_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("Plugin builder module could not be loaded")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class PluginDistributionTests(unittest.TestCase):
    def test_profile_contracts(self) -> None:
        builder = load_builder()
        profiles = {item["id"]: item for item in builder.load_profiles(ROOT)}

        self.assertEqual(set(profiles), {"chatgpt", "claude", "antigavity"})
        self.assertEqual(profiles["chatgpt"]["archive_prefix"], "AIPM-ChatGPT-Plugin")
        self.assertEqual(profiles["claude"]["archive_prefix"], "AIPM-Claude-Plugin")
        self.assertEqual(profiles["antigavity"]["archive_prefix"], "AIPM-Antigavity-Plugin")
        self.assertEqual(profiles["chatgpt"]["format_status"], "FORMAT_VERIFIED")
        self.assertEqual(profiles["claude"]["format_status"], "FORMAT_VERIFIED")
        self.assertEqual(profiles["antigavity"]["format_status"], "FORMAT_UNVERIFIED")
        self.assertEqual(
            profiles["chatgpt"]["manifest_paths"],
            ["plugin.json", ".codex-plugin/plugin.json"],
        )
        self.assertEqual(profiles["claude"]["manifest_paths"], [".claude-plugin/plugin.json"])
        self.assertEqual(profiles["antigavity"]["manifest_paths"], ["antigavity-plugin.json"])

    def test_builds_all_profiles_with_full_inventory(self) -> None:
        builder = load_builder()
        with tempfile.TemporaryDirectory(prefix="plugin-dist-", dir=ROOT / ".test-workspace") as temporary:
            output = Path(temporary) / "dist"
            results = builder.build_archives(ROOT, ["chatgpt", "claude", "antigavity"], output)
            catalog = json.loads((ROOT / "Capability-Library" / "Registry.json").read_text(encoding="utf-8"))

            self.assertEqual([item["platform"] for item in results], ["chatgpt", "claude", "antigavity"])
            for result in results:
                archive = result["archive"]
                self.assertTrue(archive.is_file())
                self.assertTrue(result["sha256"].is_file())
                validation = builder.validate_archive(ROOT, archive, result["platform"])
                self.assertEqual(validation["status"], "PASS")
                with zipfile.ZipFile(archive) as package:
                    names = set(package.namelist())
                    self.assertIn("prompts/Autonomous-Task-Execution.md", names)
                    self.assertIn("licenses/Apache-2.0.txt", names)
                    self.assertIn("NOTICE", names)
                    self.assertNotIn("skills/import-memory/SKILL.md", names)
                    self.assertNotIn("skills/morning/SKILL.md", names)
                    for skill in catalog["skills"]:
                        self.assertIn(f"skills/{skill['slug']}/SKILL.md", names)

    def test_chatgpt_archive_has_uploadable_manifests_and_skill_front_matter(self) -> None:
        builder = load_builder()
        with tempfile.TemporaryDirectory(prefix="plugin-dist-", dir=ROOT / ".test-workspace") as temporary:
            archive = builder.build_archives(ROOT, ["chatgpt"], Path(temporary) / "dist")[0]["archive"]
            with zipfile.ZipFile(archive) as package:
                portable = json.loads(package.read("plugin.json"))
                codex = json.loads(package.read(".codex-plugin/plugin.json"))
                project_url = "https://github.com/Abdulrahman3M/AI-Project-Manager-AIPM/"
                self.assertEqual(portable["$schema"], "https://agent-plugins.org/schemas/1.0.0/plugin.schema.json")
                self.assertEqual(portable["author"]["name"], "Abdulrahman Elbatrah")
                self.assertEqual(portable.get("homepage"), project_url)
                self.assertEqual(portable.get("repository"), project_url)
                self.assertEqual(portable["extensions"]["com.openai"]["interface"].get("websiteURL"), project_url)
                self.assertEqual(codex["interface"]["developerName"], "Abdulrahman Elbatrah")
                self.assertIn("displayName", codex["interface"])
                self.assertIn("shortDescription", codex["interface"])
                self.assertEqual(codex["interface"].get("websiteURL"), project_url)
                self.assertEqual(codex.get("homepage"), project_url)
                self.assertEqual(codex.get("repository"), project_url)
                for skill_path in (name for name in package.namelist() if name.startswith("skills/") and name.endswith("/SKILL.md")):
                    self.assertTrue(package.read(skill_path).startswith(b"---\n"), skill_path)

    def test_every_host_archive_documents_the_project_website(self) -> None:
        builder = load_builder()
        project_url = "https://github.com/Abdulrahman3M/AI-Project-Manager-AIPM/"
        with tempfile.TemporaryDirectory(prefix="plugin-dist-", dir=ROOT / ".test-workspace") as temporary:
            results = builder.build_archives(ROOT, ["chatgpt", "claude", "antigavity"], Path(temporary) / "dist")
            for result in results:
                with zipfile.ZipFile(result["archive"]) as package:
                    readme = package.read("README.md").decode("utf-8")
                    self.assertIn(project_url, readme, result["platform"])

    def test_archive_tampering_and_policy_gates_fail_closed(self) -> None:
        builder = load_builder()
        with tempfile.TemporaryDirectory(prefix="plugin-dist-", dir=ROOT / ".test-workspace") as temporary:
            output = Path(temporary) / "dist"
            archive = builder.build_archives(ROOT, ["chatgpt"], output)[0]["archive"]
            with zipfile.ZipFile(archive, "a") as package:
                package.writestr("skills/import-memory/SKILL.md", "forbidden")
            sidecar = archive.with_name(archive.name + ".sha256")
            sidecar.write_text(f"{builder._sha256_file(archive)}  {archive.name}\n", encoding="utf-8")
            with self.assertRaises(builder.PluginBuildError):
                builder.validate_archive(ROOT, archive, "chatgpt")
            with self.assertRaises(builder.PluginBuildError):
                builder.build_archives(ROOT, ["unknown"], output)
            with mock.patch.object(builder, "_capabilities", side_effect=builder.PluginBuildError("stale registry")):
                with self.assertRaises(builder.PluginBuildError):
                    builder.build_archives(ROOT, ["chatgpt"], output)

    def test_operator_documentation_is_actionable_and_safe(self) -> None:
        readme = (ROOT / "Plugins" / "README.md").read_text(encoding="utf-8")
        quick_start = (ROOT / "Plugins" / "Build-System" / "Quick-Start.md").read_text(encoding="utf-8")
        wrapper = (ROOT / "Plugins" / "Build-System" / "Build-AIPM-Plugin.ps1").read_text(encoding="utf-8")

        self.assertIn("Build-AIPM-Plugin.ps1", readme)
        self.assertIn("Quick-Start.md", readme)
        self.assertIn("legacy compatibility", readme.casefold())
        self.assertIn("-Platform ChatGPT", quick_start)
        self.assertIn("-Platform All", quick_start)
        self.assertIn("does not install", quick_start.casefold())
        self.assertIn("Validate", wrapper)


if __name__ == "__main__":
    unittest.main()
