# AI Project Manager v1.0.2 Release Notes

## Release Decision

`OWNER_REPOSITORY_RELEASE_ASSET`

The reproducible source archive is attached to the `v1.0.2` GitHub release in the owner-maintained AIPM repository. The repository retains its private visibility; GitHub access is required. No marketplace publication, Plugin installation, or host activation is implied.

## Included

- Deterministic `New-Release-Package.py` source packaging and archive verification.
- SHA-256 sidecar checksum and in-archive manifest with a hash for each payload file.
- English and Arabic beginner guides, Core Engine, PowerShell TUI, governed capability library, and the local AIPM Project Agent Bridge.
- AI Project Manager Personal Use License coverage for AIPM-owned material and generated distributions.

## Excluded From The Archive

- `.git`, local tool state, test workspaces, generated release outputs, caches, and transient files.
- Internal phase plans, checkpoints, handoffs, reports, and development-only planning records.
- Personal Skills, `import-memory`, `morning`, and the owner-removed third-party Skills.

## Source Archive

- Version: `1.0.2`
- Asset: `AI-Project-Manager-v1.0.2.zip`
- SHA-256: See the attached `AI-Project-Manager-v1.0.2.zip.sha256` sidecar asset.
- Payload: 823 files plus the generated release manifest.
- GitHub release: `https://github.com/Abdulrahman3M/AI-Project-Manager-AIPM/releases/tag/v1.0.2`

## Verification

Run from the repository root:

```powershell
python Maintenance-Tools/New-Release-Package.py build
python Maintenance-Tools/New-Release-Package.py verify --archive Releases/AI-Project-Manager-v1.0.2.zip
```

The builder rejects reparse points, sensitive-looking files, private-key or AWS-key patterns, and the actual local checkout path in selected payloads. The verifier checks the sidecar checksum, bounded archive layout, version metadata, manifest, and every payload hash.

## Known Limits

- The local bridge package is a format-validated sample; it is not installed or published.
- P09's physically external project fixture, live independent agent/host handoff, and durable native-terminal capture provenance remain `UNVERIFIED` under the owner-approved repository-only test boundary.
- The repository remains private. Changing visibility, marketplace listing, host installation, and live agent activation remain separate owner-controlled actions.
