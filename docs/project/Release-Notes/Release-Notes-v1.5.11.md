# AIPM v1.5.11 Release Notes

## Resilient State-Commit Recovery And TUI Menu Hardening

- **State-Commit Recovery Across Historical Drift:** Fixed `STATE_COMMIT_FAILED` in `CoreEngine._recover` when `State-Manifest.json` contains valid task records whose fields were updated outside or across earlier revisions in `History/Events/`. Once `State-Manifest.json` passes full schema validation, `_recover` uses the authoritative manifest baseline to validate pending task transitions while continuing to block tampered pending commits, unrelated field injections, and non-task state smuggling.
- **Generalized State Diagnosis & Repair:** Extended `diagnose_pending_task_commit` and `repair_pending_task_commit` (`state-diagnose` / `state-repair`) to support any pending task operation (`task.report`, `task.plan`, `task.create`, etc.) and stranded `Pending-Commit.json` files at the same revision as an updated `State-Manifest.json`, preserving all task records in a hash-verified backup and explicit `task.reconcile` history event.
- **State-First Task Rename & Delete:** Updated `TaskOperations.rename_task` and `TaskOperations.delete_task` to commit Core state updates before renaming or deleting task directories and archives on disk.
- **TUI Menu Sentinel & StrictMode Hardening:** Guarded all `Show-Menu` call sites in `App.psm1` against `__HELP__` (`?`/`F1`) and `__QUIT__` (`Q`) return values so pressing Help or Quit inside submenus never writes sentinel strings to `settings.json` or triggers a PowerShell StrictMode exception.

## Distribution

Version `1.5.11` is an unpublished repository update. No Skill or Prompt content changed, so Plugin versions remain unchanged. No GitHub Release or tag was created.
