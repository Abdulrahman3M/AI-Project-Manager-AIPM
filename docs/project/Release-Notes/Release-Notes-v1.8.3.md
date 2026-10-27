# AIPM v1.8.3 Release Notes

## Resilient Task Record Normalization, Manifest-History Drift Repair, And TUI StrictMode Hardening

- **PowerShell TUI StrictMode Hardening:** Updated `Invoke-AipmStateRecovery` in `TUI/AI-Project-Manager/src/Core/App.psm1` to safely read diagnosis and repair properties via `Get-AipmField`. This prevents terminating `PropertyNotFoundException` crashes under `Set-StrictMode -Version 2.0` when `state-diagnose` returns results lacking optional properties (such as when `cause` or `remedy` were omitted).
- **Core Engine Task Record & Manifest Normalization:** Enhanced `_validate_task_record` in `Core-Engine/aipm_core/domain.py` to auto-normalize agent-authored task entries:
  - Generates a canonical markdown plan (`# {title}\n\n{scope}\n`) when `plan` is missing or empty for valid titles and scopes.
  - Normalizes missing `report` (`None` -> `""`) and `blockers` (`None` -> `[]`).
  - Normalizes non-standard `verification.result` values (such as `PASS_WITH_LIMITATIONS`) by mapping them to canonical statuses (`UNVERIFIED`), while preserving the original token prefix in `verification.evidence`.
  - Normalizes `status_override` and recalculates top-level `manifest.task_status` when non-standard values (such as `COMPLETED_WITH_COMMIT_BLOCKED`) are present.
- **Direct Manifest-History Drift Diagnosis & Self-Healing Repair:** Extended `diagnose_pending_task_commit` and `repair_pending_task_commit` (`state-diagnose` / `state-repair`) to handle situations where `State-Manifest.json` has drifted ahead of `History/Events` without a `Pending-Commit.json`:
  - Replays contiguous historical events `1..K` and detects drifted or untracked task rows in the manifest.
  - Returns `MANIFEST_HISTORY_DRIFT_RECONCILABLE` with explicit `cause` and `remedy` guidance.
  - Performs verified state backup snapshots in `History/Snapshots/`, creates an immutable `task.reconcile` event at revision `K + 1`, and synchronizes `State-Manifest.json` and event history cleanly.
  - Guarantees `cause` and `remedy` are always returned across all diagnosis branches.
- **Language Learning Hub State Resolution:** Successfully repaired the managed LLH state via `state-repair` and imported the two in-place task folders (`Task-2026-10-26-Breadcrumb-Route-Standardization` and `Task-2026-10-26-Top-Bar-System-Unification`). All 11 LLH tasks are verified and operating cleanly.
- **Automated Regression Verification:** Added comprehensive Python unit tests in `Tests/test_task_artifacts.py` and PowerShell unit tests in `TUI/AI-Project-Manager/tests/Unit/App.Tests.ps1`. All 160 Python tests and 256 PowerShell tests pass.

## Distribution

Version `1.8.3` is a local repository maintenance update. No Skill or standalone Prompt content was changed, so independently versioned Skills and multi-host Plugin archives remain unchanged. No GitHub Release or tag was created.
