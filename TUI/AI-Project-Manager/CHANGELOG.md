# AI Project Manager TUI Change Log

## [1.8.2] — Junction Verification Synchronization

- Synchronized TUI metadata with platform `1.8.2` after Windows junction verification. No TUI runtime behavior changed.

## [1.8.1] — Screenshot To Code Browser Evidence Modes (Not Published)

- Synchronized TUI metadata with platform `1.8.1` for the updated screenshot capability. No TUI runtime behavior changed.

## [1.8.0] — Screenshot To Code Distribution Synchronization (Not Published)

- Synchronized TUI metadata with platform `1.8.0` for the new distributed capability. No TUI runtime behavior changed.

## [1.7.0] — Professional Word Designer Distribution Synchronization (Not Published)

- Synchronized the PowerShell TUI package version with AIPM platform `1.7.0` because the updated distributed Professional Word Designer capability changes the packaged product surface. No TUI runtime behavior, tag, or GitHub Release was created.

## [1.6.13] — Web Design Engineering Skill Distribution Synchronization (Not Published)

- Synchronized the PowerShell TUI package version with AIPM platform `1.6.13` because the newly shipped `web-design-engineering` General Skill changes the distributed AIPM product capability set.
- No PowerShell TUI runtime behavior changed. Local multi-host Plugin archives and the legacy Bridge are rebuilt and validated separately; none is installed or published.

## [1.5.11] — Resilient State-Commit Recovery And Menu Sentinel Hardening (Not Published)

- Synchronized with AIPM Core `1.5.11` state-commit recovery and generalized `state-diagnose` / `state-repair` support for all pending task commands (`task.report`, `task.plan`, `task.create`, etc.).
- Guarded `Show-Menu` handlers in `App.psm1` (`Invoke-DesignWizard`, `Resolve-AipmRegistryPath`, `Select Project To Unregister`, `Select Registered Project`, `Open Existing Task`, and `Select View Mode`) so pressing `?`/`F1` (`__HELP__`) or `Q` (`__QUIT__`) never persists sentinel strings into `settings.json` or triggers a StrictMode null-dereference error.
- Updated `Show-AipmTaskRecord` (`App.psm1`) to refresh `$TaskRow.title` immediately after editing a task's title and to read `task_path` reliably when opening a task folder in the system file manager.
- Synchronized the TUI version with AIPM platform `1.5.11`.

## [1.5.10] — Guided Task-State Diagnosis And Repair (Not Published)

- When task state cannot be read or task creation fails, the TUI now asks Core for a diagnosis, explains the cause and safe recovery path, and offers repair only when Core confirms the narrowly supported recovery pattern.
- The confirmed repair creates a hash-verified state snapshot, records preserved untracked tasks in an explicit event, resumes the pending create, and reports the backup and committed revision. Unsupported conflicts remain blocked with a recovery recommendation.
- Synchronized the TUI version with AIPM platform `1.5.10`.

## [1.5.9] — Legacy Task Commit Recovery (Not Published)

- Synchronized with AIPM Core 1.5.9. Creating or updating a task now succeeds after the Core normalizes legacy string verification records or the old `COMPLETED` status spelling.
- Synchronized the TUI version with AIPM platform `1.5.9`.

## [1.5.8] — Resilient Task State Normalization And Self-Healing (Not Published)

- Synchronized with AIPM Core 1.5.8 resilient state recovery and task record normalization, preventing `INVALID_STATE` notices when inspecting projects containing agent-modified task manifests.
- Synchronized the TUI version with AIPM platform `1.5.8`.

## [1.5.7] — Performance Optimization, Cross-Platform Support, And Menu Event Pump (Not Published)

- Performance Optimizations:
  - Added in-memory file write-time caching (`$script:SettingsCache`, `$script:SettingsLastWrite`) in `Settings.psm1` (`Get-UserSetting`), reducing per-session settings disk reads from hundreds to zero when settings are unchanged.
  - Added executable path caching (`$script:ExecutableCache`) in `Platform.psm1` (`Find-Executable`) and `$script:CachedPython` in `AipmClient.psm1` (`Find-AipmPython`) to prevent redundant PATH evaluations.
  - Refactored `Theme.psm1` to store style roles (`$script:BaseRoleStyles`) and accent codes (`$script:AccentCodes`) in static script hashtables, eliminating transient allocations on every render cycle. Added icon tier caching (`$script:ResolvedTier`) and UTF-8 console output guard (`$script:ConsoleUtf8Configured`).
  - Optimized menu layout metric calculation in `Menu.psm1` (`Get-MenuLayoutMetrics`) using `StringBuilder` key generation instead of JSON serialization.
  - Converted menu event loop in `Menu.psm1` (`Show-Menu`) from a busy 125ms redraw loop to a dirty-checked event pump that re-renders only on active user input or console window dimension changes.
- Usability & Cross-Platform Enhancements:
  - Upgraded `open-folder` in `App.psm1` (`Show-AipmTaskRecord`) to resolve system openers cross-platform (`explorer.exe` on Windows, `open` on macOS, and `xdg-open` on Linux).
  - Added `--no-verify` flag to git commit in `App.psm1` (`Show-AipmTaskRecord`) to prevent external project pre-commit hooks from interrupting local AIPM commits.
  - Fixed Backspace input handling in `Menu.psm1` when slash search (`/`) is active in Hybrid navigation mode.
- Synchronized the TUI version with AIPM platform `1.5.7`.

## [1.5.6] — Comprehensive Task Controls: Edit Details, Rename, Open Explorer, Archive Incomplete Tasks, Clone, And Delete (Not Published)

- Extended the Task Management menu (`Show-AipmTaskRecord`) with comprehensive task controls:
  - `Edit Task Name & Description`: interactive prompt to update title and/or description in Core state.
  - `Rename Task Folder & Identity`: interactive prompt to rename task folder and Core task ID.
  - `Open Task Folder In Explorer`: directly opens live task folder in Windows File Explorer.
  - `Duplicate Task`: clone task scope and plan into a new task with custom title.
  - `Delete Task`: permanently delete live task folder and unregister task, even if incomplete.
  - `Archive Task Folder`: archive tasks at any status (incomplete, in-progress, blocked, or complete).
- Extended `AipmClient.psm1` (`Invoke-AipmCore`) with `-NewTaskId` and `-DeleteArchive` parameter support and whitelisted `task-edit`, `task-rename`, `task-clone`, and `task-delete` Core commands.
- Synchronized the TUI version with AIPM platform `1.5.6`.

## [1.5.5] — Register Existing Task Folders Directly In Place (Not Published)

- When `Add Existing Work Folder` receives a folder inside `Shared-Project-State-Manager/Tasks/`, the TUI now registers that exact folder in place immediately without prompting for a new task name or creating a second folder.
- Added validation on `Task Name` to reject folder paths so a pasted path is never used as a task name.
- Synchronized the TUI version with AIPM platform `1.5.5`.

## [1.5.4] — Add Existing Work Folder Accepts Agent-Created Task Folders (Not Published)

- `Add Existing Work Folder` no longer rejects existing folders inside `Shared-Project-State-Manager`; only the state root and its `Tasks` root are refused.
- Synchronized the TUI version with AIPM platform `1.5.4`.

## [1.5.3] — Registry Removal Choice And Import Archived Task From ZIP (Not Published)

- After a verified archive's live folder is deleted, the archive flow now offers `Remove Task From AIPM Registry?` (the archive is always kept).
- Added `Import Archived Task From ZIP` to Task Management: choose any `.zip` path, and AIPM verifies it, re-registers the task, and restores its folder from `Metadata.json`.
- Added client commands `task-unregister` and `task-import-archive`, with regression coverage for registry removal and ZIP re-import.
- Synchronized the TUI version with AIPM platform `1.5.3`.

## [1.5.2] — Task Archive Retention Choice And Metadata Client Support (Not Published)

- Extended task archiving flow in `Show-AipmTaskRecord` to prompt with a two-choice confirmation dialog (`01 Delete Task Folder` / `02 Keep Task Folder`) after archive creation and verification pass.
- Added client commands `task-delete-folder` and `task-metadata` with optional `-DeleteFolder` parameter on `Invoke-AipmTaskArchive`.
- Displayed clear visual outcome notices differentiating between "Task Archived & Folder Removed" and "Task Archived & Folder Kept".
- Expanded scripted TUI regression suite to 239 tests covering the archive retention and folder-deletion decision dialog.
- Synchronized the TUI version with AIPM platform `1.5.2`.

## [1.5.1] — Legacy State Recovery, Git Boundary Hardening And Strict-Mode Reliability (Not Published)

- Initialized `$folderPath` unconditionally in task creation and work-folder flows under PowerShell strict mode, and added immediate input validation rejecting `Shared-Project-State-Manager` as a work folder.
- Made `$ProjectRoot` optional with automatic registry lookup in `Show-AipmTaskRecord`, and updated task detail views to display the live `task_status` from Core.
- Guarded `Review Git Changes` and `Commit Git Changes` so they verify the managed project root is the top-level Git repository before running `git status`, `git add`, or `git commit`.
- Updated `Register A Project` to reuse the existing `project_id` from `Shared-Project-State-Manager/Project-Manifest.json` when re-registering a previously managed project folder.
- Extended `Write-AppLog` to accept `WARNING` in addition to `WARN`, preventing parameter validation errors when logging design configuration warnings.
- Updated TUI regression tests for the expanded 15-item task management menu and added lifecycle coverage for task close, archive, and reopen.

## [1.5.0] — Task Lifecycle And Existing Work Registration (Not Published)

- Added task close, reopen, and portable archive actions to the task management menu.
- Added a separate existing-work-folder registration flow that records an inventory in task references.
- Repaired Create New Task Core invocation under PowerShell strict mode to ensure it does not evaluate or pass an uninitialized work-folder path.

## [1.4.9] — Escape Exit Confirmation And Apache License (Not Published)

- Pressing Esc at the main dashboard now opens an "Exit AI Project Manager?" confirmation instead of closing PowerShell immediately. Encountering the prompt requires an explicit "Exit AIPM" choice; "Stay Here" returns to the Task Dashboard.
- Added scripted regression coverage for both the confirmation prompt and the confirmed exit path.
- Made the existing work-folder task-context assertion tolerant of prompt-wrapped folder paths, which restored a green suite on `1.4.9`.
- Relicensed the TUI package under the Apache License 2.0 with `Copyright 2026 Abdulrahman Elbatrah`, added a package `NOTICE`, and updated the Capability Library license statement.

## [1.4.8] — Repository Version Synchronization (Not Published)

- Synchronized the TUI repository version with AIPM `1.4.8`. No TUI behavior change was introduced by the closeout itself; no GitHub Release or tag is created by this repository update.

## [1.4.7] — Wrapped Prompt Input (Not Published)

- Rendered long typed prompt values as explicit terminal rows, preserving the Enter/Esc instructions and preventing visual overwrites in Windows Terminal.
- Added a narrow-terminal regression test for a multi-row task report value.

## [1.4.6] — Repository Version Synchronization (Not Published)

- Synchronized the TUI version with AIPM `1.4.6` for the documentation-only repository update. No TUI behavior changed; no GitHub Release or tag was created.

## [1.4.5] — Managed Input And Frame Lifecycle

- Synchronizes the TUI package with AIPM `1.4.5`; this repository update carried no TUI product behavior change beyond the accompanying platform version metadata.

## [1.4.0] — Synchronized Product Release

- Synchronized the PowerShell TUI version with the AIPM platform at `1.4.0` for the source release.
- Carries forward the guided Registry Management, task workflow, task artifact viewing/search, pagination, and evidence-backed project/task views accumulated since `v1.0.2`.
- No native terminal visual or external AI-host gate is inferred from the version synchronization; see the Support Matrix for the tested environments and remaining UNVERIFIED items.

## [1.3.4] — Development Synchronization (Development; Not Published)

- Synchronized the TUI package version with the AIPM platform at `1.3.4` for the accumulated repository update.
- No Release or tag was created.

## [1.3.3] — Search Attached Task Files (Development; Not Published)

- Added `/` filename and relative-path search exclusively to **View Attached Task Files**.
- Search results show exact-match availability and matching artifacts; clearing the query restores the complete inventory.
- Added scripted regression coverage and synchronized the TUI version with AIPM `1.3.3`; no Release or tag was created.

## [1.3.2] — Paginated Information Pages (Development; Not Published)

- Paginated long read-only pages according to the current terminal height so late task artifacts are not hidden below the viewport.
- Added Up/Down and PageUp/PageDown navigation and an explicit page counter; Enter/Esc continue to return.
- Added short-terminal regression coverage and synchronized the TUI version with AIPM `1.3.2`; no Release or tag was created.

## [1.3.1] — Direct Task Actions And File Attachments (Development; Not Published)

- Opened the task action menu immediately after task selection and made the detailed status view optional.
- Added TUI actions to attach plans, reports, handoffs, and supporting files into task-scoped categories through Core, and to list attached task files.
- Documented that attaching copies the selected file while preserving the original; retained the 16 MiB limit and no-silent-overwrite behavior.
- Kept the TUI and platform development versions synchronized at `1.3.1`; no Release or tag was created.

## [1.3.0] — Guided Task Management (Development; Not Published)

- Added a guided task workflow that refreshes the registry and requires project selection before task operations.
- Added task creation, existing-work-folder context without file moves/copies, existing-task review, and updates for plans, checkpoints, blockers, verification evidence, and reports through whitelisted Core calls.
- Documented the workflow and its project-source safety boundary in both beginner guides and the TUI architecture guide.
- Synchronized the TUI development version with AIPM `1.3.0`; no Release or tag was created.

## [1.2.0] — Existing Registry Connection (Development; Not Published)

- Added explicit first-run and Registry Management flows for validating and selecting an existing registry file without replacing it.
- Clarified device-specific project path behavior and task-folder use within a registered project.
- Synchronized the TUI development version with AIPM `1.2.0`; no Release or tag was created.

## [1.1.9] — Projects Navigation And Registry Guidance (Development; Not Published)

- Kept registered project names inside **Projects** instead of exposing each as a separate dashboard action; registration now gives English Refresh guidance.
- Clarified that registry setup accepts any full file path ending in `.json`, and explains why a folder path alone is rejected.

## [1.1.8] — Platform Version Synchronization (Development; Not Published)

- Synchronized the TUI package version with AIPM `1.1.8`; no TUI runtime behavior changed.

## [1.1.7] — Task Context Architecture (Development; Not Published)

- Synchronized the TUI package version with the AIPM platform's `1.1.7` development version. Task authoring remains in the Core CLI; the TUI task views remain read-only.

## [1.0.7] — Protected Registry Administration

- Added first-run registry location approval and a guarded Registry Management screen for project pointers, backups, restores, and location changes.
- Routed all registry actions through the Core allowlist and surfaced the AIPM installation-protection boundary in the interface and documentation.
- Synchronized the TUI package version with the platform's v1.0.7 development update.

## [1.0.6] — Platform Version Synchronization

- Synchronized the TUI package version with the platform's v1.0.6 versioned update; no TUI runtime behavior changed.

## [1.0.5] — Platform Version Synchronization

- Synchronized the TUI package version with the v1.0.5 Plugin distribution compatibility update; no TUI runtime behavior changed.

## [1.0.4] — Platform Version Synchronization

- Synchronized the TUI package version with the platform's v1.0.4 version update; no TUI runtime behavior changed.

## [1.0.3] — Release Metadata Synchronization

- Synchronized the TUI package version with the platform's v1.0.3 source release; no runtime behavior changed.

## [1.0.2] — Documented Local Release Package

- Synchronized the TUI package with the platform's local release-ready source archive.
- Kept runtime behavior read-only; no host installation or publication occurred.

## [1.0.1] — Capability Library Refinement

- Removed repeated Skill license text from Capability Library rows, widened the Capability field, and renamed the package to AIPM Project Agent Bridge.

## [1.0.0] — Personal License And Connected Frames

- Reset the package release line to 1.0.0.
- Added connected, bounded terminal frames for the product shell and tables.

## [Unreleased]

### Added

- Added Core-Backed Task Dashboard, Command Palette, And Assistant Console Modes.
- Added Read-Only Project, Task, Phase, Evidence, Agent, Timeline, Skill, And Plugin Views.
- Added Differential Rendering, Semantic Theme Roles, Search, Help, And Persistent UI Preferences.
- Added Scrollable Menu Viewports And Compact Short-Terminal Navigation With A Persistent Keyboard Footer.

### Changed

- Replaced The Generic Demonstration Home Screen With The AIPM Project Dashboard.
- Preserved Unknown And Unverified Values When Core Does Not Supply Evidence.
- Refined Menu Styling: Selected Actions Use A Colored Arrow And Bright Text Without A Background Fill; Numbers And Descriptions Use Restrained Muted Tones.

## [0.2.1] — Product Shell, Capability Library, And Session Efficiency

### Added

- Added A Framed Product Header With The Name And Version Adjacent Across Primary Screens.
- Added Responsive Capability Tables With Imported Source Licenses And Explicitly Unverified Plugin Installation And Publication.
- Added A Session Snapshot Lifecycle So Core Facts Are Read Once At Startup And Again Only On Explicit Refresh.
- Added Stable Menu Geometry Reuse To Reduce Repeat Layout Work During Arrow Navigation.

### Changed

- Synchronized The AIPM Platform And TUI Package Versions At 0.2.1.
- Preserved The Protected Capability Registry Baseline And Existing Read-Only Behavior.

### Known Limits

- Actual Windows Terminal And Native Windows PowerShell 5.1 Visual Appearance Checks And Screenshots Remain Unverified.
- No Project Mutation, AI Session, Live Agent Session, Or Terminal-Independent Progress Calculation Is Claimed.
