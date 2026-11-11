# AIPM v1.10.5 Release Notes

AIPM v1.10.5 eliminates recurring PowerShell `Set-StrictMode -Version 2.0` crashes (`Unexpected Error: The property 'Count' cannot be found on this object`) in the terminal interface, particularly when `Invoke-AipmStateRecovery` diagnoses manifest-history drift containing zero or one reconciled task record.

## Highlights

- **StrictMode-Safe Collection Counting (`Get-AipmCount`):** Prevents scalar `[string]` / `[pscustomobject]` and `$null` pipeline-unrolling crashes across `Invoke-AipmStateRecovery`, `Get-AipmProjectSummary`, `Get-AipmPageLines`, `Get-AipmRegistryEntries`, `Show-AipmTaskRecord`, and `Invoke-AipmTaskManagement`, and ensures `Get-AipmField` falls back to explicit defaults when a JSON field is `null`.
- **State Recovery & Task Path Hardening:** Guards optional `state-validate` and `state-normalize` fields via `Get-AipmField`, replaces a non-ASCII separator in `App.psm1` with pure ASCII for Windows PowerShell 5.1 compatibility, isolates per-project summary projection failures, and recognizes both `Shared-Project-State-Manager/Operations/Tasks/` and legacy `Shared-Project-State-Manager/Tasks/`.
- **Diagnostic Error Provenance:** `Start-AIPM.ps1` now records `[<FileName>:<LineNumber>]` in `app.log` on unhandled errors while keeping terminal error messages clean.
- **Regression Suite:** Added `Set-StrictMode -Version 2.0` tests in `TUI/AI-Project-Manager/tests/Unit/App.Tests.ps1` covering `Get-AipmCount`, null-valued properties, 1-element `reconciled_tasks` drift recovery, and 0-element `reconciled_tasks` drift recovery.
- **Post-Task Governance (`AGENTS.md`):** Codified mandatory post-task cache/temporary cleanup, Git commit, and GitHub `main` push rules for authorized AIPM maintenance tasks while keeping formal GitHub Releases and tags separately gated.

Platform and TUI metadata are synchronized at `1.10.5`. No General Skill, standalone Prompt, or Plugin archive changed. Automated runtime execution of `Run-Tests.ps1` and `unittest` remains `UNVERIFIED` until run in a terminal opened on the relocated checkout; this is a local repository update, not a published GitHub Release.
