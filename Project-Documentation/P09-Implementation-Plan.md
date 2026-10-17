# P09 Integrated Security And Cross-Agent QA Plan

**Goal:** Verify the integrated managed-project lifecycle, cross-session handoff/revalidation, project isolation, and the applicable security and TUI regression gates without modifying files outside AIPM.

**Architecture:** Exercise the existing HostAdapter → CoreEngine → dashboard/CLI path using two isolated test projects under `.test-workspace`, then use a fresh adapter/engine instance as a receiving session. Reuse focused P02–P08 test suites for lower-level traversal, junction, state-integrity, Git, concurrency, resize, and fail-closed coverage; make no production changes unless a reproducible defect is found.

**Tech Stack:** Python `unittest`, AIPM Core Engine and CLI, PowerShell TUI tests, Git read-only inspection.

**Spec:** `Archive/AI-Project-Manager-AIPM-V2/Phases/P09-Integrated-Security-And-Cross-Agent-QA.md`

## Global Constraints

- Keep all tests, fixtures, reports, and edits inside the AIPM repository.
- Do not modify the Universal AI ToolKit source, stage unrelated changes, publish/install plugins, refresh protected baselines, or write user data.
- Treat unsupported host/plugin installation and unavailable external test roots as `UNVERIFIED`, never as PASS.
- Preserve the owner's supplied visual confirmation as owner-confirmed evidence; do not claim a locally retained screenshot exists.
- Do not start P10 unless every critical P09 gate is verified.

## Review Focus

- A stale/manual handoff must not become authoritative; a new session must re-read registered Core state.
- Writes and evidence from project A must never leak into project B or CLI output beyond its registered state.
- Write grants, host capabilities, project registration, revision checks, and idempotency must fail closed.
- Path traversal, junction escape, atomic recovery, stale locks, Git drift, and resize regressions must remain covered by focused lower-level suites.
- External host plugin installation/export and test projects physically outside the platform repository may remain unverified under the repository-only scope.

## File-Change Map

- Create `Tests/test_p09_integrated_security.py`: exercise two-project Core/TUI projection plus a fresh receiving session and verify no cross-project writes or path disclosure.
- Create `Project-Documentation/P09-Implementation-Plan.md`: record this scoped plan and gates.
- Update `Project-Documentation/Phase-Reports/P08-Report.md`, `Project-Documentation/Checkpoints/P08-Checkpoint.md`, and `Project-Documentation/Handoffs/P08-Next-Phase-Handoff.md`: append an owner-confirmed visual acceptance reconciliation without rewriting prior evidence or claiming a retained screenshot.
- Create `Project-Documentation/Phase-Reports/P09-Report.md`, `Project-Documentation/Checkpoints/P09-Checkpoint.md`, and `Project-Documentation/Handoffs/P09-Next-Phase-Handoff.md`: record evidence, limitations, and exact next action.

## Execution And Verification

1. Confirm current Git branch/HEAD and record the pre-existing dirty worktree without altering it.
2. Reconcile P08 from the owner's later explicit visual acceptance; keep screenshot provenance accurately described.
3. Add and run the P09 integrated two-project/session test; all transient fixtures must self-clean within `.test-workspace`.
4. Run Windows Python suites for P02–P08 and the P09 integration test, including real junction/ACL cases where the host allows them.
5. Run both PowerShell TUI test editions and targeted security/resize/static gates if available.
6. Recheck Git status and the exact paths changed by this phase. Do not stage or commit unrelated user changes.
7. Record PASS/FAIL/UNVERIFIED for every P09 gate. If any critical environment or external-boundary gate is unverified, mark P09 `IMPLEMENTED_WITH_UNVERIFIED_GATES` and do not declare it complete.
