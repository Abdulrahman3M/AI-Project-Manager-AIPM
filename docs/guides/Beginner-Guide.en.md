# AI Project Manager Beginner Guide

Welcome to **AI Project Manager (AIPM)**. This guide assumes you are new to the project and explains how to get it, open it, understand what you see, and work with its approved capabilities safely.

> **Important:** AIPM does not edit your project's source files. The TUI has explicit registry controls: when you confirm registration, Core creates only AIPM-owned state under `Shared-Project-State-Manager/`; unregistering removes only a registry pointer. Task editing remains outside the TUI workflows described here. The Agent Bridge is a package sample, not an installed agent or an automatic file-access grant.

## 1. What AIPM Does

AIPM keeps project information understandable and evidence-based for people and AI-assisted work:

| Part | In Simple Terms |
| --- | --- |
| Core Engine | Reads and validates registered project and task state. |
| Capability Library | Keeps an approved catalog of Skills and Prompts with version and provenance records. |
| PowerShell TUI | Shows a keyboard-driven dashboard and guarded project-registry controls. |
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

Before using or redistributing project material, read the root [AI Project Manager Personal Use License](../../LICENSE).

## 4. Learn The Folder Map

You do not need to open every folder before starting. These are the useful places for a new user:

| Folder Or File | What It Is For |
| --- | --- |
| `README.md` | Short project overview and quick links. |
| `Core-Engine/` | Core state handling and read-only CLI. |
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

On the first launch, the TUI asks you to approve the default registry location or choose another one. The dashboard can show registered projects, tasks, phase records, test evidence, handoffs, Skills, Prompts, and settings. The **Registry Management** screen can add/remove project pointers, change the selected registry, and back it up or restore it. It cannot edit your source code or create project tasks.

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

This is per-user application data, not a second AIPM installation and not a folder inside any project. Accept it in the first-run prompt or choose another path ending with `registry.json` outside the AIPM installation. The choice is remembered in `%APPDATA%\AIPM\settings.json`. Passing `-RegistryPath` when starting AIPM is also treated as choosing the path.

Project operational state is separate: for each registered project, AIPM stores it in that project's own `Shared-Project-State-Manager/` folder. The central registry stays small while each project's working state stays with that project.

## 7. Navigate The Screens

- Press **Up** or **Down** to move the selection.
- Press **Enter** to open the selected item.
- Type a displayed number to choose that numbered item.
- Press **/** to search or filter where available.
- Press **?** or **F1** for help.
- Press **Esc** to return to the previous screen.
- Press **Q** to exit and confirm when prompted.

The selected row is identified by a colored arrow and brighter text. Descriptions below menu items are intentionally not selected or shaded. If a symbol does not display correctly, start with the ASCII icon setting described in the [TUI User Guide](../../TUI/AI-Project-Manager/README.md).

## 8. Register And Manage A Project Safely

In the dashboard, choose **Registry Management**. To register a project:

1. Choose **Register A Project**.
2. Enter the full path to an existing project folder. Do not select the AIPM folder or a parent folder that contains AIPM; Core blocks overlapping paths.
3. Enter or accept the project display name.
4. Read the confirmation: it states that AIPM will create `Shared-Project-State-Manager/` under that project and will not edit source files.
5. Choose **Create State And Register** only if you want that state folder and registry entry.

The registry then stores an ID, name, and root path. Your code, documents, Git metadata, and other existing project files are not modified. Task and continuity records that AIPM owns remain inside its state folder.

Other registry actions:

- **View Registered Projects** lists each project's name, ID, and root folder.
- **Unregister A Project** removes only that project's pointer from the selected registry. It does not delete the project or its state folder.
- **Back Up Registry** writes a new JSON backup and a `.sha256` checksum file. It will not overwrite an existing file.
- **Restore Registry Backup** checks the checksum when its sidecar exists and automatically saves a pre-restore backup before changing the registry.
- **Change Registry Location** selects or creates another registry. It does not copy or delete the previous registry; back it up first if you need to preserve its contents.

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

For regular use, prefer the TUI confirmations. Do not commit a personal registry or its backups to GitHub or a source archive; they can reveal private project folder paths.

## 10. Understand Skills, Prompts, And The Agent Bridge

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

## 11. Work With An AI Agent Safely

Opening AIPM in an AI editor does not by itself install the bridge, start an agent, or authorize file operations. A compatible agent only has the access that its host and the owner have explicitly granted. Read the [Host Adapter Contract](../../Plugins/Adapters/Host-Adapter-Contract.md) before enabling an integration.

When using AIPM to manage another project, do not open the AIPM installation as a writable workspace for that agent. AIPM Core blocks its own state and registry operations from overlapping AIPM, and the root `AGENTS.md` tells agents not to change AIPM unless you explicitly request AIPM development. This is not an OS security boundary: an external agent with direct filesystem-write permission can bypass Core. Use host workspace/sandbox controls or Windows ACLs to deny it write access to AIPM.

When you hand work to another session, treat pasted summaries as context, not proof. The receiving session should re-read the project’s current state and evidence. Anything without supporting evidence should remain **Unknown** or **Unverified**.

## 12. Build And Verify A Source Archive

To create a reproducible source archive inside `Releases/`:

```powershell
python Maintenance-Tools\New-Release-Package.py build
python Maintenance-Tools\New-Release-Package.py verify --archive Releases\AI-Project-Manager-v1.0.2.zip
```

The package includes public project material and both beginner guides, and excludes the Git database, caches, test workspaces, and internal implementation plans. The verifier checks the checksum and payload manifest. A successful local build is not the same as a GitHub release, installation, or host activation.

## 13. Troubleshooting

| Symptom | What To Do |
| --- | --- |
| `python` is not recognized | Install Python 3.10+; reopen PowerShell and run `python --version`. |
| The TUI refuses to start | Run it in a real terminal instead of a pipeline or redirected session. |
| PowerShell 7 is unavailable | Use `AIPM.bat` or the Windows PowerShell 5.1 command above. |
| `NOT_REGISTERED` appears | Choose **Registry Management** and register the intended project. AIPM adds only its state folder after confirmation. |
| Registry setup asks for a location | Accept the default under `%LOCALAPPDATA%\AI-Project-Manager` or choose a different `registry.json` path outside the AIPM installation. |
| `AIPM_PLATFORM_PROTECTED` appears | The project, registry, or backup path overlaps AIPM. Choose a separate project or storage location; Core intentionally blocks this operation. |
| A Skill is marked unverified | Treat that as missing evidence, not as a successful host installation. Review the provenance and local catalog. |
| An icon looks wrong | Set `AIPM_ICONS=ascii` or follow the theme instructions in the TUI User Guide. |

## 14. A Safe First-Session Checklist

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
- [AI Project Manager Personal Use License](../../LICENSE)
