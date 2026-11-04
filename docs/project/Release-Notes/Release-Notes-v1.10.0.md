# AIPM v1.10.0 Release Notes

## Git-First Project Registration And Unified State Layout

New project registration now requires Git at the selected project root and installs FIRG as part of project tracking setup. FIRG files and reports live at `Shared-Project-State-Manager/FIRG/`, while the manager-level `AGENT.md` defines folder roles and artifact routing.

Task records, tool state, logs, quarantine, and locks are grouped under `Operations/`. Python bytecode and other caches belong under `Temporary-Files/Cache/`; disposable test output and fixtures belong under `Temporary-Files/Test-Workspace/`.

**Update Project** migrates existing registered projects. It moves legacy FIRG and operational folders only when destinations are clear, preserves existing project data, updates unmodified managed FIRG files with a backup, and stops for review when it finds a conflict. The update asks before initializing missing Git.

Platform and TUI versions are synchronized at `1.10.0`. This is a local, unpublished repository update.
