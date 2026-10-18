"""State continuity, read-only Git observations, and identity-bound leases."""
from __future__ import annotations

from datetime import datetime, timezone, timedelta
from contextlib import contextmanager
import ctypes
from ctypes import wintypes
import hashlib
import json
import os
from pathlib import Path
import re
import secrets
import shutil
import subprocess
from typing import Any, TYPE_CHECKING
from uuid import uuid4

from .storage import ManagedProject, StateError, _atomic_json, _canonical, _inside, validate_managed_project
if TYPE_CHECKING:
    from .domain import CoreEngine


class LockError(RuntimeError):
    pass


def _read_mapping(path: Path, error_type: type[Exception] = StateError) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding='utf-8'))
        if not isinstance(data, dict):
            raise ValueError('Expected A Mapping')
        return data
    except (OSError, ValueError, TypeError) as error:
        raise error_type('INVALID_RECORD') from error


def _move_noreplace(source: Path, target: Path) -> None:
    """Move atomically without replacing any independently created target."""
    try:
        if os.name == 'nt':
            # Windows os.rename fails if the target exists, including files.
            os.rename(source, target)
            return
        libc = ctypes.CDLL(None, use_errno=True)
        rename = getattr(libc, 'renameat2', None)
        if rename is None:
            raise StateError('Atomic No-Replace Move Is Unavailable')
        rename.argtypes = [ctypes.c_int, ctypes.c_char_p, ctypes.c_int, ctypes.c_char_p, ctypes.c_uint]
        rename.restype = ctypes.c_int
        if rename(-100, os.fsencode(source), -100, os.fsencode(target), 1):
            code = ctypes.get_errno()
            raise OSError(code, os.strerror(code))
    except OSError as error:
        raise StateError('No-Replace Move Failed') from error


def _process_identity(pid: int) -> dict[str, Any]:
    """Distinguish absence from inaccessible identity; never guess on denial."""
    if type(pid) is not int or pid <= 0:
        return {'status': 'unknown'}
    if os.name == 'nt':
        kernel = ctypes.WinDLL('kernel32', use_last_error=True)
        kernel.OpenProcess.argtypes = [wintypes.DWORD, wintypes.BOOL, wintypes.DWORD]
        kernel.OpenProcess.restype = wintypes.HANDLE
        kernel.CloseHandle.argtypes = [wintypes.HANDLE]
        kernel.GetProcessTimes.argtypes = [wintypes.HANDLE] + [ctypes.POINTER(wintypes.FILETIME)] * 4
        kernel.GetExitCodeProcess.argtypes = [wintypes.HANDLE, ctypes.POINTER(wintypes.DWORD)]
        kernel.ProcessIdToSessionId.argtypes = [wintypes.DWORD, ctypes.POINTER(wintypes.DWORD)]
        kernel.WaitForSingleObject.argtypes = [wintypes.HANDLE, wintypes.DWORD]
        kernel.WaitForSingleObject.restype = wintypes.DWORD
        handle = kernel.OpenProcess(0x101000, False, pid)
        if not handle:
            return {'status': 'gone' if ctypes.get_last_error() == 87 else 'unknown'}
        try:
            created, exited, kernel_time, user_time = [wintypes.FILETIME() for _ in range(4)]
            exit_code, session = wintypes.DWORD(), wintypes.DWORD()
            if not kernel.GetProcessTimes(handle, ctypes.byref(created), ctypes.byref(exited), ctypes.byref(kernel_time), ctypes.byref(user_time)) or not kernel.GetExitCodeProcess(handle, ctypes.byref(exit_code)):
                return {'status': 'unknown'}
            wait = kernel.WaitForSingleObject(handle, 0)
            if wait == 0:
                return {'status': 'gone'}
            if wait != 258:
                return {'status': 'unknown'}
            if not kernel.ProcessIdToSessionId(pid, ctypes.byref(session)):
                return {'status': 'unknown'}
            return {'status': 'live', 'creation': str((created.dwHighDateTime << 32) | created.dwLowDateTime), 'session': str(session.value)}
        finally:
            kernel.CloseHandle(handle)
    try:
        # Linux proc start ticks and session are stable across observations.
        fields = Path(f'/proc/{pid}/stat').read_text().rsplit(')', 1)[1].split()
        if fields[0] == 'Z':
            return {'status': 'gone'}
        return {'status': 'live', 'creation': fields[19], 'session': fields[3]}
    except FileNotFoundError:
        return {'status': 'gone'} if Path('/proc').is_dir() else {'status': 'unknown'}
    except (OSError, IndexError):
        return {'status': 'unknown'}


class ContinuityManager:
    def __init__(self, project: ManagedProject, engine: CoreEngine | None = None):
        validate_managed_project(project)
        self.project, self.engine = project, engine

    def _bounded(self, path: Path) -> Path:
        validate_managed_project(self.project)
        root, path = _canonical(self.project.state_root), _canonical(path)
        if path == root or not _inside(path, root):
            raise StateError('Path Must Remain Within Managed State Root')
        return path

    def checkpoint(self, actor: str, next_action: str, evidence: str, token_usage: int | None) -> None:
        data = {'actor': actor, 'next_action': next_action, 'last_verified_action': evidence, 'token_usage': token_usage, 'created_at': datetime.now(timezone.utc).isoformat()}
        _atomic_json(self._bounded(self.project.state_root / 'History' / 'Checkpoints' / 'checkpoint.json'), data)
        self._bounded(self.project.state_root / 'Current-State.md').write_text(f'# Current State\n\n{evidence}\n', encoding='utf-8')

    def handoff(self) -> dict:
        return json.loads(self._bounded(self.project.state_root / 'History' / 'Checkpoints' / 'checkpoint.json').read_text(encoding='utf-8'))

    def snapshot(self) -> Path:
        target = self._bounded(self.project.state_root / 'History' / 'Snapshots' / f'state-snapshot-{uuid4().hex}')
        # Validate all entries before copytree could follow an internal redirect.
        for path in self.project.state_root.rglob('*'):
            self._bounded(path)
        shutil.copytree(self.project.state_root, target, ignore=shutil.ignore_patterns('Snapshots'))
        return target

    def restore(self, snapshot: Path) -> None:
        source = self._bounded(snapshot / 'Current-State.md')
        if source.exists():
            self._bounded(self.project.state_root / 'Current-State.md').write_bytes(source.read_bytes())

    def _git(self, *args: str, optional: bool = False) -> bytes:
        result = subprocess.run(['git', '--no-optional-locks', '-C', str(self.project.root), *args], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
        if result.returncode and not optional:
            raise StateError('Git Observation Failed')
        return result.stdout if not result.returncode else b''

    def git_status(self) -> dict[str, Any]:
        if self._git('rev-parse', '--show-toplevel').decode().strip().casefold() != str(self.project.root.resolve()).replace('\\', '/').casefold():
            raise StateError('Managed Root Must Be Git Repository Root')
        branch = self._git('symbolic-ref', '--quiet', '--short', 'HEAD', optional=True).decode().strip() or None
        head = self._git('rev-parse', '--verify', 'HEAD', optional=True).decode().strip() or None
        digest = hashlib.sha256()
        exclude = f':(top,exclude,literal){self.project.state_root.name}'
        for args in [('diff', '--cached', '--binary', '--no-ext-diff', '--no-textconv'), ('diff', '--binary', '--no-ext-diff', '--no-textconv')]:
            content = self._git(*args, '--', '.', exclude)
            digest.update(len(content).to_bytes(8, 'big')); digest.update(content)
        for raw in sorted(filter(None, self._git('ls-files', '--others', '--exclude-standard', '-z', '--', '.', exclude).split(b'\x00'))):
            path = self.project.root / os.fsdecode(raw)
            canonical = _canonical(path)
            if not _inside(canonical, _canonical(self.project.root)):
                raise StateError('Untracked Path Escapes Project')
            content = canonical.read_bytes()
            digest.update(len(raw).to_bytes(8, 'big')); digest.update(raw)
            digest.update(hashlib.sha256(content).digest())
        return {'branch': branch, 'head_sha': head, 'diff_fingerprint': digest.hexdigest()}

    def reconcile_git(self) -> dict[str, Any]:
        observed = self.git_status()
        manifest = json.loads(self._bounded(self.project.state_root / 'State-Manifest.json').read_text(encoding='utf-8'))
        changed = [key for key, value in observed.items() if manifest.get(key) != value]
        return {**observed, 'drift': bool(changed), 'changed_fields': changed}

    def record_git_status(self, actor: str) -> dict[str, Any]:
        from .domain import CommandEnvelope
        if self.engine is None:
            raise StateError('Core Engine Is Required For Git Persistence')
        read = self.engine.execute(CommandEnvelope(uuid4().hex, 'state.read', actor, self.project.project_id, 0, None, {}))
        if read['status'] != 'PASS':
            return read
        return self.engine.execute(CommandEnvelope(uuid4().hex, 'state.record-git-observation', actor, self.project.project_id, read['revision'], None, self.git_status()))

    def _hashes(self, source: Path) -> dict[str, str]:
        source = self._bounded(source)
        entries = [source, *sorted(source.rglob('*'))] if source.is_dir() else [source]
        result = {}
        for entry in entries:
            entry = self._bounded(entry)
            name = '.' if entry == source else entry.relative_to(source).as_posix()
            if entry.is_dir():
                result[name + '/'] = 'directory'
            elif entry.is_file():
                result[name] = hashlib.sha256(entry.read_bytes()).hexdigest()
            else:
                raise StateError('Unsupported Archive Entry')
        return result

    @staticmethod
    def _exclusive_json(path: Path, data: dict) -> None:
        with path.open('x', encoding='utf-8') as stream:
            json.dump(data, stream, indent=2, sort_keys=True)
            stream.write('\n'); stream.flush(); os.fsync(stream.fileno())

    def _move_to_store(self, source: Path, category: str, reason: str) -> Path:
        source = self._bounded(source)
        if not isinstance(reason, str) or not reason.strip() or not source.exists():
            raise StateError('Existing Source And Reason Are Required')
        # Do not relocate manager roots, protocol records, or active manifests.
        relative = source.relative_to(self.project.state_root)
        if relative.parts[0] not in {'Tasks', 'Tool-State', 'Temporary-Files', 'Cache', 'Test-Workspace', 'Logs'} or len(relative.parts) < 2:
            raise StateError('Source Is Protected Operational State')
        hashes = self._hashes(source)
        identifier = uuid4().hex
        base = self._bounded(self.project.state_root / category / identifier)
        base.mkdir()  # Exclusive ownership; collision never overwrites.
        stored, record = base / 'Payload', base / 'Record.json'
        data = {'schema_version': '1.0', 'category': category, 'reason': reason, 'source_path': relative.as_posix(), 'stored_path': stored.relative_to(self.project.state_root).as_posix(), 'hashes': hashes, 'created_at': datetime.now(timezone.utc).isoformat()}
        self._exclusive_json(record, data)  # Durable intent makes a failed move recoverable.
        _move_noreplace(source, stored)
        if self._hashes(stored) != hashes:
            raise StateError('Archived Content Hash Mismatch')
        self._exclusive_json(base / 'Moved.json', {'created_at': datetime.now(timezone.utc).isoformat()})
        return record

    def quarantine(self, source: Path, reason: str) -> Path:
        return self._move_to_store(source, 'Quarantine', reason)

    def archive(self, source: Path, label: str) -> Path:
        return self._move_to_store(source, 'Archive', label)

    def _restore_record(self, record: Path, category: str) -> Path:
        record = self._bounded(record)
        data = _read_mapping(record)
        if data.get('schema_version') != '1.0' or any(not isinstance(data.get(key), str) or not data[key].strip() for key in ('category', 'reason', 'source_path', 'stored_path', 'created_at')) or not isinstance(data.get('hashes'), dict) or not data['hashes'] or any(not isinstance(key, str) or not isinstance(value, str) or (value != 'directory' and not re.fullmatch('[a-f0-9]{64}', value)) for key, value in data['hashes'].items()):
            raise StateError('Invalid Recovery Record Fields')
        if data['category'] != category or record.name != 'Record.json' or record.parent.parent != self.project.state_root / category:
            raise StateError('Invalid Recovery Record')
        stored = self._bounded(self.project.state_root / data['stored_path'])
        target = self._bounded(self.project.state_root / data['source_path'])
        relative = target.relative_to(self.project.state_root)
        if stored != record.parent / 'Payload' or len(relative.parts) < 2 or relative.parts[0] not in {'Tasks', 'Tool-State', 'Temporary-Files', 'Cache', 'Test-Workspace', 'Logs'}:
            raise StateError('Invalid Recovery Destination')
        intent, receipt = record.parent / 'Restore-Intent.json', record.parent / 'Restored.json'
        if intent.exists():
            recovery = _read_mapping(intent)
            if recovery.get('target') != data['source_path'] or not isinstance(recovery.get('created_at'), str) or not recovery['created_at']:
                raise StateError('Recovery Intent Mismatch')
        if receipt.exists():
            restored = _read_mapping(receipt)
            if not isinstance(restored.get('created_at'), str) or not restored['created_at']:
                raise StateError('Invalid Recovery Receipt')
        if target.exists() and not stored.exists() and intent.exists():
            if self._hashes(target) != data['hashes']:
                raise StateError('Restored Content Hash Mismatch')
            if not receipt.exists():
                self._exclusive_json(receipt, {'created_at': datetime.now(timezone.utc).isoformat()})
            return target
        if target.exists() or not stored.exists() or receipt.exists():
            raise StateError('Recovery Collision Or Missing Payload')
        if self._hashes(stored) != data['hashes']:
            raise StateError('Archived Content Hash Mismatch')
        if not intent.exists():
            self._exclusive_json(intent, {'target': data['source_path'], 'created_at': datetime.now(timezone.utc).isoformat()})
        target.parent.mkdir(parents=True, exist_ok=True)
        _move_noreplace(stored, target)
        self._exclusive_json(receipt, {'created_at': datetime.now(timezone.utc).isoformat()})
        return target

    def restore_quarantined(self, record: Path) -> Path:
        return self._restore_record(record, 'Quarantine')

    def restore_archive(self, record: Path) -> Path:
        return self._restore_record(record, 'Archive')

    def _lock_path(self, resource: str) -> Path:
        if not isinstance(resource, str) or not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_-]{0,159}', resource):
            raise LockError('INVALID_LOCK_RESOURCE')
        return self._bounded(self.project.state_root / 'Locks' / f'{resource}.json')

    @contextmanager
    def _lock_guard(self, resource: str):
        # Keep this file permanently: unlinking a guard would create two lock
        # domains for waiters holding its old inode and new arrivals.
        try:
            path = self._bounded(self._lock_path(resource).with_suffix('.guard'))
            with path.open('a+b') as guard:
                if os.fstat(guard.fileno()).st_size == 0:
                    guard.write(b'\0'); guard.flush()
                guard.seek(0)
                if os.name == 'nt':
                    import msvcrt
                    msvcrt.locking(guard.fileno(), msvcrt.LK_LOCK, 1)
                else:
                    import fcntl
                    fcntl.flock(guard.fileno(), fcntl.LOCK_EX)
                try:
                    yield
                finally:
                    guard.seek(0)
                    if os.name == 'nt':
                        msvcrt.locking(guard.fileno(), msvcrt.LK_UNLCK, 1)
                    else:
                        fcntl.flock(guard.fileno(), fcntl.LOCK_UN)
        except (OSError, StateError) as error:
            raise LockError('LOCK_GUARD_UNAVAILABLE') from error

    @staticmethod
    def _read_lock(path: Path) -> dict[str, Any]:
        data = _read_mapping(path, LockError)
        identity = data.get('process_identity')
        if type(data.get('pid')) is not int or data['pid'] <= 0 or any(not isinstance(data.get(key), str) or not data[key] for key in ('actor', 'nonce', 'created_at', 'expires_at')) or not isinstance(identity, dict) or identity.get('status') != 'live' or any(not isinstance(identity.get(key), str) or not identity[key] for key in ('creation', 'session')):
            raise LockError('INVALID_LOCK_RECORD')
        try:
            for key in ('created_at', 'expires_at'):
                if datetime.fromisoformat(data[key]).utcoffset() is None:
                    raise ValueError('Timezone Required')
        except ValueError as error:
            raise LockError('INVALID_LOCK_RECORD') from error
        return data

    def acquire_lock(self, resource: str, actor: str, lease_seconds: int = 300) -> str:
        path = self._lock_path(resource)
        if type(lease_seconds) is not int or lease_seconds <= 0 or not isinstance(actor, str) or not actor.strip():
            raise LockError('INVALID_LOCK_LEASE')
        with self._lock_guard(resource):
            identity = _process_identity(os.getpid())
            if identity.get('status') != 'live':
                raise LockError('PROCESS_IDENTITY_UNAVAILABLE')
            now, nonce = datetime.now(timezone.utc), secrets.token_urlsafe(16)
            try:
                self._exclusive_json(path, {'actor': actor, 'pid': os.getpid(), 'process_identity': identity, 'nonce': nonce, 'created_at': now.isoformat(), 'expires_at': (now + timedelta(seconds=lease_seconds)).isoformat()})
            except FileExistsError as error:
                raise LockError('LOCK_HELD') from error
            return nonce

    def recover_expired_lock(self, resource: str) -> None:
        path = self._lock_path(resource)
        with self._lock_guard(resource):
            data = self._read_lock(path)
            identity = data['process_identity']
            current = _process_identity(data['pid'])
            expired = datetime.fromisoformat(data['expires_at']) <= datetime.now(timezone.utc)
            safe = identity.get('status') == 'live' and all(isinstance(identity.get(key), str) and identity[key] for key in ('creation', 'session')) and (current.get('status') == 'gone' or (current.get('status') == 'live' and all(current.get(key) for key in ('creation', 'session')) and any(current[key] != identity[key] for key in ('creation', 'session'))))
            if not expired or not safe:
                raise LockError('LOCK_NOT_SAFE_TO_RECOVER')
            path.unlink()

    def release_lock(self, resource: str, nonce: str) -> None:
        path = self._lock_path(resource)
        with self._lock_guard(resource):
            if self._read_lock(path)['nonce'] != nonce:
                raise LockError('LOCK_NONCE_MISMATCH')
            path.unlink()
