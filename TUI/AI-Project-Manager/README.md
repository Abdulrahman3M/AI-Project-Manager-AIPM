# AI Project Manager

An Evidence-First PowerShell Terminal Workspace For AIPM Core, With Guarded Project-Registry Administration.

## Requirements

- Windows PowerShell 5.1 Or PowerShell 7.x.
- Python 3.10 Or Later On `PATH` (`python`, Then `python3`).
- A Real Interactive Terminal For Keyboard Navigation. Redirected Output Is Refused Unless Scripted Input Is Explicitly Supplied.
- The AIPM Repository Core And Capability Metadata In An Ancestor Project Folder.

## Start

On Windows, Run `AIPM.bat`. It Prefers Windows Terminal When Available, Starts PowerShell 7 First, And Falls Back To Windows PowerShell 5.1. Set `AIPM_TUI_WINDOW_HOST=console` To Force The Existing Console. On Linux Or macOS, Run `./AIPM.sh` From A Terminal With `pwsh` Installed.

```powershell
./Start-AIPM.ps1 -Version
./Start-AIPM.ps1 -RegistryPath 'C:\Path With Spaces\registry.json'
./tests/Run-Tests.ps1
```

On First Launch Without `-RegistryPath`, The TUI Asks Whether To Use `%LOCALAPPDATA%\AI-Project-Manager\registry.json` Or Choose Another `registry.json` Path Outside The AIPM Installation. It Stores That Choice In `%APPDATA%\AIPM\settings.json`. Passing `-RegistryPath` Explicitly Counts As Choosing The Path. `-ScriptedInput` Is Reserved For Tests. Exit Codes: `0` Normal Exit, `1` Unexpected Runtime Error, `2` Non-Interactive Launch Refused, `3` Required PowerShell Launcher Missing.

## View Modes

The Default Is **Task Dashboard**. Open **Settings** And **Change View Mode** To Select **Command Palette** Or **Assistant Console**. The Choice Is Stored As A Per-User UI Preference Only. Assistant Console Is An Offline, Read-Only Evidence View; It Does Not Claim An AI Or Agent Session.

All Modes Include **Projects**, **Tasks**, **Phases**, **Tests & Evidence**, **Agents & Handoffs**, **Timeline**, **Skills & Plugins**, **Registry Management**, **Settings**, **Help**, And **About**. The dashboard and project/task views are read-only. Registry Management can register a project (creating only `Shared-Project-State-Manager/` after confirmation), unregister its pointer without deleting any project files, back up or restore registry JSON, and switch registry locations. Missing weights, run counts, histories, or live process evidence stay **Unknown** or **Unverified**.

The registry contains project IDs, display names, and root paths only. Task and continuity state remains in each managed project's `Shared-Project-State-Manager/`. A registry backup includes a SHA-256 sidecar; restore validates it when present and saves a pre-restore safety copy. Switching locations does not copy or delete existing registries.

Task views in the TUI are read-only. Use the [Core CLI task workflow](../../docs/guides/Beginner-Guide.en.md#10-manage-a-task-and-hand-it-to-another-agent) to create tasks, record checkpoints, and manage task-only attachments. These commands do not edit target-project source files; AI Agents perform implementation work in the originals using their own host permissions.

## Keyboard

- **Up/Down** Moves The Highlight; **Enter** Opens Or Selects; **Esc** Goes Back.
- Type A Shown Number To Select Immediately In Numbered Or Hybrid Menus.
- Press **/** And Type To Filter Actions, Or Choose **Command Palette** For Search-First Navigation.
- Press **?** Or **F1** For Help. Press **Q** To Request Exit; The Dashboard Requires Confirmation.
- Descriptions Remain Visible Below Choices In Muted, Unshaded Text. The Selected Action Uses A Colored Arrow And Brighter Text Without A Background Fill, Including In No-Color Mode.

## Theme And Settings

The TUI Loads Semantic Color Roles And Icon Tiers From The Repository's `UX-TUI/theme.json` And `UX-TUI/semantic-icons.json`. Automatic Icons Prefer Emoji In A Detected Modern Terminal, Then Symbols, Then ASCII. Use `AIPM_ICONS=emoji|symbol|ascii|none` Or `NO_COLOR=1` To Override. Symbol Font And Width Differences Are Terminal-Dependent; Set `AIPM_ICONS=ascii` If A Glyph Is Unavailable.

UI Preferences And The Selected Registry Path Are Stored Under The Per-User `AIPM` Settings Directory (`%APPDATA%\AIPM` On Windows, `~/.config/AIPM` On Linux/macOS). The registry itself defaults to `%LOCALAPPDATA%\AI-Project-Manager\registry.json` on Windows. `AIPM_DATA_DIR` Overrides The UI Settings Location For Tests Or Portable Use. Project State Is Never Copied Into UI Settings Or The AIPM Repository.

## Safety Boundary

AIPM Core refuses to manage a project, registry, or registry backup whose path overlaps the AIPM installation. This prevents AIPM's own project-management functions from writing into its source tree. It is not a Windows security boundary: another AI process with direct write permission can bypass Core. Keep AIPM outside the agent's writable workspace or restrict it through the host sandbox/Windows ACL. Only a direct, explicit request to develop or repair AIPM authorizes changes to its files.

## Verification And Limits

Automated Renderer Tests Cover Stable Frames, Changed-Row Styling, Removed Rows, Resize Invalidation, Cursor Restoration, Input Modes, Read-Only Core Integration, And The ASCII Fallback. This Does Not Prove Visual Appearance Or Flicker Behavior In A Specific Terminal. Historical P08 implementation evidence is preserved in the repository [Build History Archive](../../docs/project/Build-History-Archive.zip); current verification limits are in the repository Support Matrix. Files In `UX-TUI/Visual-References/` Are Illustrations, Not Application Screenshots.

For Published-Release And Local-Version Status, See The Repository [Support Matrix](../../docs/project/Support-Matrix.md) And [Versioned Update Notes](../../docs/project/Release-Notes/Release-Notes-v1.1.7.md). Repository Versioning Does Not Install The TUI Into An AI Host.

## License And Notices

The AI Project Manager Personal Use License Applies To This TUI Package And Its AIPM-Owned Material.
