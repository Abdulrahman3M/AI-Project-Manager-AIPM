# Example 06 — Read Only Generated Files

## Situation

Generated task artifacts were made read-only and cleanup cannot proceed.

## State Manifest Excerpt

```json
{
  "schema_version": "2.0",
  "task_id": "Task-2026-10-08-Example-06",
  "task_title": "Example 06",
  "task_status": "IN-PROGRESS",
  "active_phase": "P03",
  "last_completed_phase": null,
  "updated_by": "Outgoing-Agent",
  "updated_at": "2026-10-08T12:00:00Z",
  "branch": "main",
  "head_sha": "example-sha-06",
  "working_tree": "dirty",
  "state_health": "CONSISTENT",
  "next_action": "Diagnose, dry-run clear-readonly, apply with confirmation, quarantine, validate, then optionally purge.",
  "file_operations_policy": "QUARANTINE-FIRST"
}
```

## Handoff

### Exact Resume Point

Artifacts are confirmed task-generated and disposable.

### First Action

Diagnose, dry-run clear-readonly, apply with confirmation, quarantine, validate, then optionally purge.

### Do Not Repeat

Permission change is narrow and applies only to confirmed task artifacts.

### Required Verification Before Editing

Inspect current project governance, branch/HEAD/working tree when available, relevant files/diff, any running operation, and the evidence that supports the last verified action. If reality differs, mark `STATE-DIVERGED` and reconcile first.

## Verification

| Phase | Check | Result | Blocking | Evidence |
|---|---|---|---|---|
| P03 | Scenario-specific verification boundary | PASS | No | Must be established from the real project, not copied from this example |

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
python .\scripts\safe_file_ops.py diagnose ".\<target>" --project-root .
```
