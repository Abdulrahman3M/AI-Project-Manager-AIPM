# P10 Release Handoff

## Current Release Artifact

- Version: `1.0.2`
- Path: `Releases/AI-Project-Manager-v1.0.2.zip`
- SHA-256: `451ED57D3C16C29C9C29841D4BED580D2E55D66112DB32AAE01AA5DE4BF702ED`
- Payload Files: `823`
- State: `RELEASED_TO_PRIVATE_GITHUB_REPOSITORY`
- Tag: `v1.0.2`
- Release: `https://github.com/Abdulrahman3M/AI-Project-Manager-AIPM/releases/tag/v1.0.2`

## Verify The Published Asset

```powershell
python Maintenance-Tools/New-Release-Package.py verify --archive Releases/AI-Project-Manager-v1.0.2.zip
python Maintenance-Tools/Invoke-Capability-Library.py validate
python Maintenance-Tools/Invoke-Capability-Library.py validate-plugin --output Plugins/aipm-project-agent-bridge
```

## Boundaries

- The requested GitHub source release is published to the owner-specified private repository. Preserve its visibility unless the owner explicitly requests a change.
- Do not install or activate the Agent Bridge, or modify the Universal AI ToolKit source, without a separate explicit owner instruction.
- P09 remains `IMPLEMENTED_WITH_UNVERIFIED_GATES`; its unresolved external-environment gates must remain visible in any public-facing release decision.
- The release builder is the only supported path for the ZIP and keeps outputs under this repository.
