# P06 Checkpoint

## Acceptance Status

PASS — P06 complete on Windows. Focused tests: 13/13. In-scope integrated P02–P06 suite: 84/84 with the authorized scoped junction capability. See [P06 Phase Report](../Phase-Reports/P06-Report.md) for exact results and scope limits.

## Durable Invariants

- The protected registry contains 17 General Skills, Skill-owned Prompt mappings, and one standalone Prompt.
- All 16 byte-preserved imports remain checked against P01 per-file hashes on every catalog scan; only `project-orchestrator` is the documented derivative.
- Personal Skills, `import-memory`, and `morning` are excluded.
- The generated Plugin contains General Skill masters only, with byte parity, source license, and Skill notices; it is local-only, unpublished, and uninstalled.
- Apache-2.0 applies only to AIPM-authored files. Imported terms and notices are preserved.
- Registry refresh requires explicit CLI confirmation, a reason, valid version/changelog metadata, and cannot rewrite the 16 preserved imports.
- No changes were made to the Universal AI ToolKit source. No remote write was performed.

## Recovery And Resume

1. Run `python Maintenance-Tools/Invoke-Capability-Library.py validate` before relying on the registry.
2. If Plugin replacement fails during both install and rollback, the CLI error identifies the preserved prior sample under `.test-workspace/p06-plugin-backup-*`; verify it before recovery.
3. Do not edit registry/provenance records by hand. Use the documented confirmation-gated maintenance command only for an approved refresh.
4. P07 has not started. Read its authoritative phase instructions and confirm P06 remains green before beginning that phase.

## Verification Boundary

The fresh P01 test module was intentionally not run because it reads the external Archive. P06 locally revalidated the full 16-Skill migration hash map. Default Windows execution cannot create the three junction fixtures; with the previously approved scoped capability the full in-scope P02–P06 suite passed. Other historical platform limitations are recorded in the P02 and P05 reports.
