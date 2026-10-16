# AI Project Manager (AIPM)

AI Project Manager is a local-first platform for governed project orchestration, shared project state, compatible Skills, and a PowerShell Intelligent TUI.

## Project Status

P01–P07 are complete. P08 adds a Core-backed, read-only PowerShell TUI implementation with Task Dashboard, Command Palette, and Assistant Console modes. Automated tests exercise its rendering and state integration; actual Windows Terminal and legacy-console visual checks remain UNVERIFIED in this non-interactive run. No plugin is installed or published.

## Capability Library

- [Capability Library Guide](Capability-Library/README.md)
- [Standalone General Prompts](02-Prompt-General/README.md)
- [Project Rules](Project-Documentation/Project-Rules.md)
- [Capability Registry](Capability-Library/Registry.json)

The library registers 18 General Skills (16 byte-preserved imports, the documented `project-orchestrator` derivative, and the AIPM-owned `tui-intelligence` Skill), their Skill-owned Prompts, and the owner-added standalone Prompt. Personal Skills, `import-memory`, and `morning` are excluded. The first-party Skill uses Apache-2.0; imported terms and notices are preserved.

## Local Plugin Sample

`Plugins/aipm-general-skills` is generated from the approved General Skill masters, with OpenAI portable/Codex compatibility, Claude Code, and Gemini CLI manifests. It is a local sample only; it is not published or installed. It contains no Personal Skills or standalone Prompts and records license scope per Skill.

## Host Adapters And Intelligent TUI

- [Host Capability Matrix](Plugin-Adapters/Host-Capability-Matrix.json) and [Adapter Contract](Plugin-Adapters/Host-Adapter-Contract.md) define tested, conditional, and unavailable capabilities. The Generic CLI routes through Core Engine; manual handoffs remain unverified and read-only.
- [Intelligent TUI Design System](UX-TUI/README.md) and the [TUI Intelligence Skill](01-Skills-General/tui-intelligence/SKILL.md) preserve the approved mockups, palette, layout, accessibility, and differential-rendering requirements. The [PowerShell TUI App](TUI/AI-Project-Manager/README.md) implements the required read-only views. Design mockups are not runtime screenshots; physical terminal appearance and flicker remain unverified until tested in their actual hosts.

## P08 Verification

- [P08 Implementation Plan](Project-Documentation/P08-Implementation-Plan.md)
- [P08 Verification Record](Project-Documentation/Phase-Reports/P08-Report.md)

## License Scope

Apache-2.0 covers AIPM-authored files and the declared first-party Skill only. Imported Skills retain the Universal AI ToolKit Personal Use License and their original third-party notices. The generated sample includes both license texts and per-Skill licensing; see `Project-Documentation/Provenance/`.
