# AI Project Manager v1.4.9

## Escape Exit Confirmation

Pressing Escape in the PowerShell TUI walks back one level at a time. Previously, reaching the main dashboard and pressing Escape again closed the application and returned directly to PowerShell.

The root dashboard now shows an explicit **Exit AI Project Manager?** confirmation with **Exit AIPM** and **Stay Here** choices. Selecting Stay Here, or pressing Escape in the confirmation, returns to the Task Dashboard; only an explicit Exit choice closes AIPM. No project data is changed by either answer.

## Verification Scope

The PowerShell TUI scripted regression suite covers the confirmation prompt and the confirmed exit path, and runs 224 pass, 0 fail, 0 unverified on Windows PowerShell 5.1. The same suite also repaired a stale assertion that expected a long work-folder path on a single prompt row; the path is now checked across the wrapped prompt rows that the renderer produces.

## Apache License 2.0

AIPM first-party project material is now distributed under the Apache License 2.0 instead of the previous AI Project Manager Personal Use License. The root `LICENSE` and the TUI package `LICENSE` contain the full license text with `Copyright 2026 Abdulrahman Elbatrah`.

A root `NOTICE` records the copyright holder and the attribution reference to the original project at `https://github.com/Abdulrahman3M/AI-Message-Writer`. Source releases and generated Plugin packages include both `LICENSE` and `NOTICE`; packaged copies use `licenses/Apache-2.0.txt`.

The protected capability baseline was refreshed through its confirmed CLI workflow, and the legacy Project Agent Bridge was regenerated at `1.0.16` with the new license metadata. Multi-host Plugin archives were not rebuilt. Historical changelog and release-note entries that describe the earlier license are preserved unchanged.

## Version Scope

- AIPM platform: `1.4.9`
- PowerShell TUI: `1.4.9`
- Skills and standalone Prompts: unchanged
- Legacy Project Agent Bridge: `1.0.16` (license and source-version metadata only)

This is an unpublished repository update. The latest published GitHub Release remains `v1.4.0`.
