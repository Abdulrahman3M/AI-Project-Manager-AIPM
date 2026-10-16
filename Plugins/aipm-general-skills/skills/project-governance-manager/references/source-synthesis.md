# Source Synthesis Behind Project Governance Manager

This Skill was designed by comparing three governance styles:

1. a compact project-wide governance model emphasizing minimum sufficient inspection, preservation, documentation synchronization, honest reporting, portable paths, and scoped specialist authority;
2. a highly prescriptive project model emphasizing mandatory pre-reading, synchronized language copies, central-system ownership, real-execution verification, problem-to-rule learning, development-history discipline, and strong preservation;
3. the Universal AI ToolKit governance model emphasizing master-vs-generated source boundaries, minimal changes, technical naming preservation, version/changelog discipline, integrity-baseline safety, packaging boundaries, and validation.

The resulting Skill does not treat any one project as the universal template.

## Common themes promoted into the universal core

The following themes appeared repeatedly or were semantically equivalent across the source governance systems:

- latest explicit owner instruction and clear authority precedence;
- preserve existing behavior, knowledge, and data;
- do not expand scope without authority;
- read current governance rather than rely on memory;
- distinguish general rules from narrow specialist rules;
- use one canonical source of truth;
- avoid duplicated shared logic and competing authorities;
- inspect only what is needed unless a project explicitly mandates broader pre-reading;
- verify affected behavior honestly;
- runtime execution is stronger evidence than syntax/type checks for runtime claims;
- keep directly affected documentation synchronized;
- preserve portable paths and technical conventions;
- protect secrets and sensitive data;
- record changes/problems through the project's actual history mechanism;
- preserve archive/legacy traceability without letting history become current authority;
- clean temporary artifacts only with evidence that removal is safe;
- report what was and was not verified.

## Rules generalized from project-specific forms

### Naming

Source projects used incompatible naming schemes. Therefore the universal rule is **not** one casing style. The reusable rule is:

> Define and follow the target project's human-facing naming policy, while protecting all technical-standard and execution-critical names.

### Mandatory pre-read vs minimum inspection

One source requires a complete rules pre-read; another explicitly prefers minimum inspection.

Generalized rule:

> Always read root governance and directly relevant specialist rules. Default to minimum sufficient inspection unless the target project explicitly requires a broader governance pre-read.

### Central systems

Specific named systems (popup managers, modal managers, article diagram systems, etc.) are not universal.

Generalized rule:

> A shared cross-cutting capability should have one canonical owner and consumers should not create competing local implementations.

### Multilingual synchronization

Exact languages are project-specific.

Generalized rule:

> If the project declares two or more governance/content variants as synchronized equivalents, update the complete declared family in the same task.

### Versioning and development history

Exact IDs, build counters, notification formats, and record folder names are project-specific.

Generalized rule:

> Follow the target project's authoritative version/history mechanism, read its current record instructions before writing, and never invent identifiers or schemas from memory.

### Distribution and plugins

Exact plugin formats are repository-specific.

Generalized rule:

> Edit canonical masters and regenerate derived/distribution copies; never let a package copy become a competing source of truth.

## Intentionally not promoted as universal rules

Examples of source rules that remain project-specific unless a target project explicitly adopts them:

- exact project folder trees;
- exact Arabic/English/Russian language requirements;
- exact article Tashkeel/Base synchronization mechanics;
- exact dictionary/build-number rules;
- exact popup/modal system filenames;
- exact React/diagram implementation contracts;
- exact plugin manifest formats;
- exact numbered directory schemes;
- exact `ASCII-Safe Title-Case` policy;
- exact notification/change/report ID schemes;
- exact content import schemas.

## Additional safeguards introduced by this Skill

The Skill also recommends several cross-project safeguards that are useful even when not identically stated in every source:

- concurrency-safe final writes;
- idempotent recurring automation where practical;
- reproducible generation for important derived outputs;
- explicit gates for external side effects;
- tested recovery before destructive migrations;
- a rule-quality standard requiring scope, authority, exceptions, and a verification method.

These additions are design recommendations, not claims that every source file contained the exact wording.
