# PowerShell TUI Architecture

## Ownership

- `Start-AIPM.ps1` Parses Launch Options And Restores Terminal State In `finally`.
- `Core/AipmClient.psm1` Finds AIPM Core, Checks Python, Invokes A Whitelisted CLI With Argument Arrays And Timeouts, And Parses JSON Fail-Closed.
- `Core/App.psm1` Converts Core Responses Into Evidence-Based Display Summaries, Composes The Three View Modes, And Orchestrates Explicit Registry Operations Through The Core CLI. It Does Not Write Registry Or Project-State Files Directly.
- `Core/Platform.psm1` Owns Operating-System Detection; `Core/Settings.psm1` Owns UI-Only User Preferences; `Core/Process.psm1` Owns Child Process Invocation.
- `TUI/Input.psm1` Is The Only Keyboard Reader. `TUI/Theme.psm1` Owns Semantic Glyphs And Color Roles. `TUI/Renderer.psm1` Is The Only Screen Writer.
- `TUI/Menu.psm1`, `Dialog.psm1`, And `Prompt.psm1` Compose Shared Input And Rendering Primitives.

## State And Evidence

Portfolio And Task State Comes From `Core-Engine/aipm.py dashboard`, Which Reads Registered Projects Through Core Engine `state.read`. Capability Metadata Comes From `aipm.py catalog`; It Is Read As-Is And Is Never Refreshed By The UI. `host-capabilities` Supplies Host Declarations, Not Proof That A Host Is Installed Or Has An Active Agent Session.

The first launch asks the owner to use the default `%LOCALAPPDATA%\AI-Project-Manager\registry.json`, connect an existing registry file, or choose another complete file path outside the AIPM installation. Existing files are validated with a read-only Core operation and are never overwritten during connection. The selected path is remembered in per-user `settings.json`. Registry Management offers project listing, registration, pointer-only unregistration, checksummed backup, validated restore with a pre-restore copy, switching locations, and connecting an existing registry. Registry files contain project paths only; project folders must exist at those paths on the current device. Registering creates `Shared-Project-State-Manager/` in the selected project only after confirmation; no project source file is changed. Switching locations leaves the old registry untouched and does not copy its data.

The **Tasks** TUI workflow re-reads the selected registry, requires the user to select a registered project, and then offers task creation, existing-work-folder context, task listing/opening, and task-state updates. Selecting a task opens its management action menu directly; the current status and task ID are shown there, while the longer status page is an explicit action. Core derives task status from recorded blockers, verification, and report evidence; the UI does not expose a manual status toggle. Existing work folders are referenced in task scope; they are never moved or copied. Task creation, plans, progress checkpoints, blockers, verification evidence, reports, and supporting-artifact attachment/listing are performed through a fixed Core command allowlist. **View Attached Task Files** alone enables `/` search: it matches full or partial artifact paths case-insensitively, marks exact filename/path matches, and supports clearing the query to restore the full inventory. Attaching a selected supporting file copies it into the task's declared category and leaves the original unchanged; file size and safe-path rules are enforced by Core. Core owns only task metadata and task-supporting files inside the project's state directory. It exposes no target-project implementation write/delete/execute API and does not run target-project tests or add an AIPM approval gate to source edits. Agents make implementation changes in the original project files using the permissions supplied by the project owner and their AI host. See the [beginner guide's task handoff workflow](../../../docs/guides/Beginner-Guide.en.md#10-manage-a-task-and-hand-it-to-another-agent).

Core rejects managed project roots, registry paths, and backup paths that overlap its detected AIPM installation. The root `AGENTS.md` repeats the owner-authorization rule. Neither safeguard is an OS sandbox: direct filesystem writes by an external agent must be restricted by its host workspace permissions or Windows ACLs.

Progress Remains `Unknown` Without Verified Weights. Test Run Counts Remain `Unverified` Without A Test Artifact. An Agent Session Remains `Unknown` Without Host Process Evidence. Phase History And Event-Level Timeline Are Not Invented From A Single Current-State Manifest.

## Rendering

Frames Are Built In Memory, Compared Row-By-Row Including SGR Style Segments, And Only Changed Rows Are Written. A Style-Only Change Invalidates Its Row. Shrinking Frames Clear Removed Rows; Resize Invalidates The Cache In Place. Arrow Navigation Does Not Call `Clear-Host` Or CSI `2J`. When VT Is Not Available, The Legacy Console Uses Cursor Positioning, Semantic Console Colors, And Row Padding. Redirected Non-Scripted Launch Is Refused; Scripted Tests Use A Separate Buffer Sink.

Long Read-Only Information Pages Are Wrapped And Paginated To Fit The Current Terminal Height. Up/Down And PageUp/PageDown Move Between Pages; Enter/Esc Return To The Previous View. This Keeps Long Attached-Artifact Inventories Reachable Without Requiring A Larger Window.

The Renderer Tests Do Not Substitute For A Terminal Visual Session. Windows Terminal And Legacy Console Screenshots Remain Unverified Unless Captured In Those Actual Hosts.

## Security And Persistence

Only A Fixed, Whitelisted Set Of Health, Dashboard, Catalog, Registry, And Task Commands Is Available Through The PowerShell TUI Client. The Client Does Not Accept Arbitrary Commands Or Invoke A Shell String. Task mutations are limited to task records in AIPM-owned state; they cannot edit project source files. Registry, task, and project-state operations are validated by Core; only view mode, appearance choices, and the selected registry path use the per-user settings store.

## Release Packaging

`Maintenance-Tools/New-Release-Package.py` Creates The Local AIPM Source Archive. It Selects Only Public Runtime, Capability, Documentation, And Provenance Inputs; excludes Internal Test And Phase-Evidence Data; uses Fixed ZIP Metadata And Sorted Entries; writes A SHA-256 Sidecar; and embeds A Manifest With A Hash For Every Payload File. The Builder Fails Closed On Reparse Points, Sensitive-Looking Files, Credential-Like Content, Or The Actual Local Checkout Path. The Archive Is Local Only And Does Not Install The TUI Or Grant Any Host Access.
