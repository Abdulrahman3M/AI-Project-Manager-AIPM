# P01 Migration Design

## Objective

Create the AI Project Manager repository baseline, migrate the approved General Skill subset, and leave an auditable Git and licensing foundation for later phases.

## Owner-Approved Exceptions

- The original package requirement to migrate 19 byte-identical General Skills is superseded for this repository by the owner's 2026-10-15 instruction: exclude `import-memory` and `morning`.
- `project-orchestrator` is a controlled AIPM derivative. Remove every `msg-*` Personal Skill reference from its `SKILL.md` and `CHANGELOG.md`; preserve the remaining files byte-identically.
- The resulting baseline is 17 migrated skill directories: 16 byte-identical and one recorded derivative. It must never be reported as 19/19 byte-identical.

## Architecture

The new repository owns only platform source, governance, tests, manifests, and static records. A deterministic Python migration utility reads the attached source tree, rejects links and unexpected input, stages copies outside the repository, performs the approved exclusions and narrowly scoped catalog removal, then validates hashes and emits a provenance report. The source tree is never written.

## Licensing

`LICENSE` at the repository root is Apache-2.0 for new AIPM-authored material only. Imported third-party notices remain in their original skill directories. The provenance record identifies the original Toolkit material and the two unresolved skills that were deliberately excluded.

## Acceptance Criteria

- Git repository is on `main` with the specified `origin` URL and no push.
- Exactly 17 Skill directories exist under `01-Skills-General`; `import-memory`, `morning`, and `02-Skills-Personal` are absent.
- The sixteen unmodified skills match the source file-for-file by SHA-256. `project-orchestrator` has only the documented Personal Skill catalog removals and no `msg-*` or `02-Skills-Personal` text.
- A machine-readable manifest records source, exclusions, hashes, licenses, and the derivative exception.
- Automated migration validation passes.
