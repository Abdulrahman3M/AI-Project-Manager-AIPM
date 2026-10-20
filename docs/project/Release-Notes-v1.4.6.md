# AI Project Manager v1.4.6

Repository documentation update; not published as a GitHub Release. The published `v1.4.5` remains the latest release. No Git tag was created.

## General Capability Documentation

- Added [General Skills](../guides/General-Skills.md), an alphabetical guide to all 12 General Skills with plain-language descriptions, when-to-use guidance, examples, and direct links to their source instructions.
- Added [General Prompts](../guides/General-Prompts.md), an alphabetical guide to the standalone Prompt library with a summary, usage guidance, and a link to the original Prompt.
- Added prominent entry links to both pages in the project README and listed them in the documentation indexes.
- Added mandatory General Skills and General Prompts documentation synchronization rules to `AGENTS.md` and an automated check for inventory parity, duplicates, order, technical names, and navigation links.

## Versions And Scope

- AIPM platform: `1.4.6`
- PowerShell TUI: `1.4.6` (version synchronization only; no TUI behavior change)
- Legacy Project Agent Bridge: `1.0.15` (metadata-only regeneration from the confirmed Capability Library baseline)
- Latest published GitHub Release: `v1.4.5`
- No Skill or Prompt content changed. The protected Capability Library baseline was refreshed through its confirmed CLI workflow. Multi-host Plugin archives remain at their previously validated `1.4.5` version and were not rebuilt.
- No GitHub Release, tag, source ZIP, or checksum sidecar was created for this repository update.

## Verification

- `python -m unittest discover -s Tests -p "test_general_capability_docs.py" -v` — verifies source inventory counts, duplicates, alphabetical ordering, inline technical names, source links, README entry links, and return-to-home links.
- General Skills indexed: 12. Standalone General Prompts indexed: 1.
- The Capability Library and regenerated legacy Bridge validate locally. No host installation or runtime acceptance is claimed.
