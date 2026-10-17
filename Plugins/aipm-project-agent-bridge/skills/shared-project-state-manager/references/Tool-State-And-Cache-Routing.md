# Tool State And Cache Routing

Centralize task-created operational state without breaking fixed tool discovery paths.

## Core Routing Principle

1. Prefer official project-local cache/temp/state configuration pointing into `Shared-Project-State`.
2. Prefer per-command or per-project environment variables.
3. Use existing project configuration only when appropriate.
4. Keep a minimal required root technical path only when the tool cannot work without it.
5. Document every unavoidable root exception.

Never change global machine configuration merely to satisfy this Skill unless explicitly requested.

## Recommended Destinations

| Artifact Type | Default Destination |
|---|---|
| Agent/runtime state | `Shared-Project-State/Tool-State/<Tool>/` |
| Generic temporary files | `Shared-Project-State/Temporary-Files/<Task-Id>/` |
| Tool/language cache | `Shared-Project-State/Cache/<Tool-Or-Language>/` |
| Temporary/generated tests | `Shared-Project-State/Test-Workspace/<Task-Id>/` |
| Large command/debug output | `Shared-Project-State/Logs/<Task-Id>/` |
| Detailed test reports | `Shared-Project-State/Tasks/<Task-Id>/Test-Reports/` |
| Reversible cleanup candidates | `Shared-Project-State/Quarantine/Items/` |

## Python

Python often creates `__pycache__` beside source. When appropriate, set `PYTHONPYCACHEPREFIX` to `Shared-Project-State/Cache/Python`, or use `PYTHONDONTWRITEBYTECODE=1` for disposable runs that need no bytecode cache. Do not change global Python configuration.

PowerShell session example:

```powershell
$env:PYTHONPYCACHEPREFIX = "$PWD\Shared-Project-State\Cache\Python"
```

POSIX example:

```bash
export PYTHONPYCACHEPREFIX="$PWD/Shared-Project-State/Cache/Python"
```

## pytest

Keep permanent committed tests in their official directory. Route pytest cache/temp data with supported options such as `--basetemp` and `cache_dir` after inspecting the existing configuration.

## Coverage, mypy, Ruff

Route task-local outputs/caches with supported project/session settings such as `COVERAGE_FILE`, mypy `--cache-dir`, or Ruff cache configuration. Verify options against the installed/current tool; do not invent flags.

## Node.js Ecosystem

Do not move `node_modules` merely because it is large. Route task-created caches/output through supported configuration, preserve lockfiles/build conventions, and do not change global package-manager cache without explicit request.

## Build Systems

Do not relocate a build directory if project scripts/IDE depend on its canonical location. Use Shared Project State only for separately configurable temporary build/test output. Permanent release artifacts remain in project-defined locations.

## VS Code

VS Code commonly discovers workspace settings/tasks/launch configuration from root `.vscode`. Do not bury a required `.vscode` under Shared Project State and assume discovery. Keep minimum required root configuration, document it in `Root-Exceptions.md`, and route generated logs/temp state to `Shared-Project-State/Tool-State/VS-Code`.

## Claude Code / Codex / Other Agents

Tools may use root folders such as `.claude`, `.codex`, `.agents`, or other documented paths. Inspect current discovery rules before moving anything. Relocate only when officially supported; otherwise keep minimum root structure, route generated cache/log/scratch/handoff state into Shared Project State, and document the exception.

## OS Temporary Directories

Do not globally redirect `TEMP`, `TMP`, or the OS temp directory for one project. Prefer per-command temporary-directory overrides under `Shared-Project-State/Temporary-Files/<Task-Id>`.

## Existing Repository Caches

Inspect existing cache/temp conventions before changing them. Preserve intentional architecture/tooling requirements. Record existing exceptions or migrate only with explicit approval and focused validation.

## Protected, Read-Only, or Locked Task State

Do not assume every failed move/delete is an ACL problem. Diagnose whether the cause is a read-only bit/attribute, ACL denial, live process handle, destination collision, or a tool rule that intentionally protects the path.

When the Skill's optional helper is available:

```powershell
python .\scripts\safe_file_ops.py diagnose ".\Problem-Path" --project-root .
```

Prefer a reversible `move` or `quarantine`. Clearing read-only state and resetting Windows ACL inheritance are separate explicit-confirmation operations. The helper does not self-elevate, kill processes, force-close handles, take ownership, grant broad permissions, or disable OS security controls.

If a live process owns the handle, release or stop the relevant authorized process/tool or record the blocker. Do not use ACL repair to solve a live handle lock.

See `File-Operations-Safety.md` and `Permission-And-Lock-Recovery.md`.

## Shared Project State Helper Tooling

The dependency-free Node.js CLI can initialize state, inspect status, run doctor checks, create checkpoints, create handoffs, and delegate safe-file operations. Python validation/file helpers are optional. Their absence must not invalidate the manual protocol.

## Cleanup

Never delete unknown caches/temp directories before confirming another task does not require them. At completion, remove only safe disposable task-local data; never delete permanent source, configuration, tests, or user data.

When uncertainty remains, quarantine first, validate the project, and either restore or explicitly purge the quarantined item after it is confirmed disposable.
