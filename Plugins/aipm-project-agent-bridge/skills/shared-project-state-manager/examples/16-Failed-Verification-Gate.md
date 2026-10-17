# Example 16 — Failed Verification Gate

## Situation

Implementation is done but a blocking focused test fails.

## State Manifest Excerpt

```json
{
  "schema_version": "2.0",
  "task_id": "Task-2026-10-08-Example-16",
  "task_title": "Example 16",
  "task_status": "READY-FOR-VERIFY",
  "active_phase": "P03",
  "last_completed_phase": null,
  "updated_by": "Outgoing-Agent",
  "updated_at": "2026-10-08T12:00:00Z",
  "branch": "main",
  "head_sha": "example-sha-16",
  "working_tree": "dirty",
  "state_health": "CONSISTENT",
  "next_action": "Keep phase READY-FOR-VERIFY or IN-PROGRESS, diagnose/fix failure, rerun affected checks.",
  "file_operations_policy": "QUARANTINE-FIRST"
}
```

## Handoff

### Exact Resume Point

Code edit completed; required test FAILS.

### First Action

Keep phase READY-FOR-VERIFY or IN-PROGRESS, diagnose/fix failure, rerun affected checks.

### Do Not Repeat

Do not advance to the next dependent phase.

### Required Verification Before Editing

Inspect current project governance, branch/HEAD/working tree when available, relevant files/diff, any running operation, and the evidence that supports the last verified action. If reality differs, mark `STATE-DIVERGED` and reconcile first.

## Verification

| Phase | Check | Result | Blocking | Evidence |
|---|---|---|---|---|
| P03 | Scenario-specific verification boundary | FAIL | Yes | Must be established from the real project, not copied from this example |

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
