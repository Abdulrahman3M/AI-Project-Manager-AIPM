# PowerShell TUI Architecture

## Ownership

- `Start-AIPM.ps1` Parses Launch Options And Restores Terminal State In `finally`.
- `Core/AipmClient.psm1` Finds AIPM Core, Checks Python, Invokes Whitelisted Read-Only CLI Commands With Argument Arrays And Timeouts, And Parses JSON Fail-Closed.
- `Core/App.psm1` Converts Core Responses Into Evidence-Based Display Summaries And Composes The Three View Modes. It Has No Project-State Writer.
- `Core/Platform.psm1` Owns Operating-System Detection; `Core/Settings.psm1` Owns UI-Only User Preferences; `Core/Process.psm1` Owns Child Process Invocation.
- `TUI/Input.psm1` Is The Only Keyboard Reader. `TUI/Theme.psm1` Owns Semantic Glyphs And Color Roles. `TUI/Renderer.psm1` Is The Only Screen Writer.
- `TUI/Menu.psm1`, `Dialog.psm1`, And `Prompt.psm1` Compose Shared Input And Rendering Primitives.

## State And Evidence

All Portfolio And Task State Comes From `Core-Engine/aipm.py dashboard`, Which Reads Registered Projects Through Core Engine `state.read`. The UI Never Writes Project State. Capability Metadata Comes From `aipm.py catalog`; It Is Read As-Is And Is Never Refreshed By The UI. `host-capabilities` Supplies Host Declarations, Not Proof That A Host Is Installed Or Has An Active Agent Session.

Progress Remains `Unknown` Without Verified Weights. Test Run Counts Remain `Unverified` Without A Test Artifact. An Agent Session Remains `Unknown` Without Host Process Evidence. Phase History And Event-Level Timeline Are Not Invented From A Single Current-State Manifest.

## Rendering

Frames Are Built In Memory, Compared Row-By-Row Including SGR Style Segments, And Only Changed Rows Are Written. A Style-Only Change Invalidates Its Row. Shrinking Frames Clear Removed Rows; Resize Invalidates The Cache In Place. Arrow Navigation Does Not Call `Clear-Host` Or CSI `2J`. When VT Is Not Available, The Legacy Console Uses Cursor Positioning, Semantic Console Colors, And Row Padding. Redirected Non-Scripted Launch Is Refused; Scripted Tests Use A Separate Buffer Sink.

The Renderer Tests Do Not Substitute For A Terminal Visual Session. Windows Terminal And Legacy Console Screenshots Remain Unverified Unless Captured In Those Actual Hosts.

## Security And Persistence

Only `health`, `dashboard`, `catalog`, And `host-capabilities` Are Available Through The PowerShell Client. The Client Does Not Accept Arbitrary Commands Or Invoke A Shell String. Project State Is Not Persisted In The UI. Only View Mode And Appearance Choices Use The Per-User Settings Store.
