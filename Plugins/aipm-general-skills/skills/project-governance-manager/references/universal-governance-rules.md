# Universal Project Governance Rules

This catalog is designed for reuse across software, documentation, data, research, content, automation, and mixed projects. It separates **Core Universal Rules** from **Conditional Modules** so a project does not inherit irrelevant constraints.

## A. Core Universal Rules

### 1. Authority and precedence

- Define one clear governance hierarchy.
- The project owner's latest explicit project instruction outranks older conflicting project instructions.
- A specialist rule may override a general rule only inside its declared narrow scope.
- Historical or archived material is evidence, not current authority, unless explicitly restored.
- Do not create two competing authoritative documents for the same rule set.

### 2. Read current rules, not remembered rules

- Read the current root governance file before material changes.
- Read directly relevant specialist rules before modifying their system.
- Do not rely on an earlier session or memory when the current authoritative file is available.
- If a project explicitly mandates reading an entire rule set before every task, obey that gate.
- Otherwise use minimum sufficient inspection rather than whole-repository scanning by default.

### 3. Understand scope before implementation

- Identify the requested objective, acceptance criteria, in-scope work, out-of-scope work, and what must be preserved.
- Ask for clarification when ambiguity could materially change architecture, data, behavior, privacy, cost, or irreversible outcomes.
- Do not invent product requirements.
- Do not implement unrelated improvements merely because they appear useful.

### 4. Preserve project knowledge, behavior, and data

- Never simplify by silently deleting useful information.
- Preserve existing behavior outside the requested scope.
- Do not remove, rename, move, overwrite, or restructure important resources without authority and impact review.
- When deprecating material, archive or clearly mark it instead of erasing traceability where history matters.

### 5. Canonical source of truth

- Each governed fact, system contract, or editable master should have one authoritative source.
- Generated, exported, packaged, mirrored, cached, or distribution copies must not become competing editing masters.
- Changes flow from the canonical source to derived copies, not the reverse.

### 6. Inspect minimally but sufficiently

Use the default progression:

**Read governance → understand minimal structure → locate the relevant area → inspect directly relevant files → inspect required direct dependencies → implement**

Expand only when evidence shows the current scope is insufficient.

### 7. Preserve technical conventions

- Names required by languages, frameworks, runtimes, package managers, import systems, build systems, file formats, entry points, or platform specifications take priority over cosmetic naming policies.
- Never rename an execution-critical path merely to satisfy a human-facing style rule.
- Keep generated interfaces and configuration contracts stable unless a migration is part of the task.

### 8. Portable paths and environment independence

- Prefer project-relative or site-relative paths where technically appropriate.
- Avoid embedding local drive letters, user directories, machine-specific hostnames, ports, or environment-specific paths unless the project explicitly requires them.
- External destinations may use normal absolute URLs.

### 9. Privacy, credentials, and external side effects

- Never place secrets, passwords, API keys, tokens, or sensitive personal data in source code, logs, or ordinary documentation.
- Do not transmit project/user data to an external service without explicit authority and a clear need.
- Treat destructive or externally visible actions as higher-risk than local reversible edits.

### 10. Dependency and service restraint

- Reuse existing project capabilities before introducing new dependencies, frameworks, databases, cloud services, APIs, or tooling.
- Add a dependency only when it provides a clear requirement-level benefit.
- Check compatibility, licensing, security, update ownership, and operational cost before adoption.

### 11. Canonical ownership and no duplication

- Shared behavior should have one clear owner.
- Do not duplicate the same central logic independently across multiple consumers.
- Keep genuinely local behavior with its local owner.
- Split code or documents by cohesive responsibility, not arbitrary line-count targets.

### 12. Backward compatibility and migration

- Do not break existing routes, interfaces, schemas, imports, or contracts casually.
- When a breaking change is required, define migration, compatibility impact, and rollback/recovery before release.
- Preserve user data throughout migration.

### 13. Proportional validation

- Test the changed files and directly affected dependencies first.
- Expand validation only when dependency impact requires it.
- A syntax/type check proves syntax/shape only; it does not prove runtime behavior.
- When runtime behavior changed, execute the affected path when technically possible.
- Do not claim a test passed if it was not actually run.

### 14. Failures must remain visible

- Never hide, disable, weaken, or bypass a failing test merely to report success.
- Reproduce relevant failures and identify the cause before completion claims.
- If a required verification cannot be run, state that explicitly.

### 15. Evidence-based performance claims

- Do not infer performance from file count, subjective feel, or code appearance alone.
- Measure the relevant route/workflow when practical.
- Correctness and data integrity outrank speculative optimization.

### 16. Documentation synchronization

- When a task changes architecture, rules, paths, contracts, structure, or workflow, update directly affected current documentation in the same task.
- Do not update unrelated documentation for appearance.
- Do not knowingly leave current editable documentation pointing at a moved or renamed resource.

### 17. Project-specific naming policy

- A project may define a naming convention for human-facing files and folders.
- Do not import another project's naming style automatically.
- Exceptions, numbering, symbols, language suffixes, and casing rules belong to the target project's policy.
- Technical-standard names remain exempt when required for correct operation.

### 18. Generated and derived artifacts

- Clearly distinguish generated/derived files from editable masters.
- Regenerate derived outputs from the authoritative source where possible.
- Do not hand-edit generated copies when a supported source-driven workflow exists.

### 19. Concurrency-safe writes

- Before important final writes, refresh the authoritative state when there is evidence another session, person, or automation may have changed it.
- Never overwrite unfamiliar concurrent work blindly.
- Reconcile conflicts and preserve both sets of legitimate changes.

### 20. Evidence-based cleanup

- Remove only temporary artifacts created for the current task and proven no longer needed.
- Do not delete uncertain files, data, backups, libraries, fixtures, or concurrent artifacts merely because they look temporary.
- Cleanup never outranks preserving required project material.

### 21. Archive and legacy separation

- Clearly distinguish current governance from historical/superseded records.
- Archived material should not silently control current implementation.
- Preserve traceability from an old rule or document to its current replacement when the project benefits from it.

### 22. Licensing and attribution

- Preserve project licenses and third-party notices.
- Verify rights and attribution requirements before importing third-party code, media, data, templates, or documentation.
- Do not strip upstream license files from redistributed material.

### 23. Honest completion reporting

A completion report should state:

- what changed;
- what was actually verified;
- what was not verified;
- known limitations or risks;
- migrations/rollback considerations when relevant;
- directly affected documentation or records that were updated.

Never claim “complete”, “verified”, “bug-free”, or equivalent beyond the evidence available.

### 24. High-risk change gate

Require an explicit risk/rollback plan for changes that may cause:

- data loss;
- security/privacy impact;
- irreversible external side effects;
- schema or storage migration;
- authentication/authorization changes;
- broad breaking compatibility;
- production/release disruption.

## B. Conditional General Modules

Enable these only when the target project actually uses the condition.

### B1. Multilingual or paired governance documents

If a project maintains two or more language/format copies of the same governance document:

- keep them equivalent in information and intent;
- update all paired copies in the same task;
- do not let one silently become stale;
- literal sentence-by-sentence translation is not required unless the project says so.

### B2. Content families or synchronized variants

If one logical resource exists in several language, format, or derived variants:

- define which member is canonical;
- define allowed differences;
- update the full family when the project requires semantic equivalence;
- validate synchronization after edits.

### B3. Central shared systems

If a capability is consumed by multiple pages/modules/areas:

- give it one canonical owner;
- expose one stable shared interface;
- do not reimplement the same logic per consumer;
- define lifecycle, initialization, and cleanup responsibilities.

### B4. Frontend/accessibility/runtime performance

For user interfaces:

- validate relevant keyboard/focus behavior, accessibility, directionality, responsive behavior, and themes when affected;
- avoid mounting or initializing unrelated inactive UI;
- clean up owned listeners, observers, timers, subscriptions, transient state, and transient DOM;
- use lazy/on-demand loading when it materially improves the architecture without harming correctness.

### B5. Versioning and changelogs

If the project versions releases or distributable artifacts:

- define one authoritative version source per versioned artifact;
- do not silently change released contents without the required version update;
- maintain the project's change-history mechanism;
- keep generated package versions independent from project versions unless policy explicitly couples them.

### B6. Development-history records

If the project has structured notifications, change records, reports, ADRs, or problem logs:

- read the current instructions for that record family before writing;
- do not invent IDs, schemas, or required fields from memory;
- update the canonical index when required;
- preserve immutable historical entries if the project defines them as immutable.

### B7. Problem-to-rule learning loop

If the project maintains a problems/solutions knowledge base:

- record meaningful solved failures;
- capture root cause, not only symptom;
- extract a preventive rule;
- add a guard test or verification step where practical.

### B8. Integrity hashes and baselines

If file hashes or integrity baselines are used:

- treat a hash difference as evidence of change, not permission to overwrite;
- update baselines only through the documented authorized process;
- never fabricate a “known good” hash.

### B9. Imports and bulk data changes

For imports or high-volume transformations:

- isolate/parse first;
- preview or stage the result;
- validate;
- report row/item-level errors where practical;
- require confirmation for destructive or externally visible application;
- keep an audit trail when the project needs one.

### B10. Distribution, packaging, and mirrors

If a project publishes packages, mirrors, plugins, builds, or exports:

- edit the master source;
- regenerate/rebuild derived packages;
- keep package metadata internally consistent;
- verify the shipped copy matches the intended master state.

### B11. Mandatory full-rule pre-read

Some projects intentionally require every rule file to be read before every task. If that is an explicit project policy, it overrides the default minimum-inspection strategy for governance documents.

## C. Recommended Additional Safeguards

These are broadly useful additions even when they were not stated identically in every source project.

### C1. Idempotent automation

Recurring scripts and automation should be safe to rerun where practical and should avoid duplicating records or side effects.

### C2. Reproducibility

Important generated outputs should be reproducible from documented source inputs and tooling where practical.

### C3. Explicit external-action gate

Sending email, publishing, deploying, deleting remote data, charging money, changing permissions, or triggering other external side effects should require the authority level appropriate to the project and should never occur as an accidental consequence of analysis.

### C4. Recovery before destructive migration

Before a destructive migration, confirm a tested recovery path or backup strategy appropriate to the value and reversibility of the affected data.

### C5. Rule quality standard

Every permanent rule should be:

- clear about scope;
- testable or verifiable where practical;
- free of unnecessary implementation coupling;
- located in one authoritative place;
- explicit about exceptions;
- written so a future agent can act without guessing.
