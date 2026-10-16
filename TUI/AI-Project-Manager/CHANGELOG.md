# AI Project Manager TUI Change Log

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
