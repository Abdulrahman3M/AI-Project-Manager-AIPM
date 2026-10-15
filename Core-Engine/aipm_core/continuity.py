"""State continuity, read-only Git observations, and identity-bound leases."""
from __future__ import annotations

from datetime import datetime, timezone, timedelta
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

from .storage import ManagedProject, StateError, _atomic_json, _canonical, _inside
if TYPE_CHECKING:
    from .domain import CoreEngine


class LockError(RuntimeError):
    pass


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
        self.project, self.engine = project, engine

    def _bounded(self, path: Path) -> Path:
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
        if not reason.strip() or not source.exists():
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
        source.rename(stored)
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
        data = json.loads(record.read_text(encoding='utf-8'))
        if data.get('category') != category or record.name != 'Record.json' or record.parent.parent != self.project.state_root / category:
            raise StateError('Invalid Recovery Record')
        stored = self._bounded(self.project.state_root / data['stored_path'])
        target = self._bounded(self.project.state_root / data['source_path'])
        if stored != record.parent / 'Payload' or target.relative_to(self.project.state_root).parts[0] not in {'Tasks', 'Tool-State', 'Temporary-Files', 'Cache', 'Test-Workspace', 'Logs'}:
            raise StateError('Invalid Recovery Destination')
        intent, receipt = record.parent / 'Restore-Intent.json', record.parent / 'Restored.json'
        if intent.exists() and json.loads(intent.read_text(encoding='utf-8')).get('target') != data['source_path']:
            raise StateError('Recovery Intent Mismatch')
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
        stored.rename(target)
        self._exclusive_json(receipt, {'created_at': datetime.now(timezone.utc).isoformat()})
        return target

    def restore_quarantined(self, record: Path) -> Path:
        return self._restore_record(record, 'Quarantine')

    def restore_archive(self, record: Path) -> Path:
        return self._restore_record(record, 'Archive')

    def _lock_path(self, resource: str) -> Path:
        if not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_-]{0,159}', resource):
            raise LockError('INVALID_LOCK_RESOURCE')
        return self._bounded(self.project.state_root / 'Locks' / f'{resource}.json')

    def acquire_lock(self, resource: str, actor: str, lease_seconds: int = 300) -> str:
        path = self._lock_path(resource)
        if type(lease_seconds) is not int or lease_seconds <= 0:
            raise LockError('INVALID_LOCK_LEASE')
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
        original = path.read_bytes()
        try:
            data = json.loads(original)
            identity = data['process_identity']
            current = _process_identity(data['pid'])
            expired = datetime.fromisoformat(data['expires_at']) <= datetime.now(timezone.utc)
            safe = identity.get('status') == 'live' and all(isinstance(identity.get(key), str) and identity[key] for key in ('creation', 'session')) and (current.get('status') == 'gone' or (current.get('status') == 'live' and all(current.get(key) for key in ('creation', 'session')) and any(current[key] != identity[key] for key in ('creation', 'session'))))
            if not expired or not safe or path.read_bytes() != original:
                raise LockError('LOCK_NOT_SAFE_TO_RECOVER')
        except (KeyError, ValueError, TypeError) as error:
            raise LockError('LOCK_NOT_SAFE_TO_RECOVER') from error
        path.unlink()

    def release_lock(self, resource: str, nonce: str) -> None:
        path = self._lock_path(resource)
        if not path.exists() or json.loads(path.read_text(encoding='utf-8'))['nonce'] != nonce:
            raise LockError('LOCK_NONCE_MISMATCH')
        path.unlink()
