# AI Project Manager v1.8.1

**Date:** 2026-10-26. Repository update; not a GitHub Release. No remote push, tag, publication, or host installation.

## Screenshot To Code

- Updated the original `screenshot-to-code` Skill from `1.0.0` to `1.1.0`.
- Screenshot-only reconstruction remains the default. Added explicit user opt-in for approved browser inspection, narrow page scope, visible client-side evidence, browser identity checks, privacy boundaries, and fallback when browser access is unavailable.
- Added examples for unknown viewport scale, separate desktop/mobile references, Arabic mixed-direction text, missing fonts, unseen dynamic states, and cropped screenshots.
- Added the rule to verify or define CSS custom properties before referencing them.
- Reviewed 29 readable primary-source projects and 538 GitHub issues. See the [hardening audit](../../research/Screenshot-To-Code-Hardening-Audit.md), [source evidence](../../research/Screenshot-To-Code-Hardening-Audit.json), and [complete issue title/status index](../../research/Screenshot-To-Code-Issue-Index.csv).

## Versions And Local Distributions

- Platform and PowerShell TUI metadata: `1.8.1`; TUI runtime behavior is unchanged.
- `project-orchestrator`: `1.0.6`; `screenshot-to-code`: `1.1.0`.
- Legacy Project Agent Bridge: `1.2.1`.
- Multi-host archives are rebuilt locally as `AIPM-ChatGPT-Plugin-v1.8.1.zip`, `AIPM-Claude-Plugin-v1.8.1.zip`, and `AIPM-Antigavity-Plugin-v1.8.1.zip`, each with a SHA-256 sidecar under `Plugins/Dist/`.
- Local package validation does not imply installation or host-native runtime acceptance.

## Verification Limits

- Focused checks passed: evidence modes (4), visual helpers (7), General Skills docs (3), Orchestrator contract (3), Plugin distribution (6), P06 Capability Library (21), and P10 release packaging (3).
- Registry and local Plugin validation passed for 14 Skills and 1 standalone Prompt; Bridge `1.2.1` generated and validated. Multi-host v1.8.1 archives and checksum sidecars were built locally. ChatGPT/Codex and Claude formats are verified; Antigavity's native acceptance is not.
- The 10 historical test identities were rerun: seven pass; three junction tests skip because Windows denied `cmd /c mklink /J`. The current outcomes and prior failure identities are recorded in the [verification record](../../research/Screenshot-To-Code-Verification.md).
- Browser-environment metadata was found, but active-process inspection was denied by Windows CIM permissions. No target page was supplied or inspected; browser availability remains unverified.
- The full repository suite and held-out autonomous reconstruction scenarios were not run.
- No GitHub push, tag, Release, or publication was performed.
