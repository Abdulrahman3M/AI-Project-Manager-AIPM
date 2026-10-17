# Example 10 — Uncommitted Unrelated Changes

## Situation

The working tree contains unrelated user changes before the task begins.

## State Manifest Excerpt

```json
{
  "schema_version": "2.0",
  "task_id": "Task-2026-10-08-Example-10",
  "task_title": "Example 10",
  "task_status": "IN-PROGRESS",
  "active_phase": "P01",
  "last_completed_phase": null,
  "updated_by": "Outgoing-Agent",
  "updated_at": "2026-10-08T12:00:00Z",
  "branch": "main",
  "head_sha": "example-sha-10",
  "working_tree": "dirty",
  "state_health": "CONSISTENT",
  "next_action": "Record only task-owned files in File-Change-Map and leave unrelated changes untouched.",
  "file_operations_policy": "QUARANTINE-FIRST"
}
```

## Handoff

### Exact Resume Point

Task scope and unrelated diff are identified.

### First Action

Record only task-owned files in File-Change-Map and leave unrelated changes untouched.

### Do Not Repeat

Never clean/revert the tree merely to simplify the task.

### Required Verification Before Editing

Inspect current project governance, branch/HEAD/working tree when available, relevant files/diff, any running operation, and the evidence that supports the last verified action. If reality differs, mark `STATE-DIVERGED` and reconcile first.

## Verification

| Phase | Check | Result | Blocking | Evidence |
|---|---|---|---|---|
| P01 | Scenario-specific verification boundary | PASS | No | Must be established from the real project, not copied from this example |

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
