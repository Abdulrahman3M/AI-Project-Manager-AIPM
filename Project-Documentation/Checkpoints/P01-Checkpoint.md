# P01 Checkpoint

## Confirmed State

- Git branch: `main`.
- Remote: `origin` points to the owner-specified GitHub repository.
- Approved migration baseline: 17 Skill directories under `01-Skills-General`.
- `Project-Documentation/Provenance/Skill-Migration-Record.json` is the machine-readable evidence record.
- P02 has not started.

## Ruling

The migration staging directory lives under the ignored `.migration-staging/` directory because this execution environment denies writes to the repository parent. It is automatically cleaned after migration. This preserves source immutability and prevents tracked staging data, but is not the package's preferred outside-repository location.
