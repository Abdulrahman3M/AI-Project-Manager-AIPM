"""Versioned commands, results, and immutable event records for AIPM."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import json
import copy
from pathlib import Path
import re
from typing import Any

from .storage import ManagedProject, StateError, _atomic_json, validate_managed_project


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

    TASK_COMMANDS = {'task.create', 'task.plan', 'task.blocker.add', 'task.blocker.clear', 'task.verify', 'task.report', 'task.checkpoint', 'task.close', 'task.reopen', 'task.restore', 'task.unregister', 'task.edit', 'task.rename'}

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
        task_id = payload.get('task_id')
        if not isinstance(task_id, str) or not re.fullmatch(r'Task-[A-Za-z0-9][A-Za-z0-9_-]{0,159}', task_id):
            raise StateError('Invalid Task Identity')
        tasks = manifest.setdefault('tasks', {})
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
        required = ("task_status", "state_health", "last_verified_action", "updated_at", "updated_by")
        if any(not isinstance(manifest.get(key), str) or not manifest[key].strip() for key in required):
            raise StateError("Invalid State Manifest Fields")
        nullable = ("task_id", "active_phase", "next_action", "branch", "head_sha")
        if any(key not in manifest or (manifest[key] is not None and not isinstance(manifest[key], str)) for key in nullable):
            raise StateError("Invalid State Manifest Fields")
        if manifest["schema_version"] == "1.1" and ("tasks" not in manifest or "diff_fingerprint" not in manifest):
            raise StateError("Missing State Manifest Fields")
        if not isinstance(manifest.get("tasks", {}), dict) or (manifest.get("diff_fingerprint") is not None and not isinstance(manifest["diff_fingerprint"], str)):
            raise StateError("Invalid State Manifest Fields")
        for task_id, task in manifest.get('tasks', {}).items():
            if not isinstance(task_id, str) or not re.fullmatch(r'Task-[A-Za-z0-9][A-Za-z0-9_-]{0,159}', task_id) or not isinstance(task, dict):
                raise StateError('Invalid Task State')
            CoreEngine._validate_task_record(task)

    @staticmethod
    def _validate_task_record(task: dict[str, Any]) -> None:
        if any(not isinstance(task.get(key), str) or not task[key].strip() for key in ('title', 'scope', 'plan')) or not isinstance(task.get('report'), str) or not isinstance(task.get('blockers'), list) or any(not isinstance(text, str) or not text.strip() for text in task['blockers']):
            raise StateError('Invalid Task State')
        verification = task.get('verification')
        if 'verification' not in task or (verification is not None and (not isinstance(verification, dict) or verification.get('result') not in ('PASS', 'FAIL', 'UNVERIFIED') or not isinstance(verification.get('evidence'), str) or not verification['evidence'].strip())):
            raise StateError('Invalid Task Evidence')
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
        current = json.loads(manifest_path.read_text(encoding="utf-8"))
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
            if current['revision'] == revision - 1 and current.get('tasks', {}) != expected['tasks']:
                raise StateError('Task History Conflicts With State')
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
        except (OSError, ValueError, KeyError, TypeError):
            return {"schema_version": "1.0", "status": "BLOCKED", "reason": "INVALID_STATE"}
        try:
            history = self._history(project, manifest["revision"])
        except (OSError, ValueError, KeyError, TypeError):
            return {"schema_version": "1.0", "status": "BLOCKED", "reason": "INVALID_HISTORY"}
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
        if command.command not in {"state.set-next-action", "state.record-git-observation"} | self.TASK_COMMANDS:
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
