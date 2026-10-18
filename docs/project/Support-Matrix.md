# AI Project Manager Support Matrix

## Verified In This Repository

| Component | Environment | Status | Evidence |
| --- | --- | --- | --- |
| Core And Capability Validation | Python 3.14 | PASS | Focused P02–P10 `unittest` suite and capability-library validation. |
| Terminal TUI Tests | PowerShell 7.6.5 | PASS | `TUI/AI-Project-Manager/tests/Run-Tests.ps1`. |
| Terminal TUI Tests | Windows PowerShell 5.1.26100.9444 | PASS | `TUI/AI-Project-Manager/tests/Run-Tests.ps1`. |
| Latest Published GitHub Source Release | Owner repository, private visibility | PASS | `v1.0.2` is the latest published release observed on GitHub. Repository version `1.0.6` is not being published as a GitHub Release in this update. |
| Local Source Package | Python standard library | PASS | Built and verified `Releases/AI-Project-Manager-v1.0.6.zip` with its SHA-256 sidecar (833 files). Not attached to a GitHub release in this update. |
| Multi-Host Plugin Archives | Local Python build and archive verification | PASS (local package checks) | ChatGPT/Codex, Claude Code, and Google Antigravity ZIP inventory, approved content, manifests, exclusions, and sidecars at version `1.0.6`. This does not verify host installation. |
| AIPM Project Agent Bridge | Local package validation | PASS | Capability-library CLI validates structure and byte parity; current Bridge version is `1.0.5`. |

## Deliberately Not Claimed

| Capability | Status | Reason And Owner-Controlled Next Action |
| --- | --- | --- |
| Plugin installation in an AI host | UNVERIFIED | Keep the bridge local until the owner authorizes an explicit supported-host installation. |
| ChatGPT Plugin uploader acceptance | UNVERIFIED | The ZIP structure and listing metadata are checked locally; upload it in the authenticated ChatGPT environment to confirm server-side acceptance. |
| Public repository visibility or marketplace listing | NOT PERFORMED | The owner repository remains private; public visibility and marketplace listing are separate owner-controlled decisions. |
| Live cross-agent handoff | UNVERIFIED | Requires a supported independent host session and explicit access grant. |
| Physically external project fixture | UNVERIFIED | The owner restricted all test writes to this repository. |
| Reproducible native-terminal capture provenance | UNVERIFIED | Owner visually accepted the UI, but no durable host/version/capture artifact is retained locally. |

## Operating Boundaries

- The TUI is read-only and requires Python 3.10 or later plus Windows PowerShell 5.1 or PowerShell 7.x.
- Host adapters remain capability-declared, permission-gated, and fail-closed.
- The GitHub source release does not grant automatic project-file access to an AI host.
