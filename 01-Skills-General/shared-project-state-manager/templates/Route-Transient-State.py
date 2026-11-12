#!/usr/bin/env python3
"""Route-Transient-State: Centralize and route Cache, Temporary Files, and Test Workspaces.

Enforces Section 7 of Global Agent Directives & Operating Rules:
- Cache/ (Python __pycache__, pytest, mypy, ruff, tool caches)
- Temporary-Files/ (scratch scripts, transient dumps, disposable files)
- Test-Workspace/ (test sandboxes, experimental fixtures, temporary test runs)
"""
from __future__ import annotations

import argparse
import importlib.util
import os
from pathlib import Path
import stat
import subprocess
import sys
from typing import Any

STATE_ROOT_NAME = "Shared-Project-State"
LEGACY_STATE_ROOT_NAME = "Shared-Project-State-Manager"
_spec = importlib.util.spec_from_file_location("_aipm_safe_move", Path(__file__).with_name("safe_move.py"))
if _spec is None or _spec.loader is None:
    raise RuntimeError("Safe move helper is unavailable")
_safe_move = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_safe_move)
move_noreplace = _safe_move.move_noreplace


def resolve_roots(start_path: Path | None = None) -> tuple[Path, Path]:
    """Dynamically resolve the project root and its Shared-Project-State-Manager directory."""
    if start_path is not None:
        raw = start_path.absolute()
        if any(_linked(part) for part in (*reversed(raw.parents), raw)):
            raise ValueError("Project root must not traverse a linked path.")
        current = raw.resolve()
        if not current.is_dir():
            raise ValueError("Explicit project root must be an existing directory.")
        candidates = [current / name for name in (STATE_ROOT_NAME, LEGACY_STATE_ROOT_NAME)
                      if (current / name).is_dir()]
        if len(candidates) > 1:
            raise ValueError("Both state roots exist; select and reconcile them explicitly.")
        return current, candidates[0] if candidates else current / STATE_ROOT_NAME
    else:
        # Check script location first: if script is in Shared-Project-State-Manager, anchor to its owning project
        script_parent = Path(__file__).resolve().parent
        if script_parent.name in (STATE_ROOT_NAME, LEGACY_STATE_ROOT_NAME):
            return script_parent.parent, script_parent
        current = Path.cwd().resolve()

    # Case 1: Currently inside Shared-Project-State-Manager or a subdirectory of it
    for parent in (current, *current.parents):
        if parent.name in (STATE_ROOT_NAME, LEGACY_STATE_ROOT_NAME):
            state_root = parent
            project_root = parent.parent
            return project_root, state_root

    # Case 2: Currently in project root containing Shared-Project-State-Manager
    for name in (STATE_ROOT_NAME, LEGACY_STATE_ROOT_NAME):
        candidate = current / name
        if candidate.is_dir():
            return current, candidate

    # Case 3: Search up the directory tree
    for parent in current.parents:
        for name in (STATE_ROOT_NAME, LEGACY_STATE_ROOT_NAME):
            candidate = parent / name
            if candidate.is_dir():
                return parent, candidate

    # Default fallback: create under current directory
    state_root = current / STATE_ROOT_NAME
    return current, state_root


def transient_paths(state_root: Path) -> dict[str, Path]:
    """Describe transient locations without creating them."""
    return {
        "cache": state_root / "Cache",
        "cache_python": state_root / "Cache" / "Python",
        "cache_pytest": state_root / "Cache" / "pytest",
        "cache_mypy": state_root / "Cache" / "mypy",
        "cache_ruff": state_root / "Cache" / "ruff",
        "temp": state_root / "Temporary-Files",
        "test_workspace": state_root / "Test-Workspace",
        "logs": state_root / "Logs",
        "locks": state_root / "Locks",
    }


def _linked(path: Path) -> bool:
    try:
        info = path.lstat()
    except FileNotFoundError:
        return False
    return bool(stat.S_ISLNK(info.st_mode) or getattr(info, "st_file_attributes", 0) & getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0x400))


def _safe_path(state_root: Path, path: Path) -> None:
    current = state_root
    if _linked(current):
        raise ValueError(f"Linked state root is not allowed: {current}")
    for part in path.relative_to(state_root).parts:
        current = current / part
        if _linked(current):
            raise ValueError(f"Linked transient path is not allowed: {current}")


def ensure_transient_structure(state_root: Path) -> dict[str, Path]:
    """Create transient subdirectories only in an existing state root."""
    if not state_root.is_dir():
        raise ValueError("An existing state root is required for mutation.")
    dirs = transient_paths(state_root)
    for directory in dirs.values():
        _safe_path(state_root, directory)
        _safe_move.ensure_directory(directory)
        _safe_path(state_root, directory)
    return dirs


def get_transient_env(state_root: Path) -> dict[str, str]:
    """Return dictionary of environment variables routing all tool caches and temps."""
    dirs = transient_paths(state_root)
    return {
        "PYTHONPYCACHEPREFIX": str(dirs["cache_python"]),
        "TEMP": str(dirs["temp"]),
        "TMP": str(dirs["temp"]),
        "TMPDIR": str(dirs["temp"]),
        "PYTEST_ADDOPTS": f"--basetemp=\"{dirs['test_workspace'] / 'pytest'}\" -o cache_dir=\"{dirs['cache_pytest']}\"",
        "MYPY_CACHE_DIR": str(dirs["cache_mypy"]),
        "RUFF_CACHE_DIR": str(dirs["cache_ruff"]),
    }


def emit_env(state_root: Path, shell: str) -> None:
    """Print shell export commands to stdout."""
    env = get_transient_env(state_root)
    if shell == "powershell":
        print("# Shared Project State Environment Variables (PowerShell)")
        for key, value in env.items():
            print(f"$env:{key} = '{value}'")
    elif shell == "cmd":
        print("REM Shared Project State Environment Variables (Command Prompt)")
        for key, value in env.items():
            print(f"set {key}={value}")
    else:  # bash / sh / zsh
        print("# Shared Project State Environment Variables (POSIX)")
        for key, value in env.items():
            print(f"export {key}=\"{value}\"")


def run_command(state_root: Path, command: list[str]) -> int:
    """Run child command with pre-configured transient environment variables."""
    if not command:
        print("Error: No command specified to run.", file=sys.stderr)
        return 1
    ensure_transient_structure(state_root)
    env = os.environ.copy()
    env.update(get_transient_env(state_root))
    try:
        process = subprocess.run(command, env=env)
        return process.returncode
    except FileNotFoundError:
        print(f"Error: Command not found: {command[0]}", file=sys.stderr)
        return 127
    except Exception as error:
        print(f"Error executing command: {error}", file=sys.stderr)
        return 1


def get_dir_size_and_count(path: Path) -> tuple[int, int]:
    """Calculate total byte size and file count of a directory."""
    total_size = 0
    total_count = 0
    if not path.is_dir():
        return 0, 0
    for root, directories, files in os.walk(path, followlinks=False):
        directories[:] = [name for name in directories if not _linked(Path(root) / name)]
        for name in files:
            file_path = Path(root) / name
            try:
                if not _linked(file_path):
                    total_size += file_path.stat().st_size
                    total_count += 1
            except OSError:
                pass
    return total_size, total_count


def format_size(bytes_count: int) -> str:
    """Format bytes into readable units."""
    units = ["B", "KiB", "MiB", "GiB"]
    val = float(bytes_count)
    for unit in units:
        if val < 1024 or unit == units[-1]:
            return f"{val:.1f} {unit}" if unit != "B" else f"{int(val)} B"
        val /= 1024.0
    return f"{bytes_count} B"


def status_report(project_root: Path, state_root: Path) -> None:
    """Print transient storage status."""
    print("=" * 70)
    print(" Shared Project State — Transient Storage Status")
    print(f" Project Root: {project_root}")
    print(f" State Root:   {state_root}")
    print("=" * 70)

    categories = [
        ("Cache / Python", state_root / "Cache" / "Python"),
        ("Cache / Tools", state_root / "Cache"),
        ("Temporary Files", state_root / "Temporary-Files"),
        ("Test Workspace", state_root / "Test-Workspace"),
        ("Logs", state_root / "Logs"),
    ]
    total_bytes = 0
    total_files = 0
    for label, path in categories:
        _safe_path(state_root, path)
        size, count = get_dir_size_and_count(path)
        total_bytes += size
        total_files += count
        print(f" • {label:<18} : {format_size(size):>10} ({count} files) -> {path.relative_to(state_root)}")
    print("-" * 70)
    print(f" TOTAL TRANSIENT STORAGE: {format_size(total_bytes):>10} ({total_files} files)")
    print("=" * 70)


def sweep_project(project_root: Path, state_root: Path, dry_run: bool = False) -> int:
    if dry_run:
        return _sweep_project(project_root, state_root, dry_run=True)
    root = Path(project_root).absolute()
    before = root.lstat()
    state_before = Path(state_root).lstat()
    with _safe_move.locked_directories(root, state_root):
        after = root.lstat()
        state_after = Path(state_root).lstat()
        if (not before.st_ino or not state_before.st_ino
                or (before.st_dev, before.st_ino) != (after.st_dev, after.st_ino)
                or (state_before.st_dev, state_before.st_ino) != (state_after.st_dev, state_after.st_ino)):
            raise OSError("Project or state root identity changed during preflight")
        return _sweep_project(root, state_root, dry_run=False)


def _sweep_project(project_root: Path, state_root: Path, dry_run: bool = False) -> int:
    """Scan project root for stray temporary files, __pycache__, test sandboxes and move them."""
    dirs = transient_paths(state_root) if dry_run else ensure_transient_structure(state_root)
    ignore_dirs = {
        state_root.name,
        STATE_ROOT_NAME,
        LEGACY_STATE_ROOT_NAME,
        ".git",
        ".agents",
        ".codex",
        "node_modules",
        "venv",
        ".venv",
        "env",
        ".env",
    }

    moved_count = 0
    failures = 0
    print(f"Scanning {project_root} for stray temporary/cache artifacts...")

    for root, dirnames, filenames in os.walk(project_root, topdown=True):
        rel_root = Path(root).relative_to(project_root)
        ignored = {name.casefold() for name in ignore_dirs}
        dirnames[:] = [name for name in dirnames
                       if name.casefold() not in ignored and not _linked(Path(root) / name)]

        # Do not descend into ignored top-level or state directories
        if rel_root.parts and rel_root.parts[0] in ignore_dirs:
            dirnames.clear()
            continue

        # 1. Sweep __pycache__ directories
        for dname in list(dirnames):
            if dname == "__pycache__":
                source_dir = Path(root) / dname
                dest_dir = dirs["cache_python"] / f"pycache_{rel_root.as_posix().replace('/', '_')}_{dname}"
                print(f" [PYCACHE] {'Would move' if dry_run else 'Moving'} {source_dir.relative_to(project_root)} -> {dest_dir.relative_to(state_root)}")
                if not dry_run:
                    try:
                        _safe_path(state_root, dest_dir)
                        if os.path.lexists(dest_dir):
                            print(f"   Warning: destination exists; preserving {dest_dir}", file=sys.stderr)
                            failures += 1
                            dirnames.remove(dname)
                            continue
                        move_noreplace(source_dir, dest_dir, source_dir.lstat())
                        moved_count += 1
                    except Exception as err:
                        print(f"   Warning: could not move {source_dir}: {err}", file=sys.stderr)
                        failures += 1
                else:
                    moved_count += 1
                dirnames.remove(dname)
            elif dname in (".pytest_cache", ".mypy_cache", ".ruff_cache"):
                source_dir = Path(root) / dname
                tool_name = dname.lstrip(".").replace("_cache", "")
                dest_dir = dirs["cache"] / tool_name / rel_root.as_posix().replace("/", "_")
                print(f" [TOOL-CACHE] {'Would move' if dry_run else 'Moving'} {source_dir.relative_to(project_root)} -> {dest_dir.relative_to(state_root)}")
                if not dry_run:
                    try:
                        _safe_path(state_root, dest_dir)
                        if os.path.lexists(dest_dir):
                            print(f"   Warning: destination exists; preserving {dest_dir}", file=sys.stderr)
                            failures += 1
                            dirnames.remove(dname)
                            continue
                        _safe_move.ensure_directory(dest_dir.parent)
                        _safe_path(state_root, dest_dir)
                        move_noreplace(source_dir, dest_dir, source_dir.lstat())
                        moved_count += 1
                    except Exception as err:
                        print(f"   Warning: could not move {source_dir}: {err}", file=sys.stderr)
                        failures += 1
                else:
                    moved_count += 1
                dirnames.remove(dname)
            elif dname in (".test-workspace", "test-workspace"):
                source_dir = Path(root) / dname
                dest_dir = dirs["test_workspace"] / f"ws_{rel_root.as_posix().replace('/', '_')}_{dname}"
                print(f" [TEST-WS] {'Would move' if dry_run else 'Moving'} {source_dir.relative_to(project_root)} -> {dest_dir.relative_to(state_root)}")
                if not dry_run:
                    try:
                        _safe_path(state_root, dest_dir)
                        if os.path.lexists(dest_dir):
                            print(f"   Warning: destination exists; preserving {dest_dir}", file=sys.stderr)
                            failures += 1
                            dirnames.remove(dname)
                            continue
                        move_noreplace(source_dir, dest_dir, source_dir.lstat())
                        moved_count += 1
                    except Exception as err:
                        print(f"   Warning: could not move {source_dir}: {err}", file=sys.stderr)
                        failures += 1
                else:
                    moved_count += 1
                dirnames.remove(dname)

        # 2. Sweep stray scratch and temp files in root/subdirs
        for fname in filenames:
            lower = fname.lower()
            if (
                lower.endswith(".pyc")
                or lower.endswith(".pyo")
                or (lower.startswith(("scratch_", "temp_", "tmp_")) and not fname.endswith(".py"))
                or lower.endswith((".tmp", ".temp", ".scratch"))
            ):
                source_file = Path(root) / fname
                dest_sub = dirs["cache_python"] if lower.endswith((".pyc", ".pyo")) else dirs["temp"]
                dest_file = dest_sub / f"{rel_root.as_posix().replace('/', '_')}_{fname}"
                print(f" [FILE] {'Would move' if dry_run else 'Moving'} {source_file.relative_to(project_root)} -> {dest_file.relative_to(state_root)}")
                if not dry_run:
                    try:
                        if _linked(source_file):
                            failures += 1
                            continue
                        _safe_path(state_root, dest_file)
                        if os.path.lexists(dest_file):
                            print(f"   Warning: destination exists; preserving {dest_file}", file=sys.stderr)
                            failures += 1
                            continue
                        move_noreplace(source_file, dest_file, source_file.lstat())
                        moved_count += 1
                    except Exception as err:
                        print(f"   Warning: could not move {source_file}: {err}", file=sys.stderr)
                        failures += 1
                else:
                    moved_count += 1

    action = "Identified" if dry_run else "Successfully moved"
    print(f"Done: {action} {moved_count} stray item(s).")
    if failures:
        print(f"Sweep incomplete: {failures} item(s) could not be moved.", file=sys.stderr)
        return -1
    return moved_count


def clean_transient(state_root: Path, dry_run: bool = False) -> int:
    if dry_run:
        return _clean_transient(state_root, dry_run=True)
    root = Path(state_root).absolute().parent
    before = root.lstat()
    state_before = Path(state_root).lstat()
    with _safe_move.locked_directories(root, state_root):
        after = root.lstat()
        state_after = Path(state_root).lstat()
        if (not before.st_ino or not state_before.st_ino
                or (before.st_dev, before.st_ino) != (after.st_dev, after.st_ino)
                or (state_before.st_dev, state_before.st_ino) != (state_after.st_dev, state_after.st_ino)):
            raise OSError("Project or state root identity changed during preflight")
        return _clean_transient(state_root, dry_run=False)


def _clean_transient(state_root: Path, dry_run: bool = False) -> int:
    """Safely purge disposable transient items from Cache, Temporary-Files, and Test-Workspace."""
    if not dry_run and not state_root.is_dir():
        raise ValueError("An existing state root is required for cleanup.")
    dirs = transient_paths(state_root)
    failures = 0
    purge_targets = [
        ("Python Bytecode Cache", dirs["cache_python"]),
        ("Temporary Files", dirs["temp"]),
        ("Test Workspace", dirs["test_workspace"]),
    ]
    for label, directory in purge_targets:
        _safe_path(state_root, directory)
        if not directory.is_dir():
            continue
        print(f"Cleaning {label} at {directory.relative_to(state_root)}...")
        for item in directory.iterdir():
            if _linked(item):
                print(f" Skipping linked item: {item.name}", file=sys.stderr)
                failures += 1
                continue
            if item.is_dir() or item.is_file():
                print(f" {'Would delete' if dry_run else 'Deleting'} item: {item.name}")
                if not dry_run:
                    try:
                        _safe_move.delete_nofollow(item, item.lstat())
                    except OSError as error:
                        print(f" Unable to clean {item.name}: {error}", file=sys.stderr)
                        failures += 1
    print("Cleanup complete." if not failures else f"Cleanup incomplete: {failures} item(s) preserved.")
    return 0 if not failures else 1


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="Route-Transient-State",
        description="Centralize and route Cache, Temporary Files, and Test Workspaces under Shared-Project-State-Manager.",
    )
    parser.add_argument("--project-root", help="Explicit project root directory.")
    parser.add_argument(
        "--env",
        choices=["powershell", "bash", "cmd"],
        nargs="?",
        const="powershell",
        help="Print shell commands to set transient routing environment variables (default: powershell).",
    )
    parser.add_argument(
        "--sweep",
        action="store_true",
        help="Scan project and move stray __pycache__, temp files, and test caches into Shared-Project-State-Manager.",
    )
    parser.add_argument(
        "--status",
        action="store_true",
        help="Display storage size and breakdown of Cache, Temporary Files, and Test Workspace.",
    )
    parser.add_argument(
        "--clean",
        action="store_true",
        help="Safely remove disposable files in Temporary-Files and Test-Workspace.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview sweep or clean actions without modifying any files.",
    )
    parser.add_argument(
        "--run",
        nargs=argparse.REMAINDER,
        help="Execute a command with all transient routing environment variables pre-configured.",
    )
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    project_root, state_root = resolve_roots(Path(args.project_root) if args.project_root else None)

    if args.run:
        return run_command(state_root, args.run)

    if args.env:
        emit_env(state_root, args.env)
        return 0

    if args.sweep:
        return 1 if sweep_project(project_root, state_root, dry_run=args.dry_run) < 0 else 0

    if args.clean:
        return clean_transient(state_root, dry_run=args.dry_run)

    if args.status or len(sys.argv) == 1:
        status_report(project_root, state_root)
        return 0

    parser.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(main())
