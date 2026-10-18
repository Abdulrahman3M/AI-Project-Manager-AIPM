# AI Project Manager v1.0.6 — Versioned Update Notes

> Repository update notes only. This version is not being published as a GitHub Release.

## Highlights

- Added the official project repository URL to the ChatGPT/Codex Plugin listing fields and to the documentation included in every host package.
- Kept portable Plugin homepage/repository metadata and the ChatGPT listing's `websiteURL` aligned with the AIPM repository.
- Reorganized the repository's current architecture documentation and consolidated 46 internal construction records into one historical ZIP archive.
- Made the source-release package include the current architecture and Plugin build sources while keeping generated Plugin ZIPs and the historical build archive as separate artifacts.
- Advanced the platform and PowerShell TUI together to `1.0.6`; the independently versioned legacy Project Agent Bridge advances to `1.0.5`.

## Verification

- The local multi-host builder validates each host archive's expected inventory, approved capability content, host manifest, exclusions, and SHA-256 sidecar.
- The `1.0.6` source ZIP and checksum sidecar were built and verified locally; neither was attached to a GitHub release in this update.
- The historical archive preserves the archived source files byte-for-byte and is not a runtime input or part of the distributable source release.

## Boundaries

- Package-format validation does not mean that a Plugin was installed, accepted by a host, published to a marketplace, or granted local project access.
- Claude Code package output is locally validated only. Google Antigravity remains `FORMAT_UNVERIFIED` pending an authoritative format and host test.
- P09's physically external project fixture, durable host-capture provenance, and live cross-agent verification remain `UNVERIFIED`; no GitHub Actions run is claimed.
