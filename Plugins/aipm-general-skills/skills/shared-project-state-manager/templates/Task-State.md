# Task Plan — {{TASK_ID}}

## Objective

{{TASK_TITLE}}

## Scope

Define the exact authorized implementation scope before substantive work begins.

## Must Preserve

- Existing project governance and user-owned unrelated work.
- Current architecture unless an authorized requirement changes it.
- Evidence-based verification.

## Out Of Scope

Anything not required by the current task or its direct dependencies.

## Acceptance Criteria

- [ ] Original requirements are mapped to phases.
- [ ] Every phase has objective evidence requirements.
- [ ] Blocking tests pass or are explicitly marked UNVERIFIED/BLOCKED.
- [ ] Final state and handoff reflect repository reality.

## Phase Map

| Phase | Objective | Status | Depends On | Verification |
|---|---|---|---|---|
| P01 | Recover/inspect current state and define exact implementation boundary | IN-PROGRESS | — | Repository/state reconciliation |
| P02 | Implement authorized changes | NOT-STARTED | P01 | Focused implementation checks |
| P03 | Integrate, regress, and close | NOT-STARTED | P02 | Final acceptance audit |

## Phase P01

### Prerequisites

Project files and applicable governance are accessible.

### Steps

1. Read project instructions and Shared Project State.
2. Inspect branch, HEAD, working tree, relevant files, and prior evidence.
3. Reconcile divergence.
4. Record exact next implementation action.

### Acceptance Criteria

The incoming agent can state what is verified, what is incomplete, and what must happen next without relying on hidden chat context.

### Verification

Record checks in `Test-Status.md`.
