# AI Project Manager Beginner Guide

Welcome to **AI Project Manager (AIPM)**. This guide assumes you are new to the project and explains how to get it, open it, understand what you see, and work with its approved capabilities safely.

> **Important:** The PowerShell terminal interface and documented `aipm` CLI commands are read-only. This release does not provide project/task editing commands in the CLI or TUI. The Agent Bridge is a validated package sample, not an installed agent or an automatic file-access grant.

## 1. What AIPM Does

AIPM keeps project information understandable and evidence-based for people and AI-assisted work:

| Part | In Simple Terms |
| --- | --- |
| Core Engine | Reads and validates registered project and task state. |
| Capability Library | Keeps an approved catalog of Skills and Prompts with version and provenance records. |
| PowerShell TUI | Shows a keyboard-driven, read-only dashboard. |
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

The dashboard is read-only. It can show registered projects, tasks, phase records, test evidence, handoffs, Skills, Prompts, and settings. It does not create or modify project tasks.

## 6. Navigate The Screens

- Press **Up** or **Down** to move the selection.
- Press **Enter** to open the selected item.
- Type a displayed number to choose that numbered item.
- Press **/** to search or filter where available.
- Press **?** or **F1** for help.
- Press **Esc** to return to the previous screen.
- Press **Q** to exit and confirm when prompted.

The selected row is identified by a colored arrow and brighter text. Descriptions below menu items are intentionally not selected or shaded. If a symbol does not display correctly, start with the ASCII icon setting described in the [TUI User Guide](../../TUI/AI-Project-Manager/README.md).

## 7. Read Core Information From PowerShell

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

If you do not have a registry path or project ID, do not invent one or edit the protected registry files. Ask the project owner for the authorized setup process. This release intentionally has no public CLI command for registering a project.

## 8. Understand Skills, Prompts, And The Agent Bridge

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

## 9. Work With An AI Agent Safely

Opening AIPM in an AI editor does not by itself install the bridge, start an agent, or authorize file operations. A compatible agent only has the access that its host and the owner have explicitly granted. Read the [Host Adapter Contract](../../Plugins/Adapters/Host-Adapter-Contract.md) before enabling an integration.

When you hand work to another session, treat pasted summaries as context, not proof. The receiving session should re-read the project’s current state and evidence. Anything without supporting evidence should remain **Unknown** or **Unverified**.

## 10. Build And Verify A Source Archive

To create a reproducible source archive inside `Releases/`:

```powershell
python Maintenance-Tools\New-Release-Package.py build
python Maintenance-Tools\New-Release-Package.py verify --archive Releases\AI-Project-Manager-v1.0.2.zip
```

The package includes public project material and both beginner guides, and excludes the Git database, caches, test workspaces, and internal implementation plans. The verifier checks the checksum and payload manifest. A successful local build is not the same as a GitHub release, installation, or host activation.

## 11. Troubleshooting

| Symptom | What To Do |
| --- | --- |
| `python` is not recognized | Install Python 3.10+; reopen PowerShell and run `python --version`. |
| The TUI refuses to start | Run it in a real terminal instead of a pipeline or redirected session. |
| PowerShell 7 is unavailable | Use `AIPM.bat` or the Windows PowerShell 5.1 command above. |
| The dashboard says `NOT_REGISTERED` | No configured project registry was found. The current release has no project-registration CLI; ask the owner for the authorized setup process. |
| A Skill is marked unverified | Treat that as missing evidence, not as a successful host installation. Review the provenance and local catalog. |
| An icon looks wrong | Set `AIPM_ICONS=ascii` or follow the theme instructions in the TUI User Guide. |

## 12. A Safe First-Session Checklist

1. Read the license and repository README.
2. Check Python and PowerShell versions.
3. Open the TUI and explore the read-only dashboard.
4. Run `health`, `catalog`, and `host-capabilities`.
5. Read the support matrix and note every `UNVERIFIED` item.
6. Do not install the bridge or grant an agent new permissions unless the owner has explicitly approved that exact integration.
7. Save project changes only through an authorized workflow; this release’s TUI and documented CLI commands do not edit project state.

## Next Reading

- [Project README](../../README.md)
- [TUI User Guide](../../TUI/AI-Project-Manager/README.md)
- [Support Matrix](../../docs/project/Support-Matrix.md)
- [Capability Library Guide](../../Capability-Library/README.md)
- [AI Project Manager Personal Use License](../../LICENSE)
