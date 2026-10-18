# AIPM Change Log

## [Unreleased]

- No unreleased changes.

## [1.1.7] — Task Context And Agent Handoff Architecture (Development; Not Published)

- Established the Core principle that AIPM manages task context, supporting artifacts, progress, evidence, and handoffs—not target-project implementation files, tests, or execution permissions.
- Added isolated per-task artifact directories, bounded atomic writes, checkpoint fields, task read/list and artifact CLI commands, and local adapter access for declared task artifacts only.
- Added bilingual beginner instructions for creating, checkpointing, and resuming tasks across separate Core CLI processes; documented that source paths are references to original project files.
- Added a regression test that demonstrates atomic replacement of generated task projections, avoiding write-through to a hard-linked project source. The direct hard-link test is skipped when the Windows host denies link creation.
- Included the sanitized, documented project-state example template for task plans, checkpoints, and handoffs.
- Synchronized platform and TUI development versions at `1.1.7` under the project's SemVer policy. Refreshed the protected capability registry and provenance through the confirmed CLI workflow; rebuilt the metadata-dependent local Bridge at `1.0.7` and multi-host archives at `1.1.7`. No Skill or Prompt content changed, and no GitHub push, tag, source release, or GitHub Release was performed.

## [1.0.7] — Protected External Project Operations And Registry Control

- Added Core-enforced protection that blocks managed project roots, registry paths, and registry backup or restore paths which overlap the AIPM installation.
- Added guarded project registry administration through the Core CLI and Intelligent TUI: first-run location selection, project registration, pointer-only removal, checksummed backup, verified restore with a safety copy, and registry-location switching.
- Documented the owner authorization boundary: normal AIPM use cannot mutate the AIPM installation through supported Core operations; host or OS permissions remain required to constrain direct external filesystem writes.
- Advanced the platform and PowerShell TUI together to `1.0.7`. No Skill or Prompt source changed; the legacy Bridge retained its independent `1.0.6` version, while the three multi-host archives were rebuilt with synchronized `1.0.7` catalog metadata.

## [1.0.6] — Project Architecture, Plugin Website, And Release Hygiene

- Added and locally validated the multi-host Plugin build system for ChatGPT/Codex, Claude Code, and Google Antigravity, with capability inventory, SHA-256, exclusion, tamper, and profile validation.
- Added the official AIPM project URL to the ChatGPT/Codex Plugin listing metadata and to every host archive's README; added homepage/repository metadata to the portable and legacy Bridge manifests.
- Reorganized the current project architecture and moved 46 internal implementation plans, phase reports, checkpoints, handoffs, and design records into `docs/project/Build-History-Archive.zip`.
- Updated the source-release allowlist to include the current architecture and Plugin build sources while excluding generated Plugin ZIPs and the internal build-history archive.
- Included the previously accumulated platform work: the Core-backed PowerShell TUI, owner-managed capability inventory, and governed cross-host Skill/Prompt packaging. P09 external-host gates remain explicitly unverified.
- Advanced the platform and TUI together to `1.0.6`; advanced the independently versioned legacy Project Agent Bridge to `1.0.5` for its metadata update.

## [1.0.5] — Plugin Upload Compatibility And Automatic Synchronization

- Made the ChatGPT/Codex distribution produce portable Agent Plugins metadata, complete listing metadata, a bundled icon, and valid YAML Skill front matter without changing canonical Skill source files.
- Added the permanent Automatic Plugin Synchronization rule for all Skill and Prompt changes, including multi-host rebuild, validation, versioning, and reporting requirements.
- Rebuilt the ChatGPT/Codex, Claude Code, and Google Antigravity distribution archives from the current protected capability registry.

## [1.0.4] — Documentation Layout Consolidation

- Grouped user guides and project records under `docs/`, and grouped host adapter specifications under `Plugins/`.
- Updated Core Engine, migration tooling, release allowlists, and documentation links to the organized paths.
- Kept the generated bridge and independently versioned Skills unchanged.

## [1.0.3] — Homepage Presentation And Release Synchronization

- Added a versioned, linked README status strip and an explicit release-synchronization rule in `AGENTS.md`.
- Published matching source metadata, release notes, ZIP, and SHA-256 checksum for the current product version.
- Kept P09 external-host gates explicitly unverified and did not run GitHub Actions.

## [1.0.2] — Documentation And GitHub Release

- Added deterministic source-release packaging with SHA-256 verification, an allowlisted file set, and credential/local-path checks.
- Added step-by-step English and Arabic beginner guides and published the v1.0.2 source archive to the owner-maintained GitHub repository.
- Kept the repository's existing private visibility; no Actions workflows, marketplace publication, Plugin installation, or host activation were performed.
- Recorded the P09 external-host and durable-capture exceptions as unverified owner-controlled gates.

## [1.0.1] — Skill Release Baseline And Agent Bridge

- Rebased all active Skills to independent `1.0.0` AIPM release baselines.
- Replaced the Skills-only sample with the local AIPM Project Agent Bridge package.

## [1.0.0] — Personal License And Refined Terminal Frames

- Reset the AIPM product release line to `1.0.0` and adopted the AI Project Manager Personal Use License.
- Removed the six third-party Skills requested by the owner and regenerated the local Capability Library sample.
- Replaced dashed terminal frames with connected, bounded Unicode borders.

## [0.2.1] — Product Shell, Capability Library, And Session Efficiency

- Added a framed product name and version header across the dashboard and primary pages.
- Added responsive Capability Library tables while retaining imported Skill source-license metadata and unverified Plugin installation/publication status.
- Cached stable menu geometry, captured one Core-backed session snapshot, and limited subsequent Core reads to explicit Refresh actions.
- Synchronized the platform and TUI package versions at 0.2.1; the protected capability registry baseline remains unchanged.

## [0.2.0] — Host Adapters And Intelligent TUI Design

- Added the first-party `tui-intelligence` Skill, scoped to Apache-2.0 and distinct from imported Skills.
- Added a permission-gated Core Engine host adapter contract and capability matrix.
- Added a design system, mockup references, and no-flicker acceptance contract; no live renderer is claimed.
- Added official-format sample manifests for OpenAI Agent Plugins, Claude Code, and Gemini CLI; no package was installed or published.
- Preserved all 16 imported Skill hashes and the documented `project-orchestrator` derivative.

## [0.1.0] — Initial Platform Version

- Added the governed capability registry, source provenance ledger, and local-only general Skills Plugin sample in P06.
- Established independent platform, Skill, and Plugin version handling; no imported Skill master was edited.
- Verified the read-only Universal AI ToolKit `main` source commit and preserved its Personal Use License alongside per-Skill notices.
- The generated Plugin remains unpublished and uninstalled; no remote write was performed.
