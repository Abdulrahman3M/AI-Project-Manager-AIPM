## [1.0.0] — AIPM Release Baseline

- Reset the Skill release line to 1.0.0 for independent AIPM development after project completion.

# Changelog

## 1.4.0 — 2026-10-13

- Added Strict Task Resume English and Arabic execution prompts, merged with Resume Task’s verified recovery and strict continuity rules.
- Preserved the `resume-task` skill identifier and existing full/short prompt compatibility.


## 1.3.0 — 2026-10-10

- Renamed the canonical Skill from `resume-verify` to `resume-task` (Resume Task) and improved limit-aware, cross-agent and cross-domain continuation.
- Updated the existing full `PROMPT.md` in place to reflect the canonical `resume-task` name and all interruption causes/AI-agent handovers, while preserving its original requirements, step-by-step verification, two-pass audit, safety boundaries, and reporting.
- Added a minimal Short Prompt plus a portable recovery reference, checkpoint example, read-only validator and tests.

## 1.2.0 — 2026-10-08

- Moved the paired task-resumption Prompt into this Skill as `PROMPT.md`.
- Removed the legacy standalone Prompt sidecars; the owning Skill version/changelog now governs this Skill-owned Prompt.
- Updated Prompt-local links to the colocated `SKILL.md`.


## 1.1.0 — 2026-10-08

- Clarified that the Skill is reusable across any project and that its source repository's rules do not govern other projects.
- Required agents to follow the active project's instructions and keep project-specific governance separate.


## 1.0.0 — 2026-10-08

- Added a reusable workflow for recovering interrupted tasks from verified state.
- Added interrupted-step-first verification, a strict acceptance gate after each step, two-pass final audit, evidence-based status reporting, and safe side-effect handling.
- Added project governance and related-Skill integration guidance.
