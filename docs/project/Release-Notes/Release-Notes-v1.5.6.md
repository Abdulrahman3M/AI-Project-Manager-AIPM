# AIPM v1.5.6 Release Notes

## Comprehensive Task Controls

- **Edit Task Details:** Added `task.edit` (`task-edit`) to Core Engine and `Edit Task Name & Description` to PowerShell TUI, allowing users to update a task's title and/or description dynamically, with automatic resynchronization of `Metadata.json`, `Task-State.md`, and related artifacts.
- **Rename Task Folder & Identity:** Added `task.rename` (`task-rename`) to Core Engine and `Rename Task Folder & Identity` to PowerShell TUI, allowing live task folders and manifest task identities to be renamed cleanly while preserving history and archives.
- **Open Live Folder in Explorer:** Added `Open Task Folder In Explorer` to PowerShell TUI to quickly launch the live task directory directly in Windows File Explorer.
- **Archive Incomplete Tasks:** Relaxed completion restrictions across Core Engine (`task-archive`, `task-delete-folder`, and `task-unregister`), allowing tasks of any status (`IN-PROGRESS`, `BLOCKED`, `COMPLETE`) to be archived with integrity verification (`.zip` + `.zip.sha256`), folder cleanup, and registry unregistration.
- **Permanently Delete Task:** Added `delete_task` (`task-delete`) in Core Engine and `Delete Task` in PowerShell TUI, allowing live folders and registry entries of unneeded or mistaken tasks to be permanently deleted without requiring completion.
- **Duplicate Task:** Added `clone_task` (`task-clone`) in Core Engine and `Duplicate Task` in PowerShell TUI, creating a new task initialized from the current task's scope and plan.

## Distribution

Version `1.5.6` is an unpublished repository update. No Skill or Prompt content changed, so Plugin versions remain unchanged.
