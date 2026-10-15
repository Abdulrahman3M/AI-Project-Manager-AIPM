# Example 17 — Blocked External Dependency

## Situation

A required external service is unavailable after all independent local work is complete.

## State Manifest Excerpt

```json
{
  "schema_version": "2.0",
  "task_id": "Task-2026-10-08-Example-17",
  "task_title": "Example 17",
  "task_status": "READY-FOR-VERIFY",
  "active_phase": "P04",
  "last_completed_phase": null,
  "updated_by": "Outgoing-Agent",
  "updated_at": "2026-10-08T12:00:00Z",
  "branch": "main",
  "head_sha": "example-sha-17",
  "working_tree": "dirty",
  "state_health": "CONSISTENT",
  "next_action": "Record the exact dependency blocker and what remains unverified; continue any safe independent work.",
  "file_operations_policy": "QUARANTINE-FIRST"
}
```

## Handoff

### Exact Resume Point

Local implementation and offline checks pass.

### First Action

Record the exact dependency blocker and what remains unverified; continue any safe independent work.

### Do Not Repeat

Do not fabricate an external-service PASS.

### Required Verification Before Editing

Inspect current project governance, branch/HEAD/working tree when available, relevant files/diff, any running operation, and the evidence that supports the last verified action. If reality differs, mark `STATE-DIVERGED` and reconcile first.

## Verification

| Phase | Check | Result | Blocking | Evidence |
|---|---|---|---|---|
| P04 | Scenario-specific verification boundary | UNVERIFIED | Yes | Must be established from the real project, not copied from this example |

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
