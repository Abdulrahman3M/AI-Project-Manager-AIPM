"""Tests for CoreEngine state inspection (state-validate) and guided record normalization (state-normalize)."""
from __future__ import annotations

import copy
import json
import os
from pathlib import Path
import shutil
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
from test_support import CORE_ROOT, CORE_SCRIPT, RUNTIME_ROOT
sys.path.insert(0, str(CORE_ROOT))

from aipm_core.domain import CommandEnvelope, CoreEngine
from aipm_core.storage import initialize_project_state, _atomic_json, ManagedProject, StateError


class StateRecoveryTests(unittest.TestCase):
    def test_reproduction_invalid_task_record_reports_detail(self):
        with tempfile.TemporaryDirectory(dir=ROOT / '.test-workspace') as temporary:
            project = initialize_project_state(Path(temporary) / 'Managed', 'managed', 'Managed')
            manifest_path = project.state_root / 'State-Manifest.json'
            raw = json.loads(manifest_path.read_text(encoding='utf-8'))
            # Inject a malformed task record lacking title and verification
            raw['tasks']['Task-Malformed-1'] = {
                'scope': 'Test scope',
                'plan': 'Some plan',
                'blockers': [],
                'report': '',
                'status_override': 'COMPLETED & VERIFIED'
            }
            manifest_path.write_text(json.dumps(raw, indent=2), encoding='utf-8')

            engine = CoreEngine({'managed': project})
            res = engine.execute(CommandEnvelope('req-1', 'task.read', 'tester', 'managed', 0, None, {'task_id': 'Task-Malformed-1'}))
            self.assertEqual(res['status'], 'BLOCKED')
            self.assertEqual(res['reason'], 'INVALID_STATE')
            self.assertIn('detail', res)
            self.assertIn('Invalid Task State', res['detail'])

            diag = engine.diagnose_pending_task_commit(project)
            self.assertEqual(diag['status'], 'BLOCKED')
            self.assertFalse(diag['repairable'])
            self.assertIn('Invalid Task State', diag['cause'])
            self.assertIn('state-validate', diag['next_step'])

    def test_inspect_state_finds_exact_missing_fields_and_is_read_only(self):
        with tempfile.TemporaryDirectory(dir=ROOT / '.test-workspace') as temporary:
            project = initialize_project_state(Path(temporary) / 'Managed', 'managed', 'Managed')
            manifest_path = project.state_root / 'State-Manifest.json'
            raw = json.loads(manifest_path.read_text(encoding='utf-8'))
            raw['tasks']['Task-2026-10-30-Sample-01'] = {
                'scope': 'Sample scope',
                'plan': 'Tasks/Task-2026-10-30-Sample-01/Task-Plan.md',
                'blockers': [],
                'report': '',
                'status_override': 'COMPLETED & VERIFIED'
            }
            raw['revision'] = 5
            manifest_path.write_text(json.dumps(raw, indent=2), encoding='utf-8')

            engine = CoreEngine({'managed': project})
            before_hashes = {p.relative_to(project.state_root): p.read_bytes() for p in project.state_root.rglob('*') if p.is_file()}

            report = engine.inspect_state(project)
            self.assertEqual(report['status'], 'BLOCKED')
            self.assertEqual(report['manifest_revision'], 5)
            self.assertEqual(report['max_event_revision'], 0)

            codes = [f['code'] for f in report['findings']]
            self.assertIn('TASK_FIELD_MISSING', codes)
            self.assertIn('TASK_STATUS_OVERRIDE_INVALID', codes)
            self.assertIn('MANIFEST_AHEAD_OF_HISTORY', codes)

            # Check that files were completely untouched
            after_hashes = {p.relative_to(project.state_root): p.read_bytes() for p in project.state_root.rglob('*') if p.is_file()}
            self.assertEqual(before_hashes, after_hashes)

    def test_state_normalize_dry_run_and_apply(self):
        with tempfile.TemporaryDirectory(dir=ROOT / '.test-workspace') as temporary:
            project = initialize_project_state(Path(temporary) / 'Managed', 'managed', 'Managed')
            state_root = project.state_root
            manifest_path = state_root / 'State-Manifest.json'
            raw = json.loads(manifest_path.read_text(encoding='utf-8'))

            task_id = 'Task-2026-10-30-Sample-01'
            task_dir = state_root / 'Tasks' / task_id
            task_dir.mkdir(parents=True)
            (task_dir / 'Task-Plan.md').write_text('# My Task Plan\n\nFull plan details.\n', encoding='utf-8')
            (task_dir / 'Metadata.json').write_text(json.dumps({
                'task_id': task_id,
                'title': 'My Recovered Task Title',
                'scope': 'Scope from metadata',
                'task_record': {
                    'title': 'My Recovered Task Title',
                    'scope': 'Scope from metadata',
                    'verification': '10/10 tests passing'
                }
            }, indent=2), encoding='utf-8')

            raw['tasks'][task_id] = {
                'scope': 'Sample scope',
                'plan': f'Tasks/{task_id}/Task-Plan.md',
                'blockers': [],
                'report': '',
                'status_override': 'COMPLETED & VERIFIED'
            }
            manifest_path.write_text(json.dumps(raw, indent=2), encoding='utf-8')

            engine = CoreEngine({'managed': project})

            # 1. Dry run
            before_hashes = {p.relative_to(project.state_root): p.read_bytes() for p in project.state_root.rglob('*') if p.is_file()}
            dry = engine.normalize_task_records(project, confirm=False)
            self.assertEqual(dry['status'], 'PASS')
            self.assertFalse(dry['applied'])
            self.assertEqual(dry['reason'], 'DRY_RUN')
            self.assertEqual(dry['normalized_tasks'], [task_id])
            self.assertIn(task_id, dry['changes'])

            # Files untouched during dry run
            after_dry = {p.relative_to(project.state_root): p.read_bytes() for p in project.state_root.rglob('*') if p.is_file()}
            self.assertEqual(before_hashes, after_dry)

            # 2. Confirm repair
            applied = engine.normalize_task_records(project, confirm=True)
            self.assertEqual(applied['status'], 'PASS')
            self.assertTrue(applied['applied'])
            self.assertEqual(applied['reason'], 'NORMALIZED')
            self.assertEqual(applied['revision'], 1)
            self.assertTrue(Path(applied['backup']).exists())

            # 3. Post-normalization verification
            post_diag = engine.diagnose_pending_task_commit(project)
            self.assertEqual(post_diag['status'], 'PASS')
            self.assertEqual(post_diag['reason'], 'NO_PENDING_COMMIT')

            post_inspect = engine.inspect_state(project)
            self.assertEqual(post_inspect['status'], 'PASS')

            task_read = engine.execute(CommandEnvelope('read-1', 'task.read', 'tester', 'managed', 1, None, {'task_id': task_id}))
            self.assertEqual(task_read['status'], 'PASS')
            self.assertEqual(task_read['task']['title'], 'My Recovered Task Title')
            self.assertEqual(task_read['task']['status_override'], 'COMPLETE')
            self.assertIn('Full plan details', task_read['task']['plan'])

    def test_state_normalize_missing_title_demands_manual_or_override(self):
        with tempfile.TemporaryDirectory(dir=ROOT / '.test-workspace') as temporary:
            project = initialize_project_state(Path(temporary) / 'Managed', 'managed', 'Managed')
            manifest_path = project.state_root / 'State-Manifest.json'
            raw = json.loads(manifest_path.read_text(encoding='utf-8'))
            task_id = 'Task-2026-10-30-Sample-02'
            raw['tasks'][task_id] = {
                'scope': 'Valid Scope',
                'plan': 'Valid Plan',
                'blockers': [],
                'report': '',
                'verification': None
            }
            manifest_path.write_text(json.dumps(raw, indent=2), encoding='utf-8')

            engine = CoreEngine({'managed': project})
            res = engine.normalize_task_records(project, confirm=False)
            self.assertEqual(res['status'], 'BLOCKED')
            self.assertEqual(res['reason'], 'MANUAL_FIELDS_REQUIRED')
            self.assertIn('title', [m['field'] for m in res['manual_fields_required'][task_id]])

            # Supply title_override
            res_override = engine.normalize_task_records(project, confirm=False, title_override='Explicit Title')
            self.assertEqual(res_override['status'], 'PASS')
            self.assertEqual(res_override['reason'], 'DRY_RUN')

    def test_state_normalize_rejects_path_traversal(self):
        with tempfile.TemporaryDirectory(dir=ROOT / '.test-workspace') as temporary:
            project = initialize_project_state(Path(temporary) / 'Managed', 'managed', 'Managed')
            manifest_path = project.state_root / 'State-Manifest.json'
            raw = json.loads(manifest_path.read_text(encoding='utf-8'))
            task_id = 'Task-2026-10-30-Sample-03'
            raw['tasks'][task_id] = {
                'title': 'Sample Title',
                'scope': 'Valid Scope',
                'plan': '../../outside.txt',
                'blockers': [],
                'report': '',
                'verification': None
            }
            manifest_path.write_text(json.dumps(raw, indent=2), encoding='utf-8')

            engine = CoreEngine({'managed': project})
            res = engine.normalize_task_records(project, confirm=False)
            self.assertEqual(res['status'], 'PASS')
            # Traversal path is not read; plan remains auto-generated or original
            change = [c for c in res['changes'].get(task_id, []) if c['field'] == 'plan']
            self.assertEqual(change, [])

    def test_state_normalize_blocks_when_pending_commit_exists(self):
        with tempfile.TemporaryDirectory(dir=ROOT / '.test-workspace') as temporary:
            project = initialize_project_state(Path(temporary) / 'Managed', 'managed', 'Managed')
            pending = project.state_root / 'History/Pending-Commit.json'
            pending.write_text('{"schema_version": "1.0"}', encoding='utf-8')
            engine = CoreEngine({'managed': project})
            res = engine.normalize_task_records(project, confirm=False)
            self.assertEqual(res['status'], 'BLOCKED')
            self.assertEqual(res['reason'], 'PENDING_COMMIT_PRESENT')

    def test_idempotent_when_healthy(self):
        with tempfile.TemporaryDirectory(dir=ROOT / '.test-workspace') as temporary:
            project = initialize_project_state(Path(temporary) / 'Managed', 'managed', 'Managed')
            engine = CoreEngine({'managed': project})
            res = engine.normalize_task_records(project, confirm=True)
            self.assertEqual(res['status'], 'PASS')
            self.assertEqual(res['reason'], 'NO_MALFORMED_TASKS')
            self.assertFalse(res['applied'])


if __name__ == '__main__':
    unittest.main()
