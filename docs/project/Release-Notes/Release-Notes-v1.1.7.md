# AI Project Manager v1.1.7 — Development Update Notes

> This is an unpublished repository development update. It does not create a Git tag, source archive, GitHub Release, or Plugin installation.

## Architectural Review Result

The core principle existed **partially** before this update. AIPM already stored managed-project state in each project's `Shared-Project-State-Manager/`, and its host adapter did not expose a general project filesystem API. However, the Core did not yet provide a complete task artifact and checkpoint workflow that a new process could use to resume independent tasks. The PowerShell TUI task views remain read-only.

## What Changed

- Established the enduring boundary: AIPM manages task context, supporting artifacts, progress, evidence, and handoffs. The AI Agent edits original project files and runs project tests under the project/host's existing permissions.
- Added CLI/Core operations for task creation, listing, reading, planning, blockers, verification, reports, structured checkpoints, and bounded task artifact list/read/write.
- Kept task records and attachments in independent folders under the managed project's own `Shared-Project-State-Manager/Tasks/<Task-ID>/`. Checkpoints record changed source paths by reference; they do not make working copies.
- Added UTF-8/binary-friendly task artifact import from a user-selected file, a 16 MiB limit, relative-path/category confinement, SHA-256 compare-before-update, and atomic writes. Generated Markdown projections use atomic replacement so they do not write through a hard-linked file.
- Updated `AGENTS.md`, project rules, architecture, TUI architecture, and both beginner guides with the source-vs-task boundary and a PowerShell task/handoff walkthrough.
- Synchronized platform and TUI development versions to `1.1.7` under the project's SemVer policy. This is not a published release.

## Verification Scope

- Three independent tasks were exercised in a temporary fixture. One task received partial progress, an original-project changed-file reference, an explicit next action, test status, and a supporting artifact. A separate Core Engine instance and later CLI subprocesses read the same persisted task state and attachment; the fixture's project source remained unchanged.
- Full Python suite: 140 tests, zero failures, four skipped because the Windows host denied junction/hard-link creation. Both TUI runs passed 190/190 on PowerShell 7.6.5 and Windows PowerShell 5.1.26100.9444.
- Tests verify task isolation, legacy task-record readability, CLI lifecycle commands, artifact path confinement, update hashes, local adapter scoping, atomic replacement, and generated Plugin/archive integrity.
- The environment denied hard-link creation with Windows `Access is denied`, so the direct hard-link scenario could not execute here. The platform-independent test confirms that generated projections are written using atomic path replacement. This does not replace a privileged live Windows hard-link test.
- No independent AI-host session was connected. A real external cross-agent session remains `UNVERIFIED`; the process-boundary/resume test is a local Core/CLI simulation only.
- No target-project test suite was run by AIPM. Test results remain agent-reported evidence.

## Distribution And Cleanup

- No Skill or Prompt content changed. The protected Capability Library registry and provenance ledger were refreshed through the confirmed CLI workflow solely to synchronize `platform_version` metadata. The legacy Bridge was rebuilt at its independent patch version `1.0.7`; ChatGPT/Codex, Claude Code, and Google Antigravity ZIPs were rebuilt at `1.1.7` and locally validated. The packages remain uninstalled and unpublished; Antigravity's authoritative host-format gate remains unverified.
- `.test-workspace/` is disposable generated test data and was removed after verifying its resolved path and confirming it contained no remaining files or reparse points. The older `Shared-Project-State/` directory contains an in-progress task record; it is not proven disposable and remains preserved. A deletion attempt was rejected by the safety review, so its contents were not removed or relocated.
- The latest published GitHub release remains `v1.0.2`. No GitHub push, tag, source ZIP, or release asset was created in this task.
