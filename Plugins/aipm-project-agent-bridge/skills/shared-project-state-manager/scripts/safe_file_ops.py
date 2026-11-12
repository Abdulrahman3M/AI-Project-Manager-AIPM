#!/usr/bin/env python3
"""Safe project-local file operations for Shared Project State Manager.

The tool prefers diagnosis, quarantine, and reversible moves. It never self-elevates,
force-closes other processes, takes ownership, or disables OS security controls.
Windows ACL reset is available only as an explicit, confirmed, project-scoped action.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
import re
import stat
import subprocess
import sys
import time
import uuid
from functools import wraps
from datetime import datetime, timezone
from pathlib import Path

STATE_ROOT = "Shared-Project-State"
PROTECTED_COMPONENTS = {".git", ".agents", ".codex", "shared-project-state", "shared-project-state-manager"}
_spec = importlib.util.spec_from_file_location("_aipm_safe_move", Path(__file__).with_name("safe_move.py"))
if _spec is None or _spec.loader is None:
    raise RuntimeError("Safe move helper is unavailable")
_safe_move = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_safe_move)
move_noreplace = _safe_move.move_noreplace


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def die(message: str, code: int = 1) -> "NoReturn":
    print(f"ERROR: {message}", file=sys.stderr)
    raise SystemExit(code)


def reject_link(path: Path) -> None:
    try:
        metadata = path.lstat()
    except FileNotFoundError:
        return
    except OSError as exc:
        die(f"Cannot inspect path safely: {exc}")
    if stat.S_ISLNK(metadata.st_mode) or getattr(metadata, "st_file_attributes", 0) & getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0x400):
        die(f"Linked or reparse-point path is not allowed: {path}")


def resolve_project_root(value: str) -> Path:
    raw = Path(value).expanduser().absolute()
    for part in (*reversed(raw.parents), raw):
        reject_link(part)
    root = raw.resolve()
    if not root.exists() or not root.is_dir():
        die(f"Project root does not exist: {root}")
    return root


def resolve_scoped(root: Path, value: str, *, must_exist: bool = True) -> Path:
    p = Path(value).expanduser()
    if not p.is_absolute():
        p = root / p
    try:
        relative = p.relative_to(root)
    except ValueError:
        die(f"Path escapes project root: {p}")
    if any(part in (".", "..") for part in relative.parts):
        die("Path traversal is not allowed.")
    current = root
    for part in relative.parts:
        current = current / part
        reject_link(current)
    p = p.resolve(strict=False)
    try:
        p.relative_to(root)
    except ValueError:
        die(f"Path escapes project root: {p}")
    if must_exist and not p.exists():
        die(f"Path does not exist: {p}")
    return p


def protected_path(root: Path, path: Path) -> bool:
    relative = path.relative_to(root)
    return not relative.parts or any(part.casefold() in PROTECTED_COMPONENTS for part in relative.parts)


def is_readonly(path: Path) -> bool:
    try:
        mode = path.stat().st_mode
        return not bool(mode & stat.S_IWUSR)
    except OSError:
        return False


def diagnostics(path: Path) -> dict:
    data = {
        "path": str(path),
        "exists": path.exists(),
        "is_file": path.is_file() if path.exists() else False,
        "is_dir": path.is_dir() if path.exists() else False,
        "is_symlink": path.is_symlink(),
        "readable": os.access(path, os.R_OK) if path.exists() else False,
        "writable": os.access(path, os.W_OK) if path.exists() else False,
        "executable": os.access(path, os.X_OK) if path.exists() else False,
        "readonly_attribute_like": is_readonly(path) if path.exists() else False,
        "platform": sys.platform,
    }
    if path.exists():
        try:
            st = path.stat()
            data.update({"mode_octal": oct(stat.S_IMODE(st.st_mode)), "size": st.st_size})
        except OSError as exc:
            data["stat_error"] = str(exc)
    if os.name == "nt" and path.exists():
        try:
            cp = subprocess.run(["icacls", str(path)], capture_output=True, text=True, timeout=15)
            data["icacls_exit"] = cp.returncode
            data["icacls"] = (cp.stdout or cp.stderr).strip()
        except Exception as exc:  # diagnostic only
            data["icacls_error"] = str(exc)
    return data


def clear_readonly(path: Path, recursive: bool = True) -> int:
    return _safe_move.clear_readonly_nofollow(path, recursive, PROTECTED_COMPONENTS)


def retry(operation, seconds: float):
    deadline = time.monotonic() + max(0.0, seconds)
    last = None
    while True:
        try:
            return operation()
        except (PermissionError, OSError) as exc:
            last = exc
            if time.monotonic() >= deadline:
                raise last
            time.sleep(min(0.5, max(0.05, deadline - time.monotonic())))


def unique_quarantine_path(root: Path, source: Path) -> tuple[Path, Path]:
    qroot = root / STATE_ROOT / "Quarantine"
    items = qroot / "Items"
    records = qroot / "Records"
    token = f"{datetime.now().strftime('%Y%m%d-%H%M%S')}-{uuid.uuid4().hex[:8]}"
    path_digest = hashlib.sha256(str(source.relative_to(root)).encode("utf-8")).hexdigest()
    dest = items / f"{token}-{path_digest}"
    record = records / f"{token}.json"
    return dest, record


def record_bytes(payload: dict) -> bytes:
    return (json.dumps(payload, indent=2) + "\n").encode("utf-8")


def cmd_diagnose(args) -> int:
    root = resolve_project_root(args.project_root)
    target = resolve_scoped(root, args.path, must_exist=False)
    print(json.dumps(diagnostics(target), indent=2))
    return 0


def cmd_clear_readonly(args) -> int:
    root = resolve_project_root(args.project_root)
    target = resolve_scoped(root, args.path)
    if protected_path(root, target):
        die("Protected project metadata and state paths cannot be modified.")
    if args.confirm != "CLEAR-READONLY":
        die("clear-readonly requires --confirm CLEAR-READONLY")
    if args.dry_run:
        print(f"DRY-RUN: would clear user read-only bits under {target}")
        return 0
    count = clear_readonly(target, recursive=not args.no_recursive)
    print(f"Cleared read-only bit on {count} item(s).")
    return 0


def cmd_move(args) -> int:
    root = resolve_project_root(args.project_root)
    src = resolve_scoped(root, args.source)
    identity = src.lstat()
    dst = resolve_scoped(root, args.destination, must_exist=False)
    if protected_path(root, src) or protected_path(root, dst):
        die("Protected project metadata and state paths cannot be moved.")
    if dst.exists():
        die(f"Destination already exists; refusing overwrite: {dst}")
    if args.dry_run:
        print(f"DRY-RUN: would move {src} -> {dst}")
        return 0
    try:
        _safe_move.ensure_directory(dst.parent)
        retry(lambda: move_noreplace(src, dst, identity), args.retry_seconds)
    except Exception as exc:
        print(json.dumps({"error": str(exc), "source": str(src), "destination": str(dst)}, indent=2), file=sys.stderr)
        return 3
    print(f"Moved: {src} -> {dst}")
    return 0


def cmd_quarantine(args) -> int:
    root = resolve_project_root(args.project_root)
    src = resolve_scoped(root, args.path)
    identity = src.lstat()
    if protected_path(root, src):
        die("Protected project metadata and state paths cannot be quarantined.")
    dst, record = unique_quarantine_path(root, src)
    payload = {
        "schema_version": "1.1",
        "operation": "quarantine",
        "created_at": utc_now(),
        "original_path": str(src.relative_to(root)),
        "quarantined_path": str(dst.relative_to(root)),
        "restored": False,
        "purged": False,
    }
    if args.dry_run:
        print(json.dumps({"dry_run": True, **payload}, indent=2))
        return 0
    resolve_scoped(root, str(dst), must_exist=False)
    resolve_scoped(root, str(record), must_exist=False)
    try:
        _safe_move.ensure_directory(dst.parent)
        _safe_move.ensure_directory(record.parent)
        resolve_scoped(root, str(dst), must_exist=False)
        resolve_scoped(root, str(record), must_exist=False)
        with _safe_move.locked_record(record, create=True) as locked:
            locked.write(record_bytes(payload))
            retry(lambda: move_noreplace(src, dst, identity), args.retry_seconds)
    except Exception as exc:
        print(json.dumps({"error": str(exc), "source": str(src), "destination": str(dst), "record": str(record)}, indent=2), file=sys.stderr)
        return 3
    print(json.dumps({"status": "QUARANTINED", "record": str(record), **payload}, indent=2))
    return 0


def load_record(root: Path, value: str, raw: bytes) -> tuple[Path, dict]:
    record = resolve_scoped(root, value)
    records = root / STATE_ROOT / "Quarantine" / "Records"
    if record.parent != records or record.suffix.lower() != ".json" or not record.is_file():
        die("Record must be a quarantine JSON record.")
    try:
        data = json.loads(raw.decode("utf-8"))
    except Exception as exc:
        die(f"Invalid quarantine record: {exc}")
    if isinstance(data, dict) and data.get("schema_version") == "1.0":
        die("Legacy quarantine record requires manual review; no files were changed.")
    if (not isinstance(data, dict) or data.get("schema_version") not in ("1.0", "1.1")
            or data.get("operation") != "quarantine" or data.get("restored") is not False
            or data.get("purged") is not False or "error" in data):
        die("Invalid or already completed quarantine record.")
    if not isinstance(data.get("created_at"), str):
        die("Invalid quarantine record timestamp.")
    try:
        datetime.fromisoformat(data["created_at"])
    except ValueError:
        die("Invalid quarantine record timestamp.")
    token = record.stem
    if not re.fullmatch(r"\d{8}-\d{6}-[0-9a-f]{8}", token):
        die("Invalid quarantine record identifier.")
    original = data.get("original_path")
    quarantined = data.get("quarantined_path")
    if not isinstance(original, str) or not original or not isinstance(quarantined, str) or not quarantined:
        die("Invalid quarantine record paths.")
    if Path(original).is_absolute() or Path(quarantined).is_absolute():
        die("Quarantine record paths must be relative.")
    destination = resolve_scoped(root, original, must_exist=False)
    source = resolve_scoped(root, quarantined, must_exist=False)
    items = root / STATE_ROOT / "Quarantine" / "Items"
    path_digest = hashlib.sha256(str(destination.relative_to(root)).encode("utf-8")).hexdigest()
    expected_name = f"{token}-{path_digest}"
    if (protected_path(root, destination)
            or source.parent != items or source.name != expected_name):
        die("Quarantine record paths do not match the original operation.")
    return record, data


def cmd_restore(args) -> int:
    root = resolve_project_root(args.project_root)
    record_path = resolve_scoped(root, args.record)
    backup = None
    try:
        with _safe_move.locked_record(record_path, read_only=args.dry_run) as locked:
            raw = locked.read()
            record_path, data = load_record(root, str(record_path), raw)
            src = resolve_scoped(root, data["quarantined_path"])
            identity = src.lstat()
            dst = resolve_scoped(root, data["original_path"], must_exist=False)
            if dst.exists():
                die(f"Original path is occupied; refusing overwrite: {dst}")
            if args.dry_run:
                print(f"DRY-RUN: would restore {src} -> {dst}")
                return 0
            _safe_move.ensure_directory(dst.parent)
            backup = record_path.with_name(f"{record_path.stem}.before-restore-{uuid.uuid4().hex}.json")
            with _safe_move.locked_record(backup, create=True) as previous:
                previous.write(raw)
            retry(lambda: move_noreplace(src, dst, identity), args.retry_seconds)
            data["restored"] = True
            data["restored_at"] = utc_now()
            locked.write(record_bytes(data))
    except Exception as exc:
        print(json.dumps({"error": str(exc), "record": str(record_path), "backup": str(backup) if backup else None}, indent=2), file=sys.stderr)
        return 3
    print(f"Restored: {dst}")
    return 0


def cmd_purge(args) -> int:
    root = resolve_project_root(args.project_root)
    if args.confirm != "PURGE-QUARANTINE":
        die("purge requires --confirm PURGE-QUARANTINE")
    record_path = resolve_scoped(root, args.record)
    backup = None
    try:
        with _safe_move.locked_record(record_path, read_only=args.dry_run) as locked:
            raw = locked.read()
            record_path, data = load_record(root, str(record_path), raw)
            target = resolve_scoped(root, data["quarantined_path"], must_exist=False)
            if not target.exists():
                die("Quarantined item is missing; refusing to mark it purged.")
            identity = target.lstat()
            if args.dry_run:
                print(f"DRY-RUN: would permanently delete {target}")
                return 0
            backup = record_path.with_name(f"{record_path.stem}.before-purge-{uuid.uuid4().hex}.json")
            with _safe_move.locked_record(backup, create=True) as previous:
                previous.write(raw)
            _safe_move.delete_nofollow(target, identity)
            data["purged"] = True
            data["purged_at"] = utc_now()
            locked.write(record_bytes(data))
    except Exception as exc:
        print(json.dumps({"error": str(exc), "record": str(record_path), "backup": str(backup) if backup else None}, indent=2), file=sys.stderr)
        return 3
    print(f"Purged quarantined item recorded by {record_path}")
    return 0


def cmd_repair_acl(args) -> int:
    root = resolve_project_root(args.project_root)
    target = resolve_scoped(root, args.path)
    if protected_path(root, target):
        die("Protected project metadata and state paths cannot be modified.")
    if os.name != "nt":
        die("repair-acl is Windows-only. Use native ownership/permission tools on this platform.")
    if args.confirm != "REPAIR-ACL":
        die("repair-acl requires --confirm REPAIR-ACL")
    cmd = ["icacls", str(target), "/inheritance:e", "/reset"]
    if target.is_dir() and not args.no_recursive:
        cmd.extend(["/T", "/C"])
    if args.dry_run:
        print("DRY-RUN:", subprocess.list2cmdline(cmd))
        return 0
    cp = subprocess.run(cmd, capture_output=True, text=True)
    print(cp.stdout or cp.stderr)
    if cp.returncode != 0:
        print("ACL repair failed. The tool does not self-elevate or take ownership. If this project is yours and policy allows it, rerun the same command from an elevated PowerShell window.", file=sys.stderr)
    return cp.returncode


def _hold_project_root(operation):
    """Keep the inspected Windows root stable through each modifying operation."""
    @wraps(operation)
    def guarded(args):
        if os.name != "nt" or args.dry_run:
            return operation(args)
        root = resolve_project_root(args.project_root)
        expected = root.lstat()
        with _safe_move.locked_directories(root):
            actual = root.lstat()
            if not expected.st_ino or (expected.st_dev, expected.st_ino) != (actual.st_dev, actual.st_ino):
                die("Project root identity changed during preflight.")
            return operation(args)
    return guarded


cmd_clear_readonly = _hold_project_root(cmd_clear_readonly)
cmd_move = _hold_project_root(cmd_move)
cmd_quarantine = _hold_project_root(cmd_quarantine)
cmd_restore = _hold_project_root(cmd_restore)
cmd_purge = _hold_project_root(cmd_purge)


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Safe project-local file operations for Shared Project State Manager")
    sub = p.add_subparsers(dest="command", required=True)

    def scoped(sp):
        sp.add_argument("--project-root", default=".", help="Project root; all operated paths must remain inside it")
        sp.add_argument("--dry-run", action="store_true")
        sp.add_argument("--retry-seconds", type=float, default=0.0, help="Retry PermissionError/OSError for this many seconds")

    s = sub.add_parser("diagnose")
    s.add_argument("path")
    s.add_argument("--project-root", default=".")
    s.set_defaults(func=cmd_diagnose)

    s = sub.add_parser("clear-readonly")
    s.add_argument("path")
    scoped(s)
    s.add_argument("--confirm")
    s.add_argument("--no-recursive", action="store_true")
    s.set_defaults(func=cmd_clear_readonly)

    s = sub.add_parser("move")
    s.add_argument("source")
    s.add_argument("destination")
    scoped(s)
    s.set_defaults(func=cmd_move)

    s = sub.add_parser("quarantine")
    s.add_argument("path")
    scoped(s)
    s.set_defaults(func=cmd_quarantine)

    s = sub.add_parser("restore")
    s.add_argument("record")
    scoped(s)
    s.set_defaults(func=cmd_restore)

    s = sub.add_parser("purge")
    s.add_argument("record")
    scoped(s)
    s.add_argument("--confirm")
    s.set_defaults(func=cmd_purge)

    s = sub.add_parser("repair-acl")
    s.add_argument("path")
    scoped(s)
    s.add_argument("--confirm")
    s.add_argument("--no-recursive", action="store_true")
    s.set_defaults(func=cmd_repair_acl)
    return p


def main() -> int:
    args = build_parser().parse_args()
    return int(args.func(args) or 0)


if __name__ == "__main__":
    raise SystemExit(main())
