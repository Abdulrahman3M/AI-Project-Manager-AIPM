"""Project-scoped task context and attachment operations; never edits project source files."""
from __future__ import annotations

from contextlib import contextmanager
from datetime import date
import hashlib
import os
from pathlib import Path
import re
import tempfile
import zipfile
from typing import Any, Iterator
from uuid import uuid4

from .domain import CommandEnvelope, CoreEngine
from .storage import ManagedProject, StateError, _canonical, _inside, validate_managed_project


TASK_ARTIFACT_CATEGORIES = frozenset({"Instructions", "Handoff", "Reports", "Scripts", "Examples", "References"})
MAX_TASK_ARTIFACT_BYTES = 16 * 1024 * 1024
MAX_TASK_ARTIFACT_PATH_CHARS = 240
CORE_PROJECTIONS = frozenset({"Task-Plan.md", "Blockers.md", "Final-Report.md", "Test-Status.md", "Task-State.md"})
_WINDOWS_RESERVED_NAMES = {"CON", "PRN", "AUX", "NUL", *(f"COM{i}" for i in range(1, 10)), *(f"LPT{i}" for i in range(1, 10))}


class TaskOperations:
    """Task metadata is Core-authoritative; task documents live only under owned state."""

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
        if not re.fullmatch(r'Task-[A-Za-z0-9][A-Za-z0-9_-]{0,159}', canonical.name):
            raise StateError('Invalid Task Identity')
        return canonical.name

    def _task_path(self, task: Path) -> Path:
        task_id = self._task_id(task)
        self._request('task.read', {'task_id': task_id})
        return self.root / 'Tasks' / task_id

    def _mutate(self, command: str, task: Path, **payload: Any) -> None:
        task_id = self._task_id(task)
        state = self._request('state.read', {})
        self._request(command, {'task_id': task_id, **payload}, revision=state['revision'], mutation=True)
        self.sync_artifacts(task)

    def create(self, title: str, scope: str) -> Path:
        if not isinstance(title, str) or not title.strip() or not isinstance(scope, str) or not scope.strip():
            raise StateError('Task Title And Scope Are Required')
        slug = re.sub(r'[^A-Za-z0-9_-]+', '-', title).strip('-')[:100] or 'Task'
        task = self.root / 'Tasks' / f'Task-{date.today():%Y-%m-%d}-{slug}-{uuid4().hex[:12]}'
        self._mutate('task.create', task, title=title, scope=scope)
        return task

    def plan(self, task: Path, text: str) -> None:
        self._mutate('task.plan', task, text=text)

    def checkpoint(
        self,
        task: Path,
        *,
        last_verified_action: str,
        next_action: str,
        completed_work: list[str] | None = None,
        changed_files: list[str] | None = None,
        test_results: list[str] | None = None,
    ) -> None:
        self._mutate(
            'task.checkpoint', task,
            last_verified_action=last_verified_action,
            next_action=next_action,
            completed_work=completed_work or [],
            changed_files=changed_files or [],
            test_results=test_results or [],
        )

    def add_blocker(self, task: Path, text: str) -> None:
        self._mutate('task.blocker.add', task, text=text)

    def clear_blockers(self, task: Path) -> None:
        self._mutate('task.blocker.clear', task)

    def verify(self, task: Path, result: str, evidence: str) -> None:
        self._mutate('task.verify', task, result=result, evidence=evidence)

    def report(self, task: Path, text: str) -> None:
        self._mutate('task.report', task, text=text)

    def close(self, task: Path, completion_note: str) -> None:
        """Mark a task complete with a user-authored closeout note."""
        self._mutate('task.close', task, text=completion_note)

    def reopen(self, task: Path, next_work: str) -> None:
        """Return a closed task to active work without losing its history."""
        self._mutate('task.reopen', task, text=next_work)

    def import_work_folder(self, title: str, scope: str, work_folder: Path) -> Path:
        """Register an existing project folder and preserve a small, readable inventory."""
        folder = _canonical(work_folder)
        project_root = _canonical(self.project.root)
        if not folder.is_dir() or not _inside(folder, project_root) or folder == self.root:
            raise StateError('Existing Work Folder Must Be Inside The Managed Project')
        task = self.create(title, f'Existing Work Folder: {folder}\n{scope}')
        entries = []
        for entry in sorted(folder.rglob('*')):
            if entry.is_file():
                relative = entry.relative_to(folder).as_posix()
                if relative.startswith('.git/') or relative.startswith('Shared-Project-State-Manager/'):
                    continue
                entries.append(f'- `{relative}` ({entry.stat().st_size} bytes)')
                if len(entries) >= 500:
                    entries.append('- Inventory truncated after 500 files.')
                    break
        body = '# Existing Work Folder\n\n'
        body += f'Original folder: `{folder}`\n\n'
        body += 'Files remain at their original paths. This inventory records the folder at registration time.\n\n'
        body += '## Files\n\n' + ('\n'.join(entries) if entries else '_No files found._') + '\n'
        self.write_artifact(task, 'References/Existing-Work-Folder.md', body.encode('utf-8'))
        return task

    def archive(self, task: Path) -> dict[str, Path]:
        """Create an integrity-checked portable ZIP while keeping the live task record."""
        task_root = self._task_path(task)
        if self.read_task(task)['task_status'] != 'COMPLETE':
            raise StateError('Only Completed Tasks Can Be Archived')
        archive_root = self.root / 'Archive'
        archive_root.mkdir(parents=True, exist_ok=True)
        archive_path = archive_root / f'{task_root.name}.zip'
        if archive_path.exists():
            raise StateError('Task Archive Already Exists')
        with zipfile.ZipFile(archive_path, 'x', compression=zipfile.ZIP_DEFLATED, compresslevel=9) as package:
            for entry in sorted(task_root.rglob('*')):
                if entry.is_file():
                    package.write(entry, entry.relative_to(task_root).as_posix())
        digest = hashlib.sha256(archive_path.read_bytes()).hexdigest()
        checksum_path = archive_path.with_suffix('.zip.sha256')
        checksum_path.write_text(f'{digest}  {archive_path.name}\n', encoding='ascii', newline='\n')
        return {'archive_path': archive_path, 'checksum_path': checksum_path}

    def read_task(self, task: Path) -> dict[str, Any]:
        task_id = self._task_id(task)
        result = self._request('task.read', {'task_id': task_id})
        return {**result['task'], 'task_id': task_id, 'task_status': result['task_status'], 'revision': result['revision']}

    def status(self, task: Path) -> dict[str, Any]:
        record = self.read_task(task)
        return {'status': record['task_status']}

    def _artifact_target(self, task: Path, relative_path: str) -> tuple[str, Path, Path]:
        task_root = self._task_path(task)
        if not isinstance(relative_path, str) or not relative_path or len(relative_path) > MAX_TASK_ARTIFACT_PATH_CHARS:
            raise StateError('Invalid Task Artifact Path')
        if '\\' in relative_path or '\x00' in relative_path or relative_path.startswith('/'):
            raise StateError('Task Artifact Path Must Be Relative POSIX Path')
        parts = relative_path.split('/')
        if len(parts) < 2 or parts[0] not in TASK_ARTIFACT_CATEGORIES:
            raise StateError('Task Artifact Must Use A Declared Category')
        for part in parts:
            stem = part.split('.', 1)[0].upper()
            if (not part or part in {'.', '..'} or part.endswith(('.', ' ')) or stem in _WINDOWS_RESERVED_NAMES
                    or any(char in part for char in '<>:"|?*') or part.startswith('.aipm-')):
                raise StateError('Invalid Task Artifact Path')
        if parts[-1] in CORE_PROJECTIONS:
            raise StateError('Core Task Projection Is Protected')
        target = task_root.joinpath(*parts)
        canonical_root = _canonical(task_root)
        canonical_target = _canonical(target)
        if not _inside(canonical_target, canonical_root) or canonical_target == canonical_root:
            raise StateError('Task Artifact Path Escapes Its Task')
        return '/'.join(parts), task_root, target

    @contextmanager
    def _artifact_lock(self, task_id: str) -> Iterator[None]:
        lock_name = hashlib.sha256(task_id.encode('utf-8')).hexdigest() + '.lock'
        lock_path = _canonical(self.root / 'Locks' / ('task-artifacts-' + lock_name))
        lock_path.parent.mkdir(parents=True, exist_ok=True)
        with lock_path.open('a+b') as stream:
            if stream.seek(0, os.SEEK_END) == 0:
                stream.write(b'\0')
                stream.flush()
            stream.seek(0)
            if os.name == 'nt':
                import msvcrt
                msvcrt.locking(stream.fileno(), msvcrt.LK_LOCK, 1)
            else:
                import fcntl
                fcntl.flock(stream.fileno(), fcntl.LOCK_EX)
            try:
                yield
            finally:
                stream.seek(0)
                if os.name == 'nt':
                    msvcrt.locking(stream.fileno(), msvcrt.LK_UNLCK, 1)
                else:
                    fcntl.flock(stream.fileno(), fcntl.LOCK_UN)

    @staticmethod
    def _atomic_replace(path: Path, content: str) -> None:
        """Replace AIPM-owned projections without writing through a possible hard link."""
        temporary: Path | None = None
        try:
            with tempfile.NamedTemporaryFile('w', encoding='utf-8', newline='\n', dir=path.parent, prefix='.aipm-projection-', suffix='.tmp', delete=False) as stream:
                temporary = Path(stream.name)
                stream.write(content)
                stream.flush()
                os.fsync(stream.fileno())
            os.replace(temporary, path)
            temporary = None
        finally:
            if temporary is not None:
                temporary.unlink(missing_ok=True)

    @staticmethod
    def _artifact_metadata(path: str, content: bytes, *, replayed: bool = False) -> dict[str, Any]:
        return {'path': path, 'size_bytes': len(content), 'sha256': hashlib.sha256(content).hexdigest(), 'replayed': replayed}

    def write_artifact(self, task: Path, relative_path: str, content: bytes, *, expected_sha256: str | None = None) -> dict[str, Any]:
        normalized, task_root, target = self._artifact_target(task, relative_path)
        task_id = task_root.name
        if not isinstance(content, bytes) or len(content) > MAX_TASK_ARTIFACT_BYTES:
            raise StateError('Task Artifact Must Be Bytes Within The 16 MiB Limit')
        if expected_sha256 is not None and not re.fullmatch(r'[0-9a-f]{64}', expected_sha256):
            raise StateError('Invalid Expected Artifact SHA-256')
        target.parent.mkdir(parents=True, exist_ok=True)
        _canonical(target.parent)
        temporary: Path | None = None
        with self._artifact_lock(task_id):
            current: bytes | None = None
            if target.exists():
                if not target.is_file():
                    raise StateError('Task Artifact Must Be A Regular File')
                _canonical(target)
                if target.stat().st_size > MAX_TASK_ARTIFACT_BYTES:
                    raise StateError('Existing Task Artifact Exceeds Size Limit')
                current = target.read_bytes()
                if current == content:
                    return self._artifact_metadata(normalized, content, replayed=True)
                if expected_sha256 is None:
                    raise StateError('Artifact Exists; Matching SHA-256 Is Required To Update')
                if hashlib.sha256(current).hexdigest() != expected_sha256:
                    raise StateError('Artifact Update Conflict')
            elif expected_sha256 is not None:
                raise StateError('Artifact Update Target Does Not Exist')

            try:
                with tempfile.NamedTemporaryFile('wb', dir=target.parent, prefix='.aipm-artifact-', suffix='.tmp', delete=False) as stream:
                    temporary = Path(stream.name)
                    stream.write(content)
                    stream.flush()
                    os.fsync(stream.fileno())
                if current is not None:
                    temporary.replace(target)
                    temporary = None
                elif os.name == 'nt':
                    os.rename(temporary, target)
                    temporary = None
                else:
                    os.link(temporary, target)
                    temporary.unlink()
                    temporary = None
            except FileExistsError as error:
                raise StateError('Artifact Create Conflict') from error
            except OSError as error:
                raise StateError('Task Artifact Write Failed') from error
            finally:
                if temporary is not None:
                    temporary.unlink(missing_ok=True)
        return self._artifact_metadata(normalized, content)

    def read_artifact(self, task: Path, relative_path: str) -> bytes:
        _, _, target = self._artifact_target(task, relative_path)
        if not target.is_file():
            raise StateError('Task Artifact Not Found')
        _canonical(target)
        if target.stat().st_size > MAX_TASK_ARTIFACT_BYTES:
            raise StateError('Task Artifact Exceeds Size Limit')
        return target.read_bytes()

    def list_artifacts(self, task: Path) -> list[dict[str, Any]]:
        task_root = self._task_path(task)
        artifacts: list[dict[str, Any]] = []
        for category in sorted(TASK_ARTIFACT_CATEGORIES):
            category_root = task_root / category
            if not category_root.exists():
                continue
            _canonical(category_root)
            for path in category_root.rglob('*'):
                _canonical(path)
                if path.is_dir():
                    continue
                if not path.is_file() or path.stat().st_size > MAX_TASK_ARTIFACT_BYTES:
                    raise StateError('Invalid Or Oversized Task Artifact')
                relative = path.relative_to(task_root).as_posix()
                data = path.read_bytes()
                artifacts.append(self._artifact_metadata(relative, data))
        return sorted(artifacts, key=lambda item: item['path'].casefold())

    def sync_artifacts(self, task: Path) -> None:
        record = self.read_task(task)
        task_root = self.root / 'Tasks' / record['task_id']
        task_root.mkdir(parents=True, exist_ok=True)
        folder_guidance = {
            'Instructions': 'Task-specific instructions only. Keep project source files at their original project paths.',
            'Handoff': 'Verified progress and exact next actions for another agent or session.',
            'Reports': 'Progress and final reports with evidence and remaining work.',
            'Scripts': 'Task-specific helper scripts, not copies of the project implementation.',
            'Examples': 'Small examples that explain or reproduce task behavior.',
            'References': 'Supporting documents, images, and links; refer to project source paths instead of copying them.',
        }
        for folder, description in folder_guidance.items():
            directory = task_root / folder
            directory.mkdir(parents=True, exist_ok=True)
            index = directory / 'README.md'
            if not index.exists():
                self._atomic_replace(index, f'# {folder}\n\n{description}\n')

        artifacts = {
            'Task-Plan.md': record['plan'],
            'Blockers.md': '\n'.join(record['blockers']),
            'Final-Report.md': record['report'],
            'Task-State.md': self._render_task_state(record),
            'Test-Status.md': self._render_test_status(record),
            'Handoff/Next-Agent-Handoff.md': self._render_handoff(record),
        }
        for name, content in artifacts.items():
            path = task_root / name
            _canonical(path)
            path.parent.mkdir(parents=True, exist_ok=True)
            self._atomic_replace(path, content)

    @staticmethod
    def _render_task_state(record: dict[str, Any]) -> str:
        lines = [
            f"# {record['title']}", '',
            f"- Task ID: `{record['task_id']}`",
            f"- Status: `{record['task_status']}`",
            f"- Last Verified Action: {record['last_verified_action']}",
            f"- Next Action: {record['next_action']}", '',
            '## Scope', '', record['scope'], '',
            '## Completed Work', '',
        ]
        lines.extend(f'- {item}' for item in record['completed_work'])
        if not record['completed_work']:
            lines.append('- None recorded.')
        lines.extend(['', '## Project Files Changed By The Agent', '', 'These are paths in the original project, not copies inside the task folder.', ''])
        lines.extend(f'- `{path}`' for path in record['changed_files'])
        if not record['changed_files']:
            lines.append('- None recorded.')
        return '\n'.join(lines) + '\n'

    @staticmethod
    def _render_test_status(record: dict[str, Any]) -> str:
        verification = record['verification']
        result = verification['result'] if verification else 'UNVERIFIED'
        evidence = verification['evidence'] if verification else 'No verification result has been recorded.'
        lines = ['# Test And Verification Status', '', f'- Verification: `{result}`', f'- Evidence: {evidence}', '', '## Recorded Test Results', '']
        lines.extend(f'- {item}' for item in record['test_results'])
        if not record['test_results']:
            lines.append('- No test runs recorded.')
        lines.extend(['', 'AIPM records agent-provided results; it does not run the target project tests.'])
        return '\n'.join(lines) + '\n'

    @staticmethod
    def _render_handoff(record: dict[str, Any]) -> str:
        lines = [
            f"# Handoff: {record['title']}", '',
            f"- Task ID: `{record['task_id']}`",
            f"- Status: `{record['task_status']}`",
            f"- Last Verified Action: {record['last_verified_action']}", '',
            '## Read First', '',
            '- The registered project instructions and the files in this task folder.',
            '- The project files at their original paths; do not look for duplicate source copies here.', '',
            '## Completed Work', '',
        ]
        lines.extend(f'- {item}' for item in record['completed_work'])
        if not record['completed_work']:
            lines.append('- None recorded.')
        lines.extend(['', '## Project Files Changed By The Agent', ''])
        lines.extend(f'- `{path}`' for path in record['changed_files'])
        if not record['changed_files']:
            lines.append('- None recorded.')
        lines.extend(['', '## Test Results', ''])
        lines.extend(f'- {item}' for item in record['test_results'])
        if not record['test_results']:
            lines.append('- None recorded; do not infer that tests passed.')
        lines.extend(['', '## Exact Next Action', '', record['next_action'], '', 'Reconcile this handoff with the current project, Git state, and actual test output before continuing.'])
        return '\n'.join(lines) + '\n'
