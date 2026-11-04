"""Focused tests for explicit project component setup."""
import json
import argparse
import contextlib
import io
import importlib.util
import os
from pathlib import Path
import subprocess
import shutil
import sys
import tempfile
import time
from types import SimpleNamespace
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "Core-Engine"))
from aipm_core import project_setup as setup
from aipm_core.storage import StateError
from aipm_core.storage import initialize_project_state, ProjectRegistry
from aipm_core.domain import CommandEnvelope, CoreEngine
import aipm


class ProjectSetupTests(unittest.TestCase):
    def setUp(self):
        base = Path(__file__).resolve().parents[1] / "Shared-Project-State-Manager" / "Test-Workspace"
        base.mkdir(parents=True, exist_ok=True)
        self.temp = tempfile.TemporaryDirectory(dir=base, prefix="project-setup-")
        self.root = Path(self.temp.name) / "Project With Spaces"
        self.root.mkdir()
        self.environment = patch.dict(os.environ, {"GIT_CEILING_DIRECTORIES": self.temp.name})
        self.environment.start()
        self.guard = patch.object(setup, "_protect_platform_path", side_effect=lambda path, **kw: Path(path).resolve())
        self.guard.start()

    def tearDown(self):
        self.guard.stop()
        self.environment.stop()
        for attempt in range(10):
            try:
                self.temp.cleanup()
                break
            except PermissionError:
                if attempt == 9:
                    raise
                time.sleep(0.2)

    def test_git_dependency_and_non_destructive_install(self):
        self.assertEqual(setup.inspect_project(self.root)["git"], "MISSING")
        with self.assertRaisesRegex(StateError, "FIRG_REQUIRES_GIT"):
            setup.install_firg(self.root)
        setup.initialize_git(self.root)
        setup.install_firg(self.root)
        self.assertEqual(setup.inspect_project(self.root)["firg"], "READY")
        validation = subprocess.run([sys.executable, str(self.root / "FIRG" / "tools" / "firg.py"), "validate", "--strict"],
                                    cwd=self.root, capture_output=True, text=True, encoding="utf-8")
        self.assertEqual(validation.returncode, 0, validation.stdout + validation.stderr)
        no_commits = subprocess.run([sys.executable, str(self.root / "FIRG" / "tools" / "firg.py"), "commit-status"], cwd=self.root, capture_output=True, text=True, encoding="utf-8")
        self.assertEqual(no_commits.returncode, 0, no_commits.stderr)
        self.assertIn('No commits', no_commits.stdout)
        with self.assertRaisesRegex(StateError, "FIRG_ALREADY_EXISTS"):
            setup.install_firg(self.root)
        rules = self.root / 'AGENTS.md'
        saved_rules = rules.read_bytes()
        rules.write_text('Locally changed rules', encoding='utf-8')
        self.assertEqual(setup.inspect_project(self.root)['firg'], 'ROOT_RULE_REVIEW_REQUIRED')
        rules.write_bytes(saved_rules)
        (self.root / "FIRG" / "README.md").write_text("Local edit", encoding="utf-8")
        self.assertEqual(setup.inspect_project(self.root)["firg"], "MODIFIED")

    def test_git_version_baseline_reports_unknown_and_old_without_guessing_latest(self):
        cases = [('git version 2.19.9', ('2.19.9', 'BELOW_BASELINE', 'OTHER_OR_UNKNOWN')),
                 ('git version 2.20.0.windows.1', ('2.20.0', 'MEETS_BASELINE', 'GIT_FOR_WINDOWS')),
                 ('unrecognized', ('UNKNOWN', 'UNVERIFIED', 'UNKNOWN'))]
        for output, expected in cases:
            with self.subTest(output=output), patch.object(setup, '_git', return_value=SimpleNamespace(returncode=0, stdout=output)):
                self.assertEqual(setup.git_version(self.root), expected)

    def test_firg_commands_reject_projects_without_git(self):
        shutil.copytree(setup.TEMPLATE, self.root / 'FIRG')
        (self.root / 'AGENTS.md').write_text('Fixture', encoding='utf-8')
        tool = self.root / 'FIRG' / 'tools' / 'firg.py'
        result = subprocess.run([sys.executable, str(tool), 'validate', '--strict'], cwd=self.root,
                                capture_output=True, text=True, encoding='utf-8')
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('git:', result.stderr.lower())

    def test_existing_instruction_is_preserved(self):
        setup.initialize_git(self.root)
        rules = self.root / "AGENTS.md"
        rules.write_text("Owner rules", encoding="utf-8")
        setup.install_firg(self.root)
        self.assertTrue(rules.read_text(encoding="utf-8").startswith("Owner rules\n"))
        self.assertIn("Mandatory FIRG", rules.read_text(encoding="utf-8"))

    def test_missing_root_rule_repair_preserves_other_instructions(self):
        setup.initialize_git(self.root)
        setup.install_firg(self.root)
        rules = self.root / 'AGENTS.md'
        rules.write_text('Owner Instructions\n', encoding='utf-8')
        self.assertEqual(setup.inspect_project(self.root)['firg'], 'ROOT_RULE_REVIEW_REQUIRED')
        setup.repair_firg_rule(self.root)
        self.assertTrue(rules.read_text(encoding='utf-8').startswith('Owner Instructions\n'))
        self.assertEqual(setup.inspect_project(self.root)['firg'], 'READY')
        rules.write_text('Owner FIRG customization\n', encoding='utf-8')
        with self.assertRaisesRegex(StateError, 'ROOT_AGENTS_REVIEW_REQUIRED'):
            setup.repair_firg_rule(self.root)
        self.assertEqual(rules.read_text(encoding='utf-8'), 'Owner FIRG customization\n')

    def test_missing_managed_files_restore_without_overwriting_data(self):
        setup.initialize_git(self.root)
        setup.install_firg(self.root)
        firg = self.root / 'FIRG'
        tool = firg / 'tools' / 'firg.py'
        original_tool = tool.read_bytes()
        tool.unlink()
        readme = firg / 'README.md'
        readme.write_text('Owner edit', encoding='utf-8')
        self.assertEqual(setup.inspect_project(self.root)['firg'], 'INCOMPLETE')
        setup.repair_firg_files(self.root)
        self.assertEqual(tool.read_bytes(), original_tool)
        self.assertEqual(readme.read_text(encoding='utf-8'), 'Owner edit')
        self.assertEqual(setup.inspect_project(self.root)['firg'], 'MODIFIED')
        ledger = firg / 'FIX-HISTORY.md'
        ledger.unlink()
        registry = firg / 'registry'
        registry.mkdir()
        (registry / 'unreviewed.json').write_text('{}', encoding='utf-8')
        with self.assertRaisesRegex(StateError, 'FIRG_LEDGER_REGENERATION_REQUIRED'):
            setup.repair_firg_files(self.root)
        self.assertFalse(ledger.exists())
        self.assertTrue((registry / 'unreviewed.json').is_file())

    def test_inspection_rejects_linked_configuration(self):
        setup.initialize_git(self.root)
        setup.install_firg(self.root)
        config = self.root / 'FIRG' / 'config.json'
        outside = self.root.parent / 'external-config.json'
        outside.write_bytes(config.read_bytes())
        config.unlink()
        try:
            os.symlink(outside, config)
        except OSError as exc:
            self.skipTest('Symbolic links unavailable: ' + str(exc))
        self.assertEqual(setup.inspect_project(self.root)['firg'], 'INVALID')
        self.assertTrue(outside.is_file())

    @unittest.skipUnless(os.name == 'nt', 'Windows junction test')
    def test_inspection_rejects_tools_junction_outside_project(self):
        setup.initialize_git(self.root)
        setup.install_firg(self.root)
        tools_dir = self.root / 'FIRG' / 'tools'
        saved = self.root / 'FIRG' / 'tools-saved'
        tools_dir.rename(saved)
        outside = self.root.parent / 'external-tools'
        shutil.copytree(saved, outside)
        env = os.environ.copy()
        env.update(FIRG_TEST_LINK=str(tools_dir), FIRG_TEST_TARGET=str(outside))
        command = "$ErrorActionPreference='Stop'; New-Item -ItemType Junction -Path $env:FIRG_TEST_LINK -Target $env:FIRG_TEST_TARGET | Out-Null"
        result = subprocess.run(['powershell', '-NoProfile', '-Command', command], env=env, capture_output=True, text=True)
        if result.returncode:
            self.skipTest('Junction creation unavailable: ' + result.stderr.strip())
        try:
            self.assertEqual(tools_dir.resolve(), outside.resolve())
            self.assertEqual(setup.inspect_project(self.root)['firg'], 'INVALID')
            self.assertTrue((outside / 'firg.py').is_file())
        finally:
            # Remove the verified junction itself; never recursively remove its target.
            if tools_dir.resolve() == outside.resolve():
                os.rmdir(tools_dir)

    def test_versioned_instruction_file_requires_review(self):
        setup.initialize_git(self.root)
        rules = self.root / 'AGENTS.md'
        content = '<!-- File MetaData: Version Number: 2026.11.01.01.01 -->\nOwner rules'
        rules.write_text(content, encoding='utf-8')
        with self.assertRaisesRegex(StateError, 'ROOT_AGENTS_METADATA_REVIEW_REQUIRED'):
            setup.install_firg(self.root)
        self.assertEqual(rules.read_text(encoding='utf-8'), content)
        self.assertFalse((self.root / 'FIRG').exists())

    def test_interrupted_install_resumes_and_preserves_local_edits(self):
        setup.initialize_git(self.root)
        rules = self.root / 'AGENTS.md'
        rules.write_text('Owner rules', encoding='utf-8')
        original_open = Path.open
        def interrupted(path, *args, **kwargs):
            if path.name == 'README.md' and path.parent.name == 'FIRG' and args and args[0] == 'xb':
                raise OSError('simulated interruption')
            return original_open(path, *args, **kwargs)
        with patch.object(Path, 'open', interrupted):
            with self.assertRaisesRegex(OSError, 'simulated interruption'):
                setup.install_firg(self.root)
        self.assertEqual(setup.inspect_project(self.root)['firg'], 'INSTALL_INTERRUPTED')
        scoped = self.root / 'FIRG' / 'AGENTS.md'
        prior = scoped.read_bytes()
        scoped.write_bytes(b'Local change')
        with self.assertRaisesRegex(StateError, 'FIRG_INSTALL_LOCAL_MODIFICATION'):
            setup.install_firg(self.root)
        self.assertEqual(scoped.read_bytes(), b'Local change')
        scoped.write_bytes(prior)
        rules.write_text('Owner changed rules', encoding='utf-8')
        with self.assertRaisesRegex(StateError, 'ROOT_AGENTS_CHANGED_DURING_INSTALL'):
            setup.install_firg(self.root)
        self.assertEqual(rules.read_text(encoding='utf-8'), 'Owner changed rules')
        rules.write_text('Owner rules', encoding='utf-8')
        setup.install_firg(self.root)
        self.assertEqual(setup.inspect_project(self.root)['firg'], 'READY')
        self.assertEqual(rules.read_text(encoding='utf-8').count('Mandatory FIRG'), 1)
        self.assertFalse((self.root / 'FIRG' / 'aipm-install.pending.json').exists())

    def test_interruption_after_install_marker_is_idempotent(self):
        setup.initialize_git(self.root)
        original_unlink = Path.unlink
        def interrupted(path, *args, **kwargs):
            if path.name == 'aipm-install.pending.json':
                raise OSError('simulated interruption')
            return original_unlink(path, *args, **kwargs)
        with patch.object(Path, 'unlink', interrupted):
            with self.assertRaisesRegex(OSError, 'simulated interruption'):
                setup.install_firg(self.root)
        self.assertEqual(setup.inspect_project(self.root)['firg'], 'INSTALL_INTERRUPTED')
        setup.install_firg(self.root)
        self.assertEqual(setup.inspect_project(self.root)['firg'], 'READY')
        self.assertEqual((self.root / 'AGENTS.md').read_text(encoding='utf-8').count('Mandatory FIRG'), 1)

    def test_declined_components_are_distinguished(self):
        state = self.root / setup.STATE_ROOT_NAME
        state.mkdir()
        (state / "Project-Manifest.json").write_text(json.dumps({"project_id": "fixture", "state_root_name": setup.STATE_ROOT_NAME}), encoding="utf-8")
        (state / "State-Manifest.json").write_text(json.dumps({"project_id": "fixture", "schema_version": "1.1"}), encoding="utf-8")
        setup.save_preferences(self.root, git=False, firg=False)
        result = setup.inspect_project(self.root)
        self.assertEqual((result["git"], result["firg"], result["shared_state"]), ("DECLINED", "DECLINED", "READY"))
        setup.save_preferences(self.root, git=True, firg=True)
        self.assertEqual(setup.inspect_project(self.root)["firg"], "GIT_REQUIRED")
        setup.save_preferences(self.root, git=None, firg=None)
        self.assertEqual((setup.inspect_project(self.root)['git'], setup.inspect_project(self.root)['firg']), ('MISSING', 'GIT_REQUIRED'))
        state_manifest = state / "State-Manifest.json"
        state_manifest.write_text('{broken', encoding='utf-8')
        self.assertEqual(setup.inspect_project(self.root)['shared_state'], 'INVALID')
        state_manifest.write_text(json.dumps({"project_id": "fixture", "schema_version": "1.0"}), encoding="utf-8")
        self.assertEqual(setup.inspect_project(self.root)['shared_state'], 'LEGACY')

    def test_metadata_write_rejects_concurrent_changes(self):
        target = self.root / 'metadata.json'
        target.write_text('{"owner": 1}', encoding='utf-8')
        original = target.read_bytes()
        target.write_text('{"owner": 2}', encoding='utf-8')
        with self.assertRaisesRegex(StateError, 'MANAGED_METADATA_CHANGED'):
            setup._write_json_safely(target, {'owner': 3}, original)
        self.assertEqual(json.loads(target.read_text(encoding='utf-8'))['owner'], 2)

    def test_commit_report_and_documentation_status(self):
        setup.initialize_git(self.root)
        setup.install_firg(self.root)
        self.assertEqual(setup.inspect_project(self.root)['commit_prompt'], 'READY')
        for args in (("config", "user.name", "Fixture"), ("config", "user.email", "fixture@example.invalid")):
            subprocess.run(["git", "-C", str(self.root), *args], check=True, capture_output=True)
        (self.root / "source.txt").write_text("fixed", encoding="utf-8")
        subprocess.run(["git", "-C", str(self.root), "add", "source.txt"], check=True, capture_output=True)
        subprocess.run(["git", "-C", str(self.root), "commit", "-m", "Fix example"], check=True, capture_output=True)
        tool = self.root / "FIRG" / "tools" / "firg.py"
        spec = importlib.util.spec_from_file_location('firg_report_failure_test', tool)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        fields = {key: 'Evidence for ' + key for key in ('problem', 'cause', 'expected', 'implementation', 'rationale', 'notes')}
        real_open = Path.open
        def report_failure(path, *args, **kwargs):
            if path.parent.name == 'reports' and args and args[0] == 'x':
                raise OSError('report write denied')
            return real_open(path, *args, **kwargs)
        with patch.object(Path, 'open', report_failure):
            with self.assertRaisesRegex(OSError, 'report write denied'):
                module.document_commit(argparse.Namespace(commit='HEAD', **fields))
        self.assertEqual(list((self.root / 'FIRG' / 'registry').glob('*.json')), [])
        command = [sys.executable, str(tool), "document-commit"]
        for key in ("problem", "cause", "expected", "implementation", "rationale", "notes"):
            command.extend(["--" + key, "Evidence for " + key])
        result = subprocess.run(command, cwd=self.root, capture_output=True, text=True, encoding="utf-8")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        records = list((self.root / "FIRG" / "registry").glob("*.json"))
        self.assertEqual(len(records), 1)
        record = json.loads(records[0].read_text(encoding="utf-8"))
        self.assertEqual(record["tests"][0]["result"], "UNVERIFIED")
        report = self.root / "FIRG" / "reports" / (record["id"] + ".md")
        self.assertIn(record["commits"][0], report.read_text(encoding="utf-8"))
        self.assertIn(record["report_reference"], (self.root / "FIRG" / "FIX-HISTORY.md").read_text(encoding="utf-8"))
        status = subprocess.run([sys.executable, str(tool), "commit-status"], cwd=self.root, capture_output=True, text=True, encoding="utf-8")
        self.assertIn("DOCUMENTED " + record["id"], status.stdout)
        (self.root / "source.txt").write_text("changed again", encoding="utf-8")
        subprocess.run(["git", "-C", str(self.root), "commit", "-am", "Second change"], check=True, capture_output=True)
        status = subprocess.run([sys.executable, str(tool), "commit-status"], cwd=self.root, capture_output=True, text=True, encoding="utf-8")
        self.assertIn("UNDOCUMENTED ", status.stdout)
        self.assertIn("DOCUMENTED " + record["id"], status.stdout)
        command.extend(["--commit", record["commits"][0]])
        duplicate = subprocess.run(command, cwd=self.root, capture_output=True, text=True, encoding="utf-8")
        self.assertNotEqual(duplicate.returncode, 0)
        self.assertEqual(len(list((self.root / "FIRG" / "registry").glob("*.json"))), 1)

    def test_existing_and_custom_hooks_are_preserved(self):
        setup.initialize_git(self.root)
        hook = self.root / '.git' / 'hooks' / 'post-commit'
        hook.write_text('#!/bin/sh\necho existing\n', encoding='utf-8')
        setup.install_firg(self.root)
        self.assertEqual(setup.inspect_project(self.root)['commit_prompt'], 'EXISTING_HOOK')
        self.assertEqual(hook.read_text(encoding='utf-8'), '#!/bin/sh\necho existing\n')
        self.assertEqual(setup.install_firg_hook(self.root), 'EXISTING_HOOK')
        subprocess.run(['git', '-C', str(self.root), 'config', 'core.hooksPath', 'custom-hooks'], check=True, capture_output=True)
        self.assertEqual(setup.hook_status(self.root)[0], 'CUSTOM_HOOKS_PATH')
        self.assertFalse((self.root / 'custom-hooks').exists())
        marker = self.root / 'FIRG' / 'aipm-install.json'
        saved_marker = marker.read_bytes()
        marker.write_text('[]', encoding='utf-8')
        with self.assertRaisesRegex(StateError, 'FIRG_HOOK_TOOL_REVIEW_REQUIRED'):
            setup.install_firg_hook(self.root)
        marker.write_bytes(saved_marker)
        (self.root / 'FIRG' / 'tools' / 'firg.py').write_text('Local tool edit', encoding='utf-8')
        with self.assertRaisesRegex(StateError, 'FIRG_HOOK_TOOL_REVIEW_REQUIRED'):
            setup.install_firg_hook(self.root)
        self.assertEqual(hook.read_text(encoding='utf-8'), '#!/bin/sh\necho existing\n')

    def test_future_managed_hook_update_preserves_local_changes(self):
        setup.initialize_git(self.root)
        setup.install_firg(self.root)
        hook = self.root / '.git' / 'hooks' / 'post-commit'
        previous = hook.read_bytes()
        state = self.root / setup.STATE_ROOT_NAME
        (state / 'Temporary-Files').mkdir(parents=True)
        marker = self.root / 'FIRG' / 'aipm-install.json'
        metadata = json.loads(marker.read_text(encoding='utf-8'))
        metadata['version'] = setup.VERSION - 1
        marker.write_text(json.dumps(metadata), encoding='utf-8')
        with self.assertRaisesRegex(StateError, 'FIRG_HOOK_TOOL_REVIEW_REQUIRED'):
            setup.install_firg_hook(self.root)
        metadata['version'] = setup.VERSION
        marker.write_text(json.dumps(metadata), encoding='utf-8')
        with patch.object(setup, 'HOOK', previous + b'# New Version\n'):
            self.assertEqual(setup.hook_status(self.root)[0], 'UPDATE_AVAILABLE')
            hook.write_bytes(previous + b'# Local Edit\n')
            self.assertEqual(setup.install_firg_hook(self.root), 'EXISTING_HOOK')
            self.assertTrue(hook.read_bytes().endswith(b'# Local Edit\n'))
            hook.write_bytes(previous)
            self.assertEqual(setup.install_firg_hook(self.root), 'READY')
            self.assertEqual(hook.read_bytes(), setup.HOOK)
            backups = list((state / 'History' / 'FIRG-Updates').glob('Hook-*'))
            self.assertEqual((backups[0] / 'post-commit').read_bytes(), previous)

    def test_interactive_prompt_respects_decline_and_collects_facts(self):
        spec = importlib.util.spec_from_file_location('firg_prompt_test', setup.TEMPLATE / 'tools' / 'firg.py')
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        class Tty(io.StringIO):
            def isatty(self): return True
        with patch.object(sys, 'stdin', Tty()), patch.object(sys, 'stdout', Tty()), patch('builtins.input', return_value='no'), patch.object(module, 'document_commit') as document:
            module.prompt_commit('abc')
            document.assert_not_called()
        with patch.object(sys, 'stdin', Tty()), patch.object(sys, 'stdout', Tty()), patch('builtins.input', side_effect=['yes', 'problem', 'cause', 'expected', 'change', 'reason', 'notes']), patch.object(module, 'document_commit') as document:
            module.prompt_commit('abc')
            self.assertEqual(document.call_args.args[0].commit, 'abc')
            self.assertEqual(document.call_args.args[0].problem, 'problem')
        with patch.object(sys, 'stdin', io.StringIO()), patch.object(module, 'document_commit') as document:
            module.prompt_commit('abc')
            document.assert_not_called()

    def test_update_preserves_data_and_refuses_modified_managed_file(self):
        setup.initialize_git(self.root)
        setup.install_firg(self.root)
        state = self.root / setup.STATE_ROOT_NAME
        (state / 'Temporary-Files').mkdir(parents=True)
        marker = self.root / 'FIRG' / 'aipm-install.json'
        data = json.loads(marker.read_text(encoding='utf-8'))
        data['version'] = setup.VERSION - 1
        data['owner_metadata'] = {'preserve': True}
        marker.write_text(json.dumps(data), encoding='utf-8')
        marker_acl = subprocess.run(['icacls', str(marker)], capture_output=True, text=True, errors='replace', check=True).stdout if os.name == 'nt' else None
        local = self.root / 'FIRG' / 'README.md'
        original = local.read_bytes()
        local.write_bytes(b'Local change')
        with self.assertRaisesRegex(StateError, 'FIRG_LOCAL_MODIFICATION'):
            setup.update_firg(self.root)
        self.assertEqual(local.read_bytes(), b'Local change')
        local.write_bytes(original)
        config = self.root / 'FIRG' / 'config.json'
        config.write_text('Local project settings', encoding='utf-8')
        setup.update_firg(self.root)
        self.assertEqual(config.read_text(encoding='utf-8'), 'Local project settings')
        self.assertEqual(json.loads(marker.read_text(encoding='utf-8'))['version'], setup.VERSION)
        self.assertTrue(json.loads(marker.read_text(encoding='utf-8'))['owner_metadata']['preserve'])
        if marker_acl is not None:
            self.assertEqual(subprocess.run(['icacls', str(marker)], capture_output=True, text=True, errors='replace', check=True).stdout, marker_acl)
        self.assertTrue(list((state / 'History' / 'FIRG-Updates').iterdir()))

    def test_interrupted_update_resumes_only_unchanged_files(self):
        import hashlib
        setup.initialize_git(self.root)
        setup.install_firg(self.root)
        state = self.root / setup.STATE_ROOT_NAME
        (state / 'Temporary-Files').mkdir(parents=True)
        marker = self.root / 'FIRG' / 'aipm-install.json'
        data = json.loads(marker.read_text(encoding='utf-8'))
        data['version'] = setup.VERSION - 1
        target = self.root / 'FIRG' / 'README.md'
        target.write_bytes(b'Previous version')
        data['files']['README.md'] = hashlib.sha256(b'Previous version').hexdigest()
        marker.write_text(json.dumps(data), encoding='utf-8')
        original_replace = setup._replace_preserving_permissions
        def interrupted(source, destination):
            if Path(destination) == target:
                raise OSError('simulated interruption')
            return original_replace(source, destination)
        with patch.object(setup, '_replace_preserving_permissions', side_effect=interrupted):
            with self.assertRaisesRegex(StateError, 'FIRG_UPDATE_FAILED'):
                setup.update_firg(self.root)
        self.assertEqual(setup.inspect_project(self.root)['firg'], 'UPDATE_INTERRUPTED')
        target.write_bytes(b'Local edit after interruption')
        with self.assertRaisesRegex(StateError, 'FIRG_LOCAL_MODIFICATION'):
            setup.update_firg(self.root)
        self.assertEqual(target.read_bytes(), b'Local edit after interruption')
        target.write_bytes(b'Previous version')
        setup.update_firg(self.root)
        self.assertEqual(setup.inspect_project(self.root)['firg'], 'READY')
        self.assertFalse((state / 'Tool-State' / 'FIRG-Update.json').exists())

    def test_future_update_changes_only_unmodified_managed_rule(self):
        setup.initialize_git(self.root)
        rules = self.root / 'AGENTS.md'
        rules.write_text('Owner Rules', encoding='utf-8')
        setup.install_firg(self.root)
        original = rules.read_text(encoding='utf-8') + '\nOwner Notes\n'
        rules.write_text(original, encoding='utf-8')
        acl_before = subprocess.run(['icacls', str(rules)], capture_output=True, text=True, errors='replace', check=True).stdout if os.name == 'nt' else None
        state = self.root / setup.STATE_ROOT_NAME
        (state / 'Temporary-Files').mkdir(parents=True)
        new_rule = setup.RULE.replace('Before material work', 'Before each material task')
        with patch.object(setup, 'VERSION', setup.VERSION + 1), patch.object(setup, 'RULE', new_rule):
            self.assertEqual(setup.inspect_project(self.root)['firg'], 'UPDATE_AVAILABLE')
            modified = original.replace('Before material work', 'Owner modified rule')
            rules.write_text(modified, encoding='utf-8')
            with self.assertRaisesRegex(StateError, 'ROOT_AGENTS_REVIEW_REQUIRED'):
                setup.update_firg(self.root)
            self.assertEqual(rules.read_text(encoding='utf-8'), modified)
            rules.write_text(original, encoding='utf-8')
            setup.update_firg(self.root)
            updated = rules.read_text(encoding='utf-8')
            self.assertEqual(updated, original.replace('Before material work', 'Before each material task'))
            if acl_before is not None:
                acl_after = subprocess.run(['icacls', str(rules)], capture_output=True, text=True, errors='replace', check=True).stdout
                self.assertEqual(acl_after, acl_before)
            self.assertEqual(setup.inspect_project(self.root)['firg'], 'READY')
            backups = list((state / 'History' / 'FIRG-Updates').iterdir())
            self.assertEqual((backups[0] / 'Root-AGENTS.md').read_text(encoding='utf-8'), original)

    def test_legacy_schema_upgrade_records_event_without_changing_user_fields(self):
        with patch('aipm_core.storage.platform_root', return_value=self.root.parent / 'Other-Platform'):
            project = initialize_project_state(self.root, 'fixture', 'Fixture')
            manifest = project.state_root / 'State-Manifest.json'
            old = json.loads(manifest.read_text(encoding='utf-8'))
            old['schema_version'] = '1.0'
            old['next_action'] = 'Keep this action'
            old.pop('tasks'); old.pop('diff_fingerprint')
            manifest.write_text(json.dumps(old), encoding='utf-8')
            engine = CoreEngine({'fixture': project})
            backup, _ = engine._create_state_backup(project, 'SCHEMA_UPGRADE')
            conflict = engine.execute(CommandEnvelope('conflict', 'state.upgrade-schema', 'tester', 'fixture', 1, None, {}))
            self.assertEqual(conflict['reason'], 'STATE_CONFLICT')
            result = engine.execute(CommandEnvelope('upgrade', 'state.upgrade-schema', 'tester', 'fixture', 0, None, {}))
            self.assertEqual(result['status'], 'PASS', result)
            updated = json.loads(manifest.read_text(encoding='utf-8'))
            self.assertEqual((updated['schema_version'], updated['revision'], updated['next_action']), ('1.1', 1, 'Keep this action'))
            self.assertEqual(json.loads((backup / 'State-Manifest.json').read_text(encoding='utf-8'))['schema_version'], '1.0')
            event = json.loads(next((project.state_root / 'History' / 'Events').glob('*.json')).read_text(encoding='utf-8'))
            self.assertEqual(event['command'], 'state.upgrade-schema')
            repeat = engine.execute(CommandEnvelope('again', 'state.upgrade-schema', 'tester', 'fixture', 1, None, {}))
            self.assertEqual(repeat['reason'], 'SCHEMA_UPGRADE_NOT_APPLICABLE')

    def test_state_upgrade_cli_preview_and_backup(self):
        with patch('aipm_core.storage.platform_root', return_value=self.root.parent / 'Other-Platform'):
            project = initialize_project_state(self.root, 'fixture', 'Fixture')
            registry = self.root.parent / 'registry.json'
            ProjectRegistry(registry).register(project)
            manifest = project.state_root / 'State-Manifest.json'
            old = json.loads(manifest.read_text(encoding='utf-8'))
            old['schema_version'] = '1.0'
            manifest.write_text(json.dumps(old), encoding='utf-8')
            arguments = ['state-upgrade', '--registry', str(registry), '--project-id', 'fixture']
            pending = project.state_root / 'History' / 'Pending-Commit.json'
            pending.write_text('{"not":"a transaction"}', encoding='utf-8')
            captured = io.StringIO()
            with contextlib.redirect_stdout(captured):
                self.assertEqual(aipm.main(arguments), 1)
            self.assertEqual(json.loads(captured.getvalue())['reason'], 'PENDING_STATE_REQUIRES_RECOVERY')
            self.assertTrue(pending.exists())
            pending.unlink()
            captured = io.StringIO()
            with contextlib.redirect_stdout(captured):
                self.assertEqual(aipm.main(arguments), 0)
            self.assertFalse(json.loads(captured.getvalue())['applied'])
            self.assertEqual(json.loads(manifest.read_text(encoding='utf-8'))['schema_version'], '1.0')
            captured = io.StringIO()
            with contextlib.redirect_stdout(captured):
                self.assertEqual(aipm.main(arguments + ['--confirm-repair']), 0)
            outcome = json.loads(captured.getvalue())
            self.assertTrue(outcome['applied'])
            self.assertTrue(Path(outcome['backup']).is_dir())
            self.assertEqual(json.loads(manifest.read_text(encoding='utf-8'))['schema_version'], '1.1')


if __name__ == "__main__":
    unittest.main()
