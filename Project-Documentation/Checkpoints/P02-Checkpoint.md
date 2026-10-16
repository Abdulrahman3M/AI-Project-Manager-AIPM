# P02 Checkpoint

## Acceptance Status

PASS — fresh Windows full suite: 71/71, zero skips (2026-10-16, authorized fixture capability). See [P02 Phase Report](../Phase-Reports/P02-Report.md) for exact evidence and limits.

## Durable Invariants

Managed state belongs only beneath a validated managed-project root; the registry stores pointers. Never overwrite an existing state root, follow a reparse component, merge legacy state automatically, or bypass schema/access validation.

## Recovery Procedure

1. Stop initialization after a path/access error; inspect the selected root and existing state/registry without deleting them.
2. Resolve the actual ACL or reparse/legacy conflict explicitly. If state already exists, inspect/reuse the validated registration rather than reinitialize over it.
3. Confirm no partial `Shared-Project-State-Manager` or `.aipm-*` access probes remain after a denied attempt, and that any prior registry bytes are intact.
4. Retry initialization only with a clean, canonical, authorized root and then register its pointer.

## Shared Boundaries

The non-Windows PID fallback, actual OS PID reuse, power-loss durability, and multi-process Core Engine writer serialization were not proven. Preserve imported Skill bytes/notices and the documented `project-orchestrator` exception. Do not add `02-Skills-Personal`, `import-memory`, or `morning`; do not modify/publish the Universal AI ToolKit source without explicit owner authorization.
