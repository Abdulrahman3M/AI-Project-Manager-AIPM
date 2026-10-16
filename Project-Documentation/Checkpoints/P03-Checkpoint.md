# P03 Checkpoint

## Acceptance Status

PASS — fresh Windows full suite: 71/71, zero skips (2026-10-16, authorized fixture capability). See [P03 Phase Report](../Phase-Reports/P03-Report.md) for exact evidence and limits.

## Durable Invariants

`CoreEngine` owns authoritative state mutations. Each accepted mutation has a matching revision/event and idempotency key; history must be contiguous and valid. Reads of legacy schema do not silently migrate disk state.

## Recovery Procedure

1. Preserve `State-Manifest.json`, `History/Events`, and `History/Pending-Commit.json` when recovery is blocked.
2. Issue a normal `state.read` through `CoreEngine.execute`; valid pending intent completes before state is exposed.
3. If INVALID_STATE or INVALID_HISTORY persists, stop writes and investigate the conflicting/malformed evidence. Do not delete pending intent or invent missing events to force progress.
4. On a revision conflict, reread authoritative state before a new mutation; reuse the accepted idempotency key when retrying the same command.

## Shared Boundaries

The non-Windows PID fallback, actual OS PID reuse, power-loss durability, and multi-process Core Engine writer serialization were not proven. Preserve imported Skill bytes/notices and the documented `project-orchestrator` exception. Do not add `02-Skills-Personal`, `import-memory`, or `morning`; do not modify/publish the Universal AI ToolKit source without explicit owner authorization.
