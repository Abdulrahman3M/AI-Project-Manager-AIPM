# AI Project Manager

An Evidence-First, Read-Only PowerShell Terminal Dashboard For AIPM Core.

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

`-RegistryPath` Reads A Registry Through The Core Dashboard Command; It Does Not Write To It. `-ScriptedInput` Is Reserved For Tests. Exit Codes: `0` Normal Exit, `1` Unexpected Runtime Error, `2` Non-Interactive Launch Refused, `3` Required PowerShell Launcher Missing.

## View Modes

The Default Is **Task Dashboard**. Open **Settings** And **Change View Mode** To Select **Command Palette** Or **Assistant Console**. The Choice Is Stored As A Per-User UI Preference Only. Assistant Console Is An Offline, Read-Only Evidence View; It Does Not Claim An AI Or Agent Session.

All Modes Include **Projects**, **Tasks**, **Phases**, **Tests & Evidence**, **Agents & Handoffs**, **Timeline**, **Skills & Plugins**, **Settings**, **Help**, And **About**. Project Data Comes From AIPM Core. Missing Weights, Run Counts, Histories, Or Live Process Evidence Stay **Unknown** Or **Unverified**. No Project Mutations Are Available In This Phase.

## Keyboard

- **Up/Down** Moves The Highlight; **Enter** Opens Or Selects; **Esc** Goes Back.
- Type A Shown Number To Select Immediately In Numbered Or Hybrid Menus.
- Press **/** And Type To Filter Actions, Or Choose **Command Palette** For Search-First Navigation.
- Press **?** Or **F1** For Help. Press **Q** To Request Exit; The Dashboard Requires Confirmation.
- Descriptions Remain Visible Below Choices In Muted, Unshaded Text. The Selected Action Uses A Colored Arrow And Brighter Text Without A Background Fill, Including In No-Color Mode.

## Theme And Settings

The TUI Loads Semantic Color Roles And Icon Tiers From The Repository's `UX-TUI/theme.json` And `UX-TUI/semantic-icons.json`. Automatic Icons Prefer Emoji In A Detected Modern Terminal, Then Symbols, Then ASCII. Use `AIPM_ICONS=emoji|symbol|ascii|none` Or `NO_COLOR=1` To Override. Symbol Font And Width Differences Are Terminal-Dependent; Set `AIPM_ICONS=ascii` If A Glyph Is Unavailable.

Only UI Preferences Are Stored Under The Per-User `AIPM` Settings Directory (`%APPDATA%\AIPM` On Windows, `~/.config/AIPM` On Linux/macOS). `AIPM_DATA_DIR` Overrides That Location For Tests Or Portable Use. Core Project State Is Never Copied Into UI Settings.

## Verification And Limits

Automated Renderer Tests Cover Stable Frames, Changed-Row Styling, Removed Rows, Resize Invalidation, Cursor Restoration, Input Modes, Read-Only Core Integration, And The ASCII Fallback. This Does Not Prove Visual Appearance Or Flicker Behavior In A Specific Terminal. The P08 Verification Record Names The PowerShell Versions Run And Any Manual Terminal Checks That Remain Unverified. Files In `UX-TUI/Visual-References/` Are Illustrations, Not Application Screenshots.

For The Local Source Release, See The Repository [Support Matrix](../../Project-Documentation/Support-Matrix.md) And [Release Notes](../../Project-Documentation/Release-Notes-v1.0.2.md). The Archive Is Prepared Locally Only; It Does Not Install This TUI Into A Host Or Publish It.

## License And Notices

The AI Project Manager Personal Use License Applies To This TUI Package And Its AIPM-Owned Material.
