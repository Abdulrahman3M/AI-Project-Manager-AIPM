# AI Project Manager (AIPM)

AI Project Manager is a local-first platform for governed project orchestration, shared project state, compatible Skills, and a PowerShell Intelligent TUI.

## Project Status

P01–P06 are complete. P06 establishes the capability registry and provenance ledger, validates the approved Skill and Prompt inventory, and provides a local-only Plugin sample. P07 has not started.

## Capability Library

- [Capability Library Guide](Capability-Library/README.md)
- [Standalone General Prompts](02-Prompt-General/README.md)
- [Project Rules](Project-Documentation/Project-Rules.md)
- [Capability Registry](Capability-Library/Registry.json)

The library registers 17 General Skills (16 byte-preserved imports and the documented `project-orchestrator` derivative), their Skill-owned Prompts, and the owner-added standalone Prompt. Personal Skills, `import-memory`, and `morning` are excluded.

## Local Plugin Sample

`Plugins/aipm-general-skills` is generated from the approved General Skill masters. It is a local sample only; it is not published or installed. It contains no Personal Skills or standalone Prompts.

## License Scope

Apache-2.0 covers AIPM-authored files only. Imported Skills retain the Universal AI ToolKit Personal Use License and their original third-party notices. The generated sample includes the source license and per-Skill notices; see `Project-Documentation/Provenance/`.
