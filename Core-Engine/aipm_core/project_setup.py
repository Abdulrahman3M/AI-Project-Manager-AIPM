"""Explicit, non-destructive setup and inspection of optional project components."""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import tempfile
import stat

from .storage import STATE_ROOT_NAME, StateError, _protect_platform_path

VERSION = 2
PREFERENCES_VERSION = 1
MIN_GIT_VERSION = (2, 20, 0)
TEMPLATE = Path(__file__).resolve().parents[2] / "Templates" / "FIRG"
PREFERENCES = "Component-Preferences.json"
RULE = ("\n\n## Mandatory FIRG Pre-Read And External-Change Safeguard\n\n"
        "Before material work, read root and applicable scoped agent instructions. Before fixes or external integrations, "
        "read FIRG/AGENTS.md, FIRG/README.md and relevant FIRG/FIX-HISTORY.md entries. "
        "Review external functional changes with FIRG before accepting, applying, merging, rebasing or cherry-picking them; "
        "use a non-destructive review and relevant tests. If FIRG is missing or incomplete, repair it without overwriting "
        "unknown material before treating incoming changes as reviewed. Never infer safety from a clean merge or AI analysis alone. "
        "When documentation is selected, record fixes with verified provenance and test evidence in the canonical registry and regenerate the ledger. "
        "Do not bypass checks or fabricate results; preserve existing rules and pending work and report unresolved risks.\n")
HOOK = b'''#!/bin/sh
# AIPM FIRG Post-Commit Prompt; Local And Bypassable.
if [ ! -t 1 ] || [ ! -r /dev/tty ]; then exit 0; fi
root=$(git rev-parse --show-toplevel) || exit 0
sha=$(git rev-parse --verify HEAD^{commit}) || exit 0
if command -v python3 >/dev/null 2>&1; then py=python3
elif command -v python >/dev/null 2>&1; then py=python
else printf '%s\\n' 'FIRG: Python unavailable; commit remains undocumented.'; exit 0
fi
"$py" "$root/FIRG/tools/firg.py" prompt-commit --commit "$sha" </dev/tty >/dev/tty 2>&1 || printf '%s\\n' 'FIRG: Documentation did not complete; the commit is preserved.'
exit 0
'''


def _rule_variant(content: bytes, rule: str) -> bytes | None:
    """Match one exact managed rule with either LF or CRLF line endings."""
    if not rule:
        return None
    variants = (rule.encode('utf-8'), rule.replace('\n', '\r\n').encode('utf-8'))
    matches = [item for item in variants if content.count(item) == 1]
    return matches[0] if len(matches) == 1 else None


def _replace_rule(content: bytes, old_rule: str) -> bytes:
    variant = _rule_variant(content, old_rule)
    if variant is None:
        raise StateError('ROOT_AGENTS_REVIEW_REQUIRED')
    replacement = RULE.replace('\n', '\r\n').encode('utf-8') if b'\r\n' in variant else RULE.encode('utf-8')
    return content.replace(variant, replacement, 1)


def _replace_preserving_permissions(source: Path, target: Path) -> None:
    """Replace existing content without silently changing target access controls."""
    if os.name == 'nt':
        import ctypes
        from ctypes import wintypes
        kernel = ctypes.WinDLL('kernel32', use_last_error=True)
        replace = kernel.ReplaceFileW
        replace.argtypes = [wintypes.LPCWSTR, wintypes.LPCWSTR, wintypes.LPCWSTR,
                            wintypes.DWORD, wintypes.LPVOID, wintypes.LPVOID]
        replace.restype = wintypes.BOOL
        if not replace(str(target), str(source), None, 0, None, None):
            raise ctypes.WinError(ctypes.get_last_error())
    else:
        info = target.stat()
        source_info = source.stat()
        if (source_info.st_uid, source_info.st_gid) != (info.st_uid, info.st_gid):
            os.chown(source, info.st_uid, info.st_gid)
        os.chmod(source, stat.S_IMODE(info.st_mode))
        if hasattr(os, 'listxattr'):
            for name in os.listxattr(target):
                os.setxattr(source, name, os.getxattr(target, name))
        os.replace(source, target)


def _write_json_safely(path: Path, data: dict, expected: bytes | None) -> None:
    """Create exclusively, or replace unchanged JSON while preserving permissions."""
    payload = (json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True) + '\n').encode('utf-8')
    if expected is None:
        with path.open('xb') as out:
            out.write(payload); out.flush(); os.fsync(out.fileno())
        return
    if path.is_symlink() or path.read_bytes() != expected:
        raise StateError('MANAGED_METADATA_CHANGED')
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(dir=path.parent, delete=False) as out:
            temporary = Path(out.name)
            out.write(payload); out.flush(); os.fsync(out.fileno())
        if path.read_bytes() != expected:
            raise StateError('MANAGED_METADATA_CHANGED')
        _replace_preserving_permissions(temporary, path)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


def _root(path: Path) -> Path:
    root = _protect_platform_path(path, operation="project setup")
    if not root.is_dir():
        raise StateError("PROJECT_DIRECTORY_REQUIRED")
    return root


def _git(root: Path, *args: str) -> subprocess.CompletedProcess:
    try:
        return subprocess.run(["git", "-C", str(root), *args], capture_output=True,
                              text=True, encoding="utf-8", errors="replace", timeout=10)
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise StateError("GIT_UNAVAILABLE") from exc


def git_status(root: Path) -> str:
    result = _git(root, "rev-parse", "--show-toplevel")
    if result.returncode:
        # An existing .git indicates a broken or inaccessible repository, not absence.
        return "ERROR" if (root / ".git").exists() else "MISSING"
    try:
        if Path(result.stdout.strip()).resolve() != root.resolve():
            return "PARENT_REPOSITORY"
    except OSError:
        return "ERROR"
    status = _git(root, "status", "--porcelain", "--untracked-files=no")
    return "READY" if status.returncode == 0 else "ERROR"


def git_version(root: Path) -> tuple[str, str, str]:
    """Compare Git with AIPM's declared offline compatibility baseline, not latest."""
    try:
        result = _git(root, '--version')
        match = re.match(r'^git version (\d+)\.(\d+)(?:\.(\d+))?', result.stdout.strip())
        if result.returncode or not match:
            return 'UNKNOWN', 'UNVERIFIED', 'UNKNOWN'
        version = tuple(int(part or 0) for part in match.groups())
        text = '.'.join(str(part) for part in version)
        distribution = 'GIT_FOR_WINDOWS' if re.search(r'\.windows(?:\.|\s|$)', result.stdout, re.IGNORECASE) else 'OTHER_OR_UNKNOWN'
        return text, 'MEETS_BASELINE' if version >= MIN_GIT_VERSION else 'BELOW_BASELINE', distribution
    except StateError:
        return 'UNKNOWN', 'UNVERIFIED', 'UNKNOWN'


def hook_status(root: Path) -> tuple[str, Path | None]:
    """Inspect only the repository-local default hook; never replace other hooks."""
    configured = _git(root, 'config', '--get', 'core.hooksPath')
    if configured.returncode == 0:
        return 'CUSTOM_HOOKS_PATH', None
    if configured.returncode != 1:
        return 'UNAVAILABLE', None
    result = _git(root, 'rev-parse', '--git-path', 'hooks/post-commit')
    git_dir = root / '.git'
    if result.returncode or not git_dir.is_dir() or git_dir.is_symlink():
        return 'UNAVAILABLE', None
    candidate = Path(result.stdout.strip())
    if not candidate.is_absolute():
        candidate = root / candidate
    if candidate.is_symlink() or not candidate.resolve().is_relative_to(git_dir.resolve()):
        return 'UNAVAILABLE', None
    if candidate.exists():
        if not candidate.is_file():
            return 'EXISTING_HOOK', None
        existing = candidate.read_bytes()
        if existing != HOOK:
            marker = root / 'FIRG' / 'aipm-install.json'
            try:
                data = json.loads(marker.read_text(encoding='utf-8'))
                if data.get('hook_sha256') == hashlib.sha256(existing).hexdigest():
                    return 'UPDATE_AVAILABLE', candidate
            except (OSError, ValueError, TypeError, AttributeError):
                pass
            return 'EXISTING_HOOK', candidate
        return ('READY' if os.name == 'nt' or os.access(candidate, os.X_OK) else 'NOT_EXECUTABLE'), candidate
    return 'MISSING', candidate


def install_firg_hook(path: Path) -> str:
    root = _root(path)
    firg = root / 'FIRG'
    tool = firg / 'tools' / 'firg.py'
    marker = firg / 'aipm-install.json'
    if git_status(root) != 'READY' or not tool.is_file():
        raise StateError('FIRG_AND_GIT_REQUIRED')
    if (not firg.resolve().is_relative_to(root) or not tool.resolve().is_relative_to(firg.resolve())
            or tool.is_symlink() or marker.is_symlink() or not marker.is_file()):
        raise StateError('FIRG_HOOK_TOOL_REVIEW_REQUIRED')
    try:
        marker_original = marker.read_bytes()
        metadata = json.loads(marker_original.decode('utf-8'))
        tool_hash = hashlib.sha256(tool.read_bytes()).hexdigest()
        template_hash = hashlib.sha256((TEMPLATE / 'tools' / 'firg.py').read_bytes()).hexdigest()
        if metadata.get('version') != VERSION or tool_hash != metadata['files']['tools/firg.py'] or tool_hash != template_hash:
            raise StateError('FIRG_HOOK_TOOL_REVIEW_REQUIRED')
    except (OSError, ValueError, KeyError, TypeError, AttributeError) as exc:
        raise StateError('FIRG_HOOK_TOOL_REVIEW_REQUIRED') from exc
    status, hook = hook_status(root)
    if status == 'READY':
        return status
    if status not in ('MISSING', 'UPDATE_AVAILABLE') or hook is None:
        return status
    hook.parent.mkdir(parents=True, exist_ok=True)
    try:
        if status == 'MISSING':
            with hook.open('xb') as out:
                out.write(HOOK)
        else:
            state = root / STATE_ROOT_NAME
            scratch = state / 'Temporary-Files'
            if not scratch.is_dir() or not scratch.resolve().is_relative_to(root):
                return 'BACKUP_WORKSPACE_REQUIRED'
            old_hook = hook.read_bytes()
            if hashlib.sha256(old_hook).hexdigest() != metadata.get('hook_sha256'):
                raise StateError('FIRG_HOOK_CHANGED_DURING_UPDATE')
            from uuid import uuid4
            backup = state / 'History' / 'FIRG-Updates' / ('Hook-' + uuid4().hex)
            if not backup.resolve().is_relative_to(state.resolve()):
                raise StateError('FIRG_BACKUP_OUTSIDE_STATE')
            backup.mkdir(parents=True)
            (backup / 'post-commit').write_bytes(old_hook)
            temporary = None
            try:
                with tempfile.NamedTemporaryFile(dir=scratch, delete=False) as out:
                    temporary = Path(out.name)
                    out.write(HOOK); out.flush(); os.fsync(out.fileno())
                if hook.read_bytes() != old_hook:
                    raise StateError('FIRG_HOOK_CHANGED_DURING_UPDATE')
                _replace_preserving_permissions(temporary, hook)
            finally:
                if temporary is not None:
                    temporary.unlink(missing_ok=True)
        hook.chmod(hook.stat().st_mode | 0o111)
        metadata['hook_sha256'] = hashlib.sha256(HOOK).hexdigest()
        _write_json_safely(marker, metadata, marker_original)
    except FileExistsError:
        return 'EXISTING_HOOK'
    return 'READY'


def inspect_project(path: Path) -> dict:
    root = _root(path)
    try:
        git = git_status(root)
    except StateError as exc:
        if str(exc) != "GIT_UNAVAILABLE":
            raise
        git = "UNAVAILABLE"
    installed_git_version, version_status, distribution = git_version(root)
    state = root / STATE_ROOT_NAME
    preference_path = state / PREFERENCES
    preferences = {}
    if preference_path.exists():
        try:
            preferences = json.loads(preference_path.read_text(encoding="utf-8"))
            if not isinstance(preferences, dict) or preferences.get("schema_version") != PREFERENCES_VERSION:
                raise ValueError("invalid preferences")
        except (OSError, ValueError) as exc:
            raise StateError("INVALID_COMPONENT_PREFERENCES") from exc
    firg = root / "FIRG"
    marker = firg / "aipm-install.json"
    if firg.is_symlink() or not firg.resolve().is_relative_to(root):
        firg_state = 'INVALID'
    elif marker.is_symlink() or not marker.resolve().is_relative_to(firg.resolve()):
        firg_state = 'INVALID'
    elif (firg / 'aipm-install.pending.json').is_file():
        firg_state = 'INSTALL_INTERRUPTED'
    elif not firg.exists():
        firg_state = ("DECLINED" if preferences.get("firg") is False else
                      "MISSING" if git == "READY" else "GIT_REQUIRED")
    elif not marker.is_file():
        firg_state = "EXISTING_UNMANAGED"
    else:
        try:
            data = json.loads(marker.read_text(encoding="utf-8"))
            version = data["version"]
            hashes = data["files"]
            required = {'AGENTS.md', 'README.md', 'tools/firg.py', 'schemas/fix-record.schema.json', 'policies/INTEGRATION.md', 'tests/test_firg.py'}
            if type(version) is not int or not isinstance(hashes, dict) or not required.issubset(hashes):
                raise ValueError("invalid marker")
            for name, digest in hashes.items():
                part = Path(name)
                if (not isinstance(name, str) or part.is_absolute() or ".." in part.parts
                        or not isinstance(digest, str) or len(digest) != 64):
                    raise ValueError("invalid marker file")
            for name in (*hashes, 'FIX-HISTORY.md', 'config.json'):
                candidate = firg / name
                if candidate.is_symlink() or not candidate.resolve().is_relative_to(firg.resolve()):
                    raise ValueError('unsafe managed file')
            root_rules = root / 'AGENTS.md'
            if root_rules.is_symlink() or not root_rules.resolve().is_relative_to(root):
                raise ValueError('unsafe root instructions')
            if version > VERSION:
                firg_state = "NEWER"
            elif any(not (firg / name).is_file() for name in (*hashes, 'FIX-HISTORY.md', 'config.json')):
                firg_state = "INCOMPLETE"
            elif any(hashlib.sha256((firg / name).read_bytes()).hexdigest() != digest
                     for name, digest in hashes.items()):
                firg_state = "MODIFIED"
            elif not (root / 'AGENTS.md').is_file():
                firg_state = "ROOT_RULE_REVIEW_REQUIRED"
            elif _rule_variant((root / 'AGENTS.md').read_bytes(), RULE) is None:
                old_rule = data.get('rule')
                current_rules = (root / 'AGENTS.md').read_bytes()
                firg_state = ('UPDATE_AVAILABLE' if version < VERSION and isinstance(old_rule, str) and old_rule.startswith('\n\n## Mandatory FIRG Pre-Read')
                              and _rule_variant(current_rules, old_rule) is not None else 'ROOT_RULE_REVIEW_REQUIRED')
            else:
                firg_state = "UPDATE_AVAILABLE" if version < VERSION else "READY"
        except (OSError, ValueError, KeyError, TypeError):
            firg_state = "INVALID"
    if git != "READY" and firg_state in ("READY", "MODIFIED", "UPDATE_AVAILABLE", "EXISTING_UNMANAGED"):
        firg_state = "GIT_REQUIRED"
    if (state / 'Tool-State' / 'FIRG-Update.json').is_file():
        firg_state = 'UPDATE_INTERRUPTED'
    state_status = "MISSING"
    if state.exists():
        state_status = "INCOMPLETE"
        try:
            project_manifest = json.loads((state / "Project-Manifest.json").read_text(encoding="utf-8"))
            state_manifest = json.loads((state / "State-Manifest.json").read_text(encoding="utf-8"))
            if (not isinstance(project_manifest, dict) or not isinstance(state_manifest, dict)
                    or not project_manifest.get("project_id")
                    or project_manifest.get("state_root_name") != STATE_ROOT_NAME
                    or project_manifest.get("project_id") != state_manifest.get("project_id")):
                raise ValueError("inconsistent state")
            version = state_manifest.get("schema_version")
            state_status = "READY" if version == "1.1" else ("LEGACY" if version == "1.0" else "UNSUPPORTED_VERSION")
        except FileNotFoundError:
            pass
        except (OSError, ValueError, TypeError):
            state_status = "INVALID"
    try:
        prompt = hook_status(root)[0] if git == 'READY' and firg.exists() else 'UNAVAILABLE'
    except (OSError, StateError):
        prompt = 'UNAVAILABLE'
    return {"git": "DECLINED" if git == "MISSING" and preferences.get("git") is False else git,
            "git_version": installed_git_version, "git_version_status": version_status,
            "git_distribution": distribution,
            "firg": firg_state, "shared_state": state_status, "commit_prompt": prompt, "preferences": preferences}


def initialize_git(path: Path) -> None:
    root = _root(path)
    status = git_status(root)
    if status == "READY":
        return
    if status != "MISSING":
        raise StateError("GIT_REPOSITORY_CONFLICT")
    result = _git(root, "init")
    if result.returncode or git_status(root) != "READY":
        raise StateError("GIT_INITIALIZATION_FAILED")


def install_firg(path: Path) -> None:
    root = _root(path)
    if git_status(root) != "READY":
        raise StateError("FIRG_REQUIRES_GIT")
    destination = root / "FIRG"
    instructions = root / "AGENTS.md"
    if instructions.is_symlink() or (instructions.exists() and not instructions.resolve().is_relative_to(root)):
        raise StateError("ROOT_AGENTS_UNSAFE")
    if any(root.glob("AGENTS.*.md")):
        raise StateError("TRANSLATED_AGENTS_REVIEW_REQUIRED")
    files = sorted(p for p in TEMPLATE.rglob("*") if p.is_file() and "__pycache__" not in p.parts)
    if not files:
        raise StateError("FIRG_TEMPLATE_MISSING")
    payloads = {p.relative_to(TEMPLATE).as_posix(): p.read_bytes() for p in files}
    all_hashes = {name: hashlib.sha256(data).hexdigest() for name, data in payloads.items()}
    pending = destination / 'aipm-install.pending.json'
    current = instructions.read_bytes() if instructions.exists() else None
    if destination.exists():
        if not destination.resolve().is_relative_to(root) or pending.is_symlink() or not pending.is_file():
            raise StateError("FIRG_ALREADY_EXISTS")
        try:
            intent = json.loads(pending.read_text(encoding='utf-8'))
        except (OSError, ValueError) as exc:
            raise StateError('FIRG_INSTALL_JOURNAL_INVALID') from exc
        if not isinstance(intent, dict) or intent.get('version') != VERSION or intent.get('files') != all_hashes:
            raise StateError('FIRG_INSTALL_JOURNAL_CONFLICT')
        before_hash, after_hash = intent.get('before'), intent.get('after')
        if before_hash is not None and not isinstance(before_hash, str):
            raise StateError('FIRG_INSTALL_JOURNAL_INVALID')
        if not isinstance(after_hash, str):
            raise StateError('FIRG_INSTALL_JOURNAL_INVALID')
    else:
        if current is not None:
            try:
                text = current.decode('utf-8')
            except UnicodeError as exc:
                raise StateError('ROOT_AGENTS_ENCODING_UNSUPPORTED') from exc
            if 'file metadata:' in text.casefold():
                raise StateError('ROOT_AGENTS_METADATA_REVIEW_REQUIRED')
            if 'firg' in text.casefold():
                raise StateError('ROOT_AGENTS_FIRG_REVIEW_REQUIRED')
        before_hash = hashlib.sha256(current).hexdigest() if current is not None else None
        final = (current + RULE.encode('utf-8')) if current is not None else ('# Project Agent Instructions\n' + RULE).encode('utf-8')
        after_hash = hashlib.sha256(final).hexdigest()
        intent = {'version': VERSION, 'files': all_hashes, 'before': before_hash, 'after': after_hash}
        destination.mkdir()
        with pending.open('x', encoding='utf-8', newline='\n') as out:
            json.dump(intent, out, indent=2); out.flush(); os.fsync(out.fileno())
    current_hash = hashlib.sha256(current).hexdigest() if current is not None else None
    if current_hash not in (before_hash, after_hash):
        raise StateError('ROOT_AGENTS_CHANGED_DURING_INSTALL')
    if current_hash != after_hash:
        expected_rules = (current + RULE.encode('utf-8')) if current is not None else ('# Project Agent Instructions\n' + RULE).encode('utf-8')
        if hashlib.sha256(expected_rules).hexdigest() != after_hash:
            raise StateError('FIRG_INSTALL_JOURNAL_CONFLICT')
    for name, payload in payloads.items():
        target = destination / name
        if target.is_symlink() or not target.resolve().is_relative_to(destination.resolve()):
            raise StateError('FIRG_INSTALL_PATH_UNSAFE: ' + name)
        if target.exists():
            if not target.is_file() or hashlib.sha256(target.read_bytes()).hexdigest() != all_hashes[name]:
                raise StateError('FIRG_INSTALL_LOCAL_MODIFICATION: ' + name)
        else:
            target.parent.mkdir(parents=True, exist_ok=True)
            with target.open('xb') as out:
                out.write(payload)
    if current_hash != after_hash:
        if current is None:
            with instructions.open('xb') as out:
                out.write(('# Project Agent Instructions\n' + RULE).encode('utf-8'))
        else:
            with instructions.open('r+b') as out:
                if hashlib.sha256(out.read()).hexdigest() != before_hash:
                    raise StateError('ROOT_AGENTS_CHANGED_DURING_INSTALL')
                out.write(RULE.encode('utf-8'))
    hashes = {name: digest for name, digest in all_hashes.items() if name not in ('FIX-HISTORY.md', 'config.json')}
    marker = destination / 'aipm-install.json'
    expected = {'version': VERSION, 'files': hashes, 'rule': RULE}
    if marker.exists():
        if marker.is_symlink() or json.loads(marker.read_text(encoding='utf-8')) != expected:
            raise StateError('FIRG_INSTALL_MARKER_CONFLICT')
    else:
        with marker.open('x', encoding='utf-8', newline='\n') as out:
            json.dump(expected, out, indent=2); out.flush(); os.fsync(out.fileno())
    pending.unlink()
    try:
        install_firg_hook(root)
    except (OSError, StateError):
        # FIRG is installed; the UI reports hook status separately.
        pass


def save_preferences(path: Path, *, git: bool | None, firg: bool | None) -> None:
    root = _root(path)
    state = root / STATE_ROOT_NAME
    if not (state / "Project-Manifest.json").is_file():
        raise StateError("PROJECT_STATE_REQUIRED")
    if not state.resolve().is_relative_to(root):
        raise StateError("PROJECT_STATE_OUTSIDE_ROOT")
    target = state / PREFERENCES
    if target.is_symlink():
        raise StateError("PREFERENCES_UNSAFE")
    data = {"schema_version": PREFERENCES_VERSION}
    original = None
    if target.exists():
        try:
            original = target.read_bytes()
            data = json.loads(original.decode("utf-8"))
            if not isinstance(data, dict) or data.get("schema_version") != PREFERENCES_VERSION:
                raise ValueError("invalid preferences")
        except (OSError, ValueError) as exc:
            raise StateError("INVALID_COMPONENT_PREFERENCES") from exc
    data.update(git=git, firg=firg)
    _write_json_safely(target, data, original)


def repair_firg_rule(path: Path) -> None:
    """Restore a missing, unambiguous root rule without replacing owner text."""
    root = _root(path)
    if git_status(root) != 'READY':
        raise StateError('FIRG_REQUIRES_GIT')
    if inspect_project(root)['firg'] != 'ROOT_RULE_REVIEW_REQUIRED':
        raise StateError('ROOT_RULE_REPAIR_NOT_APPLICABLE')
    if any(root.glob('AGENTS.*.md')):
        raise StateError('TRANSLATED_AGENTS_REVIEW_REQUIRED')
    marker = json.loads((root / 'FIRG' / 'aipm-install.json').read_text(encoding='utf-8'))
    if marker.get('version') != VERSION or marker.get('rule') != RULE:
        raise StateError('ROOT_AGENTS_REVIEW_REQUIRED')
    instructions = root / 'AGENTS.md'
    if instructions.is_symlink() or not instructions.resolve().is_relative_to(root):
        raise StateError('ROOT_AGENTS_UNSAFE')
    if not instructions.exists():
        with instructions.open('xb') as out:
            out.write(('# Project Agent Instructions\n' + RULE).encode('utf-8'))
        return
    original = instructions.read_bytes()
    try:
        text = original.decode('utf-8')
    except UnicodeError as exc:
        raise StateError('ROOT_AGENTS_ENCODING_UNSUPPORTED') from exc
    if 'file metadata:' in text.casefold() or 'firg' in text.casefold():
        raise StateError('ROOT_AGENTS_REVIEW_REQUIRED')
    with instructions.open('r+b') as out:
        if out.read() != original:
            raise StateError('ROOT_AGENTS_CHANGED_DURING_INSTALL')
        out.write(RULE.encode('utf-8'))


def repair_firg_files(path: Path) -> None:
    """Restore missing managed template files, never overwrite project data."""
    root = _root(path)
    if git_status(root) != 'READY':
        raise StateError('FIRG_REQUIRES_GIT')
    firg = root / 'FIRG'
    marker = firg / 'aipm-install.json'
    if (not firg.is_dir() or firg.is_symlink() or not firg.resolve().is_relative_to(root)
            or marker.is_symlink() or not marker.is_file()):
        raise StateError('MANAGED_FIRG_REQUIRED')
    try:
        metadata = json.loads(marker.read_text(encoding='utf-8'))
        files = metadata['files']
        if metadata.get('version') != VERSION or not isinstance(files, dict) or not files:
            raise StateError('FIRG_VERSION_REVIEW_REQUIRED')
        config_path = firg / 'config.json'
        if config_path.is_symlink() or not config_path.is_file() or not config_path.resolve().is_relative_to(firg.resolve()):
            raise StateError('FIRG_CONFIG_REVIEW_REQUIRED')
        missing = []
        for name, digest in files.items():
            if not isinstance(name, str) or not isinstance(digest, str):
                raise StateError('FIRG_INSTALL_MARKER_INVALID')
            relative = Path(name)
            target = firg / relative
            source = TEMPLATE / relative
            if relative.is_absolute() or '..' in relative.parts or target.is_symlink() or not target.resolve().is_relative_to(firg.resolve()):
                raise StateError('FIRG_REPAIR_PATH_UNSAFE')
            if not target.exists():
                if not source.is_file() or hashlib.sha256(source.read_bytes()).hexdigest() != digest:
                    raise StateError('FIRG_REPAIR_BASELINE_UNAVAILABLE: ' + name)
                missing.append((target, source.read_bytes()))
            elif not target.is_file():
                raise StateError('FIRG_REPAIR_PATH_CONFLICT: ' + name)
        ledger = firg / 'FIX-HISTORY.md'
        if ledger.is_symlink() or not ledger.resolve().is_relative_to(firg.resolve()):
            raise StateError('FIRG_REPAIR_PATH_UNSAFE')
        if not ledger.exists():
            registry = firg / 'registry'
            if registry.is_symlink() or not registry.resolve().is_relative_to(firg.resolve()):
                raise StateError('FIRG_REPAIR_PATH_UNSAFE')
            if registry.exists() and any(registry.iterdir()):
                raise StateError('FIRG_LEDGER_REGENERATION_REQUIRED')
            missing.append((ledger, (TEMPLATE / 'FIX-HISTORY.md').read_bytes()))
        elif not ledger.is_file():
            raise StateError('FIRG_REPAIR_PATH_CONFLICT: FIX-HISTORY.md')
        for target, payload in missing:
            target.parent.mkdir(parents=True, exist_ok=True)
            with target.open('xb') as out:
                out.write(payload)
    except (OSError, ValueError, KeyError, TypeError, AttributeError) as exc:
        if isinstance(exc, StateError):
            raise
        raise StateError('FIRG_REPAIR_FAILED: ' + str(exc)) from exc


def update_firg(path: Path) -> None:
    """Upgrade only files whose installed content matches the recorded baseline."""
    root = _root(path)
    if git_status(root) != "READY":
        raise StateError("FIRG_REQUIRES_GIT")
    firg = root / "FIRG"
    marker = firg / "aipm-install.json"
    state = root / STATE_ROOT_NAME
    scratch = state / "Temporary-Files"
    if not scratch.is_dir() or not marker.is_file():
        raise StateError("MANAGED_FIRG_AND_STATE_REQUIRED")
    if (not firg.resolve().is_relative_to(root) or not state.resolve().is_relative_to(root)
            or not scratch.resolve().is_relative_to(state.resolve())):
        raise StateError("FIRG_PATH_OUTSIDE_PROJECT")
    try:
        marker_original = marker.read_bytes()
        old = json.loads(marker_original.decode("utf-8"))
        if not isinstance(old, dict) or type(old.get("version")) is not int or not isinstance(old.get("files"), dict) or not old['files']:
            raise ValueError("invalid marker")
        sources = {p.relative_to(TEMPLATE).as_posix(): p for p in TEMPLATE.rglob('*')
                   if p.is_file() and '__pycache__' not in p.parts
                   and p.relative_to(TEMPLATE).as_posix() not in ('FIX-HISTORY.md', 'config.json')}
        desired = {name: hashlib.sha256(source.read_bytes()).hexdigest() for name, source in sources.items()}
        journal = state / 'Tool-State' / 'FIRG-Update.json'
        if not journal.resolve().is_relative_to(state.resolve()) or journal.is_symlink():
            raise StateError('FIRG_UPDATE_JOURNAL_UNSAFE')
        intent = json.loads(journal.read_text(encoding='utf-8')) if journal.exists() else None
        if intent is not None and (not isinstance(intent, dict) or intent.get('version') != VERSION or intent.get('targets') != desired):
            raise StateError('FIRG_UPDATE_JOURNAL_CONFLICT')
        if intent is not None and intent.get('rule_sha256') != hashlib.sha256(RULE.encode('utf-8')).hexdigest():
            raise StateError('FIRG_UPDATE_JOURNAL_CONFLICT')
        rules_path = root / 'AGENTS.md'
        if rules_path.is_symlink() or not rules_path.is_file() or not rules_path.resolve().is_relative_to(root):
            raise StateError('ROOT_AGENTS_REVIEW_REQUIRED')
        current_rules = rules_path.read_bytes()
        if old["version"] >= VERSION:
            if intent is not None and old['version'] == VERSION and hashlib.sha256(current_rules).hexdigest() == intent.get('rules_after') and all(old['files'].get(n) == h and (firg / n).is_file() and hashlib.sha256((firg / n).read_bytes()).hexdigest() == h for n, h in desired.items()):
                journal.unlink()
                return
            raise StateError("FIRG_UPDATE_NOT_AVAILABLE")
        if intent is not None and intent.get('marker_sha256') != hashlib.sha256(marker_original).hexdigest():
            raise StateError('FIRG_UPDATE_JOURNAL_CONFLICT')
        old_rule = old.get('rule')
        if old_rule is None:
            if _rule_variant(current_rules, RULE) is None:
                raise StateError('ROOT_AGENTS_REVIEW_REQUIRED')
            old_rule = RULE
        if not isinstance(old_rule, str) or not old_rule.startswith('\n\n## Mandatory FIRG Pre-Read'):
            raise StateError('ROOT_AGENTS_REVIEW_REQUIRED')
        if intent is None:
            if _rule_variant(current_rules, old_rule) is None:
                raise StateError('ROOT_AGENTS_REVIEW_REQUIRED')
            if old_rule != RULE and (any(root.glob('AGENTS.*.md')) or b'file metadata:' in current_rules.lower()):
                raise StateError('ROOT_AGENTS_REVIEW_REQUIRED')
            updated_rules = _replace_rule(current_rules, old_rule)
        else:
            current_hash = hashlib.sha256(current_rules).hexdigest()
            if current_hash not in (intent.get('rules_before'), intent.get('rules_after')):
                raise StateError('ROOT_AGENTS_CHANGED_DURING_UPDATE')
            updated_rules = None
        previous = old["files"]
        for name, digest in previous.items():
            if not isinstance(name, str) or not isinstance(digest, str):
                raise ValueError("invalid marker entry")
            relative = Path(name)
            if relative.is_absolute() or ".." in relative.parts or (firg / relative).is_symlink():
                raise ValueError("unsafe marker path")
            candidate = firg / relative
            if not candidate.is_file() or not candidate.resolve().is_relative_to(firg.resolve()):
                raise StateError("FIRG_FILE_MISSING_OR_UNSAFE: " + name)
            current = hashlib.sha256(candidate.read_bytes()).hexdigest()
            if current != digest and not (intent is not None and desired.get(name) == current):
                raise StateError("FIRG_LOCAL_MODIFICATION: " + name)
        for name in sources:
            candidate = firg / name
            if not candidate.resolve().is_relative_to(firg.resolve()):
                raise StateError("FIRG_FILE_MISSING_OR_UNSAFE: " + name)
            if name not in previous and candidate.exists() and not (intent is not None and candidate.is_file() and hashlib.sha256(candidate.read_bytes()).hexdigest() == desired[name]):
                raise StateError("FIRG_UNMANAGED_FILE_CONFLICT: " + name)
        backup = state / 'History' / 'FIRG-Updates'
        if not backup.resolve().is_relative_to(state.resolve()):
            raise StateError("FIRG_BACKUP_OUTSIDE_STATE")
        if intent is None:
            backup.mkdir(parents=True, exist_ok=True)
            from uuid import uuid4
            backup = backup / uuid4().hex
            backup.mkdir()
            (backup / 'aipm-install.json').write_bytes(marker_original)
            (backup / 'Root-AGENTS.md').write_bytes(current_rules)
            for name in previous:
                saved = backup / name
                saved.parent.mkdir(parents=True, exist_ok=True)
                saved.write_bytes((firg / name).read_bytes())
            intent = {'version': VERSION, 'marker_sha256': hashlib.sha256(marker_original).hexdigest(),
                      'targets': desired, 'backup': backup.relative_to(state).as_posix(),
                      'rule_sha256': hashlib.sha256(RULE.encode('utf-8')).hexdigest(),
                      'rules_before': hashlib.sha256(current_rules).hexdigest(),
                      'rules_after': hashlib.sha256(updated_rules).hexdigest()}
            journal.parent.mkdir(parents=True, exist_ok=True)
            _write_json_safely(journal, intent, None)
        else:
            relative_backup = Path(intent.get('backup', ''))
            if relative_backup.is_absolute() or '..' in relative_backup.parts:
                raise StateError('FIRG_UPDATE_BACKUP_INVALID')
            backup = state / relative_backup
            if not backup.resolve().is_relative_to((state / 'History' / 'FIRG-Updates').resolve()) or not (backup / 'aipm-install.json').is_file():
                raise StateError('FIRG_UPDATE_BACKUP_INVALID')
            if hashlib.sha256((backup / 'aipm-install.json').read_bytes()).hexdigest() != intent['marker_sha256']:
                raise StateError('FIRG_UPDATE_BACKUP_INVALID')
            saved_rules = (backup / 'Root-AGENTS.md').read_bytes()
            if hashlib.sha256(saved_rules).hexdigest() != intent.get('rules_before'):
                raise StateError('FIRG_UPDATE_BACKUP_INVALID')
            updated_rules = _replace_rule(saved_rules, old_rule)
            if hashlib.sha256(updated_rules).hexdigest() != intent.get('rules_after'):
                raise StateError('FIRG_UPDATE_JOURNAL_CONFLICT')
            for name, digest in previous.items():
                saved = backup / name
                if not saved.is_file() or hashlib.sha256(saved.read_bytes()).hexdigest() != digest:
                    raise StateError('FIRG_UPDATE_BACKUP_INVALID')
        hashes = dict(previous)
        for name, source in sources.items():
            target = firg / name
            target.parent.mkdir(parents=True, exist_ok=True)
            payload = source.read_bytes()
            if target.is_file() and hashlib.sha256(target.read_bytes()).hexdigest() == desired[name]:
                hashes[name] = desired[name]
                continue
            if name in previous and hashlib.sha256(target.read_bytes()).hexdigest() != previous[name]:
                raise StateError("FIRG_CHANGED_DURING_UPDATE: " + name)
            if name not in previous:
                with target.open('xb') as out:
                    out.write(payload)
            else:
                temporary = None
                try:
                    with tempfile.NamedTemporaryFile(dir=scratch, delete=False) as out:
                        temporary = Path(out.name)
                        out.write(payload); out.flush(); os.fsync(out.fileno())
                    _replace_preserving_permissions(temporary, target)
                finally:
                    if temporary is not None:
                        temporary.unlink(missing_ok=True)
            hashes[name] = hashlib.sha256(payload).hexdigest()
        if hashlib.sha256(current_rules).hexdigest() != intent['rules_after']:
            if hashlib.sha256(rules_path.read_bytes()).hexdigest() != intent['rules_before']:
                raise StateError('ROOT_AGENTS_CHANGED_DURING_UPDATE')
            temporary = None
            try:
                with tempfile.NamedTemporaryFile(dir=scratch, delete=False) as out:
                    temporary = Path(out.name)
                    out.write(updated_rules); out.flush(); os.fsync(out.fileno())
                _replace_preserving_permissions(temporary, rules_path)
            finally:
                if temporary is not None:
                    temporary.unlink(missing_ok=True)
        new_marker = dict(old)
        new_marker.update(version=VERSION, files=hashes, rule=RULE)
        _write_json_safely(marker, new_marker, marker_original)
        journal.unlink()
    except (OSError, ValueError, KeyError, TypeError) as exc:
        if isinstance(exc, StateError):
            raise
        raise StateError("FIRG_UPDATE_FAILED: " + str(exc)) from exc
