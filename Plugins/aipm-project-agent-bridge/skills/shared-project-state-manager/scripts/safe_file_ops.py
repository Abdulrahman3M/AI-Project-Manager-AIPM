#!/usr/bin/env python3
"""Safe project-local file operations for Shared Project State Manager.

The tool prefers diagnosis, quarantine, and reversible moves. It never self-elevates,
force-closes other processes, takes ownership, or disables OS security controls.
Windows ACL reset is available only as an explicit, confirmed, project-scoped action.
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import stat
import subprocess
import sys
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path

STATE_ROOT = "Shared-Project-State"


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def die(message: str, code: int = 1) -> "NoReturn":
    print(f"ERROR: {message}", file=sys.stderr)
    raise SystemExit(code)


def resolve_project_root(value: str) -> Path:
    root = Path(value).expanduser().resolve()
    if not root.exists() or not root.is_dir():
        die(f"Project root does not exist: {root}")
    return root


def resolve_scoped(root: Path, value: str, *, must_exist: bool = True) -> Path:
    p = Path(value).expanduser()
    if not p.is_absolute():
        p = root / p
    p = p.resolve(strict=False)
    try:
        p.relative_to(root)
    except ValueError:
        die(f"Path escapes project root: {p}")
    if must_exist and not p.exists():
        die(f"Path does not exist: {p}")
    return p


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
    changed = 0
    targets = [path]
    if recursive and path.is_dir():
        targets.extend(path.rglob("*"))
    for item in targets:
        try:
            mode = item.stat().st_mode
            if not mode & stat.S_IWUSR:
                item.chmod(mode | stat.S_IWUSR)
                changed += 1
        except OSError:
            continue
    return changed


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
    items.mkdir(parents=True, exist_ok=True)
    records.mkdir(parents=True, exist_ok=True)
    token = f"{datetime.now().strftime('%Y%m%d-%H%M%S')}-{uuid.uuid4().hex[:8]}"
    dest = items / f"{token}-{source.name}"
    record = records / f"{token}.json"
    return dest, record


def write_record(record: Path, payload: dict) -> None:
    record.parent.mkdir(parents=True, exist_ok=True)
    record.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def cmd_diagnose(args) -> int:
    root = resolve_project_root(args.project_root)
    target = resolve_scoped(root, args.path, must_exist=False)
    print(json.dumps(diagnostics(target), indent=2))
    return 0


def cmd_clear_readonly(args) -> int:
    root = resolve_project_root(args.project_root)
    target = resolve_scoped(root, args.path)
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
    dst = resolve_scoped(root, args.destination, must_exist=False)
    if dst.exists():
        die(f"Destination already exists; refusing overwrite: {dst}")
    if args.dry_run:
        print(f"DRY-RUN: would move {src} -> {dst}")
        return 0
    dst.parent.mkdir(parents=True, exist_ok=True)
    try:
        retry(lambda: shutil.move(str(src), str(dst)), args.retry_seconds)
    except Exception as exc:
        print(json.dumps({"error": str(exc), "source": diagnostics(src), "destination_parent": diagnostics(dst.parent)}, indent=2), file=sys.stderr)
        return 3
    print(f"Moved: {src} -> {dst}")
    return 0


def cmd_quarantine(args) -> int:
    root = resolve_project_root(args.project_root)
    src = resolve_scoped(root, args.path)
    qroot = (root / STATE_ROOT / "Quarantine").resolve()
    if qroot in src.parents or src == qroot:
        die("Source is already inside the quarantine area.")
    dst, record = unique_quarantine_path(root, src)
    payload = {
        "schema_version": "1.0",
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
    try:
        retry(lambda: shutil.move(str(src), str(dst)), args.retry_seconds)
    except Exception as exc:
        payload["error"] = str(exc)
        payload["diagnostics"] = diagnostics(src)
        write_record(record, payload)
        print(json.dumps(payload, indent=2), file=sys.stderr)
        return 3
    write_record(record, payload)
    print(json.dumps({"status": "QUARANTINED", "record": str(record), **payload}, indent=2))
    return 0


def load_record(root: Path, value: str) -> tuple[Path, dict]:
    record = resolve_scoped(root, value)
    if record.suffix.lower() != ".json":
        die("Record must be a quarantine JSON record.")
    try:
        data = json.loads(record.read_text(encoding="utf-8"))
    except Exception as exc:
        die(f"Invalid quarantine record: {exc}")
    return record, data


def cmd_restore(args) -> int:
    root = resolve_project_root(args.project_root)
    record_path, data = load_record(root, args.record)
    src = resolve_scoped(root, data["quarantined_path"])
    dst = resolve_scoped(root, data["original_path"], must_exist=False)
    if dst.exists():
        die(f"Original path is occupied; refusing overwrite: {dst}")
    if args.dry_run:
        print(f"DRY-RUN: would restore {src} -> {dst}")
        return 0
    dst.parent.mkdir(parents=True, exist_ok=True)
    try:
        retry(lambda: shutil.move(str(src), str(dst)), args.retry_seconds)
    except Exception as exc:
        print(json.dumps({"error": str(exc), "source": diagnostics(src), "destination_parent": diagnostics(dst.parent)}, indent=2), file=sys.stderr)
        return 3
    data["restored"] = True
    data["restored_at"] = utc_now()
    write_record(record_path, data)
    print(f"Restored: {dst}")
    return 0


def cmd_purge(args) -> int:
    root = resolve_project_root(args.project_root)
    record_path, data = load_record(root, args.record)
    if args.confirm != "PURGE-QUARANTINE":
        die("purge requires --confirm PURGE-QUARANTINE")
    target = resolve_scoped(root, data["quarantined_path"], must_exist=False)
    qitems = (root / STATE_ROOT / "Quarantine" / "Items").resolve()
    try:
        target.relative_to(qitems)
    except ValueError:
        die("Refusing purge: target is not inside Shared-Project-State/Quarantine/Items.")
    if not target.exists():
        print("Quarantined item is already absent.")
    elif args.dry_run:
        print(f"DRY-RUN: would permanently delete {target}")
        return 0
    else:
        if target.is_dir() and not target.is_symlink():
            shutil.rmtree(target)
        else:
            target.unlink()
    data["purged"] = True
    data["purged_at"] = utc_now()
    write_record(record_path, data)
    print(f"Purged quarantined item recorded by {record_path}")
    return 0


def cmd_repair_acl(args) -> int:
    root = resolve_project_root(args.project_root)
    target = resolve_scoped(root, args.path)
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
