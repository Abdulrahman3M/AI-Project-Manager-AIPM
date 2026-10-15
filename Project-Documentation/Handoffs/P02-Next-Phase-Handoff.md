# P02 Next Phase Handoff

## Entry Conditions

P01 is complete. Read the P01 report, checkpoint, source migration record, P02 phase instructions, state contracts, and all applicable `AGENTS.md` files before changing files.

## Preserve

- Do not modify the 16 byte-preserved migrated Skills.
- Keep `project-orchestrator`'s documented derivative status and do not restore Personal Skill references.
- Do not add `import-memory`, `morning`, or `02-Skills-Personal`.
- Do not place managed-project operational data in this repository.

## First P02 Action

Inspect and validate project-root isolation, state schema contracts, and legacy `Shared-Project-State` compatibility without migrating any live state automatically.
