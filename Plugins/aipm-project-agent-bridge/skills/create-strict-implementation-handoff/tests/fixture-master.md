<!-- HANDOFF-SPEC: 1 -->
<!-- MODE: ULTRA-STRICT -->
<!-- PACKAGE-ROLE: MASTER -->
# Illustrative SMALL Implementation Handoff — duplicate submission example

**Important:** FICTIONAL example. No real repository diagnosis or file path is asserted here. Do not use as evidence of an actual defect.

## Objective
Prevent a form from submitting the same request twice when one user action triggers repeated events; preserve keyboard submission and API contracts.

## Scope / Must Preserve / Prohibited Changes
Only the verified form submission workflow and its directly related tests; no unrelated UI change, routes, API or data migration. The executor must inspect AGENTS.md and applicable nested instructions. No guessed source files or architecture.

## Stage 01 — Verified Diagnosis
**EVID-001:** Hypothesis only: duplicate callbacks may be registered. `UNVERIFIED` until the executor reproduces in the target repository. Capture reproducible evidence and read relevant code first.

## Stage 02 — Solution Blueprint
**REQ-001:** One user action causes at most one submission while preserving accessibility and existing API behavior.
**DEC-001:** IF reproduction proves the duplicated handler path, THEN fix only that path. ELSE STOP this unit and report actual behavior; do not implement the hypothesized fix.

## Stage 03 — Handoff Compilation
The author produces instructions only and must never implement a project fix here. Every uncertain source anchor is a discovery instruction, not a filename invented by the author.

## Stage 04 — Preflight Verification
The inspected skill example is fictional. Read AGENTS.md, inspect real repository snapshot/HEAD and existing tests; reproduce issue and capture before state; stop on material mismatch from evidence packet.

## Stage 05 — Atomic Implementation
**UNIT-001** — Verify reproducible duplicate submissions, identify canonical handler from code and change only verified handling; link REQ-001 to TEST-001. If not reproducible, stop without edits.

## Stage 06 — Evidence-Based Verification
**TEST-001:** Focused regression: one submit per action; keyboard and API tests unchanged. Report PASS / FAIL / UNVERIFIED and exact command/result. Never fabricate PASS.

### Acceptance Criteria
- [ ] **AC-001:** REQ-001 passes TEST-001 with actual evidence.

### Stop and Escalate
If observed system differs from assumed cause or required fix affects unrelated modules, STOP the affected portion and give expected/actual evidence to owner or strong analyst.

### Final Report
List actual files changed, tests PASS / FAIL / UNVERIFIED, preserved data/functionality, any blockers, final COMPLETE / PARTIALLY COMPLETE / BLOCKED. Do not claim COMPLETE while mandatory tests remain unverified.

