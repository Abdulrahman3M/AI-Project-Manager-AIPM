# AI Project Manager v1.11.15

This synchronized repository update brings AIPM Platform, PowerShell TUI, the generated legacy bridge, and all multi-host Plugin distributions to `1.11.15`. It is not a formal GitHub Release; the latest-published-release badge remains unchanged.

## Changes Since v1.11.10

- Added signed, task-scoped test attestations so Core accepts verified completion only when signer workflow, repository, task ID, source commit, test suite, receipt digest, and passing result all match.
- Kept manual closure distinct from verified completion: caller-supplied results, invalid evidence, and historical records remain unverified.
- Hardened quarantine and file-state operations, transient-state routing, project-scope checks, task artifacts, capability integrity, and host fail-closed behavior.
- Added regression coverage for forged evidence, unsafe paths and moves, Windows state handling, POSIX fail-closed operation, Plugin inventories, version synchronization, and state-tool flows.
- Added a GitHub Actions verification path that runs the required Windows/POSIX checks and verifies a GitHub Artifact Attestation against the exact source revision.
- Excluded generated Python bytecode and cache folders from capability integrity checks and Plugin bundles.
- Synchronized product, TUI, legacy bridge, and multi-host Plugin metadata at `1.11.15`; standalone Skills retain their own governed SemVer versions.

## Verification And Distribution

- The verified-completion workflow succeeded on the temporary branch, including Windows Python/PowerShell tests, the Ubuntu POSIX fail-closed suite, attestation verification, and the bound Core completion check.
- Local ChatGPT/Codex, Claude Code, and Google Antigravity archives and SHA-256 sidecars are rebuilt and validated for `1.11.15`.
- Plugin archives are local build outputs only. This repository update does not install Plugins, publish a package, or create a formal GitHub Release.
- On non-Windows systems, guarded mutation operations remain unavailable and fail closed; diagnostics and dry-run remain available. This release does not claim POSIX mutation support.
