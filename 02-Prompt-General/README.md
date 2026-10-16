# General Prompts

This is the repository's standalone Prompt library.

## Placement Rule

Only Prompts that **do not have an owning Skill** belong in `02-Prompt-General`.

If a Prompt is the portable, fallback, invocation, execution, or companion form of an existing Skill, it belongs inside that Skill's master folder instead:

- use `PROMPT.md` for a single or primary Skill-owned Prompt;
- use a Skill-local `prompts/` directory for additional named Prompt variants owned by the same Skill.

Do not duplicate Skill-owned Prompts here.

If a standalone Prompt later gains an owning Skill, migrate it into that Skill folder and update affected links, indexes, documentation, versions/changelogs, and generated/plugin copies in the same change.

## Current Contents

There is currently **1 standalone Prompt** in this library: [Autonomous Task Execution](Autonomous-Task-Execution.md) (v1.0.0, English and Arabic). The Prompts that previously lived in the old shared Prompt root were Skill-owned and have been colocated with their owning Skills.

## Versioning

Standalone Prompts keep their own embedded version metadata according to [Project Rules](../Project-Documentation/Project-Rules.md). Skill-owned Prompts are released under the owning Skill's version and changelog.

The authoritative inventory and hashes are recorded in the [Capability Registry](../Capability-Library/Registry.json); this folder contains no Skill-owned Prompt duplicates.
