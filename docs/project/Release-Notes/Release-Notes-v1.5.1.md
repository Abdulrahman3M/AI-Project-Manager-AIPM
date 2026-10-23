# AIPM v1.5.1 Release Notes

## Legacy Task State Recovery, Lifecycle Hardening And TUI Reliability

- **Legacy Task State Recovery (`INVALID_STATE` Fix):** Normalized pre-`1.5.0` task records (`status_override: null`) during manifest validation and pending transaction recovery so projects created before `v1.5.0` can create and update tasks without triggering `Task History Conflicts With State`, and any stranded `Pending-Commit.json` from `v1.5.0` self-heals on the next read.
- **Task Lifecycle State Machine Fixes:** Reopening a task (`task.reopen`) now clears prior `PASS` verification in addition to `status_override`, `task.plan` resets `status_override`, non-`PASS` verification clears `status_override`, and `task.close` requires active blockers to be cleared before closing.
- **TUI Strict-Mode & Task Record Fixes:** Initialized `$folderPath` unconditionally in task creation flows, resolved `$ProjectRoot` automatically in `Show-AipmTaskRecord` when omitted, displayed live `$task.task_status` in task detail views, and allowed `WARNING` level in `Write-AppLog`.
- **Git Boundary Protection:** TUI Git status and commit actions now verify that the managed project root is the top-level Git repository root (`git rev-parse --show-toplevel`) before staging or committing.
- **Project Re-Registration:** Re-registering a folder that already contains a valid `Shared-Project-State-Manager/Project-Manifest.json` now reuses its existing `project_id` and validates its state manifest.

## Distribution

Version `1.5.1` is an unpublished repository update. No Skill or Prompt content changed, so Plugin versions remain unchanged.
