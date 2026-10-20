# AI Project Manager v1.4.5

Repository update; not published as a GitHub Release. The latest published release remains `v1.4.0`, and no `v1.4.5` tag was created.

This update follows `v1.4.0` and improves two capability workflows: more accurate Skill selection for user intent and safer PowerShell TUI input/frame handling. No breaking project API changes are intended.

## Skill Selection Improvements

- Project Orchestrator parses outcome, work mode, deliverable, intended recipient, and constraints before selecting a Skill.
- Requests for an implementation handoff, execution prompt, task brief, or Markdown instructions another AI agent will use to implement/change/repair work route to Create Strict Implementation Handoff. Generic README, tutorial, notes, or explanatory Markdown does not trigger that Skill merely because it uses `.md`.
- The Orchestrator catalog is synchronized to the active Capability Library rather than removed Skills and historical versions.
- Genuine catalog gaps trigger trusted online discovery when available, with evaluation of capability fit, provenance, maintenance, license, permissions, security, compatibility, and quality evidence. Discovery does not authorize installing or executing downloaded content.
- If network search is unavailable, the base agent may proceed using native capabilities only when it can safely verify the result; otherwise it must report the limitation.
- Added routing-contract tests for registry/catalog parity, handoff intent, and online/offline gap handling.

## PowerShell TUI Input Lifecycle

- Added `Input-Frame-Lifecycle.md`, covering cursor ownership, renderer-cache reconciliation, typed input as workflow state, resize, validation retries, Browse, result screens, and Run Again.
- Added `Write-ResultPathContext` to the generated TUI Dialog module to render real structured input/output paths within the result frame and omit unavailable values.
- Added regression tests for consecutive input sessions, replacement of old input by new input, result paths, multiple input paths, and absent output paths.
- The attached screenshots establish the visible stale/misplaced path symptoms; the handoff's proposed cursor/cache root cause remains a hypothesis unless confirmed by source-level tracing in the affected application.
- Reconciled the TUI Skill package overview and embedded version references with its current independent Skill version.

## Versions

- AIPM platform: `1.4.5`
- PowerShell TUI: `1.4.5`
- Project Orchestrator: `1.0.4`
- PowerShell TUI App Designer: `1.2.1`
- Create Strict Implementation Handoff: `1.0.0` (protected source content preserved)
- Legacy Project Agent Bridge and multi-host archives: regenerated from the v1.4.5 Capability Library.

## Verification And Limits

- Routing and generated TUI regression checks are included in repository test suites.
- ChatGPT/Codex, Claude Code, and Google Antigravity archives are local distribution builds; they do not imply host installation or acceptance.
- External-host handoff, Google Antigravity native format/runtime acceptance, and a live real-terminal visual run remain separate checks and are not inferred from package tests.
- The source ZIP and `.sha256` sidecar were generated and verified locally; they were not attached to a GitHub Release.
