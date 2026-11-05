# AIPM PowerShell Operator Guide

This guide explains how to operate the AIPM Terminal User Interface (TUI), a PowerShell application for project registration, task context, evidence, and handoffs. It focuses on day-to-day use, boundaries, strengths, and limitations.

## What AIPM Does

AIPM keeps a registry of project paths and stores AIPM-managed project state in each project's `Shared-Project-State-Manager/` directory. The TUI calls the Core Engine for validated operations. It does not implement project source code, edit source files, or run the managed project's tests. Agents or developers do that directly in the project under the host's existing permissions.

## Requirements And Launch

- Windows PowerShell 5.1 or PowerShell 7.x; PowerShell 7 is preferred.
- Python 3.10 or later available as `python` or `python3`.
- Git available on `PATH` for project registration and Git-backed workflows.
- An interactive terminal for keyboard navigation.

From the repository root, run `AIPM.bat` on Windows or `./AIPM.sh` on Linux/macOS with `pwsh` installed. Direct PowerShell options:

```powershell
Set-Location 'C:\Path\To\AI-Project-Manager-AIPM'
./TUI/AI-Project-Manager/Start-AIPM.ps1
./TUI/AI-Project-Manager/Start-AIPM.ps1 -RegistryPath 'D:\AIPM Data\registry.json'
./TUI/AI-Project-Manager/Start-AIPM.ps1 -Version
```

The first launch lets you use the default registry, connect an existing registry, or choose a location. A registry stores project IDs, names, and root paths; it does not copy the projects. Existing registry content is validated read-only when connected.

## Navigation

- **Up/Down** moves the selection; **Enter** opens or confirms; **Esc** returns.
- Type a displayed number to choose a numbered action.
- Press **/** to filter actions; **?** or **F1** opens help.
- **Q** requests exit; the dashboard asks for confirmation.
- Settings can switch among Task Dashboard, Command Palette, and Assistant Console. Assistant Console is an offline, read-only evidence view, not an AI session.

## Register A Project

Open **Registry Management** and choose **Register Project**. Select the existing project root and give it a display name. Registration checks for Git at that exact root; a parent repository does not qualify. If Git is missing, AIPM asks before initializing it. Then it creates `Shared-Project-State-Manager/`, installs FIRG at `Shared-Project-State-Manager/FIRG/`, and records the project in the registry.

The manager's `AGENT.md` describes folder roles and routes Python caches to `Temporary-Files/Cache/` and disposable test workspaces to `Temporary-Files/Test-Workspace/`. Existing instruction files that contain metadata, translated editions, or conflicting FIRG rules require review rather than automatic replacement.

## Update An Existing Project

From **Projects**, choose the registered project and **Update Project**. The updater can initialize missing Git after confirmation, move managed legacy root-level FIRG into the manager, create FIRG inside the manager if absent, and migrate legacy cache, test, and operations folders. It preserves contents and stops if a destination conflicts or it finds unmanaged/modified material requiring review. A successful move does not imply every possible project configuration was tested.

## Tasks, Evidence, And Handoffs

Open **Tasks**, select a project, then create a task or open an existing one. A task is a record of intent and progress, not a duplicate working copy. Use task actions to record scope, plan, checkpoints, blockers, verification evidence, report notes, and handoff context. Supporting files may be attached into declared task categories; attaching copies the selected support file into AIPM state and does not modify its original. Source edits and tests still happen in the original project tree.

Use **Tests & Evidence** to review agent-reported checks and their status. Unprovided evidence remains unknown or unverified; a task status or report does not independently prove that code was tested. Use **Agents & Handoffs** to prepare the task context for another agent, who should re-read the live project and verify the checkpoint before continuing.

## Git And FIRG Records

Git history belongs to the project. AIPM can offer FIRG documentation after a commit made through its task interface. An interactive local post-commit hook can prompt after other commits when installation is compatible with the existing hooks. Hooks are bypassable and non-interactive clients cannot answer the prompt. Use FIRG `commit-status` to identify commits without a linked report. A report documents the commit, change summary, analysis, root cause when applicable, remedy, and verification outcome; it does not certify the change by itself.

## Recovery And Settings

**Upgrade Shared State** previews a supported schema upgrade and requests confirmation before making a backup and recording the event. Pending transactions and normalization conflicts should be handled through the state recovery workflow first. Registry management supports connect, switch, backup, restore, register, and unregister. Unregistering removes the registry pointer; it does not delete project files. UI preferences and registry selection are stored in the user's AIPM settings directory, separately from project state.

## Strengths And Limitations

**Strengths:** one registry for project locations; task-scoped notes and evidence; explicit Git and FIRG setup; guarded state migration; backups for supported repairs; portable handoff context; PowerShell 5.1 and 7 support.

**Limitations:** AIPM is not a code editor or agent runtime; it does not execute project tests or guarantee that reported evidence is genuine; local Git hooks can be bypassed; registry paths must resolve on the current device; terminal colors and glyphs vary; scripted renderer tests do not prove visual quality or flicker-free behavior on every terminal. Core path guards protect AIPM operations, not against another process with direct filesystem permissions.

For the complete beginner workflow, see the [English Beginner Guide](Beginner-Guide.en.md). For verified environments and unverified checks, see the [Support Matrix](../project/Support-Matrix.md).
