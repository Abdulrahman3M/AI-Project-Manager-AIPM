# 1.4.0 — 2026-10-13
- Require dedicated AI browser preflight, safe Browser Environment Manager recovery and consent-based fallback chain in generated handoffs.
- Require token-optimization support and prohibit multi-agent execution without explicit owner approval.

# Change Log

## 1.3.0 — 2026-10-10
- Added explicit intake of `deep-brainstorming` evidence, root-cause confidence, option recommendation and acceptance criteria.
- Preserved standalone functionality and strict MD generation without application implementation.
- Enabled separate non-lossy `token-optimization` support during handoff authoring.


## 1.2.0 — 2026-10-08

- Moved the Skill-owned request and execution Prompts from the former shared Prompt root into this Skill's local `prompts/` directory.
- Adopted the repository-wide Skill-owned Prompt placement rule so this Skill folder is the single source of truth for its Prompt variants.


## 1.1.0 — 2026-10-04

- Moved reusable execution rules from standalone Implementation Handoff prompts into the authoritative Skill.
- Added mandatory discovery and application of applicable `AGENTS.md` and environment-specific agent instructions, including Codex- and Claude-specific rules when present.
- Clarified that investigation and ordinary implementation begin without an Owner Approval Gate; a gate is created only for a genuine blocking conflict.
- Added strict sequential phase execution, focused completion verification, explicit `COMPLETE / PARTIALLY COMPLETE / BLOCKED` status, and protection against unresolved TODOs/placeholders being reported as complete.
- Added output guidance for one coherent handoff vs. genuinely multi-phase handoff packages.

## 1.0.0 — 2026-09-18

- First version tracked by this project; existing Skill content was preserved.
