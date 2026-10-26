# AI Project Manager v1.6.13

**Release date:** 2026-10-26
**Platform and PowerShell TUI:** 1.6.13
**Compatibility:** Windows PowerShell 5.1 and PowerShell 7; Python 3.10 or later for Core and tooling.

Version 1.6.13 packages the accumulated platform updates since the previously published v1.4.0 release, including task lifecycle and recovery improvements, TUI reliability and performance fixes, capability documentation, and the new Web Design Engineering Skill.

## Added

- **Web Design Engineering Skill (`web-design-engineering` 1.0.2):** A first-party, reusable workflow for designing and implementing production web interfaces. It covers product-specific art direction, design tokens and component contracts, responsive behavior, Arabic/RTL layouts, accessibility, interaction states, reference fidelity, and rendered QA.
- Added practical Skill assets: seven focused references, five worked examples, reusable templates, configuration examples, deterministic Python helper scripts, automated helper checks, and evaluation cases.
- Added an attributed research synthesis drawing on public guidance from Impeccable, Anthropic Frontend Design, UI/UX Pro Max, Taste Skill v2, Emil Design Engineering, and complementary accessibility and verification projects. The Skill distills principles; it does not redistribute third-party Skill text, datasets, code, or assets.
- Expanded task management with editing task details, renaming task folders and identities, cloning tasks, opening task folders in Explorer, archiving tasks of any status, and confirmed deletion/unregistration workflows.
- Added self-contained, integrity-checked task archives and import/recovery workflows, including optional folder cleanup, registry removal, preservation of task history, and recovery from supported legacy task records.
- Added alphabetical General Skills and General Prompts indexes, source links, usage guidance, and automated synchronization checks.

## Fixed And Improved

- Hardened task-state recovery for legacy record formats, interrupted operations, historical event/manifest drift, and pending task commits. Recovery validates the authoritative state, creates verified backups where applicable, records explicit reconciliation events, and continues to reject unrelated or tampered state.
- Improved task rename, delete, reopen, and registration ordering so Core state changes are committed and validated before filesystem changes can leave orphaned or inconsistent records.
- Improved archive handling with checksum verification, unsafe-path defenses, extraction limits, staging, and regression coverage.
- Improved PowerShell TUI behavior for wrapped long input, resize/frame lifecycle, explicit Escape exit confirmation, task record refresh, and Help/Quit sentinels in nested menus.
- Added caching and rendering optimizations, durable atomic writes, non-blocking Windows artifact locking, cross-platform folder opening, and stricter Git-root boundaries for managed projects.
- Relicensed first-party project material under Apache License 2.0 and synchronized license/NOTICE metadata in generated distributions.
- Fixed Skill helper checks so generated Python bytecode cannot create accidental capability-catalog hash drift.

## Verification And Distribution

- The Web Design Engineering helper suite passed 3/3 checks; General Skills documentation checks passed; the updated Core dashboard test module passed 5/5 after synchronizing the expected first-party Skill inventory.
- Capability registry and provenance validation passed. The legacy Bridge and three multi-host Plugin archives were rebuilt and locally validated at the current capability baseline. ChatGPT/Codex and Claude package formats are verified; Google Antigravity archive content and hashes validate, while native host format/runtime acceptance remains unverified.
- The source archive is built from the release commit using the repository allowlist and verified against its embedded manifest and SHA-256 sidecar. The sidecar is attached with the source ZIP.
- Local package validation does not mean a Plugin is installed or accepted by ChatGPT/Codex, Claude Code, or Google Antigravity. GitHub Actions were not run for this release.
- The full Python suite was not rerun after the final dashboard assertion update; the focused dashboard suite is the evidence for that correction. Earlier full-suite evidence and host-restricted skips remain documented in the Support Matrix.

## Release Assets

- `AI-Project-Manager-v1.6.13.zip` — allowlisted source distribution.
- `AI-Project-Manager-v1.6.13.zip.sha256` — SHA-256 checksum sidecar for the source ZIP.

The [Support Matrix](../Support-Matrix.md) records verification scope and remaining host-specific limitations. See the [Host Adapter Contract](../../Plugins/Adapters/Host-Adapter-Contract.md) and [Project Rules](../Project-Rules.md) for operational boundaries.
