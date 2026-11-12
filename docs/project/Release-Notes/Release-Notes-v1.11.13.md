# AI Project Manager v1.11.13

This local repository update follows `v1.11.12`; it has not been published, installed, or pushed.

## Changes Since v1.11.12

- Capability inventory and generated Skill/Plugin packages now exclude `__pycache__`, `.pyc`, and `.pyo` artifacts. Linked/reparse directories remain rejected.
- Added a regression test for bytecode/cache exclusion. Rebuilt the protected capability baseline and local packages from canonical Skill sources.
- A restored task record cannot gain verified completion from a caller-controlled `verified` flag. Core read projections expose `UNVERIFIED` and retain the original as `reported_result` without rewriting stored records.
- The phase planner also treats caller-supplied PASS values as UNVERIFIED and acceptance entries are immutable; such values cannot advance progress or close a phase.

## Component Versions

| Component | Version |
| --- | ---: |
| AIPM Platform | 1.11.13 |
| PowerShell TUI | 1.11.13 |
| Local Plugin distributions | 1.11.13 |
| Shared Project State Manager | 2.0.4 |
| Task Scope Contract | 1.0.3 |
| Resource Optimization | 2.0.3 |

## Verification And Limits

- Full Python test suite: `227` tests run; `219` passed and `8` were skipped for environment-limited ACL, junction, and hard-link privileges.
- Capability Library suite: `22/22` passed. Shared Project State Manager suite: `50/50` passed with one hard-link privilege skip.
- All three Plugin archives passed independent SHA-256, version, path-traversal, and bytecode-exclusion checks. Runtime installation and host Skill interception remain unverified.
- The trusted test-result certificate issuer/verifier is not configured; caller-reported `PASS` remains `UNVERIFIED`. Provider token use and comparative performance are `NOT_MEASURED`.

The latest published GitHub Release remains `v1.11.10`. No release, tag, upload, installation, or remote synchronization is part of this update.
