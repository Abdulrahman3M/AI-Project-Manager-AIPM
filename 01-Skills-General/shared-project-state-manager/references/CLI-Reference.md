# CLI Reference

## Node.js State CLI

```text
node scripts/sps.mjs <command> [options]
```

- `init`: creates/reuses the Shared Project State structure and templates. Existing state files are preserved.
- `status`: prints recorded state plus a fresh Git snapshot when available.
- `doctor`: checks root files, core manifest keys, project writability, Python availability, platform, and Git state.
- `checkpoint`: creates the next `CP-NNN.md` and updates the manifest.
- `handoff`: rewrites `Next-Agent-Handoff.md` and records current Git snapshot and exact next action.
- `files`: delegates to `safe_file_ops.py`.

## Validator

```text
python scripts/validate_state.py --project-root <project-root> [--strict]
```

## Safe File Operations

```text
python scripts/safe_file_ops.py diagnose PATH --project-root ROOT
python scripts/safe_file_ops.py move SOURCE DEST --project-root ROOT [--dry-run] [--retry-seconds N]
python scripts/safe_file_ops.py quarantine PATH --project-root ROOT [--dry-run] [--retry-seconds N]
python scripts/safe_file_ops.py restore RECORD --project-root ROOT [--dry-run]
python scripts/safe_file_ops.py clear-readonly PATH --project-root ROOT --confirm CLEAR-READONLY [--dry-run]
python scripts/safe_file_ops.py repair-acl PATH --project-root ROOT --confirm REPAIR-ACL [--dry-run]
python scripts/safe_file_ops.py purge RECORD --project-root ROOT --confirm PURGE-QUARANTINE [--dry-run]
```

All operated paths are project-scoped. Destination overwrite is refused.
