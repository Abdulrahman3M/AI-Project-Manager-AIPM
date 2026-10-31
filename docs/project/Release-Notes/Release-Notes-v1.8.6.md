# AIPM v1.8.6 Release Notes

## State Recovery Diagnostics, Guided Task Normalization, And Transient Routing

- **Read-Only State Inspection (`state-validate`):** Added a non-destructive Core inspection command that checks state envelope validity, identifies exact missing or malformed task fields with source hints, and detects history drift without modifying state files.
- **Guided Record Normalization (`state-normalize`):** Added automated derivation of missing or malformed task fields from task metadata and files (`Metadata.json`, `Task-Plan.md`, `Reports/*.md`), supporting dry-run diff preview and `--confirm-repair` application with hash-verified safety backups and a single `task.reconcile` event at revision `K + 1`.
- **Diagnostic Transparency:** Replaced opaque `INVALID_STATE` failures with sanitized `detail` and actionable `next_step` guidance across Core commands and diagnosis.
- **TUI State Recovery Enhancement:** Updated the TUI state recovery interface to display technical failure reasons, specific task/field findings, and an interactive recovery menu (`Preview Repair`, `Back Up And Normalize`, `Leave Unchanged`).
- **Transient State Routing (`Route-Transient-State`):** Added programmatic routing and sweeper tools (`scripts/route_transient_state.py`, `Route-Transient-State.ps1`) to `shared-project-state-manager` and managed project roots to enforce Section 7 transient storage routing (`Cache/`, `Temporary-Files/`, `Test-Workspace/`) with `--env`, `--run`, `--sweep`, `--status`, and `--clean`.
- **Direct Manifest Editing Prohibition:** Clarified Section 11.3 handoff protocols to mandate updating `State-Manifest.json` strictly via official Core or `sps` CLI commands and never through direct manual editing; bumped `shared-project-state-manager` to `1.0.1`.
- **Operator Runbook:** Published `docs/guides/State-Recovery-Guide.md` with step-by-step diagnostic workflows, finding codes, and manual recovery procedures.
- **Info Bank Project State Repair:** Repaired Info Bank project state (`Project-afa0941b1fc0`) with a hash-verified safety backup, normalizing malformed task records and verifying all 3 tasks in `state-diagnose`, `state-validate`, and `task-list`.

## Versions And Local Distributions

- Platform and TUI versions are synchronized at `1.8.6`.
- The Shared Project State Manager Skill is `1.0.1`.
- ChatGPT/Codex, Claude Code, and Google Antigravity packages are rebuilt and locally validated; packages remain uninstalled and unpublished.
- This is an unpublished repository update. No GitHub push, tag, or Release was created.
