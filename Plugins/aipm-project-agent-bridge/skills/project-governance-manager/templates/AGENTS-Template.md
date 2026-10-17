# AGENTS.md — <Project-Name>

> Root governance for AI agents and developers working on this project. Replace placeholders and remove sections that do not apply. Do not copy project-specific examples from another project without review.

## 1. Authority and precedence

Use this project's declared authority order:

1. latest explicit owner instruction for this project;
2. this root governance file;
3. current specialist rules inside their narrow scope;
4. current architecture/system specifications;
5. current operational procedures;
6. historical/archive material for traceability only.

Later current instructions override earlier conflicting instructions at the same authority level.

## 2. Mandatory pre-read

Before material work:

- read this file;
- read directly relevant specialist rules;
- inspect the affected implementation and direct dependencies;
- do not rely on memory when current authoritative files are available.

<Project-specific full-rule pre-read requirement, if any.>

## 3. Scope and preservation

- Implement only the requested scope.
- Clarify ambiguity that materially affects architecture, data, privacy, cost, or irreversible outcomes.
- Preserve existing behavior, content, data, and project knowledge outside scope.
- Do not delete, move, rename, overwrite, or restructure important resources without authority and impact review.
- Do not perform unrelated cleanup or refactoring.

## 4. Source of truth and ownership

- Define the canonical editable source for each major system/data family.
- Generated or distribution copies are not editing masters.
- Shared behavior has one canonical owner; consumers reuse it rather than duplicate it.
- <Project-specific canonical roots/systems.>

## 5. Naming and technical conventions

Human-facing naming policy:

> <Define the project's naming convention here.>

Technical names required by platforms, runtimes, languages, frameworks, imports, package managers, build systems, entry points, file formats, or configuration contracts retain their required spelling even when they differ from the human-facing style.

## 6. Paths and portability

- Prefer relative/site-relative project paths where appropriate.
- Do not introduce machine-specific paths unless explicitly required.
- External destinations may use absolute URLs.

## 7. Security, privacy, and external side effects

- Never commit secrets or sensitive credentials.
- Do not send project/user data to external services without explicit authority and a clear need.
- Apply an explicit approval/risk gate to destructive or externally visible actions.

## 8. Dependencies and architecture

- Reuse existing capabilities before adding new dependencies or services.
- Keep modules/files cohesive; do not split by arbitrary line count.
- Avoid duplicated shared logic.
- <Project-specific architecture rules.>

## 9. Testing and verification

- Validate modified files and directly affected dependencies first.
- Expand testing only when dependency impact requires it.
- Run the affected runtime path when behavior changed and the environment permits.
- Do not claim tests or runtime behavior were verified when they were not.
- Do not hide or disable failing tests to report success.

## 10. Performance

- Preserve correctness and data integrity above speculative optimization.
- Measure material performance claims where practical.
- <Project-specific budgets or performance gates.>

## 11. Documentation synchronization

When architecture, rules, paths, contracts, structure, or workflow change, update directly affected current documentation in the same task.

<Project-specific paired-language or synchronized-document rules.>

## 12. Versioning and history

<Project-specific version source, changelog/history system, IDs, immutable-record rules, or “not used”.>

If structured history records exist, read their current instructions before creating or updating them.

## 13. Integrity and generated artifacts

<Integrity baseline/hash policy if used.>

Generated/package/distribution copies must be regenerated from canonical sources rather than edited as competing masters.

## 14. Concurrency

If another session/person/automation may have changed authoritative state, refresh it before important final writes and reconcile rather than overwrite unfamiliar changes.

## 15. Cleanup

Remove only temporary artifacts created for the current task and proven no longer required. Preserve uncertain items.

## 16. Archive and legacy

Historical/superseded material is not current authority unless explicitly restored. Preserve traceability to current replacements where useful.

## 17. Licensing and attribution

Preserve project and third-party licenses, notices, and required attribution.

## 18. Completion report

State:

- what changed;
- what was verified;
- what was not verified;
- known limitations/risks;
- migrations or rollback considerations;
- directly affected documentation/history updated.

Never overstate completion beyond available evidence.

## 19. Specialist rules

List current specialist authorities and their scopes:

| Scope | Authority file | Notes |
|---|---|---|
| <system/domain> | <path> | <scope boundary> |

## 20. Project-specific permanent rules

Add only rules that are genuinely project-wide. Keep narrow implementation contracts in their specialist authority files.
