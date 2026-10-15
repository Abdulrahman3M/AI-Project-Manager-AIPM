from __future__ import annotations

import json
import subprocess
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "Core-Engine"))
from aipm_core.domain import CommandEnvelope, CoreEngine
from aipm_core.storage import initialize_project_state, _atomic_json


class CoreEngineTests(unittest.TestCase):
    def test_git_observation_write_conflict_and_replay(self):
        with tempfile.TemporaryDirectory(dir=ROOT / '.test-workspace') as temporary:
            project = initialize_project_state(Path(temporary) / 'Managed', 'managed', 'Managed')
            engine = CoreEngine({'managed': project})
            payload = {'branch': 'feature', 'head_sha': 'a' * 40, 'diff_fingerprint': 'b' * 64}
            conflict = engine.execute(CommandEnvelope('conflict', 'state.record-git-observation', 'tester', 'managed', 5, None, payload))
            self.assertEqual(conflict['reason'], 'STATE_CONFLICT')
            command = CommandEnvelope('git', 'state.record-git-observation', 'tester', 'managed', 0, 'git-key', payload)
            self.assertEqual(engine.execute(command)['revision'], 1)
            self.assertTrue(engine.execute(command)['replayed'])
            state = engine.execute(CommandEnvelope('read', 'state.read', 'tester', 'managed', 0, None, {}))['state']
            for key, value in payload.items():
                self.assertEqual(state[key], value)
            self.assertEqual(len(list((project.state_root / 'History/Events').glob('*.json'))), 1)
    def test_atomic_json_replace_failure_preserves_previous_file(self):
        with tempfile.TemporaryDirectory(dir=ROOT / '.test-workspace') as temporary:
            path = Path(temporary) / 'State.json'
            _atomic_json(path, {'revision': 7})
            previous = path.read_bytes()
            with patch.object(Path, 'replace', side_effect=OSError('Injected Replace Failure')):
                with self.assertRaises(OSError):
                    _atomic_json(path, {'revision': 8})
            self.assertEqual(path.read_bytes(), previous)
            self.assertEqual(list(path.parent.iterdir()), [path])

    def test_event_replace_failure_recovers_before_read(self):
        with tempfile.TemporaryDirectory(dir=ROOT / '.test-workspace') as temporary:
            project = initialize_project_state(Path(temporary) / 'Managed', 'managed', 'Managed')
            original_replace = Path.replace
            def fail_event(source, target):
                if Path(target).parent.name == 'Events':
                    raise OSError('Injected Event Replace Failure')
                return original_replace(source, target)
            command = CommandEnvelope('recover-event', 'state.set-next-action', 'tester', 'managed', 0, None, {'next_action': 'Recovered Event'})
            with patch.object(Path, 'replace', fail_event):
                self.assertEqual(CoreEngine({'managed': project}).execute(command)['status'], 'BLOCKED')
            recovered = CoreEngine({'managed': project}).execute(CommandEnvelope('read', 'state.read', 'tester', 'managed', 0, None, {}))
            self.assertEqual(recovered['revision'], 1)
            self.assertEqual(recovered['state']['next_action'], 'Recovered Event')
            self.assertEqual(len(list((project.state_root / 'History/Events').glob('*.json'))), 1)

    def test_malformed_manifest_shape_is_blocked(self):
        with tempfile.TemporaryDirectory(dir=ROOT / '.test-workspace') as temporary:
            project = initialize_project_state(Path(temporary) / 'Managed', 'managed', 'Managed')
            path = project.state_root / 'State-Manifest.json'
            path.write_text(json.dumps({'schema_version': [], 'revision': 0, 'project_id': 'managed'}))
            result = CoreEngine({'managed': project}).execute(CommandEnvelope('read', 'state.read', 'tester', 'managed', 0, None, {}))
            self.assertEqual(result['reason'], 'INVALID_STATE')

    def test_failed_state_event_commit_recovers_consistent_revision(self):
        with tempfile.TemporaryDirectory(dir=ROOT / '.test-workspace') as temporary:
            project = initialize_project_state(Path(temporary) / 'Managed', 'managed', 'Managed')
            original_replace = Path.replace
            def fail_manifest(source, target):
                if Path(target).name == 'State-Manifest.json':
                    raise OSError('Injected Manifest Replace Failure')
                return original_replace(source, target)
            command = CommandEnvelope('recover', 'state.set-next-action', 'tester', 'managed', 0, 'recover-key', {'next_action': 'Recovered Action'})
            with patch.object(Path, 'replace', fail_manifest):
                failed = CoreEngine({'managed': project}).execute(command)
            self.assertEqual(failed['status'], 'BLOCKED')
            self.assertEqual(json.loads((project.state_root / 'State-Manifest.json').read_text())['revision'], 0)
            fresh = CoreEngine({'managed': project})
            recovered = fresh.execute(CommandEnvelope('read', 'state.read', 'tester', 'managed', 0, None, {}))
            self.assertEqual(recovered['revision'], 1)
            self.assertEqual(recovered['state']['next_action'], 'Recovered Action')
            events = list((project.state_root / 'History/Events').glob('*.json'))
            self.assertEqual(len(events), 1)
            self.assertEqual(json.loads(events[0].read_text())['revision'], recovered['revision'])
            self.assertTrue(fresh.execute(command)['replayed'])
            self.assertEqual(list(project.state_root.rglob('*.tmp')), [])
            self.assertFalse((project.state_root / 'History/Pending-Commit.json').exists())
    def cli(self, *args):
        return subprocess.run([sys.executable, str(ROOT / 'Core-Engine/aipm.py'), *args], capture_output=True, text=True)

    def registry(self, directory, project):
        path = Path(directory) / 'registry.json'
        path.write_text(json.dumps({'schema_version': '1.0', 'projects': [{'project_id': project.project_id, 'root_path': str(project.root), 'alias': project.alias}]}))
        return path

    def test_importing_cli_does_not_parse_process_arguments(self):
        result = subprocess.run([sys.executable, '-c', "import sys; sys.path.insert(0, 'Core-Engine'); sys.argv=['aipm','unexpected']; import aipm; assert callable(aipm.main); assert callable(aipm.build_parser)"], cwd=ROOT, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, '')

    def test_cli_inspect_returns_project_json(self):
        with tempfile.TemporaryDirectory(dir=ROOT / '.test-workspace') as temporary:
            project = initialize_project_state(Path(temporary) / 'Managed', 'managed', 'Managed')
            result = self.cli('inspect', '--registry', str(self.registry(temporary, project)), '--project-id', 'managed')
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(json.loads(result.stdout)['project']['project_id'], 'managed')

    def test_cli_state_read_returns_manifest_json(self):
        with tempfile.TemporaryDirectory(dir=ROOT / '.test-workspace') as temporary:
            project = initialize_project_state(Path(temporary) / 'Managed', 'managed', 'Managed')
            result = self.cli('state-read', '--registry', str(self.registry(temporary, project)), '--project-id', 'managed')
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(json.loads(result.stdout)['revision'], 0)

    def test_cli_invalid_registry_returns_json_error(self):
        with tempfile.TemporaryDirectory(dir=ROOT / '.test-workspace') as temporary:
            registry = Path(temporary) / 'registry.json'
            registry.write_text('{broken')
            result = self.cli('list', '--registry', str(registry))
            self.assertEqual(result.returncode, 1)
            self.assertEqual(json.loads(result.stdout)['reason'], 'INVALID_REGISTRY')
            self.assertEqual(result.stderr, '')

    def test_cli_malformed_state_returns_json_error(self):
        with tempfile.TemporaryDirectory(dir=ROOT / '.test-workspace') as temporary:
            project = initialize_project_state(Path(temporary) / 'Managed', 'managed', 'Managed')
            (project.state_root / 'State-Manifest.json').write_text('{broken')
            result = self.cli('state-read', '--registry', str(self.registry(temporary, project)), '--project-id', 'managed')
            self.assertEqual(result.returncode, 1)
            self.assertEqual(json.loads(result.stdout)['reason'], 'INVALID_STATE')
            self.assertEqual(result.stderr, '')

    def test_cli_unknown_project_returns_json_error(self):
        with tempfile.TemporaryDirectory(dir=ROOT / '.test-workspace') as temporary:
            project = initialize_project_state(Path(temporary) / 'Managed', 'managed', 'Managed')
            result = self.cli('inspect', '--registry', str(self.registry(temporary, project)), '--project-id', 'unknown')
            self.assertEqual(result.returncode, 1)
            self.assertEqual(json.loads(result.stdout)['reason'], 'PROJECT_NOT_REGISTERED')

    def legacy(self, project):
        path = project.state_root / 'State-Manifest.json'
        data = json.loads(path.read_text())
        data['schema_version'] = '1.0'
        del data['tasks'], data['diff_fingerprint']
        path.write_text(json.dumps(data))
        return path

    def test_legacy_state_read_adds_defaults_without_writing(self):
        with tempfile.TemporaryDirectory(dir=ROOT / '.test-workspace') as temporary:
            project = initialize_project_state(Path(temporary) / 'Managed', 'managed', 'Managed')
            path = self.legacy(project)
            previous = path.read_bytes()
            result = CoreEngine({'managed': project}).execute(CommandEnvelope('read', 'state.read', 'tester', 'managed', 0, None, {}))
            self.assertEqual(result['state']['tasks'], {})
            self.assertIsNone(result['state']['diff_fingerprint'])
            self.assertEqual(path.read_bytes(), previous)

    def test_legacy_state_mutation_upgrades_schema_version(self):
        with tempfile.TemporaryDirectory(dir=ROOT / '.test-workspace') as temporary:
            project = initialize_project_state(Path(temporary) / 'Managed', 'managed', 'Managed')
            path = self.legacy(project)
            result = CoreEngine({'managed': project}).execute(CommandEnvelope('write', 'state.set-next-action', 'tester', 'managed', 0, None, {'next_action': 'Run Tests'}))
            self.assertEqual(result['status'], 'PASS')
            self.assertEqual(json.loads(path.read_text())['schema_version'], '1.1')
    def test_cli_lists_pointer_only_registry_as_json(self) -> None:
        with tempfile.TemporaryDirectory(dir=ROOT / ".test-workspace") as temporary:
            registry = Path(temporary) / "registry.json"
            registry.write_text(json.dumps({"schema_version":"1.0","projects":[{"project_id":"one","root_path":"C:/One","alias":"One"}],"preferences":{}}))
            result = subprocess.run([sys.executable, str(ROOT / "Core-Engine" / "aipm.py"), "list", "--registry", str(registry)], capture_output=True, text=True, check=True)
            self.assertEqual(json.loads(result.stdout)["projects"][0]["project_id"], "one")
    def test_state_read_and_revisioned_event_write_are_idempotent(self) -> None:
        with tempfile.TemporaryDirectory(dir=ROOT / ".test-workspace") as temporary:
            project = initialize_project_state(Path(temporary) / "Managed", "managed", "Managed")
            engine = CoreEngine({"managed": project})
            initial = engine.execute(CommandEnvelope("request-001", "state.read", "tester", "managed", 0, None, {}))
            self.assertEqual(initial["status"], "PASS")
            command = CommandEnvelope("request-002", "state.set-next-action", "tester", "managed", 0, "idem-1", {"next_action": "Run Tests"})
            changed = engine.execute(command)
            replay = engine.execute(command)
            self.assertEqual(changed["revision"], 1)
            self.assertEqual(replay["status"], "PASS")
            self.assertTrue(replay["replayed"])
            self.assertEqual(replay["revision"], 1)
            self.assertEqual(len(list((project.state_root / "History" / "Events").glob("*.json"))), 1)

    def test_revision_conflict_is_blocked_without_state_overwrite(self) -> None:
        with tempfile.TemporaryDirectory(dir=ROOT / ".test-workspace") as temporary:
            project = initialize_project_state(Path(temporary) / "Managed", "managed", "Managed")
            engine = CoreEngine({"managed": project})
            result = engine.execute(CommandEnvelope("request-003", "state.set-next-action", "tester", "managed", 4, None, {"next_action": "Unsafe"}))
            manifest = json.loads((project.state_root / "State-Manifest.json").read_text())
            self.assertEqual(result["status"], "BLOCKED")
            self.assertEqual(manifest["revision"], 0)


if __name__ == "__main__":
    unittest.main()
