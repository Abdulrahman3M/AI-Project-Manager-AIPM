# AI Project Manager TUI Change Log

## [1.4.6] — Repository Version Synchronization (Not Published)

- Synchronized the TUI version with AIPM `1.4.6` for the documentation-only repository update. No TUI behavior changed; no GitHub Release or tag was created.

## [1.4.5] — Managed Input And Frame Lifecycle

- Synchronizes the TUI package with AIPM `1.4.5`; this release carries no TUI product behavior change beyond the accompanying platform release metadata.

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
