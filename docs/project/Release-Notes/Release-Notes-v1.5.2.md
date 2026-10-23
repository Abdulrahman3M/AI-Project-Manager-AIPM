# AIPM v1.5.2 Release Notes

## Task Archive Metadata And Optional Folder Deletion Lifecycle

- **Rich Task Metadata (`Metadata.json` / `Metadat.json`):** Completed and synchronized tasks now produce an exhaustive machine-readable metadata file containing task identity, lifecycle status, scope, plan, checkpoints, completed work, modified files, blockers, verification results, final reports, and a full file inventory with relative paths, sizes, categories, SHA-256 hashes, and modification timestamps.
- **Fail-Closed Archive Integrity Verification & Optional Folder Deletion:** Users can choose whether to retain or delete the live task folder in `Shared-Project-State-Manager/Tasks/<Task-ID>` once archived. Deletion is fail-closed: it strictly requires task completion, `.zip.sha256` checksum verification, `zipfile.testzip()` validation, and confirmation that `Metadata.json` and all original files are intact in the archive.
- **Archive-Backed Task Inspection & Transparent Reopen:** Core seamlessly queries metadata and artifact contents directly from `Archive/<Task-ID>.zip` when the live task folder has been deleted. Reopening a task automatically extracts and restores the live task folder to `IN-PROGRESS` status with full continuity.
- **TUI Post-Archive Decision Dialog:** The PowerShell TUI presents a clear confirmation prompt after archive verification (`01 Delete Task Folder` / `02 Keep Task Folder`) and reports accurate outcome notices.
- **Self-Healing Loop Guard:** Core command startup logic avoids regenerating deleted live folders for validly archived tasks, while keeping self-healing intact for unarchived tasks.

## Distribution

Version `1.5.2` is an unpublished repository update. No Skill or Prompt content changed, so Plugin versions remain unchanged. No GitHub Release or tag was created.
