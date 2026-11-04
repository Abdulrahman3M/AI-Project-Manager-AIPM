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

On First Launch Without `-RegistryPath`, The TUI Lets You Use The Default Registry, Connect An Existing Registry File, Or Choose A Different Location. An Existing Registry Must Be A Valid `.json` File; AIPM Validates It Read-Only And Does Not Replace Its Contents. Its Project Root Paths Must Exist On This Device; A Registry Does Not Copy Project Folders. The Choice Is Saved In `%APPDATA%\AIPM\settings.json`. The **Registry Management** Screen Also Offers **Connect Existing Registry File**. Passing `-RegistryPath` Explicitly Counts As Choosing The Path. `-ScriptedInput` Is Reserved For Tests. Exit Codes: `0` Normal Exit, `1` Unexpected Runtime Error, `2` Non-Interactive Launch Refused, `3` Required PowerShell Launcher Missing.

## View Modes

The Default Is **Task Dashboard**. Open **Settings** And **Change View Mode** To Select **Command Palette** Or **Assistant Console**. The Choice Is Stored As A Per-User UI Preference Only. Assistant Console Is An Offline, Read-Only Evidence View; It Does Not Claim An AI Or Agent Session.

All Modes Include **Projects**, **Tasks**, **Phases**, **Tests & Evidence**, **Agents & Handoffs**, **Timeline**, **Skills & Plugins**, **Registry Management**, **Settings**, **Help**, And **About**. Registered projects appear inside **Projects**, not as separate dashboard actions. After registration, return to the dashboard, choose **Refresh**, then open **Projects** to review the project. **Tasks** first refreshes the registry and asks you to select a registered project; it then lets you create a task, create task context for an existing work folder, or open and update an existing task. Task changes are made through whitelisted Core operations and affect only AIPM-owned state under that project's `Shared-Project-State-Manager/`; project source files remain in their original locations. Registry Management can connect an existing registry without rewriting it, register a project, unregister its pointer without deleting any project files, back up or restore registry JSON, and switch registry locations. Missing weights, run counts, histories, or live process evidence stay **Unknown** or **Unverified**.

Registration offers Git, then FIRG when Git is available at the project root, then Shared Project State Manager. The first two are optional; shared state is required for registration. Declining shared state does not undo optional steps already chosen. FIRG installs its own directory and adds an instruction section to the root `AGENTS.md`; existing FIRG, translated instruction editions, or versioned instruction metadata require review rather than automatic rewriting. An interrupted installation is identified and can be resumed through **Install FIRG** if its files and root instructions remain unchanged. A project under a parent Git repository is not treated as its own repository root. **Update Project** inspects registered projects, adds optional components on request, updates unmodified AIPM-managed FIRG files with a backup, and opens existing state recovery. An interrupted FIRG update is shown explicitly and can be resumed through **Update FIRG**; files modified since the interruption stop the update for review. Component choices are stored in project state; legacy projects without choices are reported as unknown or missing rather than assumed declined.

On entering task management, a background process reports component status without waiting for the check to finish. The check is a quick inspection, not a full state integrity audit. **Upgrade Shared State** previews a supported 1.0-to-1.1 schema upgrade and, after confirmation, backs up state and records an upgrade event. A pending transaction or task normalization requirement must be resolved through state recovery first. AIPM offers FIRG documentation after a commit made through its task interface. If no existing hook or custom hooks path conflicts, FIRG also installs a local post-commit prompt for interactive Git terminals. Hooks are bypassable and non-interactive clients cannot present the prompt; `commit-status` identifies missed commits. Test evidence is initially unverified until supplied.

The Git version check compares the installed executable with AIPM's conservative offline baseline of `2.20.0`; meeting the baseline is not proof that every Git version has been tested and does not establish whether a newer release exists. On Git for Windows, **Open Git For Windows Updater** offers to launch its [official interactive updater](https://gitforwindows.org/faq) in a separate window after explicitly describing its network and system-installation effects. AIPM reports only that the updater started; complete or cancel it there, restart AIPM, and recheck the version. Other distributions use their own package manager or installer. An actual Git installation update has not been tested as part of this local verification.

Future managed FIRG updates can replace the previously installed root instruction section only when it still matches the recorded version. AIPM backs up the root instruction file and preserves unrelated text; locally edited sections, translated editions, or metadata-governed instruction files require review instead.

**Restore Missing FIRG Files** restores only missing managed files whose shipped bytes match the installed baseline; it does not overwrite local edits. Missing configuration requires review. A missing ledger can be restored as empty only when the registry is empty; otherwise use FIRG's ledger regeneration workflow after reviewing the records.

The registry contains project IDs, display names, and root paths only. Task and continuity state remains in each managed project's `Shared-Project-State-Manager/`. A registry backup includes a SHA-256 sidecar; restore validates it when present and saves a pre-restore safety copy. Switching or connecting locations does not copy or delete existing registries.

The TUI supports creating tasks, attaching an existing work folder as task context, and opening a task directly into its management action menu. The current status is visible there; the detailed status page is optional. Core derives status from blockers, verification, and report evidence rather than a manual status toggle. Users can update plans, progress checkpoints, blockers, verification evidence, and report notes, attach plan/report/handoff/supporting files into task categories, and list attached files. Inside **View Attached Task Files**, press **/** to search by a full or partial filename or relative path. A blank search restores the complete list; the results show whether an exact file match exists and list partial matches with their paths and SHA-256 hashes. Attaching copies one selected file into AIPM task state, leaves its original unchanged, enforces the Core 16 MiB limit, and never silently overwrites an existing artifact. These operations update AIPM-owned task state only; AI Agents perform implementation work in the original project files using their own host permissions. See the [beginner task workflow](../../docs/guides/Beginner-Guide.en.md#10-manage-a-task-and-hand-it-to-another-agent).

## Keyboard

- **Up/Down** Moves The Highlight; **Enter** Opens Or Selects; **Esc** Goes Back.
- Type A Shown Number To Select Immediately In Numbered Or Hybrid Menus.
- Press **/** And Type To Filter Actions, Or Choose **Command Palette** For Search-First Navigation.
- Press **?** Or **F1** For Help. Press **Q** To Request Exit; The Dashboard Requires Confirmation. Pressing **Esc** At The Dashboard Also Shows The Exit Confirmation Before Returning To PowerShell.
- Descriptions Remain Visible Below Choices In Muted, Unshaded Text. The Selected Action Uses A Colored Arrow And Brighter Text Without A Background Fill, Including In No-Color Mode.

## Theme And Settings

The TUI Loads Semantic Color Roles And Icon Tiers From The Repository's `UX-TUI/theme.json` And `UX-TUI/semantic-icons.json`. Automatic Icons Prefer Emoji In A Detected Modern Terminal, Then Symbols, Then ASCII. Use `AIPM_ICONS=emoji|symbol|ascii|none` Or `NO_COLOR=1` To Override. Symbol Font And Width Differences Are Terminal-Dependent; Set `AIPM_ICONS=ascii` If A Glyph Is Unavailable.

UI Preferences And The Selected Registry Path Are Stored Under The Per-User `AIPM` Settings Directory (`%APPDATA%\AIPM` On Windows, `~/.config/AIPM` On Linux/macOS). The registry itself defaults to `%LOCALAPPDATA%\AI-Project-Manager\registry.json` on Windows. `AIPM_DATA_DIR` Overrides The UI Settings Location For Tests Or Portable Use. Project State Is Never Copied Into UI Settings Or The AIPM Repository.

## Safety Boundary

AIPM Core refuses to manage a project, registry, or registry backup whose path overlaps the AIPM installation. This prevents AIPM's own project-management functions from writing into its source tree. It is not a Windows security boundary: another AI process with direct write permission can bypass Core. Keep AIPM outside the agent's writable workspace or restrict it through the host sandbox/Windows ACL. Only a direct, explicit request to develop or repair AIPM authorizes changes to its files.

## Verification And Limits

Automated Renderer Tests Cover Stable Frames, Changed-Row Styling, Removed Rows, Resize Invalidation, Cursor Restoration, Input Modes, Read-Only Core Integration, And The ASCII Fallback. This Does Not Prove Visual Appearance Or Flicker Behavior In A Specific Terminal. Historical P08 implementation evidence is preserved in the repository [Build History Archive](../../docs/project/Build-History-Archive.zip); current verification limits are in the repository Support Matrix. Files In `UX-TUI/Visual-References/` Are Illustrations, Not Application Screenshots.

For Published-Release And Local-Version Status, See The Repository [Support Matrix](../../docs/project/Support-Matrix.md) And [Development Change Log](../../CHANGELOG.md). Repository Versioning Does Not Install The TUI Into An AI Host.

## License And Notices

The Apache License 2.0 Applies To This TUI Package And Its AIPM-Owned Material. Copyright 2026 Abdulrahman Elbatrah. See [NOTICE](NOTICE) For Attribution.
