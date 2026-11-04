# State Recovery And Guided Task Record Repair Guide

This guide explains how to diagnose, inspect, and recover registered managed project state when `State-Manifest.json` encounters schema invalidation, field divergence, or history drift.

---

## 1. Overview And Symptoms

When AIPM accesses a managed project's operational state (`Shared-Project-State-Manager/State-Manifest.json`), it enforces strict schema validity, task identity format, and contiguous historical event replay.

Common symptoms indicating state recovery is required:
- In the TUI: notice **"Task State Needs Review"** or **"Task State Needs Manual Review"** with `Error Code: INVALID_STATE` or `MANIFEST_HISTORY_DRIFT_RECONCILABLE`.
- In the Core CLI: `task-list` or `task-read` returns `{"status": "BLOCKED", "reason": "INVALID_STATE", "detail": "..."}`.
- Direct file editing: an external AI Agent or developer edited `State-Manifest.json` by hand without publishing corresponding immutable event records to `History/Events/`.

---

## 2. Core CLI Diagnostic Commands

AIPM provides three layered commands to safely analyze and resolve state discrepancies:

### 2.1 State Diagnosis (`state-diagnose`)
Checks whether there is an interrupted pending commit or reconcilable history drift.
```bash
python Core-Engine/aipm.py state-diagnose --registry "D:\Test\00 │ Project Settings\registry.json" --project-id Project-afa0941b1fc0
```
- If repairable through standard commit replay: returns `"status": "PASS"`, `"repairable": true`.
- If blocked by a malformed task record: returns `"status": "BLOCKED"`, with a descriptive `cause` and `next_step` directing to `state-validate`.

### 2.2 Deep Field-Level Inspection (`state-validate`)
A strictly **read-only** command that never touches or modifies any state file. It checks the manifest envelope, every task record against the schema, and replays history events to detect missing or drifted tasks:
```bash
python Core-Engine/aipm.py state-validate --registry "D:\Test\00 │ Project Settings\registry.json" --project-id Project-afa0941b1fc0
```
Example Output:
```json
{
  "schema_version": "1.0",
  "status": "BLOCKED",
  "project_id": "Project-afa0941b1fc0",
  "manifest_revision": 44,
  "max_event_revision": 42,
  "findings": [
    {
      "severity": "ERROR",
      "code": "TASK_FIELD_MISSING",
      "task_id": "Task-2026-10-30-Sample-01",
      "field": "title",
      "message": "Task record has no title.",
      "repairable_by": "state-normalize",
      "source_hint": "Operations/Tasks/<task-id>/Metadata.json -> task_record.title (or title); otherwise supply it manually"
    }
  ],
  "summary": "1 blocking problem(s) found; first: Task record has no title."
}
```

### 2.3 Guided Task Normalization (`state-normalize`)
Repairs malformed task records by deriving missing fields from authoritative task files (`Operations/Tasks/<task-id>/Metadata.json`, `Task-Plan.md`, `Reports/*.md`):

#### Step 1: Preview (Dry Run)
Inspect planned field derivations and diffs without modifying any files:
```bash
python Core-Engine/aipm.py state-normalize --registry "D:\Test\00 │ Project Settings\registry.json" --project-id Project-afa0941b1fc0
```

#### Step 2: Apply With Hash-Verified Backup
Once the preview is verified, apply the normalization with `--confirm-repair`:
```bash
python Core-Engine/aipm.py state-normalize --registry "D:\Test\00 │ Project Settings\registry.json" --project-id Project-afa0941b1fc0 --confirm-repair
```
What this does atomically:
1. Creates a full, hash-verified snapshot under `History/Snapshots/AIPM-State-Repair-<Timestamp>-<Hex>/` with `Backup-Manifest.json` and SHA-256 checksums of all existing state and event files.
2. Formulates a single explicit `task.reconcile` history event at revision `K + 1` containing the normalized records.
3. Updates `State-Manifest.json` atomically and verifies post-commit consistency.

---

## 3. Finding Codes Reference

| Code | Severity | Meaning & Remedy |
|---|---|---|
| `TASK_FIELD_MISSING` | ERROR | A mandatory field (`title`, `scope`, `verification`) is absent. `state-normalize` will attempt to derive it from `Metadata.json`. |
| `TASK_FIELD_INVALID` | ERROR | A field has an invalid type or empty string. Inspect task metadata. |
| `TASK_STATUS_OVERRIDE_INVALID` | WARNING | `status_override` contains an unsupported status string. Core normalizes `COMPLETED` and `COMPLETED & VERIFIED` to `COMPLETE`. |
| `MANIFEST_AHEAD_OF_HISTORY` | WARNING | The manifest revision is higher than committed events in `History/Events`. Reconciled by `state-normalize` or `state-repair`. |
| `TASK_DRIFTED_FROM_HISTORY` | WARNING | A task record was updated directly in the manifest without an event. Preserved and reconciled into history. |
| `PENDING_COMMIT_PRESENT` | WARNING | An interrupted pending transaction exists. Run `state-diagnose` and `state-repair` first. |
| `HISTORY_NON_CONTIGUOUS` | ERROR | History event files are missing revisions between 1 and N. Manual integrity review required. |

---

## 4. Mandatory Rule: Never Edit State-Manifest.json Directly

> **CRITICAL DIRECTIVE FOR AI AGENTS AND DEVELOPERS**
> Never edit or overwrite `Shared-Project-State-Manager/State-Manifest.json` manually with text editors or custom file-writing scripts.
>
> All task state transitions, checkpoints, verifications, and closures MUST be executed exclusively through official Core commands:
> - `aipm task-create`
> - `aipm task-plan`
> - `aipm task-checkpoint`
> - `aipm task-verify`
> - `aipm task-report`
> - `aipm task-close`
> - `aipm task-reopen`
>
> Or via the `sps` CLI helper (`node scripts/sps.mjs`). Direct edits bypass event logging, desynchronize revisions, and trigger `INVALID_STATE` dead ends.

---

## 5. Backup Verification And Manual Restores

Every automatic repair creates a standalone backup snapshot in `Shared-Project-State-Manager/History/Snapshots/AIPM-State-Repair-<timestamp>-<id>/`.

To manually restore a previous state snapshot:
1. Stop all AIPM or agent processes targeting the project.
2. Inspect `Backup-Manifest.json` inside the snapshot folder to view the recorded file checksums.
3. Copy `State-Manifest.json` from the snapshot back to the root of `Shared-Project-State-Manager/`.
4. Copy all `Events/*.json` files from the snapshot back to `Shared-Project-State-Manager/History/Events/`.
5. Remove `Shared-Project-State-Manager/History/Pending-Commit.json` if present.
6. Run `aipm state-validate --project-id <id>` to confirm state consistency.
