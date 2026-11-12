# CLI Reference

## PowerShell State CLI

```text
.\scripts\sps.ps1 <command> [options]
```

- `init`: creates/reuses the Shared Project State structure and templates. Existing state files are preserved.
- `status`: prints recorded state plus a fresh Git snapshot when available.
- `doctor`: checks root files, core manifest keys, project writability, Python availability, platform, and Git state.
- `checkpoint`: creates the next `CP-NNN.md` and updates the manifest.
- `handoff`: rewrites `Next-Agent-Handoff.md` and records current Git snapshot and exact next action.
- `files`: delegates to `safe_file_ops.py`.

Guarded state I/O requires Python 3.10+ as well as Node.js. Mutations currently require Windows; unsupported platforms fail closed. State-file updates retain a prior backup for recovery.

## Validator

```text
.\scripts\Validate-State.ps1 --project-root <project-root> [--strict]
```

## Safe File Operations

```text
.\scripts\sps.ps1 files diagnose PATH --project-root ROOT
.\scripts\sps.ps1 files move SOURCE DEST --project-root ROOT [--dry-run] [--retry-seconds N]
.\scripts\sps.ps1 files quarantine PATH --project-root ROOT [--dry-run] [--retry-seconds N]
.\scripts\sps.ps1 files restore RECORD --project-root ROOT [--dry-run]
.\scripts\sps.ps1 files clear-readonly PATH --project-root ROOT --confirm CLEAR-READONLY [--dry-run]
.\scripts\sps.ps1 files repair-acl PATH --project-root ROOT --confirm REPAIR-ACL [--dry-run]
.\scripts\sps.ps1 files purge RECORD --project-root ROOT --confirm PURGE-QUARANTINE [--dry-run]
```

All operated paths are project-scoped. Destination overwrite is refused.
