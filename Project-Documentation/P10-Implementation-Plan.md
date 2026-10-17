# P10 Documentation Packaging And Release Plan

## Scope

Prepare and verify the AIPM v1.0.2 source-release artifact, publish it to the owner-authorized GitHub repository, and provide beginner guides without installing the bridge or authorizing host access.

## File-Change Map

| Area | Change | Verification |
| --- | --- | --- |
| `Core-Engine/aipm_core/release.py` | Deterministic allowlisted archive builder and verifier. | `Tests/test_p10_release.py` |
| `Maintenance-Tools/New-Release-Package.py` | Repository CLI for local build and verification. | Build plus verify commands |
| Release metadata and docs | Version `1.0.2`, release notes, support matrix, README/index links. | Version/heading checks and packaged manifest |
| Capability registry and bridge | Refresh with explicit P10 reason; regenerate local bridge. | Capability CLI validation |
| `Releases/` | Ignored local ZIP and SHA-256 sidecar. | SHA-256 and archive-manifest verification |
| `docs/User-Guides/` | Beginner guides in English and Arabic. | Link, command, archive-allowlist, and content review |
| GitHub Release | Owner-authorized v1.0.2 release in the existing private repository. | Remote tag, release page, asset, and checksum reconciliation |

## Verification Commands

```powershell
python -m unittest Tests.test_p10_release -v
python Maintenance-Tools/Invoke-Capability-Library.py validate
python Maintenance-Tools/Invoke-Capability-Library.py validate-plugin --output Plugins/aipm-project-agent-bridge
python Maintenance-Tools/New-Release-Package.py build
python Maintenance-Tools/New-Release-Package.py verify --archive Releases/AI-Project-Manager-v1.0.2.zip
pwsh -NoProfile -File TUI/AI-Project-Manager/tests/Run-Tests.ps1
powershell.exe -NoProfile -ExecutionPolicy Bypass -File TUI/AI-Project-Manager/tests/Run-Tests.ps1
```

## Release Boundary

The package includes only allowlisted source, runtime, capability, public documentation, and provenance inputs, including `docs/User-Guides/`. It excludes internal phase evidence, local workspaces, cached bytecode, generated releases, Git data, and local tool state. It fails closed on reparse points, credential-like files/content, local checkout paths, metadata mismatch, checksum mismatch, or payload-hash mismatch. The release does not imply public repository visibility, marketplace publication, Plugin installation, or live host access.
