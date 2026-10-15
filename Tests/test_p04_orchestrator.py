from __future__ import annotations
from pathlib import Path
import json
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "Core-Engine"))
from aipm_core.orchestrator import Acceptance, Phase, TaskPlan, VerificationError
from aipm_core.task_ops import TaskOperations
from aipm_core.domain import CommandEnvelope, CoreEngine
from aipm_core.storage import initialize_project_state, StateError

ROOT = Path(__file__).resolve().parents[1]


class TaskLifecycleTests(unittest.TestCase):
    def setUp(self):
        self.workspace = tempfile.TemporaryDirectory(dir=ROOT / '.test-workspace')
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
        self.assertEqual(state['task_status'], 'COMPLETE')
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
        self.assertEqual(ops.status(task), {'status': 'COMPLETE'})

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
            self.assertEqual(ops.status(task)['status'], 'IN-PROGRESS')
        with self.assertRaises(ValueError):
            ops.verify(task, 'PASS', '')
        ops.verify(task, 'PASS', 'Tests Passed')
        ops.add_blocker(task, 'Access Required')
        self.assertEqual(ops.status(task)['status'], 'BLOCKED')

    def test_failed_artifact_projection_can_be_repaired(self):
        ops = self.ops()
        task = ops.create('Demo', 'Scope')
        original = Path.write_text
        def fail_projection(path, *args, **kwargs):
            if path.name == 'Task-Plan.md':
                raise OSError('Injected Projection Failure')
            return original(path, *args, **kwargs)
        with patch.object(Path, 'write_text', fail_projection):
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
        self.assertEqual(self.state()['task_status'], 'COMPLETE')

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


class OrchestratorTests(unittest.TestCase):
    def test_task_operations_create_plan_status_verify_report_and_blockers(self) -> None:
        import tempfile
        with tempfile.TemporaryDirectory(dir=Path(__file__).resolve().parents[1] / ".test-workspace") as temporary:
            project = initialize_project_state(Path(temporary) / 'Managed', 'managed', 'Managed')
            ops = TaskOperations(CoreEngine({'managed': project}), project)
            task = ops.create("Demo", "Scope")
            ops.plan(task, "Plan")
            ops.add_blocker(task, "Waiting For Access")
            self.assertEqual(ops.status(task)["status"], "BLOCKED")
            ops.clear_blockers(task)
            ops.verify(task, "PASS", "pytest -q")
            ops.report(task, "Verified")
            self.assertEqual(ops.status(task)["status"], "COMPLETE")
    def test_progress_uses_verified_weighted_acceptance_only(self) -> None:
        plan = TaskPlan("Task-2026-10-15-Demo", [Phase("P01", (), [Acceptance("A", 2, "PASS")]), Phase("P02", ("P01",), [Acceptance("B", 3, "UNVERIFIED")])])
        self.assertEqual(plan.progress(), 40)
        self.assertFalse(plan.can_complete("P02"))

    def test_complete_requires_dependencies_pass_and_report(self) -> None:
        plan = TaskPlan("Task-2026-10-15-Demo", [Phase("P01", (), [Acceptance("A", 1, "PASS")], report=True), Phase("P02", ("P01",), [Acceptance("B", 1, "PASS")])])
        self.assertFalse(plan.can_complete("P02"))
        plan.phases[1].report = True
        self.assertTrue(plan.can_complete("P02"))

    def test_rejects_fake_pass_and_unknown_dependency(self) -> None:
        with self.assertRaises(VerificationError):
            Phase("P01", (), [Acceptance("A", 1, "UNKNOWN")])
        with self.assertRaises(VerificationError):
            TaskPlan("Task-2026-10-15-Demo", [Phase("P02", ("P01",), [Acceptance("A", 1, "PASS")])])


if __name__ == "__main__": unittest.main()
