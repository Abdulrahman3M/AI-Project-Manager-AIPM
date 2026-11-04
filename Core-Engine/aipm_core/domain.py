"""Versioned commands, results, and immutable event records for AIPM."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import json
import copy
import hashlib
from pathlib import Path
import re
import shutil
from typing import Any
from uuid import uuid4

from .storage import ManagedProject, StateError, _atomic_json, _canonical, _inside, validate_managed_project


@dataclass(frozen=True)
class CommandEnvelope:
    request_id: str
    command: str
    actor: str
    project_id: str
    expected_revision: int
    idempotency_key: str | None
    input: dict[str, Any]


class CoreEngine:
    """The only P03 writer for registered managed-project state."""

    def __init__(self, projects: dict[str, ManagedProject]) -> None:
        self.projects = projects

    TASK_COMMANDS = {'task.create', 'task.plan', 'task.blocker.add', 'task.blocker.clear', 'task.verify', 'task.report', 'task.checkpoint', 'task.close', 'task.reopen', 'task.restore', 'task.unregister', 'task.edit', 'task.rename', 'task.reconcile-and-create', 'task.reconcile'}

    DIAGNOSIS_NEXT_STEP = 'Run state-validate for the exact location, then state-normalize (dry run first).'

    @classmethod
    def _diagnosis_cause(cls, error: BaseException, project: ManagedProject) -> str:
        if isinstance(error, StateError):
            return f'The state failed validation: {cls._error_detail(error, project)}.'
        return 'AIPM could not prove that this state matches the supported safe-repair pattern.'

    @staticmethod
    def task_status(task: dict[str, Any]) -> str:
        if task['blockers']:
            return 'BLOCKED'
        if task.get('status_override') == 'COMPLETE':
            return 'COMPLETE'
        verification = task['verification']
        return 'COMPLETE' if verification and verification['result'] == 'PASS' and verification['evidence'].strip() and task['report'].strip() else 'IN-PROGRESS'

    @classmethod
    def _apply_task(cls, manifest: dict[str, Any], command: str, payload: dict[str, Any]) -> None:
        tasks = manifest.setdefault('tasks', {})
        if command in {'task.reconcile-and-create', 'task.reconcile'}:
            recovered = payload.get('recovered_tasks', [])
            if not isinstance(recovered, list) or len(recovered) > 100 or (command == 'task.reconcile-and-create' and not recovered):
                raise StateError('Invalid Recovered Task Set')
            for item in recovered:
                if not isinstance(item, dict):
                    raise StateError('Invalid Recovered Task')
                recovered_id, record = item.get('task_id'), item.get('record')
                if not isinstance(recovered_id, str) or not re.fullmatch(r'Task-[A-Za-z0-9][A-Za-z0-9_-]{0,159}', recovered_id) or not isinstance(record, dict):
                    raise StateError('Invalid Recovered Task')
                if command == 'task.reconcile-and-create' and recovered_id in tasks:
                    raise StateError('Invalid Recovered Task')
                restored = copy.deepcopy(record)
                restored.setdefault('blockers', [])
                restored.setdefault('verification', None)
                restored.setdefault('report', '')
                cls._validate_task_record(restored)
                tasks[recovered_id] = restored
            if command == 'task.reconcile-and-create':
                cls._apply_task(manifest, 'task.create', {key: payload.get(key) for key in ('task_id', 'title', 'scope')})
                return
            next_command = payload.get('next_command')
            if next_command is None:
                active_id = payload.get('task_id')
                if active_id in tasks:
                    manifest['task_id'] = active_id
                    manifest['task_status'] = cls.task_status(tasks[active_id])
                elif tasks:
                    latest_id = sorted(tasks.keys())[-1]
                    manifest['task_id'] = latest_id
                    manifest['task_status'] = cls.task_status(tasks[latest_id])
                else:
                    manifest['task_id'] = None
                    manifest['task_status'] = 'NOT-STARTED'
                return
            next_input = payload.get('next_input')
            if not isinstance(next_command, str) or next_command not in (cls.TASK_COMMANDS - {'task.reconcile', 'task.reconcile-and-create'}) or not isinstance(next_input, dict):
                raise StateError('Invalid Reconciled Task Command')
            cls._apply_task(manifest, next_command, next_input)
            return
        task_id = payload.get('task_id')
        if not isinstance(task_id, str) or not re.fullmatch(r'Task-[A-Za-z0-9][A-Za-z0-9_-]{0,159}', task_id):
            raise StateError('Invalid Task Identity')
        if command == 'task.restore':
            if task_id in tasks:
                raise StateError('Task Already Exists')
            record = payload.get('record')
            allowed = ('title', 'scope', 'plan', 'blockers', 'verification', 'report', 'status_override', 'last_verified_action', 'next_action', 'completed_work', 'changed_files', 'test_results')
            if not isinstance(record, dict):
                raise StateError('Invalid Task Input')
            restored = copy.deepcopy({key: record[key] for key in allowed if key in record})
            restored.setdefault('blockers', [])
            restored.setdefault('verification', None)
            restored.setdefault('report', '')
            cls._validate_task_record(restored)
            tasks[task_id] = restored
        elif command == 'task.unregister':
            if task_id not in tasks:
                raise StateError('Task Not Found')
            del tasks[task_id]
            if manifest.get('task_id') == task_id:
                if tasks:
                    latest_id = sorted(tasks.keys())[-1]
                    manifest['task_id'] = latest_id
                    manifest['task_status'] = cls.task_status(tasks[latest_id])
                else:
                    manifest['task_id'] = None
                    manifest['task_status'] = 'NOT-STARTED'
            return
        elif command == 'task.rename':
            if task_id not in tasks:
                raise StateError('Task Not Found')
            new_task_id = payload.get('new_task_id')
            if not isinstance(new_task_id, str) or not re.fullmatch(r'Task-[A-Za-z0-9][A-Za-z0-9_-]{0,159}', new_task_id):
                raise StateError('Invalid Task Identity')
            if new_task_id in tasks and new_task_id != task_id:
                raise StateError('Task Identity Already Exists')
            tasks[new_task_id] = tasks.pop(task_id)
            task_id = new_task_id
        elif command == 'task.create':
            if task_id in tasks:
                raise StateError('Task Already Exists')
            if any(not isinstance(payload.get(key), str) or not payload[key].strip() for key in ('title', 'scope')):
                raise StateError('Invalid Task Input')
            tasks[task_id] = {'title': payload['title'], 'scope': payload['scope'], 'plan': f"# {payload['title']}\n\n{payload['scope']}\n", 'blockers': [], 'verification': None, 'report': '', 'status_override': None}
        else:
            if task_id not in tasks:
                raise StateError('Task Not Found')
            task = tasks[task_id]
            if command in {'task.plan', 'task.blocker.add', 'task.report'}:
                text = payload.get('text')
                if not isinstance(text, str) or not text.strip():
                    raise StateError('Invalid Task Text')
                if command == 'task.plan':
                    task.update(plan=text, verification=None, report='', status_override=None)
                elif command == 'task.report':
                    task['report'] = text
                else:
                    task['blockers'].append(text)
            elif command == 'task.blocker.clear':
                task['blockers'] = []
            elif command == 'task.verify':
                result, evidence = payload.get('result'), payload.get('evidence')
                if result not in ('PASS', 'FAIL', 'UNVERIFIED') or not isinstance(evidence, str) or not evidence.strip():
                    raise StateError('Invalid Task Evidence')
                task['verification'] = {'result': result, 'evidence': evidence}
                if result != 'PASS':
                    task['status_override'] = None
            elif command == 'task.checkpoint':
                last_verified = payload.get('last_verified_action')
                next_action = payload.get('next_action')
                if any(not isinstance(value, str) or not value.strip() for value in (last_verified, next_action)):
                    raise StateError('Invalid Task Checkpoint')
                task['last_verified_action'] = last_verified
                task['next_action'] = next_action
                for field in ('completed_work', 'changed_files', 'test_results'):
                    values = payload.get(field, [])
                    if not isinstance(values, list) or len(values) > 100 or any(not isinstance(value, str) or not value.strip() for value in values):
                        raise StateError('Invalid Task Checkpoint')
                    task[field] = values
            elif command == 'task.close':
                text = payload.get('text')
                if not isinstance(text, str) or not text.strip():
                    raise StateError('Invalid Task Close Note')
                if task['blockers']:
                    raise StateError('Task Blockers Must Be Cleared Before Closing')
                task['status_override'] = 'COMPLETE'
                task['report'] = text
            elif command == 'task.reopen':
                text = payload.get('text')
                if not isinstance(text, str) or not text.strip():
                    raise StateError('Invalid Task Reopen Note')
                task['status_override'] = None
                task['verification'] = None
                task['report'] = text
            elif command == 'task.edit':
                title = payload.get('title')
                scope = payload.get('scope')
                if title is None and scope is None:
                    raise StateError('Invalid Task Edit')
                if title is not None:
                    if not isinstance(title, str) or not title.strip():
                        raise StateError('Invalid Task Title')
                    task['title'] = title.strip()
                if scope is not None:
                    if not isinstance(scope, str) or not scope.strip():
                        raise StateError('Invalid Task Scope')
                    task['scope'] = scope.strip()
            else:
                raise StateError('Unsupported Task Command')
        manifest['task_id'] = task_id
        manifest['task_status'] = cls.task_status(tasks[task_id])

    @staticmethod
    def _validate_manifest(manifest: Any, project: ManagedProject) -> None:
        if not isinstance(manifest, dict) or manifest.get("schema_version") not in ("1.0", "1.1") or type(manifest.get("revision")) is not int or manifest["revision"] < 0 or manifest.get("project_id") != project.project_id:
            raise StateError("Invalid State Manifest")
        if manifest.get("schema_version") == "1.1" and ("tasks" not in manifest or "diff_fingerprint" not in manifest):
            raise StateError("Missing State Manifest Fields")
        if not isinstance(manifest.get("tasks", {}), dict) or (manifest.get("diff_fingerprint") is not None and not isinstance(manifest["diff_fingerprint"], str)):
            raise StateError("Invalid State Manifest Fields")
        for task_id, task in manifest.get('tasks', {}).items():
            if not isinstance(task_id, str) or not re.fullmatch(r'Task-[A-Za-z0-9][A-Za-z0-9_-]{0,159}', task_id) or not isinstance(task, dict):
                raise StateError('Invalid Task State')
            CoreEngine._validate_task_record(task)
        if manifest.get('task_status') not in ('NOT-STARTED', 'IN-PROGRESS', 'BLOCKED', 'COMPLETE') and isinstance(manifest.get('tasks'), dict):
            active_id = manifest.get('task_id')
            if active_id and active_id in manifest['tasks']:
                manifest['task_status'] = CoreEngine.task_status(manifest['tasks'][active_id])
            elif manifest.get('tasks'):
                latest_id = sorted(manifest['tasks'].keys())[-1]
                manifest['task_status'] = CoreEngine.task_status(manifest['tasks'][latest_id])
            else:
                manifest['task_status'] = 'NOT-STARTED'
        required = ("task_status", "state_health", "last_verified_action", "updated_at", "updated_by")
        if any(not isinstance(manifest.get(key), str) or not manifest[key].strip() for key in required):
            raise StateError("Invalid State Manifest Fields")
        nullable = ("task_id", "active_phase", "next_action", "branch", "head_sha")
        if any(key not in manifest or (manifest[key] is not None and not isinstance(manifest[key], str)) for key in nullable):
            raise StateError("Invalid State Manifest Fields")

    @staticmethod
    def _validate_task_record(task: dict[str, Any]) -> None:
        if isinstance(task.get('title'), str) and task['title'].strip() and isinstance(task.get('scope'), str) and task['scope'].strip():
            if not isinstance(task.get('plan'), str) or not task['plan'].strip():
                task['plan'] = f"# {task['title'].strip()}\n\n{task['scope'].strip()}\n"
        if task.get('report') is None:
            task['report'] = ''
        if task.get('blockers') is None:
            task['blockers'] = []
        if any(not isinstance(task.get(key), str) or not task[key].strip() for key in ('title', 'scope', 'plan')) or not isinstance(task.get('report'), str) or not isinstance(task.get('blockers'), list) or any(not isinstance(text, str) or not text.strip() for text in task['blockers']):
            raise StateError('Invalid Task State')
        verification = task.get('verification')
        if isinstance(verification, str):
            evidence = verification.strip()
            if not evidence:
                task['verification'] = None
            else:
                upper = evidence.upper()
                if upper.startswith('PASS'):
                    res = 'PASS'
                elif upper.startswith('FAIL'):
                    res = 'FAIL'
                else:
                    res = 'UNVERIFIED'
                task['verification'] = {'result': res, 'evidence': evidence}
        verification = task.get('verification')
        if isinstance(verification, dict):
            evidence = verification.get('evidence')
            if isinstance(evidence, str) and evidence.strip() and verification.get('result') not in ('PASS', 'FAIL', 'UNVERIFIED'):
                raw_res = str(verification.get('result', '')).strip().upper()
                new_res = 'PASS' if raw_res in ('PASSED', 'COMPLETE', 'COMPLETED') else ('FAIL' if raw_res in ('FAILED', 'ERROR', 'BLOCKED') else 'UNVERIFIED')
                if raw_res and not evidence.strip().startswith(f"[{raw_res}]"):
                    verification['evidence'] = f"[{raw_res}] {evidence.strip()}"
                verification['result'] = new_res
        if 'verification' not in task or (verification is not None and (not isinstance(verification, dict) or verification.get('result') not in ('PASS', 'FAIL', 'UNVERIFIED') or not isinstance(verification.get('evidence'), str) or not verification['evidence'].strip())):
            raise StateError('Invalid Task Evidence')
        if task.get('status_override') == 'COMPLETED':
            task['status_override'] = 'COMPLETE'
        elif task.get('status_override') not in (None, 'COMPLETE'):
            task['status_override'] = None
        task.setdefault('status_override', None)
        if task['status_override'] not in (None, 'COMPLETE'):
            raise StateError('Invalid Task Status Override')
        for field in ('last_verified_action', 'next_action'):
            if field in task and (not isinstance(task[field], str) or not task[field].strip()):
                raise StateError('Invalid Task Checkpoint')
        for field in ('completed_work', 'changed_files', 'test_results'):
            if field in task and (not isinstance(task[field], list) or len(task[field]) > 100 or any(not isinstance(value, str) or not value.strip() for value in task[field])):
                raise StateError('Invalid Task Checkpoint')

    @staticmethod
    def _validate_event(event: Any, project: ManagedProject) -> None:
        if not isinstance(event, dict) or event.get("schema_version") != "1.0" or event.get("project_id") != project.project_id or type(event.get("revision")) is not int or event["revision"] < 1:
            raise StateError("Invalid History Event")
        if any(not isinstance(event.get(key), str) or not event[key].strip() for key in ("request_id", "command", "actor")) or not isinstance(event.get("input"), dict):
            raise StateError("Invalid History Event Fields")
        if "idempotency_key" not in event or (event["idempotency_key"] is not None and not isinstance(event["idempotency_key"], str)):
            raise StateError("Invalid History Event Key")

    @classmethod
    def _history(cls, project: ManagedProject, maximum_revision: int, *, pending_revision: int | None = None) -> list[dict[str, Any]]:
        records = []
        revisions = set()
        for path in (project.state_root / "History" / "Events").glob("*.json"):
            event = json.loads(path.read_text(encoding="utf-8"))
            cls._validate_event(event, project)
            if event["revision"] > maximum_revision or event["revision"] in revisions:
                raise StateError("Invalid History Revision")
            revisions.add(event["revision"])
            records.append(event)
        required_count = maximum_revision if pending_revision is None else pending_revision - 1
        committed = revisions - ({pending_revision} if pending_revision is not None else set())
        # Positive, unique, bounded revisions with this count are exactly 1..N.
        if len(committed) != required_count:
            raise StateError("Missing History Revision")
        return records

    @classmethod
    def _legacy_task_normalization_matches_history(
        cls,
        raw_tasks: Any,
        normalized_tasks: Any,
        historical_tasks: Any,
    ) -> bool:
        """Allow only documented legacy field normalization to bridge old state and history."""
        if not all(isinstance(tasks, dict) for tasks in (raw_tasks, normalized_tasks, historical_tasks)):
            return False
        if raw_tasks.keys() != normalized_tasks.keys() or raw_tasks.keys() != historical_tasks.keys():
            return False
        for task_id, raw_task in raw_tasks.items():
            normalized_task = normalized_tasks[task_id]
            historical_task = historical_tasks[task_id]
            if not all(isinstance(task, dict) for task in (raw_task, normalized_task, historical_task)):
                return False
            reconciled = copy.deepcopy(historical_task)
            verification = raw_task.get('verification')
            status_override = raw_task.get('status_override')
            if isinstance(verification, str):
                reconciled['verification'] = copy.deepcopy(normalized_task.get('verification'))
            elif isinstance(verification, dict) and verification.get('result') not in ('PASS', 'FAIL', 'UNVERIFIED'):
                reconciled['verification'] = copy.deepcopy(normalized_task.get('verification'))
            if status_override == 'COMPLETED' or (status_override is not None and status_override != 'COMPLETE'):
                reconciled['status_override'] = normalized_task.get('status_override')
            if (raw_task.get('plan') is None or not str(raw_task.get('plan', '')).strip()) and normalized_task.get('plan'):
                reconciled['plan'] = normalized_task.get('plan')
            if raw_task.get('report') is None:
                reconciled['report'] = ''
            if raw_task.get('blockers') is None:
                reconciled['blockers'] = []
            if reconciled != normalized_task:
                return False
        return True

    @classmethod
    def _recover(cls, project: ManagedProject) -> None:
        """Finish a durable intent before exposing state or accepting a mutation."""
        pending = project.state_root / "History" / "Pending-Commit.json"
        if not pending.exists():
            return
        transaction = json.loads(pending.read_text(encoding="utf-8"))
        if not isinstance(transaction, dict) or transaction.get("schema_version") != "1.0":
            raise StateError("Invalid Pending Commit Envelope")
        manifest = transaction["manifest"]
        event = transaction["event"]
        cls._validate_manifest(manifest, project)
        cls._validate_event(event, project)
        revision = manifest["revision"]
        if type(revision) is not int or revision < 1 or event["revision"] != revision or manifest["project_id"] != project.project_id or event["project_id"] != project.project_id:
            raise StateError("Invalid Pending Commit")
        manifest_path = project.state_root / "State-Manifest.json"
        raw_current = json.loads(manifest_path.read_text(encoding="utf-8"))
        current = copy.deepcopy(raw_current)
        cls._validate_manifest(current, project)
        if current["revision"] not in (revision - 1, revision) or (current["revision"] == revision and current != manifest):
            raise StateError("Pending Commit Conflicts With State")
        if manifest["schema_version"] != "1.1" or manifest["updated_by"] != event["actor"]:
            raise StateError("Pending Commit Metadata Mismatch")
        if current['revision'] == revision - 1:
            permitted = {'revision', 'schema_version', 'updated_at', 'updated_by'}
            if event['command'] in cls.TASK_COMMANDS:
                permitted.update({'tasks', 'task_id', 'task_status'})
            elif event['command'] == 'state.set-next-action':
                permitted.add('next_action')
            elif event['command'] == 'state.record-git-observation':
                permitted.update({'branch', 'head_sha', 'diff_fingerprint'})
            previous = {**current}
            previous.setdefault('tasks', {})
            previous.setdefault('diff_fingerprint', None)
            unrelated = (previous.keys() | manifest.keys()) - permitted
            if any(key not in previous or key not in manifest or previous[key] != manifest[key] for key in unrelated):
                raise StateError('Pending Commit Changes Unrelated State')
        history = cls._history(project, revision, pending_revision=revision)
        if any(record["revision"] == revision and record != event for record in history):
            raise StateError("Pending Commit Conflicts With History")
        if event['command'] in cls.TASK_COMMANDS:
            # Replay accepted task intents before publishing either transaction file.
            expected = {'tasks': {}, 'task_id': None, 'task_status': 'NOT-STARTED'}
            for record in sorted(history, key=lambda record: record['revision']):
                if record['revision'] < revision and record['command'] in cls.TASK_COMMANDS:
                    cls._apply_task(expected, record['command'], record['input'])
            if current.get('tasks', {}) != expected['tasks'] and event['command'] not in {'task.reconcile-and-create', 'task.reconcile'}:
                if current['revision'] == revision - 1:
                    expected['tasks'] = copy.deepcopy(current.get('tasks', {}))
                    expected['task_id'] = current.get('task_id')
                    expected['task_status'] = current.get('task_status')
                elif current['revision'] == revision and current == manifest:
                    # State-Manifest.json was already replaced with the validated pending manifest;
                    # allow event file publication to finish even if an older revision drifted.
                    expected['tasks'] = copy.deepcopy(manifest.get('tasks', {}))
                    expected['task_id'] = manifest.get('task_id')
                    expected['task_status'] = manifest.get('task_status')
            if event['command'] in {'task.reconcile-and-create', 'task.reconcile'} and current['revision'] == revision - 1:
                current_tasks = current.get('tasks', {})
                expected_tasks = expected['tasks']
                if not isinstance(current_tasks, dict) or not set(expected_tasks).issubset(current_tasks):
                    raise StateError('Task History Conflicts With State')
                if event['command'] == 'task.reconcile-and-create':
                    if current.get('task_id') != expected['task_id'] or current.get('task_status') != expected['task_status']:
                        raise StateError('Active Task Pointer Conflicts With History')
                    extras = {key: current_tasks[key] for key in current_tasks.keys() - expected_tasks.keys()}
                    if any(current_tasks[key] != expected_tasks[key] for key in expected_tasks):
                        raw_tasks = raw_current.get('tasks') if isinstance(raw_current, dict) else None
                        if not cls._legacy_task_normalization_matches_history(raw_tasks, current_tasks, expected_tasks):
                            raise StateError('Task History Conflicts With State')
                    recovered = event['input'].get('recovered_tasks')
                    if not isinstance(recovered, list) or {item.get('task_id'): item.get('record') for item in recovered if isinstance(item, dict)} != extras or len(recovered) != len(extras):
                        raise StateError('Recovered Task Set Conflicts With State')
                else:
                    drifted = {key: current_tasks[key] for key in current_tasks if key not in expected_tasks or current_tasks[key] != expected_tasks[key]}
                    recovered = event['input'].get('recovered_tasks')
                    if not isinstance(recovered, list) or {item.get('task_id'): item.get('record') for item in recovered if isinstance(item, dict)} != drifted or len(recovered) != len(drifted):
                        raise StateError('Recovered Task Set Conflicts With State')
                expected['tasks'] = copy.deepcopy(expected_tasks)
                expected['task_id'] = current.get('task_id')
                expected['task_status'] = current.get('task_status')
            if not (current['revision'] == revision and current == manifest and event['command'] not in {'task.reconcile-and-create', 'task.reconcile'}):
                cls._apply_task(expected, event['command'], event['input'])
            if any(manifest[key] != expected[key] for key in ('tasks', 'task_id', 'task_status')):
                raise StateError('Pending Commit Task Mismatch')
        elif event["command"] == "state.set-next-action":
            action = event["input"].get("next_action")
            if not isinstance(action, str) or not action.strip() or manifest["next_action"] != action:
                raise StateError("Pending Commit Action Mismatch")
        elif event["command"] == "state.record-git-observation":
            if any(key not in event["input"] or manifest[key] != event["input"][key] for key in ("branch", "head_sha", "diff_fingerprint")):
                raise StateError("Pending Commit Git Mismatch")
        elif event["command"] == "state.upgrade-schema":
            if event['input'] or (current['revision'] == revision - 1 and current.get('schema_version') != '1.0'):
                raise StateError('Pending Schema Upgrade Mismatch')
        else:
            raise StateError("Unsupported Pending Commit Command")
        event_path = project.state_root / "History" / "Events" / f"{revision:020d}.json"
        if event_path.exists():
            if json.loads(event_path.read_text(encoding="utf-8")) != event:
                raise StateError("Pending Commit Conflicts With Event")
        else:
            _atomic_json(event_path, event)
        if current != manifest:
            _atomic_json(manifest_path, manifest)
        pending.unlink()

    @classmethod
    def diagnose_pending_task_commit(cls, project: ManagedProject) -> dict[str, Any]:
        """Explain a repairable pending task transaction blocked by untracked or drifted task rows."""
        try:
            validate_managed_project(project)
        except StateError as error:
            return {'status': 'BLOCKED', 'repairable': False, 'reason': str(error), 'cause': 'The project state path failed AIPM ownership and isolation checks.', 'remedy': 'Correct the registered project path before requesting state repair.'}
        pending_path = project.state_root / 'History' / 'Pending-Commit.json'
        if not pending_path.is_file():
            try:
                manifest_path = project.state_root / 'State-Manifest.json'
                if not manifest_path.is_file():
                    return {
                        'status': 'PASS', 'repairable': False, 'reason': 'NO_PENDING_COMMIT',
                        'cause': 'There is no pending commit and State-Manifest.json is missing.',
                        'remedy': 'Restore or reinitialize the project state.'
                    }
                raw = json.loads(manifest_path.read_text(encoding='utf-8'))
                current = copy.deepcopy(raw)
                cls._validate_manifest(current, project)

                events_dir = project.state_root / 'History' / 'Events'
                committed_events: dict[int, dict[str, Any]] = {}
                if events_dir.is_dir():
                    for p in events_dir.glob('*.json'):
                        ev = json.loads(p.read_text(encoding='utf-8'))
                        cls._validate_event(ev, project)
                        rev = ev['revision']
                        if rev in committed_events:
                            raise StateError('Duplicate History Revision')
                        committed_events[rev] = ev

                K = 0
                while (K + 1) in committed_events:
                    K += 1

                if len(committed_events) != K:
                    raise StateError('Non-contiguous history revisions detected')

                expected = {'tasks': {}, 'task_id': None, 'task_status': 'NOT-STARTED'}
                for rev in range(1, K + 1):
                    rec = committed_events[rev]
                    if rec['command'] in cls.TASK_COMMANDS:
                        cls._apply_task(expected, rec['command'], rec['input'])

                tasks = current.get('tasks', {})
                if not isinstance(tasks, dict):
                    raise StateError('Invalid Task State')

                drifted_ids: set[str] = set(tasks.keys() - expected['tasks'].keys())
                for key in expected['tasks']:
                    if key not in tasks:
                        raise StateError(f'Historical task {key} is missing from manifest')
                    if tasks[key] != expected['tasks'][key]:
                        if not cls._legacy_task_normalization_matches_history({key: (raw.get('tasks') or {}).get(key)}, {key: tasks[key]}, {key: expected['tasks'][key]}):
                            drifted_ids.add(key)

                for key in tasks:
                    cls._validate_task_record(tasks[key])

                if current['revision'] != K or drifted_ids:
                    return {
                        'status': 'PASS',
                        'repairable': True,
                        'reason': 'MANIFEST_HISTORY_DRIFT_RECONCILABLE',
                        'pending_command': 'task.reconcile',
                        'pending_task_id': current.get('task_id'),
                        'pending_revision': K + 1,
                        'untracked_tasks': sorted(drifted_ids),
                        'reconciled_tasks': sorted(drifted_ids),
                        'state_root': str(project.state_root),
                        'cause': f"State-Manifest.json is at revision {current['revision']} while History/Events contains {K} committed event(s), or task records were edited directly in State-Manifest.json.",
                        'remedy': f"Create a verified backup snapshot and record an explicit reconciliation event at revision {K + 1} preserving all current validated task records."
                    }

                return {
                    'status': 'PASS', 'repairable': False, 'reason': 'NO_PENDING_COMMIT',
                    'cause': 'There is no pending commit and the state manifest matches event history.',
                    'remedy': 'No state repair is needed.'
                }
            except (OSError, UnicodeError, ValueError, KeyError, TypeError) as error:
                return {
                    'status': 'BLOCKED', 'repairable': False,
                    'reason': str(error) if isinstance(error, StateError) else 'STATE_DIAGNOSIS_FAILED',
                    'cause': cls._diagnosis_cause(error, project),
                    'remedy': 'Keep the state unchanged and restore a verified Shared Project State backup or request a manual integrity review.',
                    'next_step': cls.DIAGNOSIS_NEXT_STEP
                }
        try:
            pending = json.loads(pending_path.read_text(encoding='utf-8'))
            manifest_path = project.state_root / 'State-Manifest.json'
            raw = json.loads(manifest_path.read_text(encoding='utf-8'))
            current = copy.deepcopy(raw)
            cls._validate_manifest(current, project)
            transaction = pending
            if not isinstance(transaction, dict) or transaction.get('schema_version') != '1.0':
                raise StateError('Invalid Pending Commit Envelope')
            event = transaction['event']
            target = transaction['manifest']
            cls._validate_event(event, project)
            cls._validate_manifest(target, project)
            if event['command'] not in (cls.TASK_COMMANDS - {'task.reconcile', 'task.reconcile-and-create'}) or target['revision'] not in (current['revision'], current['revision'] + 1) or event['revision'] != target['revision'] or target['project_id'] != project.project_id:
                raise StateError('Repair supports only a pending task command')
            if target['revision'] == current['revision']:
                history = cls._history(project, current['revision'], pending_revision=current['revision'])
                if any(record['revision'] == current['revision'] and record != event for record in history):
                    raise StateError('Pending commit conflicts with committed event at same revision')
                expected = {'tasks': {}, 'task_id': None, 'task_status': 'NOT-STARTED'}
                for record in sorted(history, key=lambda item: item['revision']):
                    if record['revision'] < current['revision'] and record['command'] in cls.TASK_COMMANDS:
                        cls._apply_task(expected, record['command'], record['input'])
                tasks = current.get('tasks', {})
                if not isinstance(tasks, dict) or not set(expected['tasks']).issubset(tasks):
                    raise StateError('Current task set is missing or conflicts with history')
                drifted_ids: set[str] = set(tasks.keys() - expected['tasks'].keys())
                for key in expected['tasks']:
                    if tasks[key] != expected['tasks'][key]:
                        drifted_ids.add(key)
                for key in drifted_ids:
                    cls._validate_task_record(tasks[key])
                return {
                    'status': 'PASS', 'repairable': True, 'reason': 'PENDING_COMMIT_SUPERSEDED_BY_MANIFEST_AT_SAME_REVISION',
                    'pending_command': event['command'],
                    'pending_task_id': event['input'].get('task_id'), 'pending_revision': event['revision'],
                    'untracked_tasks': sorted(drifted_ids), 'state_root': str(project.state_root),
                    'cause': 'A stranded Pending-Commit.json exists at the same revision as State-Manifest.json after State-Manifest.json was updated directly without recording the revision event.',
                    'remedy': 'Create a verified snapshot, record the current validated State-Manifest.json task state as the revision event, and apply the pending task command cleanly on top.'
                }
            history = cls._history(project, current['revision'])
            expected = {'tasks': {}, 'task_id': None, 'task_status': 'NOT-STARTED'}
            for record in sorted(history, key=lambda item: item['revision']):
                if record['command'] in cls.TASK_COMMANDS:
                    cls._apply_task(expected, record['command'], record['input'])
            tasks = current.get('tasks', {})
            if not isinstance(tasks, dict) or not set(expected['tasks']).issubset(tasks):
                raise StateError('Current task set is missing or conflicts with history')
            drifted_ids = set(tasks.keys() - expected['tasks'].keys())
            for key in expected['tasks']:
                if tasks[key] != expected['tasks'][key]:
                    if not cls._legacy_task_normalization_matches_history({key: (raw.get('tasks') or {}).get(key)}, {key: tasks[key]}, {key: expected['tasks'][key]}):
                        drifted_ids.add(key)
            for key in drifted_ids:
                cls._validate_task_record(tasks[key])
            candidate = copy.deepcopy(current)
            cls._apply_task(candidate, event['command'], event['input'])
            candidate.update({key: target[key] for key in ('revision', 'schema_version', 'updated_at', 'updated_by')})
            cls._validate_manifest(candidate, project)
            if candidate != target:
                raise StateError('Pending task data conflicts with the recorded intent')
            reason = 'PENDING_CREATE_WITH_UNTRACKED_TASKS' if event['command'] == 'task.create' and drifted_ids == (tasks.keys() - expected['tasks'].keys()) and drifted_ids else 'PENDING_TASK_COMMIT_RECONCILABLE'
            return {
                'status': 'PASS', 'repairable': True, 'reason': reason,
                'pending_command': event['command'],
                'pending_task_id': event['input'].get('task_id'), 'pending_revision': event['revision'],
                'untracked_tasks': sorted(drifted_ids), 'state_root': str(project.state_root),
                'cause': 'The manifest contains task records or fields that differ from the committed event history, or a pending task commit was interrupted before completion.',
                'remedy': 'Create a verified snapshot, record the preserved task records in one explicit reconciliation event, and finish committing the pending task operation.'
            }
        except (OSError, UnicodeError, ValueError, KeyError, TypeError) as error:
            return {
                'status': 'BLOCKED', 'repairable': False,
                'reason': str(error) if isinstance(error, StateError) else 'STATE_DIAGNOSIS_FAILED',
                'cause': cls._diagnosis_cause(error, project),
                'remedy': 'Keep the state unchanged and restore a verified Shared Project State backup or request a manual integrity review.',
                'next_step': cls.DIAGNOSIS_NEXT_STEP
            }

    def repair_pending_task_commit(self, project: ManagedProject) -> dict[str, Any]:
        """Back up and reconcile validated task rows blocking a pending task command."""
        diagnosis = self.diagnose_pending_task_commit(project)
        if diagnosis.get('status') != 'PASS' or not diagnosis.get('repairable'):
            return {'schema_version': '1.0', 'status': 'BLOCKED', 'reason': diagnosis.get('reason', 'STATE_NOT_REPAIRABLE'), 'diagnosis': diagnosis}
        state_root = project.state_root
        history_root = state_root / 'History'
        snapshots = history_root / 'Snapshots'
        backup = snapshots / ('AIPM-State-Repair-' + datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ') + '-' + uuid4().hex[:8])
        backup.mkdir(parents=True, exist_ok=False)
        files = [state_root / 'State-Manifest.json']
        pending_path = history_root / 'Pending-Commit.json'
        if pending_path.is_file():
            files.append(pending_path)
        files.extend(sorted((history_root / 'Events').glob('*.json')))
        checksums: dict[str, str] = {}
        try:
            for source in files:
                relative = source.relative_to(state_root)
                destination = backup / relative
                destination.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(source, destination)
                checksums[relative.as_posix()] = hashlib.sha256(destination.read_bytes()).hexdigest()
            backup_manifest = {'schema_version': '1.0', 'repair': diagnosis['reason'], 'project_id': project.project_id, 'created_at': datetime.now(timezone.utc).isoformat(), 'files': checksums}
            (backup / 'Backup-Manifest.json').write_text(json.dumps(backup_manifest, indent=2, sort_keys=True) + '\n', encoding='utf-8')

            confirmed_state = self.diagnose_pending_task_commit(project)
            if confirmed_state.get('status') != 'PASS' or not confirmed_state.get('repairable') or confirmed_state.get('pending_task_id') != diagnosis.get('pending_task_id') or confirmed_state.get('untracked_tasks') != diagnosis.get('untracked_tasks'):
                raise StateError('State Changed After Diagnosis; No Repair Was Applied')

            if diagnosis['reason'] == 'MANIFEST_HISTORY_DRIFT_RECONCILABLE':
                raw_current = json.loads((state_root / 'State-Manifest.json').read_text(encoding='utf-8'))
                current = copy.deepcopy(raw_current)
                self._validate_manifest(current, project)
                recovered = [{'task_id': task_id, 'record': copy.deepcopy(current['tasks'][task_id])} for task_id in diagnosis['untracked_tasks']]
                new_rev = diagnosis['pending_revision']
                event, manifest = self._build_reconcile(project, current, recovered, new_rev)
                state = self._publish_reconcile(project, event, manifest, new_rev)
                return {
                    'schema_version': '1.0',
                    'status': 'PASS',
                    'revision': state['revision'],
                    'recovered_tasks': diagnosis['untracked_tasks'],
                    'created_task_id': current.get('task_id'),
                    'backup': str(backup)
                }

            pending_path = history_root / 'Pending-Commit.json'
            pending = json.loads(pending_path.read_text(encoding='utf-8'))
            raw_current = json.loads((state_root / 'State-Manifest.json').read_text(encoding='utf-8'))
            current = copy.deepcopy(raw_current)
            self._validate_manifest(current, project)
            original_event = pending['event']
            if diagnosis['reason'] == 'PENDING_COMMIT_SUPERSEDED_BY_MANIFEST_AT_SAME_REVISION':
                recovered = [{'task_id': task_id, 'record': copy.deepcopy(current['tasks'][task_id])} for task_id in diagnosis['untracked_tasks']]
                event = {**original_event, 'command': 'task.reconcile', 'input': {
                    'task_id': original_event['input'].get('task_id'),
                    'next_command': original_event['command'],
                    'next_input': original_event['input'],
                    'recovered_tasks': recovered,
                }}
                manifest = copy.deepcopy(current)
                self._apply_task(manifest, original_event['command'], original_event['input'])
                manifest['schema_version'] = '1.1'
                manifest['updated_by'] = event['actor']
                manifest['updated_at'] = datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
                self._validate_manifest(manifest, project)
                self._validate_event(event, project)
                event_path = history_root / 'Events' / f"{event['revision']:020d}.json"
                if not event_path.exists():
                    _atomic_json(event_path, event)
                _atomic_json(state_root / 'State-Manifest.json', manifest)
                pending_path.unlink()
                state = json.loads((state_root / 'State-Manifest.json').read_text(encoding='utf-8'))
                self._validate_manifest(state, project)
                history = self._history(project, state['revision'])
                if state['revision'] != event['revision'] or not any(item == event for item in history):
                    raise StateError('Repaired state failed post-commit integrity checks')
                return {'schema_version': '1.0', 'status': 'PASS', 'revision': state['revision'], 'recovered_tasks': diagnosis['untracked_tasks'], 'created_task_id': original_event['input'].get('task_id'), 'backup': str(backup)}

            history = self._history(project, current['revision'])
            expected = {'tasks': {}, 'task_id': None, 'task_status': 'NOT-STARTED'}
            for record in sorted(history, key=lambda item: item['revision']):
                if record['command'] in self.TASK_COMMANDS:
                    self._apply_task(expected, record['command'], record['input'])
            recovered = [{'task_id': task_id, 'record': copy.deepcopy(current['tasks'][task_id])} for task_id in diagnosis['untracked_tasks']]
            if diagnosis['reason'] == 'PENDING_CREATE_WITH_UNTRACKED_TASKS':
                event = {**original_event, 'command': 'task.reconcile-and-create', 'input': {
                    'task_id': original_event['input']['task_id'], 'title': original_event['input']['title'],
                    'scope': original_event['input']['scope'], 'recovered_tasks': recovered
                }}
            elif recovered:
                event = {**original_event, 'command': 'task.reconcile', 'input': {
                    'task_id': original_event['input'].get('task_id'),
                    'next_command': original_event['command'],
                    'next_input': original_event['input'],
                    'recovered_tasks': recovered,
                }}
            else:
                event = copy.deepcopy(original_event)
            event['revision'] = current['revision'] + 1
            manifest = copy.deepcopy(current)
            if event['command'] in {'task.reconcile-and-create', 'task.reconcile'}:
                manifest['tasks'] = copy.deepcopy(expected['tasks'])
                manifest['task_id'] = expected['task_id']
                manifest['task_status'] = expected['task_status']
            self._apply_task(manifest, event['command'], event['input'])
            manifest.update({key: pending['manifest'][key] for key in ('revision', 'schema_version', 'updated_at', 'updated_by')})
            if manifest['revision'] != event['revision']:
                raise StateError('Pending revision changed during repair')
            self._validate_manifest(manifest, project)
            self._validate_event(event, project)
            if manifest != pending['manifest']:
                raise StateError('Pending task data changed after diagnosis')
            _atomic_json(pending_path, {'schema_version': '1.0', 'manifest': manifest, 'event': event})
            self._recover(project)
            state = json.loads((state_root / 'State-Manifest.json').read_text(encoding='utf-8'))
            self._validate_manifest(state, project)
            history = self._history(project, state['revision'])
            if state['revision'] != event['revision'] or not any(item == event for item in history):
                raise StateError('Repaired state failed post-commit integrity checks')
            return {'schema_version': '1.0', 'status': 'PASS', 'revision': state['revision'], 'recovered_tasks': diagnosis['untracked_tasks'], 'created_task_id': original_event['input'].get('task_id'), 'backup': str(backup)}
        except (OSError, UnicodeError, ValueError, KeyError, TypeError) as error:
            return {'schema_version': '1.0', 'status': 'BLOCKED', 'reason': str(error) if isinstance(error, StateError) else 'STATE_REPAIR_FAILED', 'backup': str(backup)}

    # ------------------------------------------------------------------
    # Reconcile helpers shared by state-repair and state-normalize.
    # ------------------------------------------------------------------
    def _build_reconcile(self, project: ManagedProject, current: dict[str, Any], recovered: list[dict[str, Any]], new_rev: int) -> tuple[dict[str, Any], dict[str, Any]]:
        """Build the explicit task.reconcile event and the manifest it produces from history."""
        event = {
            'schema_version': '1.0',
            'project_id': project.project_id,
            'revision': new_rev,
            'request_id': f"req-reconcile-{uuid4().hex[:12]}",
            'command': 'task.reconcile',
            'actor': 'aipm-state-repair',
            'idempotency_key': None,
            'input': {
                'task_id': current.get('task_id'),
                'next_command': None,
                'next_input': None,
                'recovered_tasks': recovered,
            }
        }
        self._validate_event(event, project)
        history_records = self._history(project, new_rev - 1)
        manifest = {'tasks': {}, 'task_id': None, 'task_status': 'NOT-STARTED'}
        for rec in sorted(history_records, key=lambda item: item['revision']):
            if rec['command'] in self.TASK_COMMANDS:
                self._apply_task(manifest, rec['command'], rec['input'])
        self._apply_task(manifest, event['command'], event['input'])
        manifest['schema_version'] = '1.1'
        manifest['revision'] = new_rev
        manifest['project_id'] = project.project_id
        manifest['state_health'] = current.get('state_health', 'HEALTHY')
        manifest['last_verified_action'] = current.get('last_verified_action', 'State Reconciled')
        manifest['updated_by'] = event['actor']
        manifest['updated_at'] = datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
        for opt_field in ('active_phase', 'next_action', 'branch', 'head_sha', 'diff_fingerprint'):
            manifest[opt_field] = current.get(opt_field)
        manifest.setdefault('diff_fingerprint', None)
        self._validate_manifest(manifest, project)
        return event, manifest

    def _publish_reconcile(self, project: ManagedProject, event: dict[str, Any], manifest: dict[str, Any], new_rev: int) -> dict[str, Any]:
        """Publish a reconcile event and manifest, then verify both from disk."""
        state_root = project.state_root
        event_path = state_root / 'History' / 'Events' / f"{new_rev:020d}.json"
        _atomic_json(event_path, event)
        _atomic_json(state_root / 'State-Manifest.json', manifest)
        state = json.loads((state_root / 'State-Manifest.json').read_text(encoding='utf-8'))
        self._validate_manifest(state, project)
        history = self._history(project, state['revision'])
        if state['revision'] != new_rev or not any(item == event for item in history):
            raise StateError('Repaired state failed post-commit integrity checks')
        return state

    @staticmethod
    def _create_state_backup(project: ManagedProject, reason: str) -> tuple[Path, dict[str, str]]:
        """Create a hash-verified backup of the manifest, pending commit and event files."""
        state_root = project.state_root
        history_root = state_root / 'History'
        backup = history_root / 'Snapshots' / ('AIPM-State-Repair-' + datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ') + '-' + uuid4().hex[:8])
        backup.mkdir(parents=True, exist_ok=False)
        files = [state_root / 'State-Manifest.json']
        pending_path = history_root / 'Pending-Commit.json'
        if pending_path.is_file():
            files.append(pending_path)
        files.extend(sorted((history_root / 'Events').glob('*.json')))
        checksums: dict[str, str] = {}
        for source in files:
            relative = source.relative_to(state_root)
            destination = backup / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, destination)
            checksums[relative.as_posix()] = hashlib.sha256(destination.read_bytes()).hexdigest()
        backup_manifest = {'schema_version': '1.0', 'repair': reason, 'project_id': project.project_id, 'created_at': datetime.now(timezone.utc).isoformat(), 'files': checksums}
        (backup / 'Backup-Manifest.json').write_text(json.dumps(backup_manifest, indent=2, sort_keys=True) + '\n', encoding='utf-8')
        return backup, checksums

    @staticmethod
    def _error_detail(error: BaseException, project: ManagedProject) -> str:
        """Return a short, path-sanitized explanation of a validation failure."""
        if isinstance(error, StateError):
            text = str(error)
            for root in (project.state_root, project.root):
                text = text.replace(str(root), '<project>')
            return text[:200]
        if isinstance(error, OSError):
            return 'A state file could not be read.'
        if isinstance(error, json.JSONDecodeError):
            return 'A state file contains invalid JSON.'
        return error.__class__.__name__

    # ------------------------------------------------------------------
    # Read-only inspection (state-validate).
    # ------------------------------------------------------------------
    _TASK_ID_PATTERN = re.compile(r'Task-[A-Za-z0-9][A-Za-z0-9_-]{0,159}')
    _TEXT_LIMIT_BYTES = 1024 * 1024

    @staticmethod
    def _metadata_hint(field: str) -> str:
        return f"Operations/Tasks/<task-id>/Metadata.json -> task_record.{field} (or {field}); otherwise supply it manually"

    @classmethod
    def _task_record_findings(cls, task_id: str, task: Any) -> list[dict[str, Any]]:
        """Return field-level findings that mirror _validate_task_record without mutating the input."""
        findings: list[dict[str, Any]] = []

        def add(severity: str, code: str, field: str, message: str, by: str = 'state-normalize', hint: str | None = None) -> None:
            findings.append({'severity': severity, 'code': code, 'task_id': task_id, 'field': field, 'message': message, 'repairable_by': by, 'source_hint': hint})

        if not isinstance(task, dict):
            add('ERROR', 'TASK_FIELD_INVALID', '*', 'Task record is not an object.', by='manual')
            return findings
        override = task.get('status_override')
        if override not in (None, 'COMPLETE'):
            add('WARNING', 'TASK_STATUS_OVERRIDE_INVALID', 'status_override', f"Value {str(override)[:60]!r} is not allowed; Core normalizes it when the record is read.")
        probe = copy.deepcopy(task)
        try:
            cls._validate_task_record(probe)
        except StateError as error:
            for field in ('title', 'scope'):
                if field not in task:
                    add('ERROR', 'TASK_FIELD_MISSING', field, f'Task record has no {field}.', hint=cls._metadata_hint(field))
                elif not isinstance(task[field], str) or not task[field].strip():
                    add('ERROR', 'TASK_FIELD_INVALID', field, f'Task {field} must be a non-empty string.', hint=cls._metadata_hint(field))
            title_ok = isinstance(task.get('title'), str) and task['title'].strip() and isinstance(task.get('scope'), str) and task['scope'].strip()
            if not title_ok and (not isinstance(task.get('plan'), str) or not task['plan'].strip()):
                add('ERROR', 'TASK_FIELD_INVALID', 'plan', 'Task plan is missing or empty and cannot be generated without a title and scope.')
            if task.get('report') is not None and not isinstance(task.get('report'), str):
                add('ERROR', 'TASK_FIELD_INVALID', 'report', 'Task report must be text.')
            blockers = task.get('blockers')
            if blockers is not None and (not isinstance(blockers, list) or any(not isinstance(text, str) or not text.strip() for text in blockers)):
                add('ERROR', 'TASK_FIELD_INVALID', 'blockers', 'Task blockers must be a list of non-empty text values.')
            if 'verification' not in task:
                add('ERROR', 'TASK_FIELD_MISSING', 'verification', 'Task record has no verification key (use null when nothing was verified).', hint='Operations/Tasks/<task-id>/Metadata.json -> task_record.verification; otherwise null')
            else:
                verification = task['verification']
                valid = verification is None or isinstance(verification, str) or (isinstance(verification, dict) and isinstance(verification.get('evidence'), str) and bool(verification['evidence'].strip()))
                if not valid:
                    add('ERROR', 'TASK_VERIFICATION_INVALID', 'verification', 'Verification must be null, text, or an object with a result and non-empty evidence.')
            for field in ('last_verified_action', 'next_action'):
                if field in task and (not isinstance(task[field], str) or not task[field].strip()):
                    add('ERROR', 'TASK_CHECKPOINT_INVALID', field, f'{field} must be non-empty text when present.', by='manual')
            for field in ('completed_work', 'changed_files', 'test_results'):
                if field in task and (not isinstance(task[field], list) or len(task[field]) > 100 or any(not isinstance(value, str) or not value.strip() for value in task[field])):
                    add('ERROR', 'TASK_CHECKPOINT_INVALID', field, f'{field} must be a list of at most 100 non-empty text values.', by='manual')
            if not any(item['severity'] == 'ERROR' for item in findings):
                add('ERROR', 'TASK_FIELD_INVALID', '*', f'The task record failed validation: {error}.', by='manual')
        else:
            for field in sorted(set(probe) | set(task)):
                if field != 'status_override' and probe.get(field) != task.get(field):
                    add('WARNING', 'TASK_FIELD_NORMALIZED', field, f'{field} is stored in a legacy shape; Core normalizes it when the record is read.')
        return findings

    @classmethod
    def _read_event_files(cls, project: ManagedProject) -> tuple[dict[int, dict[str, Any]], list[tuple[str, str]]]:
        events: dict[int, dict[str, Any]] = {}
        problems: list[tuple[str, str]] = []
        directory = project.state_root / 'History' / 'Events'
        if directory.is_dir():
            for path in sorted(directory.glob('*.json')):
                try:
                    event = json.loads(path.read_text(encoding='utf-8'))
                    cls._validate_event(event, project)
                except (OSError, UnicodeError, ValueError) as error:
                    problems.append((path.name, cls._error_detail(error, project)))
                    continue
                if event['revision'] in events:
                    problems.append((path.name, 'Duplicate History Revision'))
                    continue
                events[event['revision']] = event
        return events, problems

    @classmethod
    def inspect_state(cls, project: ManagedProject) -> dict[str, Any]:
        """Read-only, field-level state report; never writes, backs up, or normalizes files."""
        findings: list[dict[str, Any]] = []
        result: dict[str, Any] = {'schema_version': '1.0', 'status': 'BLOCKED', 'project_id': project.project_id, 'manifest_revision': None, 'max_event_revision': None, 'missing_event_revisions': [], 'pending_commit_present': False, 'findings': findings, 'summary': ''}

        def add(severity: str, code: str, message: str, *, task_id: str | None = None, field: str | None = None, by: str = 'manual', hint: str | None = None) -> None:
            findings.append({'severity': severity, 'code': code, 'task_id': task_id, 'field': field, 'message': message, 'repairable_by': by, 'source_hint': hint})

        def finish() -> dict[str, Any]:
            errors = [item for item in findings if item['severity'] == 'ERROR']
            result['status'] = 'BLOCKED' if errors else 'PASS'
            if errors:
                result['summary'] = f"{len(errors)} blocking problem(s) found; first: {errors[0]['message']}"
            elif findings:
                result['summary'] = f"No blocking problem; {len(findings)} advisory finding(s)."
            else:
                result['summary'] = 'State is valid and matches event history.'
            return result

        try:
            validate_managed_project(project)
        except StateError as error:
            add('ERROR', 'PROJECT_STATE_PATH_INVALID', cls._error_detail(error, project))
            return finish()
        state_root = project.state_root
        result['pending_commit_present'] = (state_root / 'History' / 'Pending-Commit.json').is_file()
        if result['pending_commit_present']:
            add('WARNING', 'PENDING_COMMIT_PRESENT', 'An interrupted Pending-Commit.json exists; use state-diagnose and state-repair first.', by='state-repair')
        try:
            raw = json.loads((state_root / 'State-Manifest.json').read_text(encoding='utf-8'))
        except (OSError, UnicodeError, ValueError) as error:
            add('ERROR', 'MANIFEST_UNREADABLE', 'State-Manifest.json cannot be read: ' + cls._error_detail(error, project))
            return finish()
        if not isinstance(raw, dict):
            add('ERROR', 'MANIFEST_SCHEMA_INVALID', 'State-Manifest.json is not a JSON object.')
            return finish()
        if type(raw.get('revision')) is int:
            result['manifest_revision'] = raw['revision']
        shell = copy.deepcopy(raw)
        shell['tasks'] = {}
        try:
            cls._validate_manifest(shell, project)
        except StateError as error:
            add('ERROR', 'MANIFEST_SCHEMA_INVALID', f'The manifest header failed validation: {error}.')
        tasks = raw.get('tasks', {})
        if not isinstance(tasks, dict):
            add('ERROR', 'MANIFEST_SCHEMA_INVALID', 'The manifest tasks value is not an object.')
            tasks = {}
        task_errors: set[str] = set()
        for task_id, task in sorted(tasks.items()):
            if not isinstance(task_id, str) or not cls._TASK_ID_PATTERN.fullmatch(task_id):
                add('ERROR', 'TASK_ID_INVALID', f'Task identity {str(task_id)[:80]!r} is not valid.', task_id=str(task_id))
                task_errors.add(task_id)
            task_findings = cls._task_record_findings(str(task_id), task)
            if any(item['severity'] == 'ERROR' for item in task_findings):
                task_errors.add(task_id)
            findings.extend(task_findings)
        events, problems = cls._read_event_files(project)
        for name, message in problems:
            add('ERROR', 'HISTORY_EVENT_INVALID', f'{name}: {message}')
        maximum = max(events) if events else 0
        result['max_event_revision'] = maximum
        missing = sorted(set(range(1, maximum + 1)) - set(events))
        result['missing_event_revisions'] = missing
        if missing:
            add('ERROR', 'HISTORY_NON_CONTIGUOUS', f'History events are missing revision(s): {missing[:10]}.')
        if not problems and not missing:
            manifest_revision = raw.get('revision')
            if type(manifest_revision) is int and manifest_revision > maximum:
                add('WARNING', 'MANIFEST_AHEAD_OF_HISTORY', f'State-Manifest.json is at revision {manifest_revision} but History/Events ends at {maximum}; it was probably edited without Core.', by='state-normalize' if task_errors else 'state-repair')
            elif type(manifest_revision) is int and manifest_revision < maximum:
                add('WARNING', 'MANIFEST_BEHIND_HISTORY', f'State-Manifest.json is at revision {manifest_revision} but History/Events ends at {maximum}.', by='state-repair')
            expected: dict[str, Any] = {'tasks': {}, 'task_id': None, 'task_status': 'NOT-STARTED'}
            try:
                for revision in range(1, maximum + 1):
                    record = events[revision]
                    if record['command'] in cls.TASK_COMMANDS:
                        cls._apply_task(expected, record['command'], record['input'])
            except (StateError, TypeError, KeyError) as error:
                add('ERROR', 'HISTORY_REPLAY_FAILED', 'Event history cannot be replayed: ' + cls._error_detail(error, project))
            else:
                for task_id in sorted(expected['tasks']):
                    if task_id not in tasks:
                        add('ERROR', 'TASK_MISSING_FROM_MANIFEST', f'Task {task_id} exists in history but not in the manifest.', task_id=task_id)
                for task_id in sorted(tasks):
                    if task_id in task_errors or not isinstance(task_id, str):
                        continue
                    if task_id not in expected['tasks']:
                        add('WARNING', 'TASK_NOT_IN_HISTORY', 'Task is in the manifest but has no creating event.', task_id=task_id, by='state-repair')
                        continue
                    probe = copy.deepcopy(tasks[task_id])
                    try:
                        cls._validate_task_record(probe)
                    except StateError:
                        continue
                    if probe != expected['tasks'][task_id] and not cls._legacy_task_normalization_matches_history({task_id: tasks[task_id]}, {task_id: probe}, {task_id: expected['tasks'][task_id]}):
                        add('WARNING', 'TASK_DRIFTED_FROM_HISTORY', 'Task record differs from the state rebuilt from event history.', task_id=task_id, by='state-repair')
        active = raw.get('task_id')
        if isinstance(active, str) and active and active not in tasks:
            add('WARNING', 'ACTIVE_TASK_POINTER_INVALID', f'The active task {active} is not in the manifest.')
        return finish()

    # ------------------------------------------------------------------
    # Guided repair of malformed task records (state-normalize).
    # ------------------------------------------------------------------
    @classmethod
    def _read_task_metadata(cls, project: ManagedProject, task_id: str) -> tuple[dict[str, Any] | None, str | None]:
        task_dir = project.state_root / 'Operations' / 'Tasks' / task_id
        path = task_dir / 'Metadata.json'
        try:
            canonical_dir = _canonical(task_dir)
            if not _inside(canonical_dir, _canonical(project.state_root)):
                return None, 'Task folder is outside the project state root.'
            if not path.is_file() or path.is_symlink():
                return None, 'Metadata.json was not found.'
            if path.stat().st_size > cls._TEXT_LIMIT_BYTES:
                return None, 'Metadata.json is larger than 1 MiB.'
            metadata = json.loads(path.read_text(encoding='utf-8'))
        except (StateError, OSError, UnicodeError, ValueError):
            return None, 'Metadata.json could not be read safely.'
        if not isinstance(metadata, dict) or metadata.get('task_id') != task_id:
            return None, 'Metadata.json does not belong to this task.'
        owner = metadata.get('project')
        if isinstance(owner, dict) and owner.get('project_id') not in (None, project.project_id):
            return None, 'Metadata.json belongs to a different project.'
        return metadata, None

    @classmethod
    def _resolve_task_text(cls, project: ManagedProject, task_id: str, value: Any) -> str | None:
        """Return text from a task-folder file referenced by a path-like value; never follow unsafe paths."""
        if not isinstance(value, str) or not value.strip() or len(value) > 260 or '\n' in value or '\x00' in value:
            return None
        reference = value.strip().replace('\\', '/')
        if not reference.lower().endswith(('.md', '.txt')) or reference.startswith('/') or re.match(r'^[A-Za-z]:', reference) or '..' in reference.split('/'):
            return None
        task_dir = project.state_root / 'Operations' / 'Tasks' / task_id
        for base in (project.state_root, task_dir):
            candidate = base / reference
            try:
                if not candidate.is_file():
                    continue
                canonical = _canonical(candidate)
                if not _inside(canonical, _canonical(task_dir)) or canonical.stat().st_size > cls._TEXT_LIMIT_BYTES:
                    continue
                text = canonical.read_text(encoding='utf-8')
            except (StateError, OSError, UnicodeError):
                continue
            if text.strip():
                return text
        return None

    @classmethod
    def _normalize_task_record(cls, project: ManagedProject, task_id: str, record: dict[str, Any], title_override: str | None) -> tuple[dict[str, Any], list[dict[str, Any]], list[dict[str, str]]]:
        """Derive a valid record using only the record itself and the task's own Metadata.json and files."""
        candidate = copy.deepcopy(record)
        changes: list[dict[str, Any]] = []
        manual: list[dict[str, str]] = []
        metadata, metadata_note = cls._read_task_metadata(project, task_id)
        task_record = metadata.get('task_record') if isinstance(metadata, dict) and isinstance(metadata.get('task_record'), dict) else {}
        metadata_source = f'Operations/Tasks/{task_id}/Metadata.json'
        missing = object()

        def meta_text(field: str) -> str | None:
            for container in (task_record, metadata or {}):
                value = container.get(field)
                if isinstance(value, str) and value.strip():
                    return value
            return None

        def put(field: str, value: Any, source: str) -> None:
            old = candidate.get(field, missing)
            candidate[field] = value
            changes.append({'field': field, 'old': None if old is missing else old, 'old_present': old is not missing, 'new': value, 'source': source})

        def valid_text(field: str) -> bool:
            return isinstance(candidate.get(field), str) and bool(candidate[field].strip())

        if not valid_text('title'):
            if meta_text('title'):
                put('title', meta_text('title'), metadata_source)
            elif title_override and title_override.strip():
                put('title', title_override.strip(), 'command line --title')
            else:
                manual.append({'field': 'title', 'message': 'No title is recorded; add Metadata.json for this task or supply --title.' + (f' ({metadata_note})' if metadata_note else '')})
        if not valid_text('scope'):
            if meta_text('scope'):
                put('scope', meta_text('scope'), metadata_source)
            else:
                manual.append({'field': 'scope', 'message': 'No scope is recorded; add Metadata.json for this task.' + (f' ({metadata_note})' if metadata_note else '')})
        for field in ('plan', 'report'):
            text = cls._resolve_task_text(project, task_id, candidate.get(field))
            if text is not None:
                put(field, text, f'file referenced by {field}')
        if 'verification' not in candidate:
            recorded = task_record.get('verification') if isinstance(task_record.get('verification'), str) and task_record['verification'].strip() else None
            put('verification', recorded, metadata_source if recorded else 'default (nothing recorded)')
        override = candidate.get('status_override')
        if isinstance(override, str) and override.strip().upper() in {'COMPLETE', 'COMPLETED', 'COMPLETE & VERIFIED', 'COMPLETED & VERIFIED'} and override != 'COMPLETE':
            put('status_override', 'COMPLETE', 'Core status vocabulary')
        if manual:
            return candidate, changes, manual
        probe = copy.deepcopy(candidate)
        try:
            cls._validate_task_record(probe)
        except StateError as error:
            manual.append({'field': '*', 'message': f'The record still fails validation: {error}.'})
        else:
            for field in sorted(set(probe) | set(candidate)):
                if probe.get(field, missing) != candidate.get(field, missing):
                    old = candidate.get(field, missing)
                    changes.append({'field': field, 'old': None if old is missing else old, 'old_present': old is not missing, 'new': probe.get(field), 'source': 'Core normalization'})
            candidate = probe
        return candidate, changes, manual

    @classmethod
    def _plan_normalization(cls, project: ManagedProject, title_override: str | None) -> dict[str, Any]:
        validate_managed_project(project)
        state_root = project.state_root
        if (state_root / 'History' / 'Pending-Commit.json').exists():
            raise StateError('PENDING_COMMIT_PRESENT')
        raw = json.loads((state_root / 'State-Manifest.json').read_text(encoding='utf-8'))
        shell = copy.deepcopy(raw)
        if not isinstance(shell, dict) or not isinstance(shell.get('tasks', {}), dict):
            raise StateError('Invalid State Manifest')
        tasks = raw.get('tasks', {})
        shell['tasks'] = {}
        cls._validate_manifest(shell, project)
        events, problems = cls._read_event_files(project)
        if problems:
            raise StateError(problems[0][1])
        maximum = max(events) if events else 0
        if set(events) != set(range(1, maximum + 1)):
            raise StateError('Non-contiguous history revisions detected')
        expected: dict[str, Any] = {'tasks': {}, 'task_id': None, 'task_status': 'NOT-STARTED'}
        for revision in range(1, maximum + 1):
            if events[revision]['command'] in cls.TASK_COMMANDS:
                cls._apply_task(expected, events[revision]['command'], events[revision]['input'])
        for task_id in expected['tasks']:
            if task_id not in tasks:
                raise StateError(f'Historical task {task_id} is missing from manifest')
        malformed: list[str] = []
        for task_id, task in sorted(tasks.items()):
            if not isinstance(task_id, str) or not cls._TASK_ID_PATTERN.fullmatch(task_id) or not isinstance(task, dict):
                raise StateError('Invalid Task State')
            try:
                cls._validate_task_record(copy.deepcopy(task))
            except StateError:
                malformed.append(task_id)
        lacking_title = [task_id for task_id in malformed if not (isinstance(tasks[task_id].get('title'), str) and tasks[task_id]['title'].strip())]
        override = title_override if len(lacking_title) == 1 else None
        candidates: dict[str, dict[str, Any]] = {}
        changes: dict[str, list[dict[str, Any]]] = {}
        manual: dict[str, list[dict[str, str]]] = {}
        for task_id in malformed:
            candidate, task_changes, task_manual = cls._normalize_task_record(project, task_id, tasks[task_id], override)
            candidates[task_id] = candidate
            changes[task_id] = task_changes
            if task_manual:
                manual[task_id] = task_manual
        recovered: list[dict[str, Any]] = []
        for task_id in sorted(tasks):
            if task_id in malformed:
                recovered.append({'task_id': task_id, 'record': copy.deepcopy(candidates[task_id])})
                continue
            normalized = copy.deepcopy(tasks[task_id])
            cls._validate_task_record(normalized)
            if task_id not in expected['tasks'] or (normalized != expected['tasks'][task_id] and not cls._legacy_task_normalization_matches_history({task_id: tasks[task_id]}, {task_id: normalized}, {task_id: expected['tasks'][task_id]})):
                recovered.append({'task_id': task_id, 'record': normalized})
        return {'raw': raw, 'malformed': malformed, 'candidates': candidates, 'changes': changes, 'manual': manual, 'recovered': recovered, 'committed_events': maximum, 'pending_revision': maximum + 1}

    @staticmethod
    def _plan_signature(plan: dict[str, Any]) -> str:
        return hashlib.sha256(json.dumps({'k': plan['committed_events'], 'revision': plan['raw'].get('revision'), 'malformed': plan['malformed'], 'recovered': plan['recovered']}, sort_keys=True, default=str).encode('utf-8')).hexdigest()

    def normalize_task_records(self, project: ManagedProject, *, confirm: bool = False, title_override: str | None = None) -> dict[str, Any]:
        """Preview (default) or apply a backed-up reconcile event that repairs malformed task records."""
        try:
            plan = self._plan_normalization(project, title_override)
        except (OSError, UnicodeError, ValueError, KeyError, TypeError) as error:
            return {'schema_version': '1.0', 'status': 'BLOCKED', 'reason': str(error) if isinstance(error, StateError) else 'STATE_NORMALIZATION_FAILED', 'detail': self._error_detail(error, project)}
        report: dict[str, Any] = {
            'schema_version': '1.0', 'status': 'PASS', 'applied': False,
            'normalized_tasks': list(plan['malformed']),
            'recovered_tasks': [item['task_id'] for item in plan['recovered']],
            'pending_revision': plan['pending_revision'],
            'changes': {task_id: [{'field': item['field'], 'old': self._shorten(item['old']), 'new': self._shorten(item['new']), 'source': item['source']} for item in items] for task_id, items in plan['changes'].items()},
            'manual_fields_required': plan['manual'],
        }
        if plan['manual']:
            return {**report, 'status': 'BLOCKED', 'reason': 'MANUAL_FIELDS_REQUIRED'}
        if not plan['malformed']:
            return {**report, 'reason': 'NO_MALFORMED_TASKS'}
        if not confirm:
            return {**report, 'reason': 'DRY_RUN'}
        try:
            backup, _checksums = self._create_state_backup(project, 'TASK_RECORD_NORMALIZATION')
        except (OSError, UnicodeError, ValueError) as error:
            return {**report, 'status': 'BLOCKED', 'reason': 'STATE_BACKUP_FAILED', 'detail': self._error_detail(error, project)}
        try:
            confirmed = self._plan_normalization(project, title_override)
            if confirmed['manual'] or self._plan_signature(confirmed) != self._plan_signature(plan):
                raise StateError('State Changed After Diagnosis; No Repair Was Applied')
            event, manifest = self._build_reconcile(project, plan['raw'], plan['recovered'], plan['pending_revision'])
            state = self._publish_reconcile(project, event, manifest, plan['pending_revision'])
        except (OSError, UnicodeError, ValueError, KeyError, TypeError) as error:
            return {**report, 'status': 'BLOCKED', 'reason': str(error) if isinstance(error, StateError) else 'STATE_REPAIR_FAILED', 'backup': str(backup)}
        return {**report, 'applied': True, 'reason': 'NORMALIZED', 'revision': state['revision'], 'backup': str(backup)}

    @staticmethod
    def _shorten(value: Any) -> Any:
        if isinstance(value, str) and len(value) > 160:
            return value[:157] + '...'
        if isinstance(value, (list, dict)):
            text = json.dumps(value, ensure_ascii=False)
            return text if len(text) <= 160 else text[:157] + '...'
        return value

    def _commit(self, project: ManagedProject, manifest: dict[str, Any], event: dict[str, Any]) -> None:
        pending = project.state_root / "History" / "Pending-Commit.json"
        _atomic_json(pending, {"schema_version": "1.0", "manifest": manifest, "event": event})
        self._recover(project)

    def execute(self, command: CommandEnvelope) -> dict[str, Any]:
        project = self.projects.get(command.project_id)
        if project is None:
            return {"schema_version": "1.0", "status": "BLOCKED", "reason": "PROJECT_NOT_REGISTERED"}
        try:
            validate_managed_project(project)
        except StateError as error:
            reason = "AIPM_PLATFORM_PROTECTED" if str(error).startswith("AIPM_PLATFORM_PROTECTED") else "INVALID_STATE"
            return {"schema_version": "1.0", "status": "BLOCKED", "reason": reason}
        event = {"schema_version": "1.0", "request_id": command.request_id, "command": command.command, "actor": command.actor, "project_id": command.project_id, "revision": 1, "idempotency_key": command.idempotency_key, "input": command.input}
        try:
            # Reject invalid caller metadata before recovery or any publication.
            self._validate_event(event, project)
        except StateError:
            return {"schema_version": "1.0", "status": "BLOCKED", "reason": "INVALID_INPUT"}
        manifest_path = project.state_root / "State-Manifest.json"
        try:
            self._recover(project)
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            self._validate_manifest(manifest, project)
            manifest.setdefault("tasks", {})
            manifest.setdefault("diff_fingerprint", None)
            if not isinstance(manifest["tasks"], dict):
                raise StateError("Invalid Task State")
        except (OSError, ValueError, KeyError, TypeError) as error:
            return {"schema_version": "1.0", "status": "BLOCKED", "reason": "INVALID_STATE", "detail": self._error_detail(error, project)}
        try:
            history = self._history(project, manifest["revision"])
        except (OSError, ValueError, KeyError, TypeError) as error:
            return {"schema_version": "1.0", "status": "BLOCKED", "reason": "INVALID_HISTORY", "detail": self._error_detail(error, project)}
        if command.command == "state.read":
            return {"schema_version": "1.0", "status": "PASS", "state": manifest, "revision": manifest["revision"]}
        if command.command == 'task.read':
            task_id = command.input.get('task_id')
            task = manifest['tasks'].get(task_id) if isinstance(task_id, str) else None
            if task is None:
                return {'schema_version': '1.0', 'status': 'BLOCKED', 'reason': 'TASK_NOT_FOUND'}
            resumable = dict(task)
            resumable.setdefault('last_verified_action', 'Task progress has not yet been recorded.')
            resumable.setdefault('next_action', 'Unknown; reconcile the task with current project evidence.')
            resumable.setdefault('completed_work', [])
            resumable.setdefault('changed_files', [])
            resumable.setdefault('test_results', [])
            return {'schema_version': '1.0', 'status': 'PASS', 'task': resumable, 'task_status': self.task_status(task), 'revision': manifest['revision']}
        if command.command not in {"state.set-next-action", "state.record-git-observation", "state.upgrade-schema"} | self.TASK_COMMANDS:
            return {"schema_version": "1.0", "status": "BLOCKED", "reason": "COMMAND_UNSUPPORTED"}
        if command.idempotency_key:
            for record in history:
                if record["idempotency_key"] == command.idempotency_key:
                    return {"schema_version": "1.0", "status": "PASS", "revision": manifest["revision"], "replayed": True}
        if command.expected_revision != manifest["revision"]:
            return {"schema_version": "1.0", "status": "BLOCKED", "reason": "STATE_CONFLICT", "revision": manifest["revision"]}
        if command.command in self.TASK_COMMANDS:
            manifest = copy.deepcopy(manifest)
            try:
                self._apply_task(manifest, command.command, command.input)
            except (StateError, TypeError):
                return {'schema_version': '1.0', 'status': 'BLOCKED', 'reason': 'INVALID_INPUT'}
        elif command.command == "state.set-next-action":
            next_action = command.input.get("next_action")
            if not isinstance(next_action, str) or not next_action.strip():
                return {"schema_version": "1.0", "status": "BLOCKED", "reason": "INVALID_INPUT"}
            manifest["next_action"] = next_action
        elif command.command == 'state.upgrade-schema':
            if command.input or manifest.get('schema_version') != '1.0':
                return {'schema_version': '1.0', 'status': 'BLOCKED', 'reason': 'SCHEMA_UPGRADE_NOT_APPLICABLE'}
        else:
            keys = ("branch", "head_sha", "diff_fingerprint")
            if any(key not in command.input or (command.input[key] is not None and (not isinstance(command.input[key], str) or not command.input[key].strip())) for key in keys):
                return {"schema_version": "1.0", "status": "BLOCKED", "reason": "INVALID_INPUT"}
            manifest.update({key: command.input[key] for key in keys})
        manifest["revision"] += 1
        manifest["schema_version"] = "1.1"
        manifest["updated_by"] = command.actor
        manifest["updated_at"] = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        event['revision'] = manifest['revision']
        try:
            self._validate_manifest(manifest, project)
            self._validate_event(event, project)
        except StateError:
            return {"schema_version": "1.0", "status": "BLOCKED", "reason": "INVALID_INPUT"}
        try:
            self._commit(project, manifest, event)
        except (OSError, ValueError, KeyError, TypeError):
            return {"schema_version": "1.0", "status": "BLOCKED", "reason": "STATE_COMMIT_FAILED"}
        return {"schema_version": "1.0", "status": "PASS", "revision": manifest["revision"], "replayed": False}
