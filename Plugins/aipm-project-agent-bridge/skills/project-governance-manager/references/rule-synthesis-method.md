# Rule Synthesis Method

Use this method when merging governance from several projects, files, conversations, or historical rule sets.

## 1. Build a source inventory

For each source, record:

- source name;
- authority level;
- current vs historical status;
- scope;
- whether it is project-wide or specialist;
- whether it is synchronized with another copy.

Do not assume two files have equal authority merely because both contain rules.

## 2. Extract rules atomically

Split compound paragraphs into atomic behavioral requirements.

A useful rule record contains:

| Field | Meaning |
|---|---|
| Rule | The behavioral requirement |
| Source | Where it came from |
| Scope | Project-wide / specialist / workflow / historical |
| Type | Universal / conditional / project-specific / technical standard |
| Authority | Relative precedence |
| Dependencies | Paths/systems/other rules required |
| Exceptions | Explicit allowed deviations |
| Verification | How compliance can be checked |

## 3. Normalize wording, not meaning

Different source phrases may represent one rule.

Example:

- “Do not inspect the whole repository by default.”
- “Read only directly relevant files first.”

Possible normalized rule:

> Use minimum sufficient inspection by default, except where the target project explicitly mandates a broader governance pre-read.

The normalized rule must preserve both constraints rather than delete one.

## 4. Universalization decision

A rule qualifies as universal only if its behavioral intent survives all of these substitutions:

- different project name;
- different folder tree;
- different programming language;
- different framework;
- different human language;
- different deployment model;
- different content domain.

If the rule fails because it names one source project's tool or folder, attempt to generalize the intent.

Example:

Project-specific:

> Use `PopupManagerSystem` for every popup.

Generalized conditional rule:

> When a project defines a canonical shared manager for a cross-cutting UI behavior, all consumers must use that manager instead of creating isolated competing implementations.

## 5. Conflict-resolution procedure

For every apparent conflict:

1. Compare scope.
2. Compare authority.
3. Compare recency.
4. Check whether both can coexist as conditional rules.
5. Parameterize a policy difference rather than declaring one universal.
6. If a material owner choice remains, stop at an Owner Approval Gate.

### Example: inspection breadth

One project may require reading every rules file before every task; another may forbid broad inspection by default.

Reusable synthesis:

- always read root governance and relevant specialist rules;
- default to minimum sufficient inspection;
- if the target project explicitly mandates a full rule pre-read, obey that project-specific gate.

### Example: file naming

One project may require ASCII-safe hyphenated names; another may require natural names with spaces.

Reusable synthesis:

- every project should define its human-facing naming policy;
- do not transfer another project's convention automatically;
- technical-standard names always retain required spelling.

## 6. Keep project-specific rules scoped

Do not put these into a universal baseline unless the target project actually needs them:

- exact folder names;
- exact build counters or ID prefixes;
- one framework's module name;
- a particular popup/modal implementation;
- article-specific variant rules;
- a project's exact supported languages;
- a plugin/package format unique to one repository;
- one project's naming convention;
- domain-specific data methodology.

Project-specific does not mean unimportant. It means the rule belongs in a specialist/project layer instead of the universal baseline.

## 7. Preserve technical standards

A technical convention may be universal as a **boundary**, even if the concrete name varies.

Reusable form:

> Names required by a platform, runtime, framework, import system, package manager, file format, or execution contract are exempt from cosmetic naming rules.

This avoids breaking projects while still allowing human-facing naming policies.

## 8. Distill recurring mistakes into rules

When a defect reveals a repeatable failure class:

1. record the root cause;
2. identify the general behavior that would have prevented it;
3. place that rule at the narrowest authority level that protects every affected consumer;
4. add a regression guard or verification step where practical.

Do not over-generalize a one-off symptom.

## 9. Validate the merged governance

A merge is incomplete until you can answer yes to all applicable questions:

- Is there one clear authority hierarchy?
- Did every source rule receive a disposition?
- Are duplicates consolidated without information loss?
- Are conflicts resolved or explicitly gated?
- Are project-specific rules kept out of the universal core?
- Are technical names protected?
- Are current paths real?
- Are synchronized copies still equivalent?
- Are archives clearly non-authoritative?
- Can a future agent follow the rules without guessing?

## 10. Recommended merge report

Keep a short synthesis record with:

- universal rules adopted;
- conditional rules adopted;
- project-specific rules retained elsewhere;
- historical rules excluded;
- conflicts and their resolution;
- new safeguards added by design rather than copied from a source;
- unresolved owner decisions.
