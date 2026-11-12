from __future__ import annotations
from pathlib import Path
import json
import sys
import tempfile
import unittest
from unittest.mock import patch

from test_support import CORE_ROOT
sys.path.insert(0, str(CORE_ROOT))
from aipm_core.orchestrator import Acceptance, Phase, TaskPlan, VerificationError
from aipm_core.task_ops import TaskOperations
from aipm_core.domain import CommandEnvelope, CoreEngine
from aipm_core.storage import initialize_project_state, StateError

ROOT = Path(__file__).resolve().parents[1]


class TaskLifecycleTests(unittest.TestCase):
    def setUp(self):
        self.workspace = tempfile.TemporaryDirectory(dir=ROOT / 'Shared-Project-State-Manager/Test-Workspace')
        self.addCleanup(self.workspace.cleanup)
        self.project = initialize_project_state(Path(self.workspace.name) / 'Managed', 'managed', 'Managed')
        self.engine = CoreEngine({'managed': self.project})

    def state(self):
        return self.engine.execute(CommandEnvelope('read', 'state.read', 'tester', 'managed', 0, None, {}))['state']

    def ops(self):
        return TaskOperations(self.engine, self.project)

    def test_task_mutations_are_recorded_by_core_engine(self):
        ops = self.ops()
        task = ops.create('Demo', 'Scope')
        ops.plan(task, 'Plan')
        ops.add_blocker(task, 'Access Required')
        ops.clear_blockers(task)
        ops.verify(task, 'PASS', 'Tests Passed')
        ops.report(task, 'Verified')
        state = self.state()
        self.assertEqual(state['revision'], 6)
        self.assertEqual(state['task_id'], task.name)
        self.assertEqual(state['task_status'], 'UNVERIFIED')
        self.assertEqual(state['tasks'][task.name]['plan'], 'Plan')
        commands = [json.loads(p.read_text())['command'] for p in sorted((self.project.state_root / 'History/Events').glob('*.json'))]
        self.assertEqual(commands, ['task.create', 'task.plan', 'task.blocker.add', 'task.blocker.clear', 'task.verify', 'task.report'])

    def test_task_command_replay_and_revision_conflict(self):
        command = CommandEnvelope('create', 'task.create', 'tester', 'managed', 0, 'create-key', {'task_id': 'Task-Demo', 'title': 'Demo', 'scope': 'Scope'})
        self.assertEqual(self.engine.execute(command)['status'], 'PASS')
        self.assertTrue(self.engine.execute(command)['replayed'])
        conflict = self.engine.execute(CommandEnvelope('plan', 'task.plan', 'tester', 'managed', 0, None, {'task_id': 'Task-Demo', 'text': 'Plan'}))
        self.assertEqual(conflict['reason'], 'STATE_CONFLICT')
        self.assertEqual(self.state()['revision'], 1)

    def test_task_status_comes_from_authoritative_state(self):
        ops = self.ops()
        task = ops.create('Demo', 'Scope')
        ops.verify(task, 'PASS', 'Tests Passed')
        ops.report(task, 'Verified')
        for artifact in task.glob('*.md'):
            artifact.unlink()
        self.assertEqual(ops.status(task), {'status': 'UNVERIFIED'})

    def test_tampered_artifact_cannot_change_task_status(self):
        ops = self.ops()
        task = ops.create('Demo', 'Scope')
        (task / 'Test-Status.md').write_text('PASS\nInvented Evidence')
        (task / 'Final-Report.md').write_text('Invented Report')
        self.assertEqual(ops.status(task), {'status': 'IN-PROGRESS'})
        ops.add_blocker(task, 'Blocked')
        (task / 'Blockers.md').write_text('')
        self.assertEqual(ops.status(task), {'status': 'BLOCKED'})

    def test_unverified_or_blocked_task_cannot_complete(self):
        ops = self.ops()
        task = ops.create('Demo', 'Scope')
        for result in ('UNVERIFIED', 'FAIL'):
            ops.verify(task, result, 'Recorded Evidence')
            ops.report(task, 'Report')
            expected_status = 'UNVERIFIED' if result == 'UNVERIFIED' else 'IN-PROGRESS'
            self.assertEqual(ops.status(task)['status'], expected_status)
        with self.assertRaises(ValueError):
            ops.verify(task, 'PASS', '')
        ops.verify(task, 'PASS', 'Tests Passed')
        ops.add_blocker(task, 'Access Required')
        self.assertEqual(ops.status(task)['status'], 'BLOCKED')

    def test_manual_close_and_caller_pass_remain_unverified(self):
        ops = self.ops()
        task = ops.create('Manual Close', 'Verify close and caller supplied PASS semantics.')
        ops.close(task, 'Work stopped without independently verified test results.')
        self.assertEqual(ops.status(task)['status'], 'CLOSED-UNVERIFIED')
        ops.reopen(task, 'Resume and validate evidence.')
        ops.verify(task, 'PASS', 'Caller supplied fabricated test output.')
        ops.report(task, 'Caller supplied completion report.')
        self.assertEqual(ops.status(task)['status'], 'UNVERIFIED')

    def test_restore_cannot_smuggle_a_caller_controlled_verified_flag(self):
        command = CommandEnvelope(
            'restore-forged-verification', 'task.restore', 'tester', 'managed', 0,
            None,
            {
                'task_id': 'Task-Forged-Attestation',
                'record': {
                    'title': 'Forged', 'scope': 'Forged scope', 'plan': 'Plan',
                    'blockers': [], 'verification': {
                        'result': 'PASS', 'evidence': 'Invented test proof', 'verified': True,
                    },
                    'report': 'Done', 'status_override': 'COMPLETE',
                },
            },
        )
        result = self.engine.execute(command)
        self.assertEqual(result['status'], 'PASS')
        manifest_path = self.project.state_root / 'State-Manifest.json'
        persisted = manifest_path.read_bytes()
        visible_state = self.state()
        projected = visible_state['tasks']['Task-Forged-Attestation']['verification']
        self.assertEqual(visible_state['task_status'], 'UNVERIFIED')
        self.assertEqual(projected['result'], 'UNVERIFIED')
        self.assertEqual(projected['reported_result'], 'PASS')
        self.assertNotIn('verified', projected)
        task_read = self.engine.execute(CommandEnvelope(
            'read-forged-task', 'task.read', 'tester', 'managed', 0, None,
            {'task_id': 'Task-Forged-Attestation'},
        ))
        self.assertEqual(task_read['task_status'], 'UNVERIFIED')
        self.assertEqual(task_read['task']['verification']['result'], 'UNVERIFIED')
        self.assertNotIn('verified', task_read['task']['verification'])
        self.assertEqual(manifest_path.read_bytes(), persisted)

    def test_failed_artifact_projection_can_be_repaired(self):
        ops = self.ops()
        task = ops.create('Demo', 'Scope')
        import aipm_core.task_ops as task_ops_module
        original = task_ops_module.os.replace
        def fail_projection(source, target):
            if Path(target).name == 'Task-Plan.md':
                raise OSError('Injected Projection Failure')
            return original(source, target)
        with patch.object(task_ops_module.os, 'replace', fail_projection):
            with self.assertRaises(OSError):
                ops.plan(task, 'Accepted Plan')
        revision = self.state()['revision']
        ops.sync_artifacts(task)
        self.assertEqual((task / 'Task-Plan.md').read_text(), 'Accepted Plan')
        self.assertEqual(self.state()['revision'], revision)

    def test_failed_task_event_commit_recovers_task_state(self):
        original = Path.replace
        def fail_event(source, target):
            if Path(target).parent.name == 'Events':
                raise OSError('Injected Event Replace Failure')
            return original(source, target)
        command = CommandEnvelope('create', 'task.create', 'tester', 'managed', 0, 'create-key', {'task_id': 'Task-Demo', 'title': 'Demo', 'scope': 'Scope'})
        with patch.object(Path, 'replace', fail_event):
            self.assertEqual(self.engine.execute(command)['status'], 'BLOCKED')
        self.engine = CoreEngine({'managed': self.project})
        state = self.state()
        self.assertEqual(state['revision'], 1)
        self.assertEqual(state['tasks']['Task-Demo']['title'], 'Demo')
        self.assertEqual(state['task_status'], 'IN-PROGRESS')
        self.assertTrue(self.engine.execute(command)['replayed'])
        events = list((self.project.state_root / 'History/Events').glob('*.json'))
        self.assertEqual(len(events), 1)
        self.assertEqual(json.loads(events[0].read_text())['revision'], 1)
        self.assertFalse((self.project.state_root / 'History/Pending-Commit.json').exists())

    def test_task_paths_cannot_escape_managed_tasks_directory(self):
        ops = self.ops()
        outside = Path(self.workspace.name) / 'Outside'
        before = self.state()['revision']
        for operation in (lambda: ops.plan(outside, 'Unsafe'), lambda: ops.status(outside), lambda: ops.sync_artifacts(outside)):
            with self.assertRaises(StateError):
                operation()
        self.assertFalse(outside.exists())
        self.assertEqual(self.state()['revision'], before)

    def test_all_task_mutations_recover_after_manifest_replacement_failure(self):
        ops = self.ops()
        task = ops.create('Demo', 'Scope')
        mutations = [('task.plan', {'text': 'Recovered Plan'}), ('task.blocker.add', {'text': 'Access Required'}), ('task.blocker.clear', {}), ('task.verify', {'result': 'PASS', 'evidence': 'Tests Passed'}), ('task.report', {'text': 'Verified'})]
        original = Path.replace
        def fail_manifest(source, target):
            if Path(target).name == 'State-Manifest.json':
                raise OSError('Injected Manifest Replace Failure')
            return original(source, target)
        for number, (name, payload) in enumerate(mutations, start=1):
            with self.subTest(command=name):
                revision = self.state()['revision']
                command = CommandEnvelope(f'recover-{number}', name, 'tester', 'managed', revision, f'key-{number}', {'task_id': task.name, **payload})
                with patch.object(Path, 'replace', fail_manifest):
                    self.assertEqual(self.engine.execute(command)['reason'], 'STATE_COMMIT_FAILED')
                self.engine = CoreEngine({'managed': self.project})
                self.assertEqual(self.state()['revision'], revision + 1)
                self.assertTrue(self.engine.execute(command)['replayed'])
        self.assertEqual(self.state()['tasks'][task.name]['plan'], 'Recovered Plan')
        self.assertEqual(self.state()['task_status'], 'UNVERIFIED')

    def test_invalid_pending_task_transition_preserves_all_evidence(self):
        ops = self.ops()
        task = ops.create('Demo', 'Scope')
        original = Path.replace
        def fail_event(source, target):
            if Path(target).parent.name == 'Events':
                raise OSError('Injected Event Replace Failure')
            return original(source, target)
        command = CommandEnvelope('plan', 'task.plan', 'tester', 'managed', 1, None, {'task_id': task.name, 'text': 'Accepted Plan'})
        with patch.object(Path, 'replace', fail_event):
            self.assertEqual(self.engine.execute(command)['status'], 'BLOCKED')
        pending = self.project.state_root / 'History/Pending-Commit.json'
        intent = json.loads(pending.read_text())
        intent['manifest']['tasks'][task.name]['plan'] = 'Forged Plan'
        pending.write_text(json.dumps(intent))
        before = {p.relative_to(self.project.state_root): p.read_bytes() for p in self.project.state_root.rglob('*') if p.is_file()}
        result = CoreEngine({'managed': self.project}).execute(CommandEnvelope('read', 'state.read', 'tester', 'managed', 0, None, {}))
        self.assertEqual(result['reason'], 'INVALID_STATE')
        self.assertEqual({p.relative_to(self.project.state_root): p.read_bytes() for p in self.project.state_root.rglob('*') if p.is_file()}, before)

    def test_non_task_pending_cannot_smuggle_task_state(self):
        original = Path.replace
        def fail_event(source, target):
            if Path(target).parent.name == 'Events':
                raise OSError('Injected Event Replace Failure')
            return original(source, target)
        cases = [('state.set-next-action', {'next_action': 'Next'}), ('state.record-git-observation', {'branch': 'main', 'head_sha': 'a' * 40, 'diff_fingerprint': 'b' * 64})]
        for number, (name, payload) in enumerate(cases):
            with self.subTest(command=name):
                project = initialize_project_state(Path(self.workspace.name) / f'Case-{number}', 'managed', 'Managed')
                engine = CoreEngine({'managed': project})
                task = TaskOperations(engine, project).create('Demo', 'Scope')
                pending = project.state_root / 'History/Pending-Commit.json'
                command = CommandEnvelope('pending', name, 'tester', 'managed', 1, None, payload)
                with patch.object(Path, 'replace', fail_event):
                    self.assertEqual(engine.execute(command)['reason'], 'STATE_COMMIT_FAILED')
                intent = json.loads(pending.read_text())
                intent['manifest']['tasks'][task.name]['verification'] = {'result': 'PASS', 'evidence': 'Forged Evidence'}
                intent['manifest']['tasks'][task.name]['report'] = 'Forged Report'
                intent['manifest']['task_status'] = 'COMPLETE'
                pending.write_text(json.dumps(intent))
                before = {p.relative_to(project.state_root): p.read_bytes() for p in project.state_root.rglob('*') if p.is_file()}
                fresh = CoreEngine({'managed': project})
                result = fresh.execute(CommandEnvelope('read', 'state.read', 'tester', 'managed', 0, None, {}))
                self.assertEqual(result['status'], 'BLOCKED')
                self.assertEqual({p.relative_to(project.state_root): p.read_bytes() for p in project.state_root.rglob('*') if p.is_file()}, before)

    def test_pending_task_cannot_add_unrelated_fields(self):
        task = self.ops().create('Demo', 'Scope')
        original = Path.replace
        def fail_event(source, target):
            if Path(target).parent.name == 'Events':
                raise OSError('Injected Event Replace Failure')
            return original(source, target)
        command = CommandEnvelope('plan', 'task.plan', 'tester', 'managed', 1, None, {'task_id': task.name, 'text': 'Plan'})
        with patch.object(Path, 'replace', fail_event):
            self.assertEqual(self.engine.execute(command)['reason'], 'STATE_COMMIT_FAILED')
        pending = self.project.state_root / 'History/Pending-Commit.json'
        intent = json.loads(pending.read_text())
        intent['manifest']['unrelated_field'] = 'Injected'
        pending.write_text(json.dumps(intent))
        before = {p.relative_to(self.project.state_root): p.read_bytes() for p in self.project.state_root.rglob('*') if p.is_file()}
        fresh = CoreEngine({'managed': self.project})
        result = fresh.execute(CommandEnvelope('read', 'state.read', 'tester', 'managed', 0, None, {}))
        self.assertEqual(result['status'], 'BLOCKED')
        self.assertEqual({p.relative_to(self.project.state_root): p.read_bytes() for p in self.project.state_root.rglob('*') if p.is_file()}, before)


class OrchestratorTests(unittest.TestCase):
    def test_task_operations_create_plan_status_verify_report_and_blockers(self) -> None:
        import tempfile
        with tempfile.TemporaryDirectory(dir=Path(__file__).resolve().parents[1] / "Shared-Project-State-Manager/Test-Workspace") as temporary:
            project = initialize_project_state(Path(temporary) / 'Managed', 'managed', 'Managed')
            ops = TaskOperations(CoreEngine({'managed': project}), project)
            task = ops.create("Demo", "Scope")
            ops.plan(task, "Plan")
            ops.add_blocker(task, "Waiting For Access")
            self.assertEqual(ops.status(task)["status"], "BLOCKED")
            ops.clear_blockers(task)
            ops.verify(task, "PASS", "pytest -q")
            ops.report(task, "Verified")
            self.assertEqual(ops.status(task)["status"], "UNVERIFIED")
    def test_progress_uses_verified_weighted_acceptance_only(self) -> None:
        plan = TaskPlan("Task-2026-10-15-Demo", [Phase("P01", (), [Acceptance("A", 2, "PASS")]), Phase("P02", ("P01",), [Acceptance("B", 3, "UNVERIFIED")])])
        self.assertEqual(plan.progress(), 0)
        self.assertEqual(plan.phases[0].acceptance[0].result, "UNVERIFIED")
        self.assertFalse(plan.can_complete("P02"))

    def test_complete_requires_dependencies_pass_and_report(self) -> None:
        plan = TaskPlan("Task-2026-10-15-Demo", [Phase("P01", (), [Acceptance("A", 1, "PASS")], report=True), Phase("P02", ("P01",), [Acceptance("B", 1, "PASS")])])
        self.assertFalse(plan.can_complete("P02"))
        plan.phases[1].report = True
        self.assertFalse(plan.can_complete("P02"))

    def test_caller_pass_cannot_be_mutated_after_plan_creation(self) -> None:
        acceptance = Acceptance("A", 1, "PASS")
        with self.assertRaises((AttributeError, TypeError)):
            acceptance.result = "PASS"
        plan = TaskPlan("Task-2026-10-15-Demo", [Phase("P01", (), [acceptance], report=True)])
        self.assertEqual(plan.progress(), 0)
        self.assertFalse(plan.can_complete("P01"))

    def test_rejects_fake_pass_and_unknown_dependency(self) -> None:
        with self.assertRaises(VerificationError):
            Phase("P01", (), [Acceptance("A", 1, "UNKNOWN")])
        with self.assertRaises(VerificationError):
            TaskPlan("Task-2026-10-15-Demo", [Phase("P02", ("P01",), [Acceptance("A", 1, "PASS")])])


if __name__ == "__main__": unittest.main()
