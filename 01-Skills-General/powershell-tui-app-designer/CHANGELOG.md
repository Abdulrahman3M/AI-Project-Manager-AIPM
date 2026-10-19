## [1.0.0] — AIPM Release Baseline

- Reset the Skill release line to 1.0.0 for independent AIPM development after project completion.

## 1.2.1 — 2026-10-20

- Synchronized the package overview and embedded version references with the managed Input/Frame lifecycle release.

## 1.2.0 — 2026-10-19

- Added a managed Input/Frame lifecycle contract and reference for typed prompts, cursor ownership, renderer-cache reconciliation, retries, Browse, resize, completion, and Run Again behavior.
- Added structured result-path rendering to the generated TUI template, preserving only explicit input/output values and avoiding stale input residue.
- Added regression coverage for consecutive path prompts, result frames, multiple inputs, and omitted output paths; documented the attached screenshots' root-cause explanation as a hypothesis unless source tracing confirms it.
- Updated the skill package validator to require the new lifecycle guidance and template behavior.

# Changelog

## 1.1.0 - 2026-10-19

- Added an end-to-end resize/frame lifecycle reference covering full-frame ownership, bounded idle resize detection, state preservation, stale-row cleanup, input/renderer architecture, test seams, failure modes, and real-terminal verification.
- Updated the generated Input, Renderer, Menu, and Prompt modules so interactive waits observe viewport changes without a key press, return an internal Resize event, and recompose without resetting workflow state or busy-spinning.
- Added regression tests for frame planning, idle resize, menu/prompt state retention, stale-frame removal, and deterministic scripted Resize events.
- Added evidence-first Windows Terminal launcher diagnostics for quoted paths with trailing separators, including a native `CommandLineToArgvW` parser probe and a separate child-execution acceptance requirement.
- Updated the reusable design prompt, architecture, compatibility, testing, design, engineering lessons, and checklists. This skill release does not claim native Windows Terminal visual verification.

## 2.0.3 - 2026-10-14

- Required centralized ANSI in-place frames with differential changed-row rendering; added the reusable Flicker-Free PowerShell TUI Architecture Prompt and robust fallback rules.
- Added terminal cursor-home and trailing erase behavior to the application scaffold, with safe legacy fallback.
- Reinforced independently colored icons, Emoji/Symbol/Ascii tiers, semantic colors, and muted help/description lines.
- Kept the master and bundled Plugin copies synchronized.

## 2.0.2 - 2026-10-11

- Added a Windows Terminal versus standalone Console host question; Windows Terminal is the default when the choice is skipped, unanswered or omitted.
- Specified Windows Terminal Emoji support with Unicode-symbol and ASCII fallbacks.
- Required English Title Case for static user-facing application text.
- Added package checks for the new host, icon fallback and text-style requirements.

## 2.0.1 - 2026-10-10

- Corrected malformed step numbering in Phase 1 and removed leftover compulsory-numbering examples from design and architecture guidance.
- Clarified that visual presets and navigation modes are independent, including the optional Classic Numbered appearance.
- Separated historical v1 test evidence from verified v2 scripted behavior and labeled SVG references as illustrative, not runtime screenshots.
- Synchronized developer documentation for the coordinated Universal AI ToolKit v0.9.0 project release; no runtime PowerShell module behavior changed.

## 2.0.0 - 2026-10-10

- Replaced mandatory numbers with arrows/numbers/hybrid/search modes; Classic Numbered remains optional.
- Introduced 20 reusable, neutral visual profiles and an interactive design questionnaire.
- Implemented generated-app design wizard, per-user persisted preferences, optional muted/shaded descriptions, colors and icon suppression.
- Extended generator options and added regression tests.
- Removed project-specific dependencies and historical reference illustrations.


## 1.0.0 - 2026-10-04

- Initial release in Universal AI ToolKit (formerly "PowerShell TUI Application Designer").
- 13-phase methodology, references, scripts, templates, examples and assets.
