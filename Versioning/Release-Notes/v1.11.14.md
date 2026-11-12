# AI Project Manager v1.11.14

This local, unpublished repository update follows `v1.11.13`. It adds a task-scoped verified completion path while keeping unsigned and historical caller results unverified.

## Changes

- Core can verify a GitHub Actions test-result attestation using the signed receipt digest, the configured repository and workflow identity, the recorded source commit, the task ID, and the fixed test suite contract. Core verifies evidence only; it never runs project tests.
- A Windows CI workflow runs the complete Python and PowerShell suites, creates and signs a test receipt, verifies that attestation with GitHub CLI, and executes the real Core completion path using the signed receipt.
- The PowerShell task verification UI can pass the expected source commit. A missing receipt, invalid signature, untrusted signer, wrong task/source, mismatched suite, or missing local GitHub CLI keeps the task `UNVERIFIED`.
- Manual close remains `CLOSED-UNVERIFIED`. Existing archives, task IDs, APIs, and historical records remain compatible; prior records are not promoted retroactively.
- Tests now expect imported legacy PASS values to stay unverified and the evidence dashboard not to count them as verified.
- Generated capability bundles now exclude Python bytecode; legacy bundle upgrades tolerate untracked runtime caches while continuing to validate canonical file bytes.
- Ubuntu compatibility tests confirm non-Windows guarded mutations refuse unsafe operations without changing source data, while read-only diagnostics and dry-run continue to work.
- GitHub Actions ran 238 Windows Python tests (two POSIX-only cases skipped there), 278 PowerShell checks with zero failures or unverified results, and 2/2 POSIX compatibility tests on Ubuntu. The signed receipt passed GitHub verification and the bound Core completion path.

## Component Versions

| Component | Version |
| --- | ---: |
| AIPM Platform | 1.11.14 |
| PowerShell TUI | 1.11.14 |
| Local Plugin distributions | 1.11.13 (unchanged) |

## Verification Status

- Local unit tests for the attestation verifier and task lifecycle passed; the branch workflow records the exact Python and PowerShell test counts and verifies the signed receipt.
- The Core positive-path check returned `COMPLETE` only for the task/source-bound receipt on the tested commit. Caller-provided completion remains unverified.
- Non-Windows guarded mutations remain unsupported and fail closed; Ubuntu tests verify refusal and preserve existing data. This is not POSIX mutation support.
- The latest published release remains `v1.11.10`. This update is not a release, is not merged, and does not install or publish Plugins.
