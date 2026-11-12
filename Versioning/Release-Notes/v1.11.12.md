# AI Project Manager v1.11.12

This is a local repository update following the published `v1.11.10` release. It has not been published, installed, or pushed.

## Changes Since v1.11.11

- Corrected the transient-routing test's explicit-root output comparison to account for Windows case-insensitive path identity.
- Preserved ACL tests as `UNVERIFIED` skips when the current host token bypasses explicit deny ACLs; retained the actual safety assertions when denial can be enforced.
- Updated the Shared Project State Manager, platform, TUI, Plugin, and capability metadata versions. Rebuilt artifacts remain local.

## Component Versions

| Component | Version |
| --- | ---: |
| AIPM Platform | 1.11.12 |
| PowerShell TUI | 1.11.12 |
| Local Plugin distributions | 1.11.12 |
| Shared Project State Manager | 2.0.3 |
| Task Scope Contract | 1.0.3 |
| Resource Optimization | 2.0.3 |

## Verification And Limits

- The full Python suite ran 224 tests: 220 passed, 4 failed, 5 skipped. The failures were three Windows ACL probes that this elevated host token bypasses and one stale dashboard expectation for caller-reported `PASS`. The affected ACL cases now skip as `UNVERIFIED`; the dashboard expectation was corrected and its 5-test suite passed.
- Shared Project State Manager Python tests ran 50 tests: 49 passed, 1 failed on case-sensitive text comparison of equivalent Windows paths; the corrected test and full Skill suite must be rerun.
- Windows PowerShell 7 integration passed. Windows PowerShell 5.1 execution, link/hardlink capabilities, and runtime Plugin activation remain environment-limited or unverified.
- No trusted test-result certificate issuer/verifier is configured; caller-reported `PASS` remains `UNVERIFIED`. Provider token usage and comparable performance are `NOT_MEASURED`.

The latest published GitHub Release remains `v1.11.10`. No release, tag, upload, installation, or remote synchronization is part of this update.
