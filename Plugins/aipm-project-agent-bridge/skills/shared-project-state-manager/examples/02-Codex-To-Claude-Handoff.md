# Example 02 — Codex To Claude Handoff

## Situation

Codex completes a refactor phase and hands documentation/verification back to Claude Code.

## State Manifest Excerpt

```json
{
  "schema_version": "2.0",
  "task_id": "Task-2026-10-08-Example-02",
  "task_title": "Example 02",
  "task_status": "IN-PROGRESS",
  "active_phase": "P04",
  "last_completed_phase": null,
  "updated_by": "Outgoing-Agent",
  "updated_at": "2026-10-08T12:00:00Z",
  "branch": "main",
  "head_sha": "example-sha-02",
  "working_tree": "dirty",
  "state_health": "CONSISTENT",
  "next_action": "Claude verifies the same integration boundary then executes P05 docs/QA.",
  "file_operations_policy": "QUARANTINE-FIRST"
}
```

## Handoff

### Exact Resume Point

Refactor integration test passes.

### First Action

Claude verifies the same integration boundary then executes P05 docs/QA.

### Do Not Repeat

Preserve the refactor; do not reopen settled architecture unless evidence shows divergence.

### Required Verification Before Editing

Inspect current project governance, branch/HEAD/working tree when available, relevant files/diff, any running operation, and the evidence that supports the last verified action. If reality differs, mark `STATE-DIVERGED` and reconcile first.

## Verification

| Phase | Check | Result | Blocking | Evidence |
|---|---|---|---|---|
| P04 | Scenario-specific verification boundary | PASS | No | Must be established from the real project, not copied from this example |

## Expected Agent Behavior

1. Treat this example as a pattern, not evidence about the active project.
2. Reconstruct the active task from its own files and governance.
3. Verify the recorded boundary before repeating or advancing work.
4. Preserve unrelated user/project changes.
5. Update state and handoff with observed facts only.

## Relevant Helper

```powershell
node .\scripts\sps.mjs status --project-root .
node .\scripts\sps.mjs doctor --project-root .

```
