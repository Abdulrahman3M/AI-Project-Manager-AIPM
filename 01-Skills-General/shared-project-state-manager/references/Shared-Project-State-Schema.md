# Shared Project State Schema

This reference defines the default project-local structure created by the `shared-project-state-manager` Skill.

## Canonical Structure

```text
Shared-Project-State/
├── README.md
├── State-Manifest.json
├── Current-State.md
├── Next-Agent-Handoff.md
├── Root-Exceptions.md
├── File-Operations-Policy.md
├── Tasks/
│   └── <Task-Id>/
│       ├── Task-Plan.md
│       ├── Decision-Log.md
│       ├── File-Change-Map.md
│       ├── Test-Status.md
│       ├── Blockers.md
│       ├── Final-Report.md
│       ├── Checkpoints/
│       ├── Phase-Reports/
│       ├── Test-Reports/
│       └── Agent-Sessions/
├── Tool-State/
├── Temporary-Files/
├── Cache/
├── Test-Workspace/
└── Logs/
```

Human-facing paths use ASCII-safe Title-case with hyphen separators. Technical names required by a platform may retain their required spelling inside `Tool-State`.

## Task IDs

Use an ASCII-safe stable identifier, recommended as `Task-YYYY-MM-DD-Short-Name`. Do not rename it after agents begin referencing it without a compelling governance reason.

## State-Manifest.json

Keep it small and machine-readable:

```json
{
  "schema_version": "2.0",
  "task_id": "Task-2026-10-04-Example",
  "task_title": "Example",
  "task_status": "IN-PROGRESS",
  "active_phase": "P02",
  "last_completed_phase": "P01",
  "updated_by": "Codex",
  "updated_at": "2026-10-04T07:30:00+04:00",
  "branch": "main",
  "head_sha": "abcdef123456",
  "working_tree": "dirty",
  "state_health": "CONSISTENT",
  "next_action": "Run the focused P02 validation and write the phase report.",
  "file_operations_policy": "QUARANTINE-FIRST"
}
```

Allowed `state_health`: `CONSISTENT`, `STATE-DIVERGED`, `RECOVERY-IN-PROGRESS`, `BLOCKED`. Use actual values only.

For schema version 2.0, record `file_operations_policy` as `QUARANTINE-FIRST`. The machine-readable contract is `schemas/state-manifest.schema.json`.

## Current-State.md

Required fields: Task, Task Status, Active Phase, Phase Status, Last Verified Action, Exact Next Action, Branch, HEAD, Working Tree, State Health, Blocking Issues, Updated By, Updated At. Then concise sections for verified work, work in progress, work not to repeat, risks, and key paths.

## Next-Agent-Handoff.md

Required sections: Read First, Exact Resume Point, First Action, Do Not Repeat, Required Verification Before Editing, Known Modified Files, Blocking Issues, Owner Decisions, Relevant Reports.

Keep it concise and point to reports/logs.

## Task-Plan.md

Include Objective, Scope, Must Preserve, Out of Scope, Acceptance Criteria, a Phase Map table, and per-phase details with prerequisites, steps, expected files, acceptance criteria, tests, and dependency.

## Decision-Log.md

Append entries with Decision ID, decision, authority, reason, affected phases/files, owner-approval requirement, and superseded decision when applicable.

## File-Change-Map.md

Use a table with Path, Phase, Reason, Expected Change, Status, and Permanent/Temporary.

## Test-Status.md

Use only `PASS`, `FAIL`, or `UNVERIFIED`. Record phase, check, method/command, result, evidence, and whether blocking.

## Blockers.md

Separate Blocking, Non-Blocking, and Owner Approval Gates.

## Checkpoints

Use names such as `Checkpoints/CP-001.md`. Record task/phase, last verified action, exact next action, branch/HEAD, modified files, test state, blockers/risks, and creating agent/tool. A checkpoint is not a Git commit unless a real commit SHA is recorded.

## Phase Reports

Use names such as `Phase-Reports/P01-Discovery-And-Plan.md`. Record status, agent, branch/HEAD, working tree, objective, work completed, exact files changed, decisions, tests/evidence, review, preserved behavior, non-blocking items, and next phase.

## Agent Sessions

Use one file per meaningful session, such as `Agent-Sessions/Session-2026-10-04-Codex.md`. Record start state, actions, last verified action, end state, exact next action, and relevant checkpoint/report paths. Do not paste full chats.

## Final-Report.md

Record objective, final outcome, phases completed, permanent files changed, final tests/results, unverified items, preserved behavior, remaining blockers, documentation/history updates when applicable, final branch/HEAD, and retained temporary data.

## Root-Exceptions.md

Document only technical items that cannot safely be relocated:

```markdown
| Root Path | Tool | Why Root Is Required | Relocatable Data Routed To | Verified By |
|---|---|---|---|---|
| .vscode/ | VS Code | Workspace discovery | Shared-Project-State/Tool-State/VS-Code/ | Documentation/runtime |
```

## File Operations Policy

`File-Operations-Policy.md` records the project-local cleanup/relocation safety model. Diagnose failures first, prefer reversible moves or quarantine, never overwrite destinations silently, and never weaken permissions outside the project root.

## Quarantine

`Quarantine/Items` contains data moved by the optional safe-file helper; `Quarantine/Records` contains the corresponding JSON recovery records. A record captures original path, quarantined path, timestamps, restore/purge state, and diagnostics when available.

Permanent purge is intentionally limited to a target identified by a valid quarantine record and verified to remain below `Quarantine/Items`.

## Templates and Machine-Readable Schemas

The Skill-local `templates/` directory includes project state, task plan, handoff, verification, checkpoint, blockers, decisions, file-change map, root-exception, and file-operation-policy templates.

The `schemas/` directory currently defines:

- `state-manifest.schema.json`;
- `quarantine-record.schema.json`.

These schemas validate shape, not truth. Repository/runtime reality and real verification evidence remain authoritative.

## State Retention

Do not delete state records automatically at completion. Task-local volatile data may be cleaned only when no longer needed, safe, allowed by project policy, and not requested for preservation. Prefer quarantine before permanent purge when uncertainty remains.
