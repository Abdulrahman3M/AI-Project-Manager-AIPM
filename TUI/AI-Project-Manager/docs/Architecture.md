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

The first launch asks the owner to approve the default `%LOCALAPPDATA%\AI-Project-Manager\registry.json` or enter another complete file path outside the AIPM installation. Any filename ending in `.json` is accepted; a folder path alone is not. The selected path is remembered in per-user `settings.json`. Registry Management offers project listing, registration, pointer-only unregistration, checksummed backup, validated restore with a pre-restore copy, and switching to another registry location. Registering creates `Shared-Project-State-Manager/` in the selected project only after confirmation; no project source file is changed. Switching locations leaves the old registry untouched and does not copy its data.

The TUI's project/task views are read-only. Task creation, checkpointing, and task-artifact operations are exposed by the Core CLI/API, not by the TUI. Core owns only task metadata and task-supporting files inside the project's state directory. It exposes no target-project implementation write/delete/execute API and does not run target-project tests or add an AIPM approval gate to source edits. Agents make implementation changes in the original project files using the permissions supplied by the project owner and their AI host. See the [beginner guide's task handoff workflow](../../../docs/guides/Beginner-Guide.en.md#10-manage-a-task-and-hand-it-to-another-agent).

Core rejects managed project roots, registry paths, and backup paths that overlap its detected AIPM installation. The root `AGENTS.md` repeats the owner-authorization rule. Neither safeguard is an OS sandbox: direct filesystem writes by an external agent must be restricted by its host workspace permissions or Windows ACLs.

Progress Remains `Unknown` Without Verified Weights. Test Run Counts Remain `Unverified` Without A Test Artifact. An Agent Session Remains `Unknown` Without Host Process Evidence. Phase History And Event-Level Timeline Are Not Invented From A Single Current-State Manifest.

## Rendering

Frames Are Built In Memory, Compared Row-By-Row Including SGR Style Segments, And Only Changed Rows Are Written. A Style-Only Change Invalidates Its Row. Shrinking Frames Clear Removed Rows; Resize Invalidates The Cache In Place. Arrow Navigation Does Not Call `Clear-Host` Or CSI `2J`. When VT Is Not Available, The Legacy Console Uses Cursor Positioning, Semantic Console Colors, And Row Padding. Redirected Non-Scripted Launch Is Refused; Scripted Tests Use A Separate Buffer Sink.

The Renderer Tests Do Not Substitute For A Terminal Visual Session. Windows Terminal And Legacy Console Screenshots Remain Unverified Unless Captured In Those Actual Hosts.

## Security And Persistence

Only A Fixed, Whitelisted Set Of Health, Dashboard, Catalog, And Registry Commands Is Available Through The PowerShell TUI Client. The Client Does Not Accept Arbitrary Commands Or Invoke A Shell String. Separate Core CLI task commands manage only AIPM-owned task records and supporting artifacts. Registry, task, and project-state operations are validated by Core; only view mode, appearance choices, and the selected registry path use the per-user settings store.

## Release Packaging

`Maintenance-Tools/New-Release-Package.py` Creates The Local AIPM Source Archive. It Selects Only Public Runtime, Capability, Documentation, And Provenance Inputs; excludes Internal Test And Phase-Evidence Data; uses Fixed ZIP Metadata And Sorted Entries; writes A SHA-256 Sidecar; and embeds A Manifest With A Hash For Every Payload File. The Builder Fails Closed On Reparse Points, Sensitive-Looking Files, Credential-Like Content, Or The Actual Local Checkout Path. The Archive Is Local Only And Does Not Install The TUI Or Grant Any Host Access.
