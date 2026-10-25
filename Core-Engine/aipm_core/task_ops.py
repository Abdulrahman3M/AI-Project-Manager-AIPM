"""Project-scoped task context and attachment operations; never edits project source files."""
from __future__ import annotations

import copy
from contextlib import contextmanager
from datetime import date, datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import tempfile
import zipfile
from typing import Any, Iterator
from uuid import uuid4

from .domain import CommandEnvelope, CoreEngine
from .storage import ManagedProject, StateError, _canonical, _inside, validate_managed_project


TASK_ARTIFACT_CATEGORIES = frozenset({"Instructions", "Handoff", "Reports", "Scripts", "Examples", "References"})
MAX_TASK_ARTIFACT_BYTES = 16 * 1024 * 1024
MAX_TASK_ARTIFACT_PATH_CHARS = 240
CORE_PROJECTIONS = frozenset({"Task-Plan.md", "Blockers.md", "Final-Report.md", "Test-Status.md", "Task-State.md", "Metadata.json", "Metadat.json"})
TASK_RECORD_FIELDS = ('title', 'scope', 'plan', 'blockers', 'verification', 'report', 'status_override', 'last_verified_action', 'next_action', 'completed_work', 'changed_files', 'test_results')
MAX_IMPORT_ARCHIVE_ENTRIES = 20000
MAX_IMPORT_ARCHIVE_BYTES = 1024 * 1024 * 1024
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

    def edit(self, task: Path, *, title: str | None = None, scope: str | None = None) -> None:
        """Update task title and/or scope description, resyncing task artifacts."""
        if title is None and scope is None:
            raise StateError('Task Title Or Scope Is Required')
        payload = {}
        if title is not None:
            if not isinstance(title, str) or not title.strip():
                raise StateError('Task Title Cannot Be Empty')
            payload['title'] = title.strip()
        if scope is not None:
            if not isinstance(scope, str) or not scope.strip():
                raise StateError('Task Scope Cannot Be Empty')
            payload['scope'] = scope.strip()
        self._mutate('task.edit', task, **payload)

    def rename_task(self, task: Path, new_task_id: str) -> Path:
        """Rename a task folder and its identity in Core manifest, preserving all artifacts and archives."""
        old_id = self._task_id(task)
        new_id = new_task_id.strip()
        if not re.fullmatch(r'Task-[A-Za-z0-9][A-Za-z0-9_-]{0,159}', new_id):
            raise StateError('Invalid Task Identity (Must start with Task- and contain only letters, numbers, hyphens, and underscores)')
        if old_id == new_id:
            return self.root / 'Tasks' / new_id
        new_task_root = self.root / 'Tasks' / new_id
        if new_task_root.exists():
            raise StateError('Target Task Folder Already Exists')
        old_archive = self.root / 'Archive' / f'{old_id}.zip'
        new_archive = self.root / 'Archive' / f'{new_id}.zip'
        if new_archive.exists():
            raise StateError('Target Task Archive Already Exists')
        state = self._request('state.read', {})
        self._request('task.rename', {'task_id': old_id, 'new_task_id': new_id}, revision=state['revision'], mutation=True)
        old_task_root = self.root / 'Tasks' / old_id
        if old_task_root.exists():
            old_task_root.rename(new_task_root)
        old_checksum = old_archive.with_suffix('.zip.sha256')
        if old_archive.is_file():
            new_checksum = new_archive.with_suffix('.zip.sha256')
            old_archive.rename(new_archive)
            if old_checksum.is_file():
                old_checksum.rename(new_checksum)
        if new_task_root.exists():
            self.sync_artifacts(new_task_root)
        return new_task_root

    def clone_task(self, task: Path, new_title: str | None = None) -> Path:
        """Create a new task initialized with the scope and plan of an existing task."""
        record = self.read_task(task)
        title = new_title.strip() if new_title and new_title.strip() else f"Copy of {record['title']}"
        scope = record['scope']
        new_task = self.create(title, scope)
        if record.get('plan'):
            self.plan(new_task, record['plan'])
        return new_task

    def delete_task(self, task: Path, *, delete_archive: bool = False) -> dict[str, Any]:
        """Permanently delete a live task folder and unregister it from the AIPM registry, even if incomplete."""
        task_id = self._task_id(task)
        state = self._request('state.read', {})
        self._request('task.unregister', {'task_id': task_id}, revision=state['revision'], mutation=True)
        task_root = self.root / 'Tasks' / task_id
        if task_root.exists():
            shutil.rmtree(task_root)
        if delete_archive:
            archive_path = self.root / 'Archive' / f'{task_id}.zip'
            checksum_path = archive_path.with_suffix('.zip.sha256')
            archive_path.unlink(missing_ok=True)
            checksum_path.unlink(missing_ok=True)
        return {'task_id': task_id, 'task_deleted': True, 'status': 'PASS'}

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
        """Return a closed task to active work without losing its history, restoring live folder if archived."""
        task_id = self._task_id(task)
        task_root = self.root / 'Tasks' / task_id
        archive_path = self.root / 'Archive' / f'{task_id}.zip'
        if not task_root.exists() and archive_path.is_file():
            sidecar = archive_path.with_suffix('.zip.sha256')
            digest = hashlib.sha256(archive_path.read_bytes()).hexdigest()
            if sidecar.is_file() and not sidecar.read_text(encoding='ascii', errors='ignore').strip().startswith(digest):
                raise StateError('Task Archive Checksum Mismatch')
            with zipfile.ZipFile(archive_path, 'r') as package:
                bad = package.testzip()
                if bad is not None:
                    raise StateError(f'Task Archive Corrupted: {bad}')
                infos = package.infolist()
                if len(infos) > MAX_IMPORT_ARCHIVE_ENTRIES or sum(info.file_size for info in infos) > MAX_IMPORT_ARCHIVE_BYTES:
                    raise StateError('Task Archive Exceeds Import Limits')
                for info in infos:
                    name = info.filename
                    parts = name.split('/')
                    if info.is_dir():
                        continue
                    if (not name or name.startswith('/') or '\\' in name or '\x00' in name or ':' in name
                            or any(part in {'', '.', '..'} for part in parts)):
                        raise StateError('Task Archive Contains An Unsafe Path')
                staging: Path | None = Path(tempfile.mkdtemp(prefix='.aipm-reopen-', dir=self.root))
                try:
                    for info in infos:
                        if info.is_dir() or info.filename.startswith('.aipm-') or info.filename.endswith('.tmp'):
                            continue
                        destination = staging.joinpath(*info.filename.split('/'))
                        if not _inside(_canonical(destination), _canonical(staging)):
                            raise StateError('Task Archive Contains An Unsafe Path')
                        destination.parent.mkdir(parents=True, exist_ok=True)
                        destination.write_bytes(package.read(info.filename))
                    (self.root / 'Tasks').mkdir(parents=True, exist_ok=True)
                    os.replace(staging, task_root)
                    staging = None
                finally:
                    if staging is not None:
                        shutil.rmtree(staging, ignore_errors=True)
        self._mutate('task.reopen', task, text=next_work)

    @staticmethod
    def _infer_task_record_from_folder(folder: Path, title: str, scope: str) -> dict[str, Any]:
        """Infer a Core task record from an existing task folder without overwriting its files."""
        for name in ('Metadata.json', 'Metadat.json'):
            candidate = folder / name
            if candidate.is_file():
                try:
                    meta = json.loads(candidate.read_text(encoding='utf-8'))
                    if isinstance(meta, dict):
                        record = TaskOperations._record_from_metadata(meta)
                        if title.strip():
                            record['title'] = title.strip()
                        if scope.strip():
                            record['scope'] = scope.strip()
                        return record
                except Exception:
                    pass

        inferred_title = title.strip()
        inferred_scope = scope.strip()
        inferred_plan = ''
        inferred_report = ''
        inferred_blockers: list[str] = []

        state_file = folder / 'Task-State.md'
        if state_file.is_file():
            try:
                state_text = state_file.read_text(encoding='utf-8', errors='replace')
                if not inferred_title:
                    first_line = next((line.strip() for line in state_text.splitlines() if line.strip()), '')
                    if first_line.startswith('# '):
                        inferred_title = first_line[2:].strip()
                if not inferred_scope and '## Scope' in state_text:
                    after_scope = state_text.split('## Scope', 1)[1]
                    scope_section = re.split(r'\n##\s+', after_scope, maxsplit=1)[0].strip()
                    if scope_section:
                        inferred_scope = scope_section
            except OSError:
                pass

        plan_file = folder / 'Task-Plan.md'
        if plan_file.is_file():
            try:
                inferred_plan = plan_file.read_text(encoding='utf-8', errors='replace')
                if not inferred_title:
                    first_line = next((line.strip() for line in inferred_plan.splitlines() if line.strip()), '')
                    if first_line.startswith('# '):
                        inferred_title = first_line[2:].strip()
            except OSError:
                pass

        report_file = folder / 'Final-Report.md'
        if report_file.is_file():
            try:
                inferred_report = report_file.read_text(encoding='utf-8', errors='replace')
            except OSError:
                pass

        blockers_file = folder / 'Blockers.md'
        if blockers_file.is_file():
            try:
                inferred_blockers = [line.strip() for line in blockers_file.read_text(encoding='utf-8', errors='replace').splitlines() if line.strip()]
            except OSError:
                pass

        if not inferred_title:
            if folder.name.startswith('Task-'):
                stem = re.sub(r'^Task-(?:\d{4}-\d{2}-\d{2}-)?', '', folder.name)
                stem = re.sub(r'-[0-9a-fA-F]{12}$', '', stem)
                inferred_title = stem.replace('-', ' ').replace('_', ' ').strip() or folder.name
            else:
                inferred_title = folder.name

        if not inferred_scope:
            inferred_scope = f'Existing Work Folder: {folder}\nFiles Remain In Their Original Location.'

        if not inferred_plan.strip():
            inferred_plan = f'# {inferred_title}\n\n{inferred_scope}\n'

        record: dict[str, Any] = {
            'title': inferred_title,
            'scope': inferred_scope,
            'plan': inferred_plan,
            'blockers': inferred_blockers,
            'verification': None,
            'report': inferred_report,
            'status_override': None,
        }
        CoreEngine._validate_task_record(record)
        return record

    def import_work_folder(self, title: str = '', scope: str = '', work_folder: Path | None = None) -> Path:
        """Register an existing project folder or an existing task folder in place without creating duplicates."""
        if work_folder is None:
            raise StateError('Existing Work Folder Is Required')
        folder = _canonical(work_folder)
        project_root = _canonical(self.project.root)
        state_root = _canonical(self.root)
        tasks_root = _canonical(state_root / 'Tasks')
        if not folder.is_dir() or not _inside(folder, project_root) or folder in {state_root, tasks_root}:
            raise StateError('Existing Work Folder Must Be Inside The Managed Project')

        # Case 1: The folder is already a direct child of Shared-Project-State-Manager/Tasks/
        if folder.parent == tasks_root:
            if not re.fullmatch(r'Task-[A-Za-z0-9][A-Za-z0-9_-]{0,159}', folder.name):
                slug = re.sub(r'[^A-Za-z0-9_-]+', '-', folder.name).strip('-')[:100] or 'Task'
                target_name = f'Task-{slug}'
                target_folder = tasks_root / target_name
                if target_folder.exists():
                    target_folder = tasks_root / f'Task-{slug}-{uuid4().hex[:8]}'
                os.replace(folder, target_folder)
                folder = _canonical(target_folder)
            task_id = folder.name
            state = self._request('state.read', {})
            if task_id in state['state'].get('tasks', {}):
                self.sync_artifacts(folder)
                return folder
            record = self._infer_task_record_from_folder(folder, title, scope)
            self._request('task.restore', {'task_id': task_id, 'record': record}, revision=state['revision'], mutation=True)
            self.sync_artifacts(folder)
            return folder

        # Case 2: The folder is elsewhere inside the managed project; register a task referencing it in place.
        record_info = self._infer_task_record_from_folder(folder, title, scope)
        effective_title = record_info['title']
        effective_scope = scope.strip() if scope.strip() else f'Existing Work Folder: {folder}\nFiles Remain In Their Original Location.'
        if f'{folder}' not in effective_scope:
            effective_scope = f'Existing Work Folder: {folder}\n{effective_scope}'
        task = self.create(effective_title, effective_scope)
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

    def generate_metadata(self, task: Path, *, archive_sha256: str | None = None) -> dict[str, Any]:
        """Compile complete task state, steps, and file metadata into Metadata.json and Metadat.json."""
        task_root = self.root / 'Tasks' / self._task_id(task)
        record = self.read_task(task)
        task_id = record['task_id']

        files_data: list[dict[str, Any]] = []
        categories_count: dict[str, int] = {}
        total_bytes = 0

        if task_root.exists():
            for entry in sorted(task_root.rglob('*')):
                if not entry.is_file():
                    continue
                if entry.name.startswith('.aipm-') or entry.name.endswith('.tmp'):
                    continue
                rel_posix = entry.relative_to(task_root).as_posix()
                if rel_posix in {'Metadata.json', 'Metadat.json'}:
                    continue
                content = entry.read_bytes()
                size = len(content)
                total_bytes += size
                digest = hashlib.sha256(content).hexdigest()
                category = rel_posix.split('/')[0] if '/' in rel_posix else 'Root'
                categories_count[category] = categories_count.get(category, 0) + 1
                try:
                    mtime = datetime.fromtimestamp(entry.stat().st_mtime, tz=timezone.utc).isoformat()
                except (OSError, OverflowError):
                    mtime = datetime.now(timezone.utc).isoformat()
                files_data.append({
                    'relative_path': rel_posix,
                    'file_name': entry.name,
                    'category': category,
                    'size_bytes': size,
                    'sha256': digest,
                    'modified_at': mtime,
                    'is_projection': entry.name in CORE_PROJECTIONS or rel_posix == 'Handoff/Next-Agent-Handoff.md' or rel_posix.endswith('/README.md'),
                })

        metadata: dict[str, Any] = {
            'schema_version': '1.1',
            'format': 'AIPM-Task-Metadata',
            'exported_at': datetime.now(timezone.utc).isoformat(),
            'restore_instructions': 'Self-contained task record. Use AIPM "Import Archived Task From ZIP" (CLI: task-import-archive) to re-register this task and restore its folder, even if it was removed from State-Manifest.json.',
            'task_record': {key: copy.deepcopy(record[key]) for key in TASK_RECORD_FIELDS if key in record},
            'history': self._task_history(task_id),
            'task_id': task_id,
            'title': record.get('title', ''),
            'scope': record.get('scope', ''),
            'task_status': record.get('task_status', ''),
            'status_override': record.get('status_override'),
            'revision': record.get('revision', 0),
            'plan': record.get('plan', ''),
            'last_verified_action': record.get('last_verified_action', ''),
            'next_action': record.get('next_action', ''),
            'completed_work': record.get('completed_work', []),
            'changed_files': record.get('changed_files', []),
            'blockers': record.get('blockers', []),
            'verification': record.get('verification'),
            'test_results': record.get('test_results', []),
            'report': record.get('report', ''),
            'project': {
                'project_id': self.project.project_id,
                'project_root': str(self.project.root),
                'state_root': str(self.project.state_root),
            },
            'archive_info': {
                'archive_name': f'{task_id}.zip',
                'archive_sha256': archive_sha256,
            },
            'files_summary': {
                'file_count': len(files_data),
                'total_bytes': total_bytes,
                'categories': categories_count,
            },
            'files': files_data,
        }

        if task_root.exists():
            payload = json.dumps(metadata, indent=2, ensure_ascii=False) + '\n'
            self._atomic_replace(task_root / 'Metadata.json', payload)
            self._atomic_replace(task_root / 'Metadat.json', payload)

        return metadata

    def read_metadata(self, task: Path) -> dict[str, Any]:
        """Read task metadata from live task folder, archived ZIP, or authoritative Core state."""
        task_id = self._task_id(task)
        task_root = self.root / 'Tasks' / task_id
        for candidate in (task_root / 'Metadata.json', task_root / 'Metadat.json'):
            if candidate.is_file():
                try:
                    return json.loads(candidate.read_text(encoding='utf-8'))
                except (json.JSONDecodeError, OSError):
                    pass
        archive_path = self.root / 'Archive' / f'{task_id}.zip'
        if archive_path.is_file():
            with zipfile.ZipFile(archive_path, 'r') as package:
                for arc_name in ('Metadata.json', 'Metadat.json'):
                    if arc_name in package.namelist():
                        try:
                            return json.loads(package.read(arc_name).decode('utf-8'))
                        except (json.JSONDecodeError, UnicodeDecodeError):
                            pass
        return self.generate_metadata(task)

    def _verify_archive_integrity(self, task_root: Path, archive_path: Path, expected_sha256: str) -> None:
        """Verify the integrity of a task archive, its checksum sidecar, and internal metadata."""
        if not archive_path.is_file():
            raise StateError('Task Archive File Missing')
        actual_sha256 = hashlib.sha256(archive_path.read_bytes()).hexdigest()
        if actual_sha256 != expected_sha256:
            raise StateError('Task Archive Checksum Mismatch')
        checksum_path = archive_path.with_suffix('.zip.sha256')
        if not checksum_path.is_file() or not checksum_path.read_text(encoding='ascii').startswith(expected_sha256):
            raise StateError('Task Archive Checksum Sidecar Invalid')
        with zipfile.ZipFile(archive_path, 'r') as package:
            test_bad_file = package.testzip()
            if test_bad_file is not None:
                raise StateError(f'Task Archive Corrupted: {test_bad_file}')
            names = set(package.namelist())
            if 'Metadata.json' not in names or 'Metadat.json' not in names:
                raise StateError('Task Archive Missing Metadata.json')
            try:
                meta = json.loads(package.read('Metadata.json').decode('utf-8'))
                if meta.get('task_id') != task_root.name or meta.get('format') != 'AIPM-Task-Metadata':
                    raise StateError('Task Archive Metadata Invalid')
            except Exception as exc:
                raise StateError('Task Archive Metadata Cannot Be Read') from exc
            if task_root.exists():
                for entry in task_root.rglob('*'):
                    if entry.is_file():
                        rel = entry.relative_to(task_root).as_posix()
                        if rel not in names:
                            raise StateError(f'Task Archive Missing File: {rel}')

    def archive(self, task: Path, *, delete_folder: bool = False) -> dict[str, Any]:
        """Create an integrity-checked portable ZIP with Metadata.json while optionally keeping the live task record."""
        task_root = self._task_path(task)
        task_id = task_root.name
        self.sync_artifacts(task)
        self.generate_metadata(task)
        archive_root = self.root / 'Archive'
        archive_root.mkdir(parents=True, exist_ok=True)
        archive_path = archive_root / f'{task_id}.zip'
        if archive_path.exists():
            raise StateError('Task Archive Already Exists')
        try:
            with zipfile.ZipFile(archive_path, 'x', compression=zipfile.ZIP_DEFLATED, compresslevel=9) as package:
                for entry in sorted(task_root.rglob('*')):
                    if entry.is_file():
                        package.write(entry, entry.relative_to(task_root).as_posix())
            digest = hashlib.sha256(archive_path.read_bytes()).hexdigest()
            checksum_path = archive_path.with_suffix('.zip.sha256')
            checksum_path.write_text(f'{digest}  {archive_path.name}\n', encoding='ascii', newline='\n')
            self._verify_archive_integrity(task_root, archive_path, digest)
        except Exception:
            archive_path.unlink(missing_ok=True)
            archive_path.with_suffix('.zip.sha256').unlink(missing_ok=True)
            raise

        if delete_folder:
            shutil.rmtree(task_root)

        with zipfile.ZipFile(archive_path, 'r') as package:
            package_names = package.namelist()
        return {
            'archive_path': archive_path,
            'checksum_path': checksum_path,
            'task_id': task_id,
            'verified': True,
            'folder_deleted': delete_folder,
            'sha256': digest,
            'file_count': len(package_names),
        }

    def delete_task_folder(self, task: Path) -> dict[str, Any]:
        """Safely delete the live task folder after verifying the archive is intact."""
        task_id = self._task_id(task)
        task_root = self.root / 'Tasks' / task_id
        archive_path = self.root / 'Archive' / f'{task_id}.zip'
        checksum_path = archive_path.with_suffix('.zip.sha256')
        if not archive_path.is_file() or not checksum_path.is_file():
            raise StateError('Cannot Delete Task Folder: Verified Archive Does Not Exist')
        expected_sha = checksum_path.read_text(encoding='ascii').split()[0].strip()
        self._verify_archive_integrity(task_root, archive_path, expected_sha)
        if task_root.exists():
            shutil.rmtree(task_root)
        return {'task_id': task_id, 'folder_deleted': True, 'status': 'PASS'}

    def _task_history(self, task_id: str) -> list[dict[str, Any]]:
        """Return the ordered Core command history for one task (no copied project sources)."""
        events: list[dict[str, Any]] = []
        events_root = self.root / 'History' / 'Events'
        if not events_root.is_dir():
            return events
        for path in sorted(events_root.glob('*.json')):
            try:
                event = json.loads(path.read_text(encoding='utf-8'))
            except (OSError, ValueError):
                continue
            payload = event.get('input')
            if not isinstance(event, dict) or not isinstance(payload, dict) or payload.get('task_id') != task_id:
                continue
            summary = {key: value for key, value in payload.items() if key != 'record'}
            events.append({'revision': event.get('revision'), 'command': event.get('command'), 'actor': event.get('actor'), 'input': summary})
        return sorted(events, key=lambda item: item.get('revision') or 0)

    @staticmethod
    def _record_from_metadata(meta: dict[str, Any]) -> dict[str, Any]:
        """Rebuild and validate the Core task record from Metadata.json (v1.1 record or v1.0 flat fields)."""
        source = meta.get('task_record') if isinstance(meta.get('task_record'), dict) else meta
        record = copy.deepcopy({key: source[key] for key in TASK_RECORD_FIELDS if key in source})
        record.setdefault('blockers', [])
        record.setdefault('verification', None)
        record.setdefault('report', '')
        try:
            CoreEngine._validate_task_record(record)
        except StateError as error:
            raise StateError('Archive Metadata Does Not Contain A Valid Task Record') from error
        return record

    def unregister_task(self, task: Path) -> dict[str, Any]:
        """Remove a completed, archived task from the AIPM registry; the verified archive remains the only copy."""
        task_id = self._task_id(task)
        task_root = self.root / 'Tasks' / task_id
        if task_root.exists():
            raise StateError('Delete The Live Task Folder Before Removing The Registry Record')
        archive_path = self.root / 'Archive' / f'{task_id}.zip'
        checksum_path = archive_path.with_suffix('.zip.sha256')
        if not archive_path.is_file() or not checksum_path.is_file():
            raise StateError('Cannot Remove Registry Record: Verified Archive Does Not Exist')
        self._verify_archive_integrity(task_root, archive_path, checksum_path.read_text(encoding='ascii').split()[0].strip())
        with zipfile.ZipFile(archive_path, 'r') as package:
            self._record_from_metadata(json.loads(package.read('Metadata.json').decode('utf-8')))
        state = self._request('state.read', {})
        self._request('task.unregister', {'task_id': task_id}, revision=state['revision'], mutation=True)
        return {'task_id': task_id, 'registry_record_removed': True, 'archive_path': archive_path, 'status': 'PASS'}

    def import_archive(self, zip_path: Path) -> dict[str, Any]:
        """Verify an external task ZIP, re-register its task record, and restore its live folder."""
        source = Path(zip_path)
        if not source.is_file():
            raise StateError('Task Archive File Not Found')
        source = source.resolve()
        with zipfile.ZipFile(source, 'r') as package:
            bad = package.testzip()
            if bad is not None:
                raise StateError(f'Task Archive Corrupted: {bad}')
            infos = package.infolist()
            if len(infos) > MAX_IMPORT_ARCHIVE_ENTRIES or sum(info.file_size for info in infos) > MAX_IMPORT_ARCHIVE_BYTES:
                raise StateError('Task Archive Exceeds Import Limits')
            for info in infos:
                name = info.filename
                parts = name.split('/')
                if info.is_dir():
                    continue
                if (not name or name.startswith('/') or '\\' in name or '\x00' in name or ':' in name
                        or any(part in {'', '.', '..'} for part in parts)):
                    raise StateError('Task Archive Contains An Unsafe Path')
            meta_name = next((candidate for candidate in ('Metadata.json', 'Metadat.json') if candidate in package.namelist()), None)
            if meta_name is None:
                raise StateError('Task Archive Missing Metadata.json')
            try:
                meta = json.loads(package.read(meta_name).decode('utf-8'))
            except (ValueError, UnicodeDecodeError) as error:
                raise StateError('Task Archive Metadata Cannot Be Read') from error
            if not isinstance(meta, dict) or meta.get('format') != 'AIPM-Task-Metadata':
                raise StateError('Task Archive Metadata Invalid')
            task_id = meta.get('task_id')
            if not isinstance(task_id, str) or not re.fullmatch(r'Task-[A-Za-z0-9][A-Za-z0-9_-]{0,159}', task_id):
                raise StateError('Task Archive Metadata Invalid')
            record = self._record_from_metadata(meta)
            names = set(package.namelist())
            for item in meta.get('files', []):
                relative = item.get('relative_path') if isinstance(item, dict) else None
                if relative not in names:
                    raise StateError(f'Task Archive Missing File: {relative}')
                if hashlib.sha256(package.read(relative)).hexdigest() != item.get('sha256'):
                    raise StateError(f'Task Archive File Hash Mismatch: {relative}')

            sidecar = source.with_suffix('.zip.sha256')
            digest = hashlib.sha256(source.read_bytes()).hexdigest()
            if sidecar.is_file() and not sidecar.read_text(encoding='ascii', errors='ignore').strip().startswith(digest):
                raise StateError('Task Archive Checksum Mismatch')

            state = self._request('state.read', {})
            if task_id in state['state'].get('tasks', {}):
                raise StateError('Task Already Registered; Use Reopen Task Instead')
            task_root = self.root / 'Tasks' / task_id
            if task_root.exists():
                raise StateError('Live Task Folder Already Exists')

            archive_root = self.root / 'Archive'
            archive_root.mkdir(parents=True, exist_ok=True)
            target_archive = archive_root / f'{task_id}.zip'
            if target_archive.exists():
                if hashlib.sha256(target_archive.read_bytes()).hexdigest() != digest:
                    raise StateError('A Different Archive Already Exists For This Task')
            else:
                shutil.copy2(source, target_archive)
            checksum_path = target_archive.with_suffix('.zip.sha256')
            if not checksum_path.is_file():
                checksum_path.write_text(f'{digest}  {target_archive.name}\n', encoding='ascii', newline='\n')

            staging = Path(tempfile.mkdtemp(prefix='.aipm-import-', dir=self.root))
            try:
                for info in infos:
                    if info.is_dir() or info.filename.startswith('.aipm-') or info.filename.endswith('.tmp'):
                        continue
                    destination = staging.joinpath(*info.filename.split('/'))
                    if not _inside(_canonical(destination), _canonical(staging)):
                        raise StateError('Task Archive Contains An Unsafe Path')
                    destination.parent.mkdir(parents=True, exist_ok=True)
                    destination.write_bytes(package.read(info.filename))
                (self.root / 'Tasks').mkdir(parents=True, exist_ok=True)
                self._request('task.restore', {'task_id': task_id, 'record': record}, revision=state['revision'], mutation=True)
                try:
                    os.replace(staging, task_root)
                    staging = None
                    self.sync_artifacts(task_root)
                except Exception:
                    state = self._request('state.read', {})
                    self._request('task.unregister', {'task_id': task_id}, revision=state['revision'], mutation=True)
                    raise
            finally:
                if staging is not None:
                    shutil.rmtree(staging, ignore_errors=True)
        restored = self.read_task(task_root)
        return {
            'task_id': task_id,
            'title': restored['title'],
            'task_status': restored['task_status'],
            'archive_path': target_archive,
            'task_path': task_root,
            'source_project_id': (meta.get('project') or {}).get('project_id'),
            'status': 'PASS',
        }

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
                import time
                deadline = time.monotonic() + 10.0
                while True:
                    try:
                        msvcrt.locking(stream.fileno(), msvcrt.LK_NBLCK, 1)
                        break
                    except OSError:
                        if time.monotonic() >= deadline:
                            raise StateError('Could not acquire task artifact lock (timeout)')
                        time.sleep(0.05)
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
        normalized, task_root, target = self._artifact_target(task, relative_path)
        if not target.is_file():
            archive_path = self.root / 'Archive' / f'{task_root.name}.zip'
            if archive_path.is_file():
                with zipfile.ZipFile(archive_path, 'r') as package:
                    if normalized in package.namelist():
                        data = package.read(normalized)
                        if len(data) > MAX_TASK_ARTIFACT_BYTES:
                            raise StateError('Task Artifact Exceeds Size Limit')
                        return data
            raise StateError('Task Artifact Not Found')
        _canonical(target)
        if target.stat().st_size > MAX_TASK_ARTIFACT_BYTES:
            raise StateError('Task Artifact Exceeds Size Limit')
        return target.read_bytes()

    def list_artifacts(self, task: Path) -> list[dict[str, Any]]:
        task_root = self._task_path(task)
        task_id = task_root.name
        archive_path = self.root / 'Archive' / f'{task_id}.zip'
        if not task_root.exists() and archive_path.is_file():
            meta = self.read_metadata(task)
            artifacts: list[dict[str, Any]] = []
            for f in meta.get('files', []):
                if f.get('category') in TASK_ARTIFACT_CATEGORIES:
                    artifacts.append({
                        'path': f['relative_path'],
                        'size_bytes': f['size_bytes'],
                        'sha256': f['sha256'],
                        'replayed': False,
                    })
            return sorted(artifacts, key=lambda item: item['path'].casefold())

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
        self.generate_metadata(task)

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
