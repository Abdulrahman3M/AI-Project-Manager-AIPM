"""Test-only isolated AIPM runtime for tests whose fixtures live in this repository."""
from __future__ import annotations

import atexit
import os
from pathlib import Path
import shutil

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
TEST_WORKSPACE = REPOSITORY_ROOT / ".test-workspace"
# A test runner can be interrupted while a child process still has a copied
# runtime file open. Per-process paths prevent a later test process from
# deleting or reusing that live runtime.
RUNTIME_ROOT = TEST_WORKSPACE / f"aipm-test-runtime-{os.getpid()}"


def _prepare_runtime() -> None:
    TEST_WORKSPACE.mkdir(exist_ok=True)
    if RUNTIME_ROOT.exists():
        shutil.rmtree(RUNTIME_ROOT)
    RUNTIME_ROOT.mkdir()
    for name in ("Core-Engine", "Capability-Library", "VERSION"):
        source = REPOSITORY_ROOT / name
        destination = RUNTIME_ROOT / name
        if source.is_dir():
            shutil.copytree(source, destination, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
        else:
            shutil.copy2(source, destination)
    for name in ("aipm-project-agent-bridge", "Adapters"):
        source = REPOSITORY_ROOT / "Plugins" / name
        if source.is_dir():
            shutil.copytree(source, RUNTIME_ROOT / "Plugins" / name, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))


_prepare_runtime()
CORE_ROOT = RUNTIME_ROOT / "Core-Engine"
CORE_SCRIPT = CORE_ROOT / "aipm.py"


def cleanup_runtime() -> None:
    resolved = RUNTIME_ROOT.resolve()
    expected_parent = TEST_WORKSPACE.resolve()
    if resolved.parent == expected_parent and resolved.name == f"aipm-test-runtime-{os.getpid()}":
        shutil.rmtree(resolved, ignore_errors=True)


atexit.register(cleanup_runtime)
