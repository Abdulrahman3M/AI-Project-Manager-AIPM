# Orchestration Model

Project Orchestrator uses one management system with three layers.

## Manager Layer

Inputs:

- owner request;
- project governance;
- current project state;
- available Skill metadata.

Outputs:

- objective;
- scope;
- capability map;
- selected Skill roster;
- Team Map;
- phase/workstream plan;
- acceptance criteria.

The Manager owns strategic allocation, not specialist implementation details.

## Supervisor Layer

Inputs:

- Manager plan;
- project governance;
- specialist outputs;
- tests/evidence;
- Shared Project State.

Outputs:

- approval/rework/block decisions;
- conflict resolution;
- scope-compliance findings;
- integration readiness;
- final quality status.

The Supervisor must remain sufficiently independent from implementation to challenge unsupported claims.

## Team Leader Layer

Inputs:

- approved Team Map;
- active phase;
- dependencies;
- assigned specialist Skill instructions.

Outputs:

- executable work packets;
- coordinated specialist outputs;
- progress/blocker updates;
- integration inputs.

The Team Leader turns strategy into concrete work.

## Logical Team Definition

A "team" means a bounded workstream with:

- an objective;
- an assigned Lead Skill;
- optional Support Skills;
- inputs;
- deliverable;
- dependencies;
- verification gate.

A logical team does not imply a separate running AI agent.

## Example

User asks for a large desktop application feature.

Manager:

- reads governance;
- identifies architecture, UI, testing, documentation, and state needs;
- selects foundational assistants plus relevant specialists.

Team Leader:

- creates workstreams and executes them in dependency order.

Supervisor:

- checks each workstream for project-rule compliance, test evidence, and integration safety before approval.

## Control Loop

```text
Owner Request
    |
    v
Manager: Plan + Select Skills
    |
    v
Team Leader: Execute Workstream
    |
    v
Supervisor: Review
    |
    +--> REWORK --> Team Leader
    |
    +--> BLOCKED --> Manager / Owner Decision
    |
    +--> APPROVED --> Next Workstream
    |
    v
Integration + Final Supervisor Gate
    |
    v
Final Management Report
```

## Foundation Integration

`project-governance-manager` supplies the governance interpretation layer.

`shared-project-state-manager` supplies the continuity, phase, checkpoint, recovery, and handoff layer.

The Orchestrator remains responsible for combining those foundations with task-specific specialist Skills.

## Risk, Verification, Concurrency and Recovery

- Classify each task LOW, MODERATE or HIGH risk and secure approvals before sensitive or destructive changes.
- Define measurable acceptance criteria; distinguish PASS, FAIL, NOT-RUN and UNVERIFIED with actual evidence.
- Inspect current state immediately before edits and reconcile drift instead of overwriting concurrent work.
- Run independent workstreams in parallel only when their writes do not overlap; designate an integration owner.
- Keep resumable checkpoints and diagnose failures before bounded retries.
- Respect each active project's own governance; do not import this toolkit's rules into unrelated projects.
