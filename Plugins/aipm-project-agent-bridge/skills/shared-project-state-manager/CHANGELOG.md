## [2.0.1] — 2026-11-10

- Route active operational examples and validation through PowerShell entry points.

## [2.0.0] — 2026-11-10

- Make the separate state tool explicitly owner-invoked through PowerShell; preserve Core state operations.

## [1.0.1] — 2026-10-31

- Added `Route-Transient-State` programmatic CLI (`scripts/route_transient_state.py`, `Route-Transient-State.ps1`) and `sps route` command to automate Section 7 routing of Cache, Temporary Files, and Test Workspaces under `Shared-Project-State-Manager`.
- Added automatic copy of `Route-Transient-State.py` and `Route-Transient-State.ps1` to the state manager root upon initialization.
- Clarified Section 11.3 handoff instructions to mandate updating `State-Manifest.json` strictly through official Core or `sps` commands and never through direct manual file edits.

## [1.0.0] — AIPM Release Baseline

- Reset the Skill release line to 1.0.0 for independent AIPM development after project completion.

# Changelog

## 2.1.0 — 2026-10-08

- Adopted the repository-wide Skill-owned Prompt placement rule.
- Kept the primary portable protocol at `PROMPT.md` and moved the RichViz companion Prompt into `prompts/RichViz.md`.
- Removed the redundant external copy of the primary Shared Project State Prompt; the Skill folder is now its single source of truth.


## 2.0.0 — 2026-10-08

- Major expansion from a protocol-focused Skill into a vendor-neutral continuity protocol plus executable local tooling.
- Added portable `PROMPT.md`, a standalone-compatible agent protocol, reusable templates, machine-readable schemas, and twenty worked cross-agent/recovery examples.
- Added a dependency-free Node.js CLI for initialization, status, doctor checks, checkpoints, handoffs, and safe-file-operation delegation.
- Added Python validation plus project-scoped safe file operations: diagnosis, reversible move/quarantine/restore, confirmed read-only repair, confirmed Windows ACL reset, and quarantine-only confirmed purge.
- Added PowerShell wrapper and prerequisite checker/installer with explicit installation opt-in and documented Node.js/Python setup.
- Added quarantine-first file-operation policy and permission/lock safety rules that prohibit self-elevation, force-closing handles, indiscriminate process termination, ownership takeover, or OS-security bypasses.
- Added Node/Python regression tests and documented degraded/manual operation when optional runtimes are unavailable.


## 1.0.0 — 2026-10-04

- Initial release.
- Added canonical `Shared-Project-State` workflow for resumable cross-agent project execution.
- Added restartable phase planning, checkpoints, per-phase QA gates, phase reports, recovery, state-divergence detection, and exact next-agent handoff rules.
- Added containment rules for temporary files, caches, temporary/generated test workspaces, logs, and relocatable agent/tool state.
- Added technical root-exception handling so required folders such as `.vscode`, `.claude`, `.codex`, or `.agents` are never moved in a way that breaks their tools.
