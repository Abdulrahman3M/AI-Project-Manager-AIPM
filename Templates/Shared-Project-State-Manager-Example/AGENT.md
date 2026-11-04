# Shared Project State Manager Agent Rules

This folder contains AIPM operational records and FIRG. Keep project implementation files in the project source tree.

## Layout

- `FIRG/`: fix and change records, reports, tools, policies, schemas, and FIRG configuration.
- `Temporary-Files/Cache/`: disposable runtime caches, including Python `__pycache__`, bytecode, and tool caches.
- `Temporary-Files/Test-Workspace/`: temporary test runs, generated fixtures, experiments, and disposable harnesses.
- `Archive/`: retained snapshots and completed task archives.
- `History/`: chronological events, backups, and change history.
- `Operations/Tasks/`: task-scoped plans, evidence, reports, and handoffs.
- `Operations/Tool-State/`: resumable tool and integration state.
- `Operations/Logs/`: diagnostics and execution logs.
- `Operations/Quarantine/`: isolated suspicious or damaged state for review.
- `Operations/Locks/`: concurrency markers.
- `Project-Manifest.json` and `State-Manifest.json`: Core-owned authoritative metadata; update them only through AIPM.

## Routing Rules

Never create temporary files, test artifacts, caches, or bytecode outside `Temporary-Files/` in this project. Route Python caches to `Temporary-Files/Cache/` (set `PYTHONPYCACHEPREFIX` when running Python), test outputs and fixtures to `Temporary-Files/Test-Workspace/`, and other disposable tool caches to `Temporary-Files/Cache/`. Keep logs, archives, history, task records, and tool state in their named sections. Do not copy implementation files into this state folder.

## FIRG Records

FIRG protects project fixes, including projects without a literal fork. Read project governance, `FIRG/README.md`, `FIRG/policies/INTEGRATION.md`, relevant registry records, and affected code/tests before recording or reviewing a fix. Registry JSON files are canonical; `FIRG/FIX-HISTORY.md` is generated and must not be edited independently. Preserve provenance and evidence, never invent facts, and use only `PASS`, `FAIL`, or `UNVERIFIED` for test results. For a completed commit, check `commit-status`; document the actual commit with `document-commit`, recording the problem, root cause, expected behavior, implementation, rationale, and evidence. State unknown causes and unavailable test evidence honestly. The interactive post-commit prompt is optional and can be bypassed.
