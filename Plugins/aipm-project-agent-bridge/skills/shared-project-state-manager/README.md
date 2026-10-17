# Shared Project State Manager

A vendor-neutral continuity protocol and optional local toolset for long-running AI-agent work. It lets Claude Code, Codex, ChatGPT coding agents, IDE agents, and other file-capable agents hand a task to one another through verified project state instead of hidden conversation context.

## What v2 Adds

Version 2 combines the original Shared Project State protocol with executable helpers:

- canonical project state, task plans, checkpoints, verification evidence, and exact handoffs;
- a reusable `PROMPT.md` for agents that do not load Skills, plus `prompts/RichViz.md` as a focused continuation companion Prompt;
- Node.js CLI commands to initialize, inspect, checkpoint, hand off, and diagnose state;
- Python safe-file operations for diagnosis, reversible quarantine/restore, read-only repair, scoped moves, and explicitly confirmed Windows ACL reset;
- PowerShell wrapper and prerequisite installer/checker;
- machine-readable JSON Schemas and reusable templates;
- 20 worked examples spanning agent switches, session limits, crashes, verification failures, locked/read-only folders, ACL problems, state divergence, monorepos, and final closure.

The protocol still works manually if Node.js or Python is unavailable. The scripts are helpers, not a new source of truth.

## Runtime Requirements

| Capability | Requirement |
|---|---|
| Skill / Prompt protocol only | No runtime dependency |
| `sps.mjs` CLI | Node.js 18+ |
| Safe file operations / validation | Python 3.10+ |
| Windows ACL reset | Windows built-in `icacls` plus the user's existing OS permissions |
| Git snapshot fields | Git, when the project uses Git |

The JavaScript helpers use only Node.js built-in modules. **No `npm install` is required.** `package.json` exists for version metadata and convenient test commands.

### Install Node.js and Python from PowerShell

```powershell
winget install --id OpenJS.NodeJS.LTS --exact
winget install --id Python.Python.3.13 --exact
node --version
python --version
```

Or use:

```powershell
.\scripts\Install-Prerequisites.ps1
.\scripts\Install-Prerequisites.ps1 -Install
```

The first command only reports status. `-Install` performs the `winget` installs; it never silently installs software.

## Quick Start

```powershell
node .\scripts\sps.mjs init --project-root "D:\Projects\MyProject" --task-id "Task-2026-10-08-Feature" --title "Implement Feature" --agent "Claude Code"
node .\scripts\sps.mjs status --project-root "D:\Projects\MyProject"
node .\scripts\sps.mjs doctor --project-root "D:\Projects\MyProject"
```

Create a checkpoint:

```powershell
node .\scripts\sps.mjs checkpoint --project-root "D:\Projects\MyProject" --agent "Claude Code" --phase P02 --last-verified "Focused P02 tests pass" --next-action "Implement P03"
```

Hand the task to another agent:

```powershell
node .\scripts\sps.mjs handoff --project-root "D:\Projects\MyProject" --from-agent "Claude Code" --to-agent "Codex" --phase P02 --last-verified "P02 verified" --next-action "Begin P03 after reconciling Git state"
```

The incoming agent reads the Shared Project State and then verifies real repository/runtime state before editing.

## Safe File Operations

Diagnose first:

```powershell
python .\scripts\safe_file_ops.py diagnose ".\Temp-Work" --project-root .
```

Prefer reversible quarantine instead of deletion:

```powershell
python .\scripts\safe_file_ops.py quarantine ".\Temp-Work" --project-root .
```

Restore from the generated record:

```powershell
python .\scripts\safe_file_ops.py restore ".\Shared-Project-State\Quarantine\Records\<record>.json" --project-root .
```

Clear read-only bits only when diagnosed and authorized:

```powershell
python .\scripts\safe_file_ops.py clear-readonly ".\Temp-Work" --project-root . --confirm CLEAR-READONLY
```

If Windows ACLs are actually the problem on a project-owned path:

```powershell
python .\scripts\safe_file_ops.py repair-acl ".\Temp-Work" --project-root . --confirm REPAIR-ACL
```

The helper does **not** self-elevate, kill processes, force-close file handles, take ownership, disable security controls, overwrite destinations, or operate outside the selected project root. If a process owns the lock, release/stop that authorized process or agent session first. If ACL repair legitimately requires elevation, the tool reports that requirement rather than bypassing it.

Permanent deletion is limited to an item already moved into this Skill's quarantine area and requires an explicit token:

```powershell
python .\scripts\safe_file_ops.py purge ".\Shared-Project-State\Quarantine\Records\<record>.json" --project-root . --confirm PURGE-QUARANTINE
```

## Canonical Project State

```text
Shared-Project-State/
├── README.md
├── State-Manifest.json
├── Current-State.md
├── Next-Agent-Handoff.md
├── Root-Exceptions.md
├── File-Operations-Policy.md
├── Tasks/<Task-Id>/...
├── Tool-State/
├── Temporary-Files/
├── Cache/
├── Test-Workspace/
├── Logs/
└── Quarantine/
    ├── Items/
    └── Records/
```

The real project files, Git state, official tests, and project governance remain authoritative. Shared state is an operational resume record, never proof by itself.

## Files

| Path | Purpose |
|---|---|
| `SKILL.md` | Authoritative workflow and safety rules |
| `PROMPT.md` | Primary portable protocol for agents without Skill loading |
| `prompts/RichViz.md` | Focused task-resumption companion Prompt owned by this Skill |
| `README.md` | Human setup and usage guide |
| `templates/` | Project/task/handoff/verification/file-policy templates |
| `references/` | Protocol, CLI, permission/lock recovery, schema, and routing guidance |
| `schemas/` | Machine-readable JSON Schemas |
| `scripts/sps.mjs` | Node.js state CLI |
| `scripts/safe_file_ops.py` | Project-scoped safe file operations |
| `scripts/validate_state.py` | State-tree validator |
| `scripts/sps.ps1` | Windows wrapper around the Node CLI |
| `scripts/Install-Prerequisites.ps1` | Node/Python checker/installer |
| `tests/` | Node/Python regression tests |
| `examples/` | Twenty worked scenarios |
| `package.json` | Node requirement and test shortcuts; no external dependencies |

## Testing

```powershell
npm test
python -m unittest discover -s tests -p "test_*.py"
python .\scripts\validate_state.py --project-root "D:\Projects\MyProject"
```

PowerShell-specific behavior should additionally be checked on Windows because a non-Windows development environment cannot validate Windows ACL semantics.

## Safety Boundary

This Skill coordinates authorized project work; it does not grant new permissions. The default file policy is **diagnose -> reversible action -> verify -> destructive cleanup only if explicitly intended**.

Current version: **2.1.0**.
