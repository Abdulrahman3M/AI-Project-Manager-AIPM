#!/usr/bin/env python3
"""Route-Transient-State: Centralize and route Cache, Temporary Files, and Test Workspaces.

Enforces Section 7 of Global Agent Directives & Operating Rules:
- Cache/ (Python __pycache__, pytest, mypy, ruff, tool caches)
- Temporary-Files/ (scratch scripts, transient dumps, disposable files)
- Test-Workspace/ (test sandboxes, experimental fixtures, temporary test runs)
"""
from __future__ import annotations

import argparse
import os
from pathlib import Path
import shutil
import subprocess
import sys
from typing import Any

STATE_ROOT_NAME = "Shared-Project-State-Manager"
LEGACY_STATE_ROOT_NAME = "Shared-Project-State"


def resolve_roots(start_path: Path | None = None) -> tuple[Path, Path]:
    """Dynamically resolve the project root and its Shared-Project-State-Manager directory."""
    if start_path is not None:
        current = start_path.resolve()
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


def ensure_transient_structure(state_root: Path) -> dict[str, Path]:
    """Ensure standard transient directories exist inside Shared-Project-State-Manager."""
    dirs = {
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
    for directory in dirs.values():
        directory.mkdir(parents=True, exist_ok=True)
    return dirs


def get_transient_env(state_root: Path) -> dict[str, str]:
    """Return dictionary of environment variables routing all tool caches and temps."""
    dirs = ensure_transient_structure(state_root)
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
    for root, _, files in os.walk(path):
        for name in files:
            file_path = Path(root) / name
            try:
                if not file_path.is_symlink():
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
    ensure_transient_structure(state_root)
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
        size, count = get_dir_size_and_count(path)
        total_bytes += size
        total_files += count
        print(f" • {label:<18} : {format_size(size):>10} ({count} files) -> {path.relative_to(state_root)}")
    print("-" * 70)
    print(f" TOTAL TRANSIENT STORAGE: {format_size(total_bytes):>10} ({total_files} files)")
    print("=" * 70)


def sweep_project(project_root: Path, state_root: Path, dry_run: bool = False) -> int:
    """Scan project root for stray temporary files, __pycache__, test sandboxes and move them."""
    dirs = ensure_transient_structure(state_root)
    ignore_dirs = {
        state_root.name,
        STATE_ROOT_NAME,
        LEGACY_STATE_ROOT_NAME,
        ".git",
        "node_modules",
        "venv",
        ".venv",
        "env",
        ".env",
    }

    moved_count = 0
    print(f"Scanning {project_root} for stray temporary/cache artifacts...")

    for root, dirnames, filenames in os.walk(project_root, topdown=True):
        rel_root = Path(root).relative_to(project_root)

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
                        if dest_dir.exists():
                            shutil.rmtree(dest_dir, ignore_errors=True)
                        shutil.move(str(source_dir), str(dest_dir))
                        moved_count += 1
                    except Exception as err:
                        print(f"   Warning: could not move {source_dir}: {err}", file=sys.stderr)
                else:
                    moved_count += 1
                dirnames.remove(dname)
            elif dname in (".pytest_cache", ".mypy_cache", ".ruff_cache"):
                source_dir = Path(root) / dname
                tool_name = dname.lstrip(".").replace("_cache", "")
                dest_dir = dirs["cache"] / tool_name / rel_root.as_posix().replace("/", "_")
                dest_dir.parent.mkdir(parents=True, exist_ok=True)
                print(f" [TOOL-CACHE] {'Would move' if dry_run else 'Moving'} {source_dir.relative_to(project_root)} -> {dest_dir.relative_to(state_root)}")
                if not dry_run:
                    try:
                        if dest_dir.exists():
                            shutil.rmtree(dest_dir, ignore_errors=True)
                        shutil.move(str(source_dir), str(dest_dir))
                        moved_count += 1
                    except Exception as err:
                        print(f"   Warning: could not move {source_dir}: {err}", file=sys.stderr)
                else:
                    moved_count += 1
                dirnames.remove(dname)
            elif dname in (".test-workspace", "test-workspace"):
                source_dir = Path(root) / dname
                dest_dir = dirs["test_workspace"] / f"ws_{rel_root.as_posix().replace('/', '_')}_{dname}"
                print(f" [TEST-WS] {'Would move' if dry_run else 'Moving'} {source_dir.relative_to(project_root)} -> {dest_dir.relative_to(state_root)}")
                if not dry_run:
                    try:
                        if dest_dir.exists():
                            shutil.rmtree(dest_dir, ignore_errors=True)
                        shutil.move(str(source_dir), str(dest_dir))
                        moved_count += 1
                    except Exception as err:
                        print(f"   Warning: could not move {source_dir}: {err}", file=sys.stderr)
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
                        shutil.move(str(source_file), str(dest_file))
                        moved_count += 1
                    except Exception as err:
                        print(f"   Warning: could not move {source_file}: {err}", file=sys.stderr)
                else:
                    moved_count += 1

    action = "Identified" if dry_run else "Successfully moved"
    print(f"Done: {action} {moved_count} stray item(s).")
    return moved_count


def clean_transient(state_root: Path, dry_run: bool = False) -> None:
    """Safely purge disposable transient items from Cache, Temporary-Files, and Test-Workspace."""
    dirs = ensure_transient_structure(state_root)
    purge_targets = [
        ("Python Bytecode Cache", dirs["cache_python"]),
        ("Temporary Files", dirs["temp"]),
        ("Test Workspace", dirs["test_workspace"]),
    ]
    for label, directory in purge_targets:
        if not directory.is_dir():
            continue
        print(f"Cleaning {label} at {directory.relative_to(state_root)}...")
        for item in directory.iterdir():
            if item.is_dir():
                print(f" {'Would delete' if dry_run else 'Deleting'} directory: {item.name}")
                if not dry_run:
                    shutil.rmtree(item, ignore_errors=True)
            elif item.is_file():
                print(f" {'Would delete' if dry_run else 'Deleting'} file: {item.name}")
                if not dry_run:
                    try:
                        item.unlink()
                    except OSError:
                        pass
    print("Cleanup complete.")


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
        sweep_project(project_root, state_root, dry_run=args.dry_run)
        return 0

    if args.clean:
        clean_transient(state_root, dry_run=args.dry_run)
        return 0

    if args.status or len(sys.argv) == 1:
        status_report(project_root, state_root)
        return 0

    parser.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(main())
