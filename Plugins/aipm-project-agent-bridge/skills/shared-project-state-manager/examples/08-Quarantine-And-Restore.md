# Example 08 — Quarantine And Restore

## Situation

A folder is suspected disposable but the agent wants a reversible cleanup path.

## State Manifest Excerpt

```json
{
  "schema_version": "2.0",
  "task_id": "Task-2026-10-08-Example-08",
  "task_title": "Example 08",
  "task_status": "IN-PROGRESS",
  "active_phase": "P04",
  "last_completed_phase": null,
  "updated_by": "Outgoing-Agent",
  "updated_at": "2026-10-08T12:00:00Z",
  "branch": "main",
  "head_sha": "example-sha-08",
  "working_tree": "dirty",
  "state_health": "CONSISTENT",
  "next_action": "Quarantine it, run project verification, then restore from the record if behavior regresses.",
  "file_operations_policy": "QUARANTINE-FIRST"
}
```

## Handoff

### Exact Resume Point

Folder ownership/purpose is known, but deletion is not yet justified.

### First Action

Quarantine it, run project verification, then restore from the record if behavior regresses.

### Do Not Repeat

Prefer restore over recreating unknown contents.

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
python .\scripts\safe_file_ops.py diagnose ".\<target>" --project-root .
```
