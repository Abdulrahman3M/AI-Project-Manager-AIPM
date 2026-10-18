# AI Project Manager Architecture And Plugin Distribution

## Product Overview

AI Project Manager (AIPM) is a local-first project-management platform with two complementary roles:

1. The local product manages project registration, task state, evidence, continuity, capability governance, and explicit registry administration through the TUI.
2. The Capability Library is the governed source of reusable Skills and Prompts that can be assembled into host-specific Plugin packages.

The Plugin path complements the platform; it does not replace the Core Engine or automatically connect a remote AI host to local project files.

## Architecture At A Glance

```text
Project Owner
    │
    ├── Operates AIPM locally ──> PowerShell TUI ──> Python Core Engine
    │                                                ├── Project/task state
    │                                                ├── Pointer-only registry administration
    │                                                ├── Protected AIPM installation boundary
    │                                                ├── Evidence and continuity
    │                                                ├── Capability validation
    │                                                └── Permission-gated host adapters
    │
    └── Uses approved capabilities ──> Capability Library Registry
                                       ├── 01-Skills-General/ (12 Skills)
                                       ├── Skill-owned Prompts
                                       └── 02-Prompt-General/ (standalone Prompts)
                                               │
                                               ▼
                                    Multi-Host Plugin Build System
                                      ├── ChatGPT/Codex ZIP
                                      ├── Claude Code ZIP
                                      └── Google Antigravity ZIP
```

## Current Repository Map

| Path | Responsibility | Source Or Generated |
| --- | --- | --- |
| `01-Skills-General/` | Owner-managed General Skill masters, their references, scripts, tests, and Skill-owned Prompts. | Source |
| `02-Prompt-General/` | Standalone project-management Prompts not owned by a Skill. | Source |
| `Capability-Library/Registry.json` | Approved capability inventory, versions, content hashes, and provenance references. | Protected generated baseline; update through its confirmed CLI workflow |
| `docs/project/Provenance/` | Source revision, migration, license, and capability integrity records. | Governance evidence |
| `Core-Engine/aipm_core/` | Python domain, storage, task operations, orchestration, continuity, capability validation, release packaging, and host adapters. | Product source |
| `%LOCALAPPDATA%\AI-Project-Manager\registry.json` | Per-user pointer-only list of managed project IDs, aliases, and root paths; created only after TUI first-run location approval. | Runtime user data; never repository content |
| `<project-root>/Shared-Project-State-Manager/` | Operational state, task records, evidence, and continuity data for one managed project. | Runtime project data; stays inside that managed project |
| `%APPDATA%\AIPM\settings.json` | Per-user TUI preferences, including the selected registry path. | Runtime user settings; never repository content |
| `TUI/AI-Project-Manager/` | PowerShell terminal application, tests, user documentation, and UI assets. | Product source |
| `Maintenance-Tools/` | Explicit repository maintenance, registry, Plugin, and release commands. | Product tooling |
| `Plugins/Build-System/` | PowerShell entry point, Python packager/validator, and host profiles. | Product tooling |
| `Plugins/Adapters/` | Host adapter contract, capability matrix, and schema. | Product documentation/schema |
| `Plugins/aipm-project-agent-bridge/` | Compatibility Bridge generated from the Capability Library; independently versioned. | Generated compatibility package |
| `Plugins/Dist/` | Locally generated host-specific Plugin ZIPs and SHA-256 sidecars. | Generated output; not a source-of-truth folder |
| `Tests/` | Python integration, security, packaging, and regression tests. | Product verification |
| `UX-TUI/` | Approved brand assets, themes, and visual references for the terminal UI. | Product assets |
| `docs/guides/` | Beginner-oriented English and Arabic usage guides. | User documentation |
| `docs/project/Architecture/` | Current architecture and distribution model. | Maintained project documentation |
| `docs/project/Support-Matrix.md` | Verified environments and explicitly unverified owner/host gates. | Maintained verification summary |
| `docs/project/Release-Notes-v*.md` | Human-readable notes for product releases. | Maintained release documentation |
| `docs/project/Provenance/` | Retained source and integrity evidence. | Maintained governance records |
| `Releases/` | Deterministic source archives and checksum sidecars prepared for a release. | Generated, local release output |

## Capability And Plugin Source Of Truth

`Capability-Library/Registry.json` is the sole accepted inventory for Plugin generation. The builder validates the registry and provenance before copying any content. It includes all approved General Skills, their declared Skill-owned Prompts, and standalone Prompts from `02-Prompt-General/`. The personal Skills area and the excluded `import-memory` and `morning` capabilities are not included.

Canonical Skill and Prompt files remain the source. Host-specific projections—such as ChatGPT-compatible YAML front matter—are produced in the staging/package layer and do not rewrite those source files. Each host archive receives a capability index, host metadata, the project license, and its own validation/checksum evidence.

The legacy Project Agent Bridge remains for backward compatibility. It is not the source of truth and is not the only Plugin distribution route.

## Runtime Project Registry And Self-Protection

On the first interactive launch, the TUI asks the owner to accept `%LOCALAPPDATA%\AI-Project-Manager\registry.json` or select another file named `registry.json` outside the AIPM installation. The selected path is remembered in `%APPDATA%\AIPM\settings.json`. Passing `-RegistryPath` explicitly is treated as the owner's path selection.

The runtime registry contains pointers only; project operational data is stored under each project's `Shared-Project-State-Manager/`. The **Registry Management** screen can list, register, and unregister projects, create a JSON/SHA-256 backup, restore a verified backup, and switch the selected registry. Registering creates only AIPM-owned state after a confirmation. Unregistering removes a pointer only. Restore saves an automatic pre-restore backup. Switching paths does not migrate, copy, or delete either registry.

The Core detects its installation root from the executing package and rejects managed project roots, registry destinations, and registry backups that equal, contain, or are contained by that installation. The guard protects operations performed through AIPM Core. It cannot prevent an external agent with independent direct filesystem-write permission from editing AIPM files; host workspace restrictions or Windows ACLs are required for that stronger boundary. The agent instruction lives in the root `AGENTS.md` and permits AIPM source changes only after a direct, explicit owner request to work on AIPM itself.

## Plugin Build And Validation

Run from the repository root in Windows PowerShell or PowerShell 7:

```powershell
.\Plugins\Build-System\Build-AIPM-Plugin.ps1 -Platform All -Validate
```

The command creates three local archives under `Plugins/Dist/`:

- `AIPM-ChatGPT-Plugin-v<platform-version>.zip`
- `AIPM-Claude-Plugin-v<platform-version>.zip`
- `AIPM-Antigavity-Plugin-v<platform-version>.zip`

Each archive has a `.sha256` sidecar and is checked against the current capability inventory. This proves local package structure and source integrity only—not installation, account acceptance, live execution, publication, or local-project access by an AI host. The Antigavity format remains explicitly unverified until its authoritative format and host behavior are tested.

## Legacy Bridge Workflow

Use the approved capability CLI rather than editing generated Bridge files by hand:

```powershell
python .\Maintenance-Tools\Invoke-Capability-Library.py validate
python .\Maintenance-Tools\Invoke-Capability-Library.py build-plugin --output Plugins/aipm-project-agent-bridge
python .\Maintenance-Tools\Invoke-Capability-Library.py validate-plugin --output Plugins/aipm-project-agent-bridge
```

The Bridge remains a local compatibility package. A successful generation or validation does not install it or publish it to a marketplace.

## Tests And Release Packaging

Run the full local Python suite:

```powershell
python -m unittest discover -s Tests -p 'test_*.py'
```

Build and verify the deterministic source release:

```powershell
python .\Maintenance-Tools\New-Release-Package.py build
python .\Maintenance-Tools\New-Release-Package.py verify --archive Releases/AI-Project-Manager-v<version>.zip
```

Platform and TUI versions move together under SemVer. Skill versions remain independent; the Bridge is also independently versioned. A release package is not published until its local version metadata, source ZIP, and SHA-256 sidecar have been verified. The exact verified source ZIP and sidecar must match the assets attached to the matching GitHub Release.

## Security, License, And Status Boundaries

- Apply the AI Project Manager Personal Use License to project material and generated distributions.
- Host adapters are capability-declared, permission-gated, and fail-closed.
- The AIPM installation is protected during work on other projects; Core-managed state and registry paths cannot overlap the installation.
- A Plugin package manifest is descriptive metadata, not proof of authorization or installation.
- No ChatGPT text conversation is assumed to have local file access.
- P09 external-project, live cross-agent, and durable host-capture gates remain as recorded in the [Support Matrix](../Support-Matrix.md); never convert an unavailable host check into a passing result.
- The source and Plugin build paths exclude temporary test/cache directories from their deliverables.
