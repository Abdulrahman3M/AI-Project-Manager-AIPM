# P05 Checkpoint

## Acceptance Status

PASS — fresh Windows full suite: 73/73 in 20.598s, exit 0, zero skips (2026-10-16, authorized fixture capability). Default run: 73 tests in 29.547s, exit 1, three denied junction fixtures, zero skips. See [P05 Phase Report](../Phase-Reports/P05-Report.md) for exact evidence and limits.

## Durable Invariants

Continuity paths remain within validated operational state. Archive/quarantine restore never replaces a destination; immutable intent, hashes, and receipts survive retries. Lock retirement requires the current lease identity/nonce and resource guard. Checkpoint JSON is separate from event JSON; unknown usage stays `null`.

## Recovery Procedure

1. Before resuming work, read the handoff and reconcile branch/HEAD/diff observations; treat drift as evidence to inspect, not authority to modify Git.
2. Retry interrupted archive/quarantine restore using its original validated record. Preserve payload, destination, intent, and receipts on hash mismatch, collision, or malformed metadata.
3. Recover an expired lease only through `recover_expired_lock(resource)` after OS identity proves the original owner absent/different; keep the lease on live/unknown identity. Release normally only with its matching nonce. Never unlink the persistent guard.
4. For a snapshot, validate its managed-state path and understand that `restore(snapshot)` restores only `Current-State.md`; it does not restore manifest/events or Git code. Use Core Engine recovery for authoritative transactions.

## Shared Boundaries

The non-Windows PID fallback, actual OS PID reuse, power-loss durability, and multi-process Core Engine writer serialization were not proven. Direct file-symlink creation was unavailable (`WinError 1314`); the guard regression uses a real Windows junction plus a narrowly modeled redirected file open, not live file-symlink traversal. Preserve imported Skill bytes/notices and the documented `project-orchestrator` exception. Do not add `02-Skills-Personal`, `import-memory`, or `morning`; do not modify/publish the Universal AI ToolKit source without explicit owner authorization.
