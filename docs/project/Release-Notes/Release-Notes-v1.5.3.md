# AIPM v1.5.3 Release Notes

## Self-Contained Archive Metadata, Registry Removal And ZIP Import

- **Self-Contained `Metadata.json`:** Archive metadata (schema `1.1`) embeds the complete Core task record and the task's ordered command history alongside the readable task fields and the full file inventory (paths, sizes, SHA-256 hashes, timestamps). An archive alone is enough to restore the task, even if its registry entry in `State-Manifest.json` no longer exists.
- **Optional Registry Removal:** After the verified archive's live folder is deleted, the TUI offers to remove the task from the AIPM registry. Core refuses unless the task is complete, the live folder is gone, and the archive passes its integrity and metadata checks. The archive is always kept.
- **Import Archived Task From ZIP:** `task-import-archive` (and the Task Management menu item) accepts a ZIP from any location, verifies it (CRC, unsafe paths, size limits, per-file SHA-256 against the inventory, optional `.sha256` sidecar), re-registers the task, atomically restores its folder, and stores a checksummed copy under `Archive/`. It refuses tampered archives and tasks that are already registered. Archives from `1.5.2` (flat metadata) remain importable.
- **Fix:** The archive result `file_count` now reports the number of files rather than the ZIP byte size.

## Distribution

Version `1.5.3` is an unpublished repository update. No Skill or Prompt content changed, so Plugin versions remain unchanged.
