# AIPM Plugins

AIPM is a local-first project-management platform. Its Core Engine and PowerShell TUI remain the authority for project state, tasks, tests, and evidence. This folder adds a governed way to distribute the same approved project-management Skills and Prompts to supported AI-agent hosts.

| Path | Purpose |
| --- | --- |
| [`Build-System/`](Build-System/Quick-Start.md) | Builds and validates complete local ZIP packages for ChatGPT/Codex, Claude, and Antigavity. |
| [`Adapters/`](Adapters/Host-Adapter-Contract.md) | Capability declarations, permission boundaries, and host adapter contract. |
| [`aipm-project-agent-bridge/`](aipm-project-agent-bridge/README.md) | Legacy compatibility package for the original project-agent bridge workflow. |

## Build A Plugin

From the repository root, run:

```powershell
.\Plugins\Build-System\Build-AIPM-Plugin.ps1 -Platform ChatGPT
```

Replace `ChatGPT` with `Claude`, `Antigavity`, or `All`. The command creates a verified ZIP and SHA-256 sidecar under `Plugins/Dist/`. See [Quick Start](Build-System/Quick-Start.md) for installation boundaries and validation details.

The `aipm-project-agent-bridge` folder remains a **legacy compatibility** package. It is not the only distribution path and it intentionally retains its separate version history.

Package metadata proves package format only. It does not install or publish a Plugin, connect it to AIPM Core, or grant access to project files. ChatGPT/Codex and Claude availability, import, installation, and permissions are controlled by their respective host and workspace.
