# AI Project Manager v1.8.0

**Date:** 2026-10-26. Repository update; no GitHub Release, tag or host installation.

## Screenshot To Code

- Added original first-party `screenshot-to-code` `1.0.0` for direct, editable frontend reconstruction from screenshots and design images in the existing project stack.
- Added evidence/confidence records, CSS-vs-raster calibration, typography and asset resolution, Arabic RTL, regional comparison, bounded repairs and separate fidelity/behavior/responsive/accessibility gates.
- Added original Pillow tools for source pixel inspection and equal-size diagnostic comparisons, seven numeric regression tests, a runnable optional browser fixture and explicitly unexecuted behavioral evaluation scenarios.
- Reviewed 29 readable primary-source repositories from 31 attempted candidates. The research matrix distinguishes Skills, prompt generators, applications, QA tools and historical research, with strengths, limitations and file-content provenance.
- Updated `project-orchestrator` to `1.0.5` for current routing/catalog synchronization; General Skills inventory is 14.
- Source packaging now retains `.gitattributes` and the research/verification records in `docs/research/`.
- Restored seven original Skill VERSION files to the exact CRLF bytes already recorded by the protected hash baseline; added Git attributes to preserve those bytes. This repairs a checkout transport mismatch without altering the affected Skills' content versions or accepting a new hash for their originals. The generated Bridge copies were restored before the governed upgrade.

## Distribution And Verification

- Platform/TUI metadata: `1.8.0`; TUI runtime behavior unchanged.
- Legacy Project Agent Bridge: `1.2.0`, regenerated through the governed CLI.
- Multi-host local archive names: `AIPM-ChatGPT-Plugin-v1.8.0.zip`, `AIPM-Claude-Plugin-v1.8.0.zip`, `AIPM-Antigavity-Plugin-v1.8.0.zip`, each with a SHA-256 sidecar under `Plugins/Dist/`.
- The Python builder called by the approved PowerShell wrapper was used directly because PowerShell is absent on this host. All three archives passed local inventory/hash/manifest validation. Antigravity native format/runtime acceptance remains UNVERIFIED.
- See [verification evidence and limitations](../../research/Screenshot-To-Code-Verification.md). Local package validation is not host installation or runtime acceptance.
