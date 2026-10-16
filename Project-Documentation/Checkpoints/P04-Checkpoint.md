# P04 Checkpoint

## Acceptance Status

PASS — fresh Windows full suite: 73/73 in 20.598s, exit 0, zero skips (2026-10-16, authorized fixture capability). Default run: 73 tests in 29.547s, exit 1, three denied junction fixtures, zero skips. See [P04 Phase Report](../Phase-Reports/P04-Report.md) for exact evidence and limits.

## Durable Invariants

Task status and verification come from manifest records, never artifact edits. COMPLETE requires PASS evidence, a report, and no blockers; phase completion also requires dependencies. Task mutation/recovery may change only command-permitted fields.

## Recovery Procedure

1. Read the task through `CoreEngine`/`TaskOperations.status`; let normal pending recovery validate and complete an interrupted transaction.
2. If only projection files are missing/stale, call `TaskOperations.sync_artifacts(task)` to regenerate them from authoritative state without changing its revision.
3. If pending replay or state/history validation fails, retain all evidence and stop writes; investigate the mismatch rather than promoting artifact text into state.
4. After a plan change, obtain fresh verification and a report through task commands; clear genuine blockers through the command interface before completion.

## Shared Boundaries

The non-Windows PID fallback, actual OS PID reuse, power-loss durability, and multi-process Core Engine writer serialization were not proven. Direct file-symlink creation was unavailable (`WinError 1314`); the guard regression uses a real Windows junction plus a narrowly modeled redirected file open, not live file-symlink traversal. Preserve imported Skill bytes/notices and the documented `project-orchestrator` exception. Do not add `02-Skills-Personal`, `import-memory`, or `morning`; do not modify/publish the Universal AI ToolKit source without explicit owner authorization.
