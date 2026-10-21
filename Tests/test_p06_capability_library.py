from __future__ import annotations

import json
import os
from pathlib import Path
import shutil
import sys
import tempfile
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
from test_support import CORE_ROOT
sys.path.insert(0, str(CORE_ROOT))

from aipm_core.capabilities import (  # noqa: E402
    CapabilityError,
    build_plugin,
    bump_semver,
    classify_version_change,
    initialize_registry,
    refresh_registry,
    scan_library,
    validate_plugin,
    validate_registry,
)
from aipm_core import capabilities  # noqa: E402


EXPECTED_SKILLS = {
    "audio-timing-author",
    "browser-environment-manager",
    "create-strict-implementation-handoff",
    "doc-to-md",
    "powershell-tui-app-designer",
    "professional-word-designer",
    "project-governance-manager",
    "project-orchestrator",
    "resume-task",
    "shared-project-state-manager",
    "token-optimization",
    "tui-intelligence",
}

EXPECTED_OWNED_PROMPTS = {
    "browser-environment-manager": ["PROMPT.md"],
    "create-strict-implementation-handoff": [
        "prompts/Strict-Impl-Handoff-Execute.md",
        "prompts/Strict-Impl-Handoff-Request.md",
    ],
    "powershell-tui-app-designer": ["Prompts/Flicker-Free-PowerShell-TUI-Architecture.md"],
    "resume-task": ["PROMPT.md", "prompts/Short-Prompt.md"],
    "shared-project-state-manager": ["PROMPT.md", "prompts/RichViz.md"],
    "tui-intelligence": ["PROMPT.md"],
}


def copy_library_fixture(destination: Path, *, include_registry: bool) -> Path:
    destination.mkdir(parents=True)
    shutil.copytree(ROOT / "01-Skills-General", destination / "01-Skills-General")
    shutil.copytree(ROOT / "02-Prompt-General", destination / "02-Prompt-General")
    provenance = destination / "docs/project" / "Provenance"
    (provenance / "Source-Licenses").mkdir(parents=True)
    for name in ("Skill-Migration-Record.json", "Source-Revision.json"):
        shutil.copy2(ROOT / "docs/project" / "Provenance" / name, provenance / name)
    shutil.copy2(ROOT / "VERSION", destination / "VERSION")
    shutil.copy2(ROOT / "CHANGELOG.md", destination / "CHANGELOG.md")
    shutil.copy2(ROOT / "LICENSE", destination / "LICENSE")
    shutil.copy2(ROOT / "NOTICE", destination / "NOTICE")
    if include_registry:
        shutil.copytree(ROOT / "Capability-Library", destination / "Capability-Library")
    else:
        capability_root = destination / "Capability-Library"
        capability_root.mkdir()
        shutil.copy2(ROOT / "Capability-Library" / "First-Party-Skills.json", capability_root / "First-Party-Skills.json")
    return destination


class CapabilityLibraryTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_root = ROOT / ".test-workspace"
        self.temp_root.mkdir(exist_ok=True)
        self.temp = tempfile.TemporaryDirectory(prefix="p06-", dir=self.temp_root)
        self.workspace = Path(self.temp.name)

    def tearDown(self) -> None:
        self.temp.cleanup()

    def test_inventory_registers_only_approved_skills_and_exact_prompt_relationships(self) -> None:
        catalog = scan_library(ROOT)
        self.assertEqual({item["slug"] for item in catalog["skills"]}, EXPECTED_SKILLS)
        self.assertEqual(len(catalog["skills"]), 12)
        self.assertEqual(catalog["skill_owned_prompts"], EXPECTED_OWNED_PROMPTS)
        self.assertEqual([item["name"] for item in catalog["standalone_prompts"]], ["Autonomous Task Execution"])
        self.assertNotIn("import-memory", {item["slug"] for item in catalog["skills"]})
        self.assertNotIn("morning", {item["slug"] for item in catalog["skills"]})

    def test_aipm_owned_browser_environment_manager_is_not_byte_preserved_import(self) -> None:
        migration = json.loads((ROOT / "docs" / "project" / "Provenance" / "Skill-Migration-Record.json").read_text(encoding="utf-8"))
        first_party = json.loads((ROOT / "Capability-Library" / "First-Party-Skills.json").read_text(encoding="utf-8"))
        self.assertNotIn("browser-environment-manager", migration["byte_preserved_skills"])
        self.assertIn("browser-environment-manager", {item["slug"] for item in first_party["skills"]})

    def test_owner_maintained_powershell_tui_skill_preserves_historical_source_hashes(self) -> None:
        migration = json.loads((ROOT / "docs" / "project" / "Provenance" / "Skill-Migration-Record.json").read_text(encoding="utf-8"))
        first_party = json.loads((ROOT / "Capability-Library" / "First-Party-Skills.json").read_text(encoding="utf-8"))
        slug = "powershell-tui-app-designer"
        self.assertNotIn(slug, migration["byte_preserved_skills"])
        self.assertIn(slug, migration["source_hashes"])
        self.assertIn(slug, {item["slug"] for item in first_party["skills"]})
        self.assertTrue(any(item["slug"] == slug and item["historical_source_hashes_retained"] for item in migration["owner_approved_maintenance"]))

    def test_current_registry_and_generated_plugin_validate(self) -> None:
        registry = validate_registry(ROOT)
        self.assertEqual(registry["status"], "PASS")
        self.assertEqual((registry["skill_count"], registry["standalone_prompt_count"]), (12, 1))
        plugin = validate_plugin(ROOT, ROOT / "Plugins" / "aipm-project-agent-bridge")
        self.assertEqual(plugin["status"], "PASS")
        self.assertEqual(plugin["skill_count"], 12)

    def test_owner_can_remove_a_general_skill_without_a_hardcoded_denylist(self) -> None:
        fixture = copy_library_fixture(self.workspace / "owner-removal", include_registry=False)
        shutil.rmtree(fixture / "01-Skills-General" / "audio-timing-author")
        shutil.rmtree(fixture / "01-Skills-General" / "project-orchestrator")
        shutil.rmtree(fixture / "01-Skills-General" / "tui-intelligence")
        manifest_path = fixture / "Capability-Library" / "First-Party-Skills.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["skills"] = [item for item in manifest["skills"] if item["slug"] != "tui-intelligence"]
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        catalog = scan_library(fixture)
        active = {item["slug"] for item in catalog["skills"]}
        self.assertFalse({"audio-timing-author", "project-orchestrator", "tui-intelligence"} & active)

    def test_owner_can_add_a_declared_first_party_skill(self) -> None:
        fixture = copy_library_fixture(self.workspace / "owner-addition", include_registry=False)
        source = fixture / "01-Skills-General" / "tui-intelligence"
        added = fixture / "01-Skills-General" / "owner-added-test"
        shutil.copytree(source, added)
        skill_doc = added / "SKILL.md"
        skill_doc.write_text(skill_doc.read_text(encoding="utf-8").replace("name: tui-intelligence", "name: owner-added-test", 1), encoding="utf-8")
        manifest_path = fixture / "Capability-Library" / "First-Party-Skills.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        record = dict(manifest["skills"][0])
        record.update({"slug": "owner-added-test", "version": "1.0.0", "source_reference": "Owner-approved test fixture"})
        manifest["skills"].append(record)
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        catalog = scan_library(fixture)
        self.assertIn("owner-added-test", {item["slug"] for item in catalog["skills"]})

    def test_generated_package_is_a_project_agent_bridge_not_a_skill_only_bundle(self) -> None:
        package = ROOT / "Plugins" / "aipm-project-agent-bridge"
        manifest = json.loads((package / "AIPM-Distribution-Manifest.json").read_text(encoding="utf-8"))
        bridge = (package / "AIPM-Agent-Bridge.md").read_text(encoding="utf-8")
        self.assertEqual(manifest["plugin_name"], "aipm-project-agent-bridge")
        self.assertIn("AIPM Core", bridge)
        self.assertIn("does not install", bridge)

    def test_generated_plugin_manifests_publish_the_project_website(self) -> None:
        package = ROOT / "Plugins" / "aipm-project-agent-bridge"
        project_url = "https://github.com/Abdulrahman3M/AI-Project-Manager-AIPM/"
        codex = json.loads((package / ".codex-plugin" / "plugin.json").read_text(encoding="utf-8"))
        portable = json.loads((package / "plugin.json").read_text(encoding="utf-8"))
        self.assertEqual(codex["interface"].get("websiteURL"), project_url)
        self.assertEqual(portable.get("homepage"), project_url)
        self.assertEqual(portable.get("repository"), project_url)

    def test_source_revision_records_verified_read_only_main_commit(self) -> None:
        source = scan_library(ROOT)["source"]
        self.assertEqual(source["repository"], "Abdulrahman3M/Universal-AI-ToolKit")
        self.assertEqual(source["ref"], "main")
        self.assertEqual(source["commit_sha"], "162dcdcac08d36967c00a6b4cadaf3ce8bddb4f2")
        self.assertEqual(source["commit_status"], "VERIFIED")
        self.assertEqual(source["writes"], 0)

    def test_version_classification_and_owner_minor_carry_forward(self) -> None:
        self.assertEqual(classify_version_change({"alpha": "old"}, {"alpha": "new"}), "patch")
        self.assertEqual(classify_version_change({}, {"alpha": "new"}), "minor")
        self.assertEqual(classify_version_change({"alpha": "old"}, {}), "minor")
        self.assertEqual(classify_version_change({}, {}, breaking=True), "major")
        self.assertEqual(bump_semver("0.9.5", "patch", project=True), "0.9.6")
        self.assertEqual(bump_semver("0.9.5", "minor", project=True), "0.10.5")
        self.assertEqual(bump_semver("0.9.5", "minor", project=False), "0.10.0")
        self.assertEqual(bump_semver("0.9.5", "major", project=True), "1.0.0")
        with self.assertRaises(CapabilityError):
            bump_semver("0.9", "patch")

    def test_initial_registry_is_one_time_and_detects_source_drift(self) -> None:
        fixture = copy_library_fixture(self.workspace / "fixture", include_registry=False)
        initialized = initialize_registry(fixture)
        self.assertEqual(initialized["status"], "PASS")
        registry_path = fixture / "Capability-Library" / "Registry.json"
        before = registry_path.read_bytes()
        with self.assertRaises(CapabilityError):
            initialize_registry(fixture)
        self.assertEqual(registry_path.read_bytes(), before)
        changed = fixture / "01-Skills-General" / "audio-timing-author" / "SKILL.md"
        changed.write_text(changed.read_text(encoding="utf-8") + "\nControlled test drift.\n", encoding="utf-8")
        with self.assertRaises(CapabilityError):
            validate_registry(fixture)

    def test_baseline_refresh_cannot_rewrite_a_byte_preserved_import(self) -> None:
        fixture = copy_library_fixture(self.workspace / "immutable", include_registry=False)
        initialize_registry(fixture)
        skill = fixture / "01-Skills-General" / "audio-timing-author"
        skill_doc = skill / "SKILL.md"
        skill_doc.write_text(skill_doc.read_text(encoding="utf-8") + "\nUnauthorized imported edit.\n", encoding="utf-8")
        (skill / "VERSION").write_text("1.0.1\n", encoding="utf-8")
        changelog = skill / "CHANGELOG.md"
        changelog.write_text("## 1.0.1 — Test Edit\n\n- Test fixture.\n\n" + changelog.read_text(encoding="utf-8"), encoding="utf-8")
        (fixture / "VERSION").write_text("0.1.1\n", encoding="utf-8")
        project_log = fixture / "CHANGELOG.md"
        project_log.write_text("## [0.1.1] — Test Edit\n\n- Test fixture.\n\n" + project_log.read_text(encoding="utf-8"), encoding="utf-8")
        with self.assertRaises(CapabilityError):
            refresh_registry(fixture, confirmed=True, reason="An import-byte mutation must stay prohibited")

    def test_malformed_skill_version_fails_closed_before_baseline_creation(self) -> None:
        fixture = copy_library_fixture(self.workspace / "malformed", include_registry=False)
        (fixture / "01-Skills-General" / "audio-timing-author" / "VERSION").write_text("one\n", encoding="utf-8")
        with self.assertRaises(CapabilityError):
            initialize_registry(fixture)
        self.assertFalse((fixture / "Capability-Library" / "Registry.json").exists())

    def test_failed_atomic_write_preserves_existing_bytes_and_cleans_temporary_file(self) -> None:
        record = self.workspace / "atomic.json"
        record.write_bytes(b"original\n")
        with mock.patch.object(capabilities.os, "replace", side_effect=OSError("injected replace failure")):
            with self.assertRaises(CapabilityError):
                capabilities._write_json_atomic(record, {"replacement": True})
        self.assertEqual(record.read_bytes(), b"original\n")
        self.assertEqual(list(self.workspace.glob(".atomic.json.*.tmp")), [])

    def test_failed_second_baseline_record_rolls_back_first_record(self) -> None:
        fixture = copy_library_fixture(self.workspace / "rollback", include_registry=False)
        original_write = capabilities._write_json_atomic

        def fail_ledger(path: Path, document: dict) -> None:
            if path.name == "Capability-Library-Ledger.json":
                raise CapabilityError("Injected ledger failure")
            original_write(path, document)

        with mock.patch.object(capabilities, "_write_json_atomic", side_effect=fail_ledger):
            with self.assertRaises(CapabilityError):
                initialize_registry(fixture)
        self.assertFalse((fixture / "Capability-Library" / "Registry.json").exists())
        self.assertFalse((fixture / "docs/project" / "Provenance" / "Capability-Library-Ledger.json").exists())

    def test_baseline_refresh_requires_confirmation_reason_and_version_policy(self) -> None:
        fixture = copy_library_fixture(self.workspace / "refresh", include_registry=False)
        initialize_registry(fixture)
        skill = fixture / "01-Skills-General" / "project-orchestrator"
        skill_doc = skill / "SKILL.md"
        skill_doc.write_text(skill_doc.read_text(encoding="utf-8") + "\nApproved test edit.\n", encoding="utf-8")
        registry_path = fixture / "Capability-Library" / "Registry.json"
        before = registry_path.read_bytes()
        with self.assertRaises(CapabilityError):
            refresh_registry(fixture, confirmed=False, reason="")
        self.assertEqual(registry_path.read_bytes(), before)
        with self.assertRaises(CapabilityError):
            refresh_registry(fixture, confirmed=True, reason="Test authorization without version updates")
        self.assertEqual(registry_path.read_bytes(), before)
        skill_version = skill / "VERSION"
        skill_version.write_text("1.3.11\n", encoding="utf-8")
        changelog = skill / "CHANGELOG.md"
        changelog.write_text("## 1.3.11 — Approved Test Edit\n\n- Test fixture only.\n\n" + changelog.read_text(encoding="utf-8"), encoding="utf-8")
        version = fixture / "VERSION"
        next_project_version = bump_semver(version.read_text(encoding="utf-8").strip(), "patch", project=True)
        version.write_text(next_project_version + "\n", encoding="utf-8")
        root_log = fixture / "CHANGELOG.md"
        root_log.write_text(f"## [{next_project_version}] — Test Fixture\n\n- Approved test edit.\n\n" + root_log.read_text(encoding="utf-8"), encoding="utf-8")
        refreshed = refresh_registry(fixture, confirmed=True, reason="Test-only confirmed edit with required versions")
        self.assertEqual(refreshed["status"], "PASS")
        self.assertEqual(validate_registry(fixture)["status"], "PASS")

    def test_release_baseline_reset_requires_its_own_explicit_confirmation(self) -> None:
        fixture = copy_library_fixture(self.workspace / "release-baseline", include_registry=True)
        for version_path in (fixture / "01-Skills-General").glob("*/VERSION"):
            version_path.write_text("1.0.0\n", encoding="utf-8")
        first_party_path = fixture / "Capability-Library" / "First-Party-Skills.json"
        first_party = json.loads(first_party_path.read_text(encoding="utf-8"))
        for skill in first_party["skills"]:
            skill["version"] = "1.0.0"
        first_party_path.write_text(json.dumps(first_party, indent=2) + "\n", encoding="utf-8")
        registry_path = fixture / "Capability-Library" / "Registry.json"
        registry = json.loads(registry_path.read_text(encoding="utf-8"))
        registry["skills"][0]["version"] = "1.0.1"
        registry["skills"][0]["sha256"] = "0" * 64
        registry_path.write_text(json.dumps(registry, indent=2) + "\n", encoding="utf-8")
        with self.assertRaises(CapabilityError):
            refresh_registry(fixture, confirmed=True, reason="Reset release baseline")
        refreshed = refresh_registry(fixture, confirmed=True, reason="Reset release baseline", release_baseline_reset=True)
        self.assertEqual(refreshed["status"], "PASS")

    def test_plugin_generation_is_idempotent_and_contains_only_skill_masters(self) -> None:
        target = self.workspace / "Plugin-Sample"
        first = build_plugin(ROOT, target)
        second = build_plugin(ROOT, target)
        self.assertEqual(first["status"], "PASS")
        self.assertEqual(second["status"], "UNCHANGED")
        self.assertEqual(len(list((target / "skills").iterdir())), 12)
        self.assertFalse((target / "02-Prompt-General").exists())
        self.assertFalse((target / "02-Skills-Personal").exists())
        self.assertFalse((target / "skills" / "import-memory").exists())
        self.assertFalse((target / "skills" / "morning").exists())
        manifest = json.loads((target / "AIPM-Distribution-Manifest.json").read_text(encoding="utf-8"))
        self.assertEqual(len(manifest["skills"]), 12)
        self.assertNotIn("license", json.loads((target / ".codex-plugin" / "plugin.json").read_text(encoding="utf-8")))
        self.assertTrue((target / "licenses" / "Apache-2.0.txt").is_file())

        original_validate = capabilities.validate_plugin
        validation_calls = 0

        def report_stale_once(root: Path, output: Path) -> dict:
            nonlocal validation_calls
            validation_calls += 1
            if validation_calls == 1:
                raise CapabilityError("Injected stale-output condition")
            return original_validate(root, output)

        original_replace = capabilities.os.replace
        replace_calls = 0

        def fail_install_and_restore(source: Path, destination: Path) -> None:
            nonlocal replace_calls
            replace_calls += 1
            if replace_calls in {2, 3}:
                raise OSError("Injected replacement and rollback failure")
            original_replace(source, destination)

        with mock.patch.object(capabilities, "validate_plugin", side_effect=report_stale_once):
            with mock.patch.object(capabilities.os, "replace", side_effect=fail_install_and_restore):
                with self.assertRaisesRegex(CapabilityError, "preserved at"):
                    build_plugin(ROOT, target, replace_generated=True)
        preserved = list((ROOT / ".test-workspace").glob("p06-plugin-backup-*/previous"))
        self.assertEqual(len(preserved), 1)
        self.assertTrue((preserved[0] / "AIPM-Distribution-Manifest.json").is_file())
        self.assertFalse(target.exists())
        original_replace(preserved[0], target)
        preserved[0].parent.rmdir()

        validation_calls = 0
        with mock.patch.object(capabilities, "validate_plugin", side_effect=report_stale_once):
            rebuilt = build_plugin(ROOT, target, replace_generated=True)
        self.assertEqual(rebuilt["status"], "PASS")
        self.assertEqual(list((ROOT / ".test-workspace").glob("p06-plugin-backup-*")), [])
        self.assertEqual(list((ROOT / ".test-workspace").glob("p06-plugin-stage-*")), [])

    def test_explicit_rebuild_upgrades_only_known_website_metadata_drift(self) -> None:
        target = self.workspace / "Website-Metadata-Upgrade"
        first = build_plugin(ROOT, target)
        self.assertEqual(first["status"], "PASS")

        portable_path = target / "plugin.json"
        portable = json.loads(portable_path.read_text(encoding="utf-8"))
        portable.pop("homepage")
        portable.pop("repository")
        portable_path.write_text(json.dumps(portable, indent=2, sort_keys=True) + "\n", encoding="utf-8")

        codex_path = target / ".codex-plugin" / "plugin.json"
        codex = json.loads(codex_path.read_text(encoding="utf-8"))
        codex.pop("homepage")
        codex.pop("repository")
        codex["interface"].pop("websiteURL")
        codex_path.write_text(json.dumps(codex, indent=2, sort_keys=True) + "\n", encoding="utf-8")

        readme_path = target / "README.md"
        readme = readme_path.read_text(encoding="utf-8")
        readme_path.write_text(readme.replace("\n\nProject Website: [https://github.com/Abdulrahman3M/AI-Project-Manager-AIPM/](https://github.com/Abdulrahman3M/AI-Project-Manager-AIPM/)\n", "\n"), encoding="utf-8")

        with self.assertRaisesRegex(CapabilityError, "explicit --replace-generated"):
            build_plugin(ROOT, target)

        (target / "unexpected-user-file.txt").write_text("preserve me\n", encoding="utf-8")
        with self.assertRaisesRegex(CapabilityError, "unexpected files"):
            build_plugin(ROOT, target, replace_generated=True)
        self.assertEqual((target / "unexpected-user-file.txt").read_text(encoding="utf-8"), "preserve me\n")
        (target / "unexpected-user-file.txt").unlink()

        rebuilt = build_plugin(ROOT, target, replace_generated=True)
        self.assertEqual(rebuilt["status"], "PASS")
        manifest = json.loads((target / "AIPM-Distribution-Manifest.json").read_text(encoding="utf-8"))
        self.assertEqual(manifest["plugin_version"], "1.0.1")
        self.assertEqual(manifest["previous_plugin_version"], "1.0.0")
        self.assertEqual(validate_plugin(ROOT, target)["status"], "PASS")
        portable = json.loads((target / "plugin.json").read_text(encoding="utf-8"))
        codex = json.loads((target / ".codex-plugin" / "plugin.json").read_text(encoding="utf-8"))
        self.assertEqual(portable["homepage"], "https://github.com/Abdulrahman3M/AI-Project-Manager-AIPM/")
        self.assertEqual(codex["interface"]["websiteURL"], "https://github.com/Abdulrahman3M/AI-Project-Manager-AIPM/")

    def test_plugin_tampering_or_sensitive_source_file_blocks_distribution(self) -> None:
        target = self.workspace / "Tamper-Sample"
        build_plugin(ROOT, target)
        copied_skill = target / "skills" / "audio-timing-author" / "SKILL.md"
        copied_skill.write_text(copied_skill.read_text(encoding="utf-8") + "\nTampered.\n", encoding="utf-8")
        with self.assertRaises(CapabilityError):
            validate_plugin(ROOT, target)
        fixture = copy_library_fixture(self.workspace / "sensitive", include_registry=True)
        sensitive = fixture / "01-Skills-General" / "audio-timing-author" / "credentials.json"
        sensitive.write_text('{"token":"not-a-real-secret"}\n', encoding="utf-8")
        blocked_target = fixture / ".test-workspace" / "Plugin-Sample"
        with self.assertRaises(CapabilityError):
            build_plugin(fixture, blocked_target)
        self.assertFalse(blocked_target.exists())

    def test_plugin_target_must_remain_inside_project(self) -> None:
        outside = ROOT / ".." / "AIPM-P06-Outside"
        with self.assertRaises(CapabilityError):
            build_plugin(ROOT, outside)


if __name__ == "__main__":
    unittest.main()
