# P02–P05 Hardening Design

## Objective

Complete the remaining P02–P05 acceptance gaps with implementation and repeatable evidence. All source edits, tests, fixtures, temporary repositories, and test-generated data for this work must remain inside the AIPM repository at `D:\Test\02 │ Assistance Projects\AI Project Manager (AIPM)`. Tests must use the repository-local `.test-workspace`; they must not create or modify external managed projects. The Universal AI Toolkit source, imported Skills, and remote GitHub repository are out of scope for this change.

## Accepted Scope

- P02: strengthen Windows path/reparse-point isolation and exercise actual ACL and junction behavior.
- P03: provide import-safe CLI `inspect` and state-read behavior, and prove atomic-write failure handling.
- P04: make task operations call Core Engine commands and keep authoritative task/project status in versioned project state; keep task Markdown as readable materialized artifacts.
- P05: reconcile persisted Git branch, HEAD, and working-tree diff; provide recoverable quarantine/archive operations with audit evidence; validate lease ownership against a real OS process identity rather than a caller-supplied liveness flag.
- Refresh P02–P05 test evidence, reports, checkpoints, and handoffs to distinguish verified results from unsupported or unavailable platform checks.

## Non-Goals and Constraints

- Do not change P00 or the owner-accepted P01 exceptions.
- Do not add excluded personal Skills, `import-memory`, or `morning`; do not rewrite imported Skill contents.
- Do not edit the Universal AI Toolkit source or any path outside the AIPM project.
- Do not push or publish changes as part of this implementation.
- Preserve current public CLI behavior, existing command envelopes, project-isolation rules, event history, task evidence gates, and state-only rollback behavior unless a compatibility-safe extension is required by the acceptance criteria.
- Use Title Case for new human-facing labels, preserving technical identifiers and existing filenames.

## Design

### P02: Path and ACL Isolation

Path validation will inspect the canonical target and its existing path components for Windows reparse points, including junctions, rather than checking only whether the final path reports itself as a symlink. The managed root and state-root boundary checks remain authoritative. Before state initialization or registry mutation, the implementation will perform an effective access probe appropriate to the operation and return a structured denial instead of leaving a partial state tree. Tests will create actual junctions and restricted ACLs wholly under `.test-workspace`, restore any ACL changes during cleanup, and verify both rejection and safe cleanup behavior. A platform capability or privilege limitation must be reported as `UNVERIFIED`, not silently treated as PASS.

### P03: CLI and Recoverable State Writes

The CLI will expose a reusable parser/`main(argv)` entry point without running commands at import time. `inspect` and `state-read` will validate registry and manifest shape, return stable JSON envelopes for success and expected errors, and avoid raw tracebacks for operator input errors. State updates will use an explicit recoverable write protocol for the event and manifest pair. A failed operation must not return PASS or leave a state revision that lacks matching event evidence; recovery or rollback behavior will be deterministic and covered with injected filesystem failures, including replacement failure. Existing idempotency and revision-conflict semantics remain intact.

### P04: Core-Engine-Owned Task Lifecycle

`TaskOperations` will be constructed around a `CoreEngine` and registered `ManagedProject`, and each lifecycle mutation (create, plan, blocker changes, verification, and report) will be represented as a versioned command with revision and idempotency handling. The state manifest/event stream is authoritative for task identity, lifecycle status, phase, and acceptance evidence. Human-readable Markdown files remain materialized artifacts; they must be written only from accepted engine state and be safely repairable if projection writing fails. `status` and completion decisions must read engine state and preserve the existing rule that blockers, FAIL, or UNVERIFIED evidence cannot yield COMPLETE or 100% progress.

### P05: Git Reconciliation and Continuity Safety

Git observations will be read-only and captured from the managed project repository: current branch, HEAD SHA, and a deterministic summary/fingerprint of staged, unstaged, and untracked changes. Reconciliation will compare those observations with saved state and report drift without modifying Git history or the working tree. Quarantine/archive will be move-based and recoverable, with collision-safe destinations, source/destination identity, hashes, timestamps, and an append-only record; it must not silently overwrite or delete data. Lease recovery will query the OS for the actual process and a non-reusable identity (PID plus process creation identity/session); inaccessible or ambiguous process state is treated as live/unknown and prevents unsafe release. Git rollback remains out of scope.

## Failure Handling and Compatibility

- Expected user/input, access, missing-project, corrupt-state, and drift conditions return stable BLOCKED/UNKNOWN results with reason codes; unexpected errors remain diagnosable and must not be disguised as success.
- Atomic file replacement preserves the previous valid file on pre-commit failure. Multi-file state changes use a journal/recovery boundary so event and manifest revisions cannot be falsely reported as committed independently.
- Existing state roots and schema version `1.0` require compatibility-safe reads. If a schema extension is needed, missing new fields receive safe defaults and the change is versioned explicitly; old valid state is not overwritten during migration.
- Any quarantine/archive action is reversible from its recorded metadata. No operation in this scope performs destructive cleanup of user data.

## Verification Plan

All test-created paths must be descendants of the repository-local `.test-workspace`; test helpers will assert this boundary. Coverage will include:

1. Actual Windows junction and ACL behavior, with precise skip/UNVERIFIED reporting only when the host lacks the required capability.
2. CLI subprocess tests for `inspect`, `state-read`, malformed registry/state, and stable JSON error envelopes.
3. Failure injection before and between event/manifest commit steps, asserting previous valid state, event history, and subsequent recovery remain consistent.
4. End-to-end task commands through Core Engine, including idempotent replay, revision conflict, blockers, FAIL/UNVERIFIED gates, artifact projection failure, and status derived from authoritative state.
5. Temporary Git repositories inside `.test-workspace` covering branch/HEAD/diff drift and clean/dirty reconciliation.
6. Quarantine/archive hash-preservation, collision, restoration, and audit-record checks.
7. Lease tests against a real spawned process and its termination, including PID-identity mismatch and inaccessible/unknown results.
8. Full `python -m unittest discover -s Tests -v`, `git diff --check`, import/CLI smoke checks, and a final review of phase reports/checkpoints against captured outputs.

## Acceptance Criteria

- Every implementation and test artifact is within the AIPM repository; no external project, package source, Toolkit repository, or GitHub state is changed.
- P02–P05 behaviors above have direct automated regression tests, and the full suite passes on the available Windows host.
- Windows ACL and junction checks execute against real filesystem objects; if host policy prevents a check, the report names the exact limitation and does not claim full verification.
- P03 never reports a failed state mutation as PASS; manifest/event revisions reconcile after injected failures and restart/recovery.
- P04 task lifecycle mutations pass through Core Engine, and authoritative state—not standalone artifact files—controls status and completion.
- P05 drift, archive/quarantine, and lease decisions use real repository/filesystem/process observations and preserve recoverability.
- P02–P05 reports, checkpoints, and handoffs state exact verification evidence and any remaining limitation; no phase is labeled complete without its gates passing.
