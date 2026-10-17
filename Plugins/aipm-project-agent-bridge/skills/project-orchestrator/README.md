# Project Orchestrator

A management Skill that coordinates complex project work and large Skill libraries through three operating roles: **Manager, Supervisor, and Team Leader**.

## Purpose

The Orchestrator lets the user request an outcome without manually deciding which Skills to use, in what order, or how to supervise them.

It:

- reads project governance;
- checks Shared Project State;
- decomposes work into capabilities and workstreams;
- maintains a current catalog of every library Skill, version, function, and selection trigger;
- selects the smallest sufficient set of specialist Skills;
- assigns one Lead Skill per responsibility where practical;
- supervises quality and integration;
- maintains resumable execution state for substantial work.

## Foundational Assistants

- `project-governance-manager` - governance arm.
- `shared-project-state-manager` - continuity and execution-state arm.

## Files

| Path | Purpose |
|---|---|
| `SKILL.md` | Authoritative orchestration workflow |
| `VERSION` | Independent Skill version |
| `CHANGELOG.md` | Release history |
| `references/Skill-Selection-Protocol.md` | Minimal-sufficient Skill selection method |
| `references/Orchestration-Model.md` | Manager/Supervisor/Team Leader operating model |
| `templates/Orchestration-Brief.md` | Reusable project/task orchestration plan |

Current version: **1.3.10**.

## Core Capabilities — Detailed Guide

### 1. Automatic Skill Discovery and Selection

Identify required capabilities, consult the local Skill catalog, and choose the smallest sufficient set. If a capability is missing, direct the agent to research trusted sources (including `find-skills` where available). Compare candidate Skills for functional fit, provenance, maintenance, license, compatibility, permission requirements, security, and demonstrated quality. Read instructions and dependencies before use. Never auto-install or execute untrusted third-party code; ask for owner approval for new installations, dependencies, or permissions. Preserve explicit user-selected Skills unless substitution is approved. If none is safe, proceed using native capabilities only when verifiable, otherwise report the limitation.

### 2. Risk Management

Classify each operation as low, moderate, or high risk. Identify destructive or security-sensitive actions, affected resources, required approvals, and rollback options. Obtain authorization before high-impact changes; minimize permissions and limit changes to the approved scope.

### 3. Independent Verification and Quality Gates

Define measurable acceptance criteria before execution. Have the Supervisor independently inspect results and supporting evidence instead of accepting a worker agent’s success claim. Report checks as PASS, FAIL, NOT-RUN, or UNVERIFIED, and never present untested behavior as verified.

### 4. Concurrent Change and Conflict Prevention

Inspect the latest repository or workspace state before editing and again at integration. Detect drift from the initial baseline; reconcile legitimate concurrent edits rather than silently overwriting another worker’s changes. Use scoped ownership and safe integration boundaries.

### 5. Parallel Workstream Coordination

Decompose work into independent streams with a Lead Skill, deliverables, dependencies, and acceptance gates. Parallelize only non-conflicting work; serialize overlapping file writes and use an integration owner to combine results safely.

### 6. Resumable Execution and Recovery

Maintain concise checkpoints of completed actions, pending tasks, evidence, blockers, and the next safe step using Shared Project State when available. After interruption, verify the current state before resuming. Diagnose failures and use bounded retries instead of repeating unsuccessful operations blindly.

### Completion Standard

Apply all six capabilities under the active project’s own governance, preserve the owner’s explicit Skill choices, and communicate any unresolved or unverified items accurately.

## External Skill Source Governance

When routing to a third-party Skill, consult the project's [External Skill Sources Registry](../../External-Skill-Sources/README.md) for pinned upstream versions, local adaptations and update-review status. The Orchestrator never replaces local Skills automatically.
