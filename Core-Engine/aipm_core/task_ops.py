"""Core Engine task commands with repairable human-readable projections."""
from __future__ import annotations

from datetime import date
from pathlib import Path
import re
from typing import Any
from uuid import uuid4

from .domain import CommandEnvelope, CoreEngine
from .storage import ManagedProject, StateError, _canonical, validate_managed_project


class TaskOperations:
    def __init__(self, engine: CoreEngine, project: ManagedProject):
        validate_managed_project(project)
        self.engine = engine
        self.project = project
        self.root = project.state_root

    def _request(self, command: str, payload: dict[str, Any], *, revision: int = 0, mutation: bool = False) -> dict[str, Any]:
        request_id = uuid4().hex
        result = self.engine.execute(CommandEnvelope(request_id, command, 'aipm-task-operations', self.project.project_id, revision, request_id if mutation else None, payload))
        if result['status'] != 'PASS':
            raise StateError(result.get('reason', 'Task Command Failed'))
        return result

    def _task_id(self, task: Path) -> str:
        validate_managed_project(self.project)
        tasks_root = _canonical(self.root / 'Tasks')
        canonical = _canonical(task)
        if canonical.parent != tasks_root:
            raise StateError('Task Must Be Inside Project Tasks')
        return canonical.name

    def _mutate(self, command: str, task: Path, **payload: Any) -> None:
        task_id = self._task_id(task)
        state = self._request('state.read', {})
        self._request(command, {'task_id': task_id, **payload}, revision=state['revision'], mutation=True)
        self.sync_artifacts(task)

    def create(self, title: str, scope: str) -> Path:
        if not isinstance(title, str) or not title.strip():
            raise StateError('Task Title Is Required')
        slug = re.sub(r'[^A-Za-z0-9_-]+', '-', title).strip('-')[:100] or 'Task'
        task = self.root / 'Tasks' / f'Task-{date.today():%Y-%m-%d}-{slug}-{uuid4().hex[:12]}'
        self._mutate('task.create', task, title=title, scope=scope)
        return task

    def plan(self, task: Path, text: str) -> None:
        self._mutate('task.plan', task, text=text)

    def add_blocker(self, task: Path, text: str) -> None:
        self._mutate('task.blocker.add', task, text=text)

    def clear_blockers(self, task: Path) -> None:
        self._mutate('task.blocker.clear', task)

    def verify(self, task: Path, result: str, evidence: str) -> None:
        self._mutate('task.verify', task, result=result, evidence=evidence)

    def report(self, task: Path, text: str) -> None:
        self._mutate('task.report', task, text=text)

    def status(self, task: Path) -> dict[str, Any]:
        result = self._request('task.read', {'task_id': self._task_id(task)})
        return {'status': result['task_status']}

    def sync_artifacts(self, task: Path) -> None:
        record = self._request('task.read', {'task_id': self._task_id(task)})['task']
        task.mkdir(parents=True, exist_ok=True)
        artifacts = {'Task-Plan.md': record['plan'], 'Blockers.md': '\n'.join(record['blockers']), 'Final-Report.md': record['report']}
        verification = record['verification']
        artifacts['Test-Status.md'] = f"{verification['result']}\n{verification['evidence']}\n" if verification else 'UNVERIFIED\n'
        for name, content in artifacts.items():
            path = task / name
            _canonical(path)
            path.write_text(content, encoding='utf-8')
