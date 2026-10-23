# AIPM v1.5.5 Release Notes

## Register Existing Task Folders In Place

- **Fix:** When **Add Existing Work Folder** (TUI and Core `task-import-work-folder`) is given an existing task folder inside `Shared-Project-State-Manager/Tasks/`, AIPM now registers that exact folder officially in place (`task.restore`) and reads its existing `Metadata.json`, `Task-State.md`, or `Task-Plan.md` instead of prompting for a new task name or creating a duplicate `Task-...` folder.
- **Guard:** The `Task Name` prompt now rejects folder paths so a pasted path cannot accidentally be used to generate a new folder name.

## Distribution

Version `1.5.5` is an unpublished repository update. No Skill or Prompt content changed, so Plugin versions remain unchanged.
