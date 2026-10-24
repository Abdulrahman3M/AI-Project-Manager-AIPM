# AIPM v1.5.7 Release Notes

## Performance Optimizations, Security Hardening, and Robustness Enhancements

- **TUI Settings & Executable Discovery Caching:** Added in-memory file write-time caching in `Settings.psm1` (`Get-UserSetting`) and executable discovery caching in `Platform.psm1` (`Find-Executable`) and `AipmClient.psm1` (`Find-AipmPython`), eliminating hundreds of redundant disk reads and PATH scans per session.
- **TUI Rendering Acceleration:** Migrated role styles and accent color tables to static script hashtables in `Theme.psm1`, eliminating thousands of transient object allocations during render cycles. Added tier resolution caching and guarded UTF-8 console output re-initialization.
- **Event-Driven Menu Loop:** Converted the menu loop in `Menu.psm1` (`Show-Menu`) from a busy 125ms redraw loop to a dirty-checked event pump that re-renders only upon user keystrokes or terminal window dimension resizing, significantly reducing CPU usage when idle.
- **Core CLI Task Listing Optimization:** In `aipm.py` (`task-list`), derive task status directly in-memory via `CoreEngine.task_status(record)` instead of invoking `read_task()` with full engine evaluation for each task in a loop.
- **Atomic File Durability (`fsync`):** Added `os.fsync(stream.fileno())` before atomic file replacement in `_atomic_json` (`storage.py`) ensuring filesystem durability prior to metadata swaps.
- **Hardened Task Reopen Archive Extraction:** Hardened `TaskOperations.reopen` (`task_ops.py`) with strict Zip-Slip path validation, sidecar checksum verification, entry count and uncompressed byte limits, and atomic extraction through an isolated staging directory.
- **Non-Blocking File Locking on Windows:** Upgraded `_artifact_lock` in `task_ops.py` to use non-blocking `msvcrt.LK_NBLCK` with a retry deadline loop, eliminating blocking deadlock `EDEADLK` exceptions under contention.
- **Unregister Task State Transition:** In `domain.py` (`task.unregister`), only reset active task pointer when the unregistered task matches the current active task, gracefully falling back to the latest remaining task or `NOT-STARTED`.
- **Cross-Platform Task Folder Opening:** Updated `open-folder` in `App.psm1` to support macOS (`open`) and Linux (`xdg-open`) alongside Windows (`explorer.exe`).
- **Git Commit Isolation:** Added `--no-verify` to git commit in `App.psm1` (`Show-AipmTaskRecord`) to prevent external project test hooks from interrupting AIPM commits.
- **Hybrid Search Input Fix:** Fixed Backspace handling in `Menu.psm1` when slash search (`/`) is active in Hybrid navigation mode.

## Distribution

Version `1.5.7` is an unpublished repository update. No Skill or Prompt content changed, so Plugin versions remain unchanged.
