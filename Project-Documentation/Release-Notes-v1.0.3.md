# AI Project Manager v1.0.3

This patch release refreshes the GitHub project homepage and aligns the published source package with it. No project runtime behavior or individual Skill version was changed.

## Highlights

- Added an adjacent product version and a restrained status-badge strip to the repository README.
- Added release synchronization requirements to `AGENTS.md` so future releases keep the README, version metadata, source archive, and GitHub release aligned.
- Synchronized the platform and TUI product versions at `1.0.3`; independent Skill and Agent Bridge package versions remain unchanged.
- Rebuilt the allowlisted source archive and its SHA-256 sidecar using the local release tool.

## Verification And Boundaries

- The local release archive and checksum must pass `Maintenance-Tools/New-Release-Package.py verify` before publication.
- GitHub Actions were not run; this avoids consuming the owner's unavailable Actions minutes.
- P09 live external-host and cross-agent gates remain `UNVERIFIED`. This release does not claim those checks passed.
- The repository remains private. The release does not install or activate the Agent Bridge in an AI host.

## Assets

- `AI-Project-Manager-v1.0.3.zip` — source package.
- `AI-Project-Manager-v1.0.3.zip.sha256` — SHA-256 checksum sidecar for the source package.
