# AI Project Manager Beginner Guide

Welcome to **AI Project Manager (AIPM)**. This guide assumes you are new to the project and explains how to get it, open it, understand what you see, and work with its approved capabilities safely.

> **Important:** AIPM manages task context and supporting files under `Shared-Project-State-Manager/`; it does not edit, test, or approve changes to your project's source files. AI Agents work on the originals in your project folder under the permissions of your project and AI host. The TUI can create and manage task records, while keeping project source files untouched. The Agent Bridge is a package sample, not an installed agent or an automatic file-access grant.

## 1. What AIPM Does

AIPM keeps project information understandable and evidence-based for people and AI-assisted work:

| Part | In Simple Terms |
| --- | --- |
| Core Engine | Reads and validates project state; it also provides task and handoff commands. |
| Capability Library | Keeps an approved catalog of Skills and Prompts with version and provenance records. |
| PowerShell TUI | Shows a keyboard-driven dashboard, project registry controls, and guided task management. |
| Project Agent Bridge | Describes how a compatible agent could work with AIPM; the included package is not installed or active. |
| Host Adapters | Describe permitted integrations and deny unsupported operations by default. |

## 2. Prepare Your Computer

Use Windows PowerShell 5.1 or PowerShell 7.x (`pwsh`). Install Python 3.10 or later and make sure `python` works in a new terminal. Keyboard navigation requires a real interactive terminal, such as Windows Terminal; redirected or piped input is not an interactive session.

Check the tools:

```powershell
python --version
pwsh --version
```

If `pwsh` is not installed, you can still use the Windows PowerShell 5.1 launcher provided by the project.

## 3. Get The Project

If you have access to the owner’s GitHub repository, clone it:

```powershell
git clone https://github.com/Abdulrahman3M/AI-Project-Manager-AIPM.git
Set-Location AI-Project-Manager-AIPM
```

If you received a ZIP instead, extract it to a folder you control, open PowerShell in that folder, and continue. The project root is the folder containing `README.md`, `VERSION`, `Core-Engine`, and `TUI`.

Before using or redistributing project material, read the root [Apache License 2.0](../../LICENSE).

## 4. Learn The Folder Map

You do not need to open every folder before starting. These are the useful places for a new user:

| Folder Or File | What It Is For |
| --- | --- |
| `README.md` | Short project overview and quick links. |
| `Core-Engine/` | Project state, task lifecycle, handoffs, and CLI commands. |
| `TUI/AI-Project-Manager/` | PowerShell terminal app and its usage notes. |
| `01-Skills-General/` | Owner-managed General Skills. |
| `02-Prompt-General/` | Reusable standalone Prompts. |
| `Capability-Library/` | Protected catalog and first-party Skill declarations. |
| `Plugins/` | Host adapter specifications and the generated bridge package. |
| `docs/` | User guides and project governance/evidence documents. |

## 5. Open The Terminal Dashboard

From the repository root, run:

```powershell
TUI\AI-Project-Manager\AIPM.bat
```

The launcher chooses an available supported PowerShell host. To start the app directly with PowerShell 7, use:

```powershell
pwsh -NoProfile -File TUI\AI-Project-Manager\Start-AIPM.ps1
```

To request Windows PowerShell 5.1 explicitly:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File TUI\AI-Project-Manager\Start-AIPM.ps1
```

On the first launch, the TUI lets you use the default registry, connect an existing registry file, or choose another location. The dashboard offers sections for projects, tasks, phase records, test evidence, handoffs, Skills, Prompts, and settings. Registered project names appear inside **Projects**, not as separate dashboard actions. The **Registry Management** screen can connect an existing registry, add/remove project pointers, change the selected registry, and back it up or restore it. The **Tasks** section first refreshes the registry and requires you to choose a registered project before it can create or manage that project's task records. These task operations update AIPM-owned state only, never project source files.

## 6. Choose Where AIPM Stores Its Project List

The registry is a small private file that stores each project's ID, display name, and folder path. It does not contain your project files or task history.

On Windows, the default is:

```text
%LOCALAPPDATA%\AI-Project-Manager\registry.json
```

For your Windows account, `%LOCALAPPDATA%` usually expands to:

```text
C:\Users\YourWindowsName\AppData\Local
```

So the usual full path is:

```text
C:\Users\YourWindowsName\AppData\Local\AI-Project-Manager\registry.json
```

This is per-user application data, not a second AIPM installation and not a folder inside any project. On a new device, choose **Use An Existing Registry File** during first-run setup and enter the full path to the registry JSON you copied to that device. You can also choose **Registry Management → Connect Existing Registry File** later. AIPM validates the file read-only and saves the selection in `%APPDATA%\AIPM\settings.json`; it does not rewrite the registry. The file stores project paths, not project folders or task state. Those project folders must exist at the recorded paths on this device, or their entries will appear unverified. If you choose a new location instead, enter a complete file path outside the AIPM installation; any file name ending in `.json` is accepted, but entering only a folder is not enough. Passing `-RegistryPath` when starting AIPM is also treated as choosing the path.

Project operational state is separate: for each registered project, AIPM stores it in that project's own `Shared-Project-State-Manager/` folder. The central registry stays small while each project's working state stays with that project.

For sample task plans, handoffs, and file-operation notes, see [`Templates/Shared-Project-State-Manager-Example/`](../../Templates/Shared-Project-State-Manager-Example/README.md). It is fictional learning material, not a live project or a folder to register/copy wholesale. Register your project first so Core creates fresh project-specific state; then consult or adapt individual example documents. Never copy the example manifest over the generated runtime manifest.

## 7. Navigate The Screens

- Press **Up** or **Down** to move the selection.
- Press **Enter** to open the selected item.
- Type a displayed number to choose that numbered item.
- Press **/** to search or filter where available.
- Press **?** or **F1** for help.
- Press **Esc** to return to the previous screen. At the main dashboard, **Esc** shows an exit confirmation instead of closing PowerShell immediately; choose **Stay Here** to remain in AIPM.
- Press **Q** to exit and confirm when prompted.

The selected row is identified by a colored arrow and brighter text. Descriptions below menu items are intentionally not selected or shaded. If a symbol does not display correctly, start with the ASCII icon setting described in the [TUI User Guide](../../TUI/AI-Project-Manager/README.md).

## 8. Register And Manage A Project Safely

In the dashboard, choose **Registry Management**. To register a project:

1. Choose **Register A Project**.
2. Enter the full path to an existing project folder. Do not select the AIPM folder or a parent folder that contains AIPM; Core blocks overlapping paths.
3. Enter or accept the project display name.
4. Read the confirmation: it states that AIPM will create `Shared-Project-State-Manager/` under that project and will not edit source files.
5. Choose **Create State And Register** only if you want that state folder and registry entry.

The registry then stores an ID, name, and root path. Your code, documents, Git metadata, and other existing project files are not modified. Task and continuity records that AIPM owns remain inside its state folder. After successful registration, the TUI displays a message asking you to return to the dashboard and choose **Refresh**. Then open **Projects**; the registered project appears there, not as a separate dashboard action.

Other registry actions:

- **View Registered Projects** lists each project's name, ID, and root folder.
- **Unregister A Project** removes only that project's pointer from the selected registry. It does not delete the project or its state folder.
- **Back Up Registry** writes a new JSON backup and a `.sha256` checksum file. It will not overwrite an existing file.
- **Restore Registry Backup** checks the checksum when its sidecar exists and automatically saves a pre-restore backup before changing the registry.
- **Change Registry Location** selects or creates another registry. It does not copy or delete the previous registry; back it up first if you need to preserve its contents.
- **Connect Existing Registry File** validates and selects an existing `.json` registry without replacing its contents. Use this when moving your AIPM setup to another device; make sure project folders exist at the paths recorded in that file.

Never place the registry or backup inside the AIPM installation. Core rejects AIPM-root and overlapping paths.

## 9. Read Core Information From PowerShell

Run these commands from the repository root. They print JSON that you can read or save for your own review:

```powershell
python Core-Engine\aipm.py health
python Core-Engine\aipm.py catalog
python Core-Engine\aipm.py host-capabilities
python Core-Engine\aipm.py dashboard
```

`health` reports that the Core CLI starts. `catalog` lists capability metadata; it does not prove that a host installed or invoked a Skill. `host-capabilities` lists declared adapter permissions. `dashboard` reads the configured project registry and state.

To inspect a project registry explicitly, pass its path. Replace the example path and ID with values supplied by your administrator:

```powershell
python Core-Engine\aipm.py list --registry "C:\path\to\project-registry.json"
python Core-Engine\aipm.py inspect --registry "C:\path\to\project-registry.json" --project-id "YOUR_PROJECT_ID"
python Core-Engine\aipm.py state-read --registry "C:\path\to\project-registry.json" --project-id "YOUR_PROJECT_ID"
```

The CLI also offers explicit registry commands for scripting. Use real, authorized paths and IDs. Registering creates an AIPM-owned state folder in the selected project; unregistering removes only the registry pointer.

```powershell
python Core-Engine\aipm.py registry-init --registry "$env:LOCALAPPDATA\AI-Project-Manager\registry.json"
python Core-Engine\aipm.py registry-register --registry "$env:LOCALAPPDATA\AI-Project-Manager\registry.json" --project-root "D:\Work\My-Project" --project-id "my-project" --alias "My Project"
python Core-Engine\aipm.py registry-backup --registry "$env:LOCALAPPDATA\AI-Project-Manager\registry.json" --destination "$env:USERPROFILE\Documents\registry-backup.json"
python Core-Engine\aipm.py registry-unregister --registry "$env:LOCALAPPDATA\AI-Project-Manager\registry.json" --project-id "my-project"
python Core-Engine\aipm.py registry-restore --registry "$env:LOCALAPPDATA\AI-Project-Manager\registry.json" --source "$env:USERPROFILE\Documents\registry-backup.json"
```

For regular registry use, prefer the TUI confirmations. Do not commit a personal registry or its backups to GitHub or a source archive; they can reveal private project folder paths.

## 10. Manage A Task And Hand It To Another Agent

Each registered project stores independent task records and supporting files under its own `Shared-Project-State-Manager/Tasks/<Task-ID>/` folder. For the normal beginner workflow, no commands are needed:

1. From the dashboard, choose **Tasks**.
2. AIPM refreshes the selected registry. If it is empty, choose **Register A Project First**, finish project registration, then return to **Tasks**.
3. Select the registered project that owns this work. A folder of tasks is not itself a project unless it is an independent project workspace.
4. Choose **Create New Task** to create a fresh AIPM task record, or **Add Existing Work Folder** to register a folder that already exists inside the selected project. AIPM keeps the original files in place and stores a dated inventory in the task references so a later agent can identify the registered work.
5. Choose **Open Existing Task** and select the task. Its **Manage Task** action menu opens immediately; the current status and task ID appear in the menu header. Choose **Mark Task Complete** to close it with a completion note, or **Reopen Task** when follow-up work is required. **Archive Completed Task** creates an integrity-verified ZIP and SHA-256 checksum under `Shared-Project-State-Manager/Archive`, containing complete task metadata and step history in `Metadata.json`. Once verified, AIPM prompts whether to delete the live task folder or keep it; the system can inspect task details and attachments directly from the archive metadata at any time, and reopening automatically restores the task folder if deleted. After the folder is deleted, AIPM also offers to remove the task from the AIPM registry (`State-Manifest.json`); the verified archive is always kept. `Metadata.json` stores the complete task record and its command history, so the ZIP can be moved anywhere and later restored with **Task Management > Import Archived Task From ZIP**, which verifies the archive, re-registers the task, and restores its folder even if the registry entry was deleted. Use **View Task Status And Details** for the longer status page. AIPM records evidence; it does not run the project's tests.
6. To attach a report or plan file, choose **Attach Plan, Report Or Supporting File**, select **Reports** or **Instructions And Plans**, enter the full path to the existing file, confirm the task filename, and approve the copy. AIPM copies the selected file into that task's supporting-artifact folder; the original stays in place. Files are limited to 16 MiB, and an existing artifact is never silently overwritten. Choose **View Attached Task Files** to review attachments. Long lists show a page counter; use Up/Down or PageUp/PageDown to browse all entries, including Reports near the end. From this screen only, press **/** and enter a full or partial filename or relative path. An exact-match result confirms whether that file is attached; partial matches show candidate paths and hashes. Leave the search empty to restore the full list. Press Enter/Esc to return. **Update Task Report** saves a short note in task state; it does not attach a document.
7. Give the AI Agent the task name/ID and ask it to work on the original project files. Put only instructions, handoffs, reports, scripts, examples, or references that the agent needs under the task's declared support folders. Keep source files in the project tree.

Advanced users can also manage tasks from the Core CLI. To use those commands, set the AIPM installation folder, registry path, and registered project ID, then run them in PowerShell:

If the files you are working on are already inside a task subfolder of a registered project, do **not** register that subfolder as a project. Create a task under the registered project's ID and mention the existing folder path in the task scope or instructions. AIPM creates its own task-state folder; the agent continues working with the existing files in their original folder. Use a descriptive task title—AIPM generates a unique `Task-ID`; names such as `Task 01` are not required. Register a folder as a separate project only when it is an independent project workspace.

```powershell
$aipmRoot = 'C:\Path\To\AI-Project-Manager-AIPM'
$registry = Join-Path $env:LOCALAPPDATA 'AI-Project-Manager\registry.json'
$projectId = 'YOUR_PROJECT_ID'
$cli = Join-Path $aipmRoot 'Core-Engine\aipm.py'

$createdJson = python $cli task-create --registry $registry --project-id $projectId --title 'Add Search' --scope 'Add and verify search in the existing application.'
if ($LASTEXITCODE -ne 0) { throw 'Could not create the task.' }
$created = $createdJson | ConvertFrom-Json
$taskId = $created.task.task_id
$taskId
```

Keep the returned task ID. Add a plan and, when useful, import a task-supporting instruction or reference file. Import only material that helps an agent understand or resume the task—do not import copies of source files that the agent should edit in place.

```powershell
python $cli task-plan --registry $registry --project-id $projectId --task-id $taskId --text 'Inspect existing search behavior; implement in the original project files; run the project tests.'
python $cli task-artifact-write --registry $registry --project-id $projectId --task-id $taskId --relative-path 'Instructions/Task-Instructions.md' --from-file 'D:\Work\My-Project\Task-Instructions.md'
```

While working, the agent edits the original project files itself. At a pause or handoff, record what was actually verified and exactly what remains. File paths in `--changed-file` refer to files in the original project; AIPM does not copy or modify them.

```powershell
python $cli task-checkpoint --registry $registry --project-id $projectId --task-id $taskId `
  --last-verified-action 'Search form is implemented in the original src files.' `
  --next-action 'Run the focused UI tests, inspect the diff, and fix any failures.' `
  --completed-work 'Added the search form and connected the existing query handler.' `
  --changed-file 'src/SearchForm.tsx' `
  --test-result 'UNVERIFIED: focused tests have not been run.'
python $cli task-read --registry $registry --project-id $projectId --task-id $taskId
python $cli task-artifact-list --registry $registry --project-id $projectId --task-id $taskId
```

The next agent should open the same project folder, read `Task-State.md` and `Handoff/Next-Agent-Handoff.md` plus any instructions/references, then check the current original source, Git diff, and test evidence before continuing. Do not trust an old note as proof that the source still matches. AIPM records agent-reported evidence; it does not run project tests or place an AIPM approval gate on source edits.

Other commands include `task-list`, `task-blocker-add`, `task-blocker-clear`, `task-verify`, `task-report`, and `task-artifact-read`. Artifact writes are confined to task categories and limited to 16 MiB per file. Existing artifacts cannot be silently overwritten; pass the current `--expected-sha256` when updating one.

## 11. Understand Skills, Prompts, And The Agent Bridge

The owner may add or remove Skills under `01-Skills-General/` and standalone Prompts under `02-Prompt-General/`. Before editing:

1. Make a backup or a Git commit so you can review or undo your own change.
2. Keep each Skill’s technical folder name and `SKILL.md` clear.
3. Check provenance and license terms. The project license cannot override a third-party author’s license.
4. Follow SemVer: start a new or reset Skill at `1.0.0`, then increase its version when you improve it.
5. Update the version and changelog before refreshing protected catalog metadata.
6. Validate the catalog and rebuild the local bridge sample with the commands below.

```powershell
python Maintenance-Tools\Invoke-Capability-Library.py validate
python Maintenance-Tools\Invoke-Capability-Library.py refresh-baseline --confirm-integrity-baseline-update --reason "Describe the authorized catalog change"
python Maintenance-Tools\Invoke-Capability-Library.py build-plugin
python Maintenance-Tools\Invoke-Capability-Library.py validate-plugin --output Plugins\aipm-project-agent-bridge
```

Only run `refresh-baseline` when the approved Skill or Prompt inventory has changed and its version/changelog updates are ready. Do not edit `Capability-Library/Registry.json` or its provenance ledger by hand. Keep the bridge local and unpublished unless the owner separately approves a supported host installation or publication.

## 12. Work With An AI Agent Safely

Opening AIPM in an AI editor does not by itself install the bridge, start an agent, or authorize file operations. A compatible agent only has the access that its host and the owner have explicitly granted. Read the [Host Adapter Contract](../../Plugins/Adapters/Host-Adapter-Contract.md) before enabling an integration.

When using AIPM to manage another project, do not open the AIPM installation as a writable workspace for that agent. AIPM Core blocks its own state and registry operations from overlapping AIPM, and the root `AGENTS.md` tells agents not to change AIPM unless you explicitly request AIPM development. This is not an OS security boundary: an external agent with direct filesystem-write permission can bypass Core. Use host workspace/sandbox controls or Windows ACLs to deny it write access to AIPM.

When you hand work to another session, treat pasted summaries as context, not proof. The receiving session should re-read the project’s current state and evidence. Anything without supporting evidence should remain **Unknown** or **Unverified**.

## 13. Build And Verify A Source Archive

To create a reproducible source archive inside `Releases/`:

```powershell
python Maintenance-Tools\New-Release-Package.py build
python Maintenance-Tools\New-Release-Package.py verify --archive Releases\AI-Project-Manager-v1.0.2.zip
```

The package includes public project material and both beginner guides, and excludes the Git database, caches, test workspaces, and internal implementation plans. The verifier checks the checksum and payload manifest. A successful local build is not the same as a GitHub release, installation, or host activation.

## 14. Troubleshooting

| Symptom | What To Do |
| --- | --- |
| `python` is not recognized | Install Python 3.10+; reopen PowerShell and run `python --version`. |
| The TUI refuses to start | Run it in a real terminal instead of a pipeline or redirected session. |
| PowerShell 7 is unavailable | Use `AIPM.bat` or the Windows PowerShell 5.1 command above. |
| `NOT_REGISTERED` appears | Choose **Registry Management** and register the intended project. AIPM adds only its state folder after confirmation. |
| Registry setup asks for a location | Accept the default under `%LOCALAPPDATA%\AI-Project-Manager` or enter a complete file path outside the AIPM installation. Any file name is allowed if it ends in `.json`; a folder path alone is not accepted. |
| `AIPM_PLATFORM_PROTECTED` appears | The project, registry, or backup path overlaps AIPM. Choose a separate project or storage location; Core intentionally blocks this operation. |
| A Skill is marked unverified | Treat that as missing evidence, not as a successful host installation. Review the provenance and local catalog. |
| An icon looks wrong | Set `AIPM_ICONS=ascii` or follow the theme instructions in the TUI User Guide. |

## 15. A Safe First-Session Checklist

1. Read the license and repository README.
2. Check Python and PowerShell versions.
3. Open the TUI, approve a registry location, and explore the dashboard.
4. Run `health`, `catalog`, and `host-capabilities`.
5. Read the support matrix and note every `UNVERIFIED` item.
6. Do not install the bridge or grant an agent new permissions unless the owner has explicitly approved that exact integration.
7. Register only the intended project folder. Confirm that `Shared-Project-State-Manager/` is the only AIPM-created project content; existing source files are not changed.

## Next Reading

- [Project README](../../README.md)
- [TUI User Guide](../../TUI/AI-Project-Manager/README.md)
- [Support Matrix](../../docs/project/Support-Matrix.md)
- [Capability Library Guide](../../Capability-Library/README.md)
- [Apache License 2.0](../../LICENSE)
