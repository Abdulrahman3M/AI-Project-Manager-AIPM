<div align="center">
  <img src="UX-TUI/Branding/AIPM-Project-Cover.png" alt="AI Project Manager — AIPM project cover" width="100%" />

  <h1>AI Project Manager <sub>v1.0.3</sub></h1>
  <p><strong>A governed, local-first workspace for AI-assisted project execution.</strong></p>

  <p>
    <a href="https://github.com/Abdulrahman3M/AI-Project-Manager-AIPM/releases/tag/v1.0.3"><img alt="Release v1.0.3" src="https://img.shields.io/badge/RELEASE-v1.0.3-0EA5E9?style=for-the-badge" /></a>
    <img alt="Private repository" src="https://img.shields.io/badge/REPOSITORY-PRIVATE-334155?style=for-the-badge" />
    <a href="LICENSE"><img alt="AI Project Manager Personal Use License" src="https://img.shields.io/badge/LICENSE-PERSONAL%20USE-F59E0B?style=for-the-badge" /></a>
    <img alt="Windows PowerShell 5.1 and PowerShell 7.x" src="https://img.shields.io/badge/RUNTIME-WINDOWS%20PS%205.1%20%7C%20PS%207.x-2563EB?style=for-the-badge" />
    <img alt="Python 3.10 or later" src="https://img.shields.io/badge/PYTHON-3.10%2B-3776AB?style=for-the-badge" />
    <a href="Project-Documentation/Phase-Reports/P09-Report.md"><img alt="P09 external gates unverified" src="https://img.shields.io/badge/P09%20EXTERNAL%20GATES-UNVERIFIED-D97706?style=for-the-badge" /></a>
  </p>

  <p>
    <a href="#overview">Overview</a> ·
    <a href="#capabilities">Capabilities</a> ·
    <a href="#quick-start">Quick Start</a> ·
    <a href="#security-and-privacy">Security</a> ·
    <a href="#project-status">Project Status</a>
  </p>
</div>

---

## Overview

AI Project Manager (AIPM) is a local-first project orchestration platform built to help AI agents and people work from clear project state, controlled capabilities, and verifiable evidence. Its Core Engine manages project and task state; host adapters define permission boundaries; and the PowerShell Intelligent TUI gives you a read-only view of projects, work, evidence, capabilities, and handoffs.

AIPM is designed to make project context explicit and portable while keeping authority with the project owner. A compatible package does not grant an agent access to local files or start an AI session on its own.

## Capabilities

| Area | What It Provides |
| --- | --- |
| **Core Engine** | Project registration, validated state, task lifecycle, evidence records, and continuity operations. |
| **Capability Library** | A governed catalog of Skills and Prompts with version, provenance, and integrity metadata. |
| **Agent Bridge** | A local package that explains how an AI agent should use AIPM Core and the approved Skills. |
| **Host Adapters** | Declared host capabilities, explicit permission gates, and fail-closed behavior for unsupported operations. |
| **Intelligent TUI** | Read-only project dashboards, task and evidence views, capability catalog, keyboard navigation, and accessible terminal styling. |

## Quick Start

New To AIPM? Follow The [English Beginner Guide](docs/User-Guides/Beginner-Guide.en.md) Or [دليل المبتدئين بالعربية](docs/User-Guides/دليل-المبتدئين.ar.md) For A Step-By-Step Walkthrough.

### Requirements

- Windows PowerShell 5.1 or PowerShell 7.x
- Python 3.10 or later available on `PATH`
- A real interactive terminal for keyboard navigation

### Launch the terminal interface

On Windows, run:

```powershell
TUI\AI-Project-Manager\AIPM.bat
```

Or launch PowerShell directly:

```powershell
pwsh -NoProfile -File TUI\AI-Project-Manager\Start-AIPM.ps1
```

For command-line options and view-mode guidance, see the [TUI User Guide](TUI/AI-Project-Manager/README.md).

## How AIPM Works

```text
Project Owner
     │ defines scope and permissions
     ▼
AI Agent ───────► Host Adapter ───────► AIPM Core Engine
     ▲                                      │
     │ approved Skills and handoff          │ project state and evidence
     └──────────────────────────────────────┘
                                            ▼
                                   Read-Only Terminal UI
```

The Core Engine is the authority for registered project and task state. Host adapters expose only declared operations and require explicit permission for writes. The terminal UI reads Core-backed data and does not mutate project state. Values without supporting evidence remain unknown or unverified.

## Security and Privacy

- Project state remains within the project and AIPM Core storage boundaries.
- Host operations are capability-declared, permission-gated, and fail-closed.
- Manual handoff text is treated as unverified input until a receiving session re-reads authoritative state.
- The local Agent Bridge does not install itself, start a background agent, or grant automatic file access.
- Capability metadata records Skill versions, provenance, and integrity information.

Read the [Host Adapter Contract](Plugin-Adapters/Host-Adapter-Contract.md) and [Project Rules](Project-Documentation/Project-Rules.md) for operational details.

## Project Status

AIPM includes a Python Core Engine, an owner-managed Skill and Prompt library, a generated local Agent Bridge, host capability declarations, and a PowerShell terminal interface. Automated regression suites cover the Core, capability library, and TUI.

The P09 report documents remaining external-environment checks as `UNVERIFIED`, including a live independent-host handoff and retained terminal-capture provenance. Download the verified [v1.0.3 source release](https://github.com/Abdulrahman3M/AI-Project-Manager-AIPM/releases/tag/v1.0.3). The owner repository remains private, so GitHub access is required; a release does not imply host installation or close those external gates. The README release badge and version are updated with every product release.

See the [Support Matrix](Project-Documentation/Support-Matrix.md), [P09 Security and Cross-Agent QA Report](Project-Documentation/Phase-Reports/P09-Report.md), and [P10 Packaging and Release Report](Project-Documentation/Phase-Reports/P10-Report.md) for evidence and limits.

## Repository Map

| Path | Purpose |
| --- | --- |
| `Core-Engine/` | Core runtime, state, orchestration, adapters, and capability logic. |
| `01-Skills-General/` | Owner-managed General Skills. |
| `02-Prompt-General/` | Standalone reusable Prompts. |
| `Capability-Library/` | Machine-readable registry and first-party capability declarations. |
| `Plugin-Adapters/` | Host capability matrix and adapter contract. |
| `Plugins/` | Locally generated Agent Bridge package. |
| `TUI/AI-Project-Manager/` | PowerShell terminal application, launchers, documentation, and tests. |
| `UX-TUI/` | Interface design system, visual references, and project brand assets. |
| `Tests/` | Python integration and regression suites. |
| `Project-Documentation/` | Architecture, support matrix, provenance, phase evidence, and release notes. |

## Validation

Run the PowerShell terminal application tests:

```powershell
pwsh -NoProfile -File TUI\AI-Project-Manager\tests\Run-Tests.ps1
```

Run the Core and integration tests:

```powershell
python -m unittest discover -s Tests -v
```

Validate the capability catalog and local Agent Bridge:

```powershell
python Maintenance-Tools\Invoke-Capability-Library.py validate
python Maintenance-Tools\Invoke-Capability-Library.py validate-plugin --output Plugins\aipm-project-agent-bridge
```

## Documentation

- [Project Index](Index.md)
- [Beginner Guides — English And Arabic](docs/User-Guides/README.md)
- [Capability Library](Capability-Library/README.md)
- [Host Capability Matrix](Plugin-Adapters/Host-Capability-Matrix.json)
- [Intelligent TUI Design System](UX-TUI/README.md)
- [TUI User Guide](TUI/AI-Project-Manager/README.md)
- [Support Matrix](Project-Documentation/Support-Matrix.md)
- [Release Notes](Project-Documentation/Release-Notes-v1.0.3.md)

## License

The project is distributed under the [AI Project Manager Personal Use License](LICENSE). Review its terms before copying, modifying, redistributing, or using project material.
