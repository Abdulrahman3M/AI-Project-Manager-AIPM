# AI Project Manager v1.11.11

This is a **local repository update**, following the published `v1.11.10` release. It has not been published, installed, or pushed. The changes focus on the security and technical audit of AIPM task evidence, Skills, state tooling, and local Plugin packaging.

## Changes Since v1.11.10

- AIPM Core no longer treats caller-supplied `PASS` text or manual task closure as verified completion. Manual closure is shown as `CLOSED-UNVERIFIED`; legacy `COMPLETE` records remain stored but are surfaced as `UNVERIFIED` unless trusted verification exists.
- State reads derive the visible task status without rewriting existing manifests or history. UI labels distinguish closed-unverified and unverified tasks.
- Task Scope Contract reports caller results as `REPORTED_PASS` and path preflight as provisional. Resource Optimization rejects ambiguous overlapping aliases. Neither policy helper claims to enforce host filesystem or subagent permissions.
- Shared Project State Manager quarantine, guarded file operations, transient routing, and Node state access reject forged/legacy records and protect project roots, nested protected directories, links, destination collisions, and dry-run behavior. Old quarantine records without source binding are refused for manual review.
- Plugin build metadata now explicitly identifies status as build-time only. Host packages are local archives, not installed host integrations.
- Updated the affected Skill, platform, TUI, Plugin, and capability metadata versions and the related operator documentation.

## Component Versions

| Component | Version |
| --- | ---: |
| AIPM Platform | 1.11.11 |
| PowerShell TUI | 1.11.11 |
| Local Plugin distributions | 1.11.11 |
| Task Scope Contract | 1.0.3 |
| Resource Optimization | 2.0.3 |

## Verification And Limits

- Core task lifecycle and task artifact suites: 17/17 and 22/22 passed; one hard-link fixture was skipped because Windows denied the required privilege.
- Host adapter suite: 9/9 passed. Integrated security suite: 3/3 passed after updating caller-reported PASS expectations.
- Shared state safety, PowerShell, and routing focused suites are recorded in the audit checkpoint. Windows PowerShell 5.1 could not run under the current authorization policy; PowerShell 7 integration passed.
- Plugin archives are built locally only after the capability baseline is validated. Archive validation does not prove installation or runtime activation in ChatGPT/Codex, Claude Code, or Antigravity.
- A production trusted test-result attestation source is not configured in this repository. Caller-reported PASS remains `UNVERIFIED`; verified completion through a genuine trusted certificate is therefore not established. Provider token and comparable performance measurements are `NOT_MEASURED`.

The latest published GitHub release remains `v1.11.10`. No release, tag, upload, installation, or remote synchronization is part of this update.
