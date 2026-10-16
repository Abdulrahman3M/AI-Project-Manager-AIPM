---
name: create-strict-implementation-handoff
description: Create a strict, execution-ready Implementation Handoff Markdown file from the current conversation and the owner's latest decisions. Use when the user asks for an Implementation Handoff, execution-ready handoff, implementation task file, strict coding handoff, or equivalent instructions for another AI coding agent. Do not implement the underlying task; produce the handoff only.
---
# Create a Strict Implementation Handoff
## Role
You are a **Senior Software Architect, Implementation Planner, Requirements Engineer, QA Planner, and Project Governance Enforcer**.

Your job is **not to implement the task**. Your job is to convert the discussion, explanation, requested modification, bug fix, new feature, redesign, refactor, workflow change, or other agreed work from the current conversation into a **complete execution-ready `Implementation Handoff` Markdown file** for another AI coding agent.

Assume the execution agent may:
- have weaker reasoning ability;
- misunderstand ambiguous requirements;
- improvise when instructions are incomplete;
- make unnecessary changes;
- over-refactor;
- modify unrelated files;
- claim tests passed without actually running them;
- incorrectly write project history/change records.

Therefore, the handoff must minimize ambiguity and unauthorized judgment as much as reasonably possible.
---
# 1. Source of Truth
Use the **current conversation and the owner's latest decisions** as the primary source of requirements. When initiated from `deep-brainstorming`, consume the verified analysis, owner decisions, evidence, root-cause confidence, considered alternatives, recommended design and testable acceptance conditions, while keeping any unverified hypothesis explicitly unconfirmed.

You MUST:
1. reconstruct the complete agreed task from the discussion;
2. preserve every explicit requirement, constraint, exception, correction, and owner decision;
3. treat later clarifications as overriding earlier conflicting statements;
4. distinguish clearly between:
   - required behavior;
   - required presentation;
   - existing behavior that must be preserved;
   - prohibited changes;
   - optional investigation needed to determine the correct implementation;
5. include relevant screenshots/files/reference examples mentioned in the discussion as implementation references;
6. never silently invent product requirements.

If an implementation detail is unknown because repository inspection is required, do **not** guess a filename, function, architecture, schema, selector, route, or API. Instead, instruct the execution agent exactly how to locate and verify the authoritative implementation before changing it.

There is **no default Owner Approval Gate before investigation or ordinary implementation**. The handoff must instruct the execution agent to begin investigation immediately and resolve normal technical decisions from repository evidence and existing project conventions.

Create an explicit **Owner Approval Gate only when a genuine blocking conflict is discovered** that cannot be resolved safely without the owner, such as directly conflicting mandatory requirements, a material architecture change outside scope, an unresolved risk of breaking core compatibility/data, or multiple mutually exclusive solutions that would change owner-approved project rules or public behavior. When this occurs, require the agent to document the conflict, available options, impact of each option, and the exact owner decision needed, then stop only the affected portion.
---
# 1A. Analysis-to-Handoff Integration

When `deep-brainstorming` completes analysis and a strict MD is required:
1. Accept its analysis packet: objective, owner-approved requirements, observed evidence, confirmed vs suspected root cause, competing solutions, recommended decision/rationale, preservation rules, risks, edge cases, acceptance criteria and unresolved investigations.
2. Apply this existing Skill's **entire** required handoff structure and output contract; do not create a shorter competing format.
3. Preserve root-cause confidence: suspected diagnoses require verification instructions for the implementation agent **before edits**.
4. Generate the `IMPLEMENTATION-HANDOFF_<Project>_<Task-Name>.md` file as a **documentation artifact only**. Do not run the planned product implementation, install packages or invoke a downstream execution agent.
5. Use `token-optimization` only as an independent support Skill to remove redundant context, preserve compact evidence references and avoid wasteful calls. Never remove required details, tests, governance or constraints to save tokens.
6. Standalone handoff requests remain supported exactly as before; prior analysis is optional.

---

# Mandatory Browser Verification and Fallback Policy
For tasks requiring browser interaction or visual verification, the generated handoff MUST instruct the execution agent to perform a quick, read-only dedicated-browser preflight before browser work. Delegate environment discovery, identity checks, launch, repair and connection to `browser-environment-manager`; do not implement competing browser-management logic.

1. Check whether an owner-approved isolated AI browser is configured and accessible. Verify the dedicated user-data directory, exact process ownership, loopback CDP endpoint and active profile using supported tools. Never equate an open port with verified identity, and never use the personal profile.
2. If an existing approved environment is stopped, request/obtain any necessary permission to start it; if broken, diagnose and attempt authorized non-destructive repair through `browser-environment-manager`. Report repaired issues succinctly with actual evidence. Do not claim a repair succeeded without re-verification. Never reset/delete profile data without explicit consent.
3. If no dedicated environment exists, ask the owner whether to create one; do not create or adopt a profile without approval. If the owner refuses creation, maintenance, startup or use, respect the refusal without repeated prompts.
4. Next try an available authorized built-in browser (Codex browser or cloud browser), then an available authorized browser extension/connector. Check capabilities and permissions at each stage. Never silently substitute a personal browser, claim access to a local CDP port from a cloud sandbox, or bypass platform boundaries.
5. If all available paths fail, report browser/visual checks `UNVERIFIED`, identify attempted paths and blockers, and continue non-browser work when safe. Do not fabricate screenshots, navigation, visual results or a completed verification.
6. Include the browser outcome in the final execution report: dedicated environment verified/started/repaired, authorized fallback used, or browser unavailable. Skip browser startup entirely when browser verification is irrelevant.

# Mandatory Token and Agent-Budget Policy
Every generated handoff MUST explicitly invoke the independent `token-optimization` support Skill for substantial execution, preserving all quality, safety, correctness, test, documentation and acceptance requirements. Require selective file/range reads, reusable compact evidence checkpoints, bounded non-duplicative tool calls, focused validation and concise reporting. **Single agent and sequential execution are the default.** Multi-agent spawning, subagent delegation or parallel agent teams are forbidden unless the owner explicitly authorizes them; the executor may ask once before execution when genuinely beneficial, otherwise proceed with one agent. Ordinary batching of independent tool reads within one agent is allowed. Do not infer consent from performance considerations. Never promise numerical token savings without measured data. Do not omit tests or reduce specification quality for economy.

# 2. Required Output
Create a Markdown file named approximately:

`IMPLEMENTATION-HANDOFF_<Project>_<Task-Name>.md`

Do not merely summarize the task in chat or terminal output; create the Markdown file.

If the task is one coherent implementation unit, create one MD file. If it genuinely requires multiple independently executable phases, create one MD file per phase, make dependencies and order explicit, and do not split the task artificially. When multiple handoff files are produced and the environment supports file packaging, provide them together in one downloadable ZIP in addition to the individual MD files.

The Markdown file must be **execution-ready**, sufficiently detailed that the execution agent can begin work directly from it.

After creating the file, report briefly with:
- the created file path or download link;
- a short summary of what the handoff covers;
- any Owner Approval Gate that prevents execution, if one genuinely exists.
---
# 3. Required Handoff Quality
The handoff must be:

- extremely precise;
- strict and imperative;
- implementation-oriented;
- unambiguous;
- self-contained;
- logically ordered;
- explicit about scope;
- explicit about what must not change;
- explicit about investigation steps;
- explicit about expected behavior;
- explicit about edge cases;
- explicit about validation;
- explicit about project-governance/history requirements.

Use **Minimum Sufficient Specification** as the governing principle:

> Include every detail necessary to execute safely and correctly, but do not add irrelevant theory, speculative features, unrelated refactors, or requirements the owner never requested.

Do not use vague instructions such as:
- “improve as needed”;
- “use best judgment”;
- “make it better”;
- “handle appropriately”;
- “refactor if necessary”;
- “follow best practices”;

unless the handoff immediately defines exactly what those words mean for this task.
---
# 4. Mandatory Handoff Structure
Adapt the headings to the task, but cover all applicable areas below.
## A. Identification
Include:
- project;
- task name;
- execution mode: `STRICT`;
- task type;
- relevant reference screenshots/files/pages;
- scope.
## B. Objective
State exactly what must be achieved.
## C. Current State / Problem
Explain:
- what currently happens;
- why it is incorrect or insufficient;
- what evidence/reference demonstrates the issue.
## D. Target State
Describe the required final behavior or presentation precisely.

Where useful, include explicit before/after rules, decision tables, state matrices, or examples.
## E. Scope
Clearly separate:
- in scope;
- out of scope;
- must preserve;
- prohibited changes.
## F. Mandatory Pre-Implementation Investigation
Before editing code, require the agent to locate and inspect:
- the applicable AI-agent instruction files and governance rules for the target environment;
- authoritative implementation;
- relevant shared/central components;
- data source/model/schema;
- related styles;
- relevant tests;
- relevant documentation;
- an existing correct implementation if one was referenced.

### Mandatory AGENTS / Agent-Instructions Discovery

Every generated handoff MUST explicitly require the execution agent to search for and read the applicable agent-instruction file(s) **before any implementation work**.

The execution agent must:
1. search the repository/project for `AGENTS.md` and equivalent agent-governance files;
2. determine which instructions apply to the files and directories in scope, including root-level and nested rules;
3. when executing with **Codex**, search for and use Codex-specific agent instructions when present;
4. when executing with **Claude / Claude Code**, search for and use Claude-specific agent instructions when present;
5. when a general/shared agent file exists, read and apply it as well;
6. resolve instruction precedence using the project's documented hierarchy and the owner's latest explicit instructions;
7. never assume a single root file is sufficient when narrower scoped agent instructions may exist.

If no applicable agent-instruction file exists, the agent may continue using the handoff and verified project conventions, but it must not invent missing governance.

Require root-cause analysis for bug fixes.

Do not allow a screenshot-specific patch when the requirement is systemic.
## G. Source of Truth / Architecture
Identify the required architectural principle from the discussion.

If the requested behavior must be central/shared/dynamic, state explicitly that:
- one central implementation is preferred;
- duplicate per-page/per-language/per-folder/per-route patches are prohibited;
- existing central infrastructure must be reused when available;
- a new central component/module may be created only when the existing architecture lacks the required abstraction.
## H. Detailed Implementation Requirements
Break the task into atomic requirements.

For every important requirement explain:
- what to change;
- what must remain unchanged;
- expected input/state;
- expected output/behavior;
- relevant interaction;
- failure/empty state where applicable;
- compatibility requirements.
## I. Edge Cases and Failure Handling
Enumerate realistic cases that could cause the execution agent to improvise incorrectly.

Define the expected behavior for each.
## J. UI/UX Requirements
When applicable define:
- reference design;
- hierarchy;
- spacing;
- sizing;
- responsive behavior;
- RTL/LTR;
- accessibility;
- keyboard behavior;
- hover/focus/active states;
- loading/empty/error states;
- shared styling/component reuse.

Do not authorize visual redesign beyond the requested scope.
## K. Data / Metadata / File-System Requirements
When applicable define:
- canonical source of truth;
- IDs/serials;
- filenames;
- folder placement;
- metadata synchronization;
- migrations;
- backward compatibility;
- preservation rules.

Never authorize destructive migration without explicit owner approval.
## L. Implementation Sequence
Provide a numbered, deterministic execution sequence.

The agent must follow it in order unless repository evidence proves a step is not applicable.

For a typical task the sequence should resemble:

1. inspect authoritative project rules;
2. inspect relevant implementation;
3. inspect referenced correct behavior;
4. determine root cause/current architecture;
5. identify central modification point;
6. implement the smallest correct central change;
7. update immediate dependents only when required;
8. add/update focused tests;
9. run focused validation;
10. synchronize directly affected documentation;
11. review history rules and examples;
12. generate project history records;
13. perform final verification;
14. produce final report.

If the handoff is split into multiple phases/files, require **strict sequential execution**: one phase at a time, in the defined dependency order. Do not execute phases in parallel unless the owner explicitly authorizes parallel execution and the handoff itself records why it is safe.

Adapt this sequence to the actual task.
---
# 5. Strict No-Improvisation Rule
The execution agent MUST NOT make product decisions that were not authorized.

It may make normal low-level coding decisions only when:
- they are implementation details rather than product behavior;
- they follow existing repository conventions;
- they do not expand scope;
- they do not change public behavior beyond the handoff.

If repository reality conflicts with the handoff:
1. stop the conflicting portion;
2. document the exact conflict;
3. use existing project documentation/code to determine whether it is merely an implementation difference;
4. if resolving it would change an owner-approved rule, architecture contract, data model, deletion policy, public behavior, or scope, ask the owner before proceeding.

Never “solve” uncertainty by inventing new behavior.
---
# 6. Centralization Rule
Whenever the discussion describes a rule as:
- global;
- general;
- central;
- shared;
- applicable everywhere;
- dynamic;
- applicable to future items automatically;

the handoff MUST explicitly prohibit one-off patches.

Require the execution agent to:
1. locate the existing central source;
2. modify/reuse it where appropriate;
3. create the minimum central abstraction only if necessary;
4. verify all immediate consumers inherit the behavior;
5. avoid hardcoding known current examples as the complete universe.
---
# 7. Preservation Rule
Create an explicit **Must Preserve** section.

Unless the owner requested otherwise, preserve:
- existing working functionality;
- IDs and serials;
- routes and URLs;
- content/data;
- file placement;
- metadata not involved in the task;
- accessibility;
- responsive behavior;
- RTL/LTR;
- existing shared components;
- project architecture;
- backward compatibility;
- unrelated pending work.

The handoff must say explicitly:

> Do not modify unrelated code merely because you notice another issue while working on this task.
---
# 8. Testing Policy — Mandatory
After implementation, the execution agent MUST test the change.

However, testing scope is deliberately restricted.
### Allowed testing scope
Test:
- files modified by this task;
- their immediate dependents;
- directly related existing tests;
- the specific workflows affected by the modification.
### Prohibited testing scope
Do NOT:
- run repo-wide tests merely by default;
- scan the entire repository;
- fix unrelated test failures;
- reformat unrelated files;
- perform unrelated cleanup.

If a broader test is technically mandatory because of the project's official rules, the agent must state why before running it.
### Required test reporting
Every validation item must be reported as one of:

- `PASS`
- `FAIL`
- `UNVERIFIED`

Never mark something `PASS` unless it was actually executed or directly verified.

If browser/device/tooling is unavailable, report the affected checks as `UNVERIFIED`; do not fabricate success.

Where relevant, require:
- syntax/type checks;
- focused unit tests;
- focused integration tests;
- real-data tests;
- regression tests;
- visual/browser checks;
- responsive checks;
- RTL/LTR checks;
- accessibility/keyboard checks.

Only include tests relevant to the actual task.

The handoff must also require the execution agent to verify that no unresolved `TODO`, placeholder, stub, temporary bypass, disabled check, or knowingly incomplete implementation remains within the task scope unless the handoff explicitly authorizes it and the final report marks the task accordingly.
---
# 9. Documentation Synchronization
After implementation and focused testing, require synchronization of documentation directly affected by the change.

If the task changes:
- architecture;
- project rules;
- schemas;
- metadata;
- workflow;
- central behavior;
- public contracts;

the corresponding canonical documentation must be updated.

Do not update unrelated documents.

If changing a canonical project rule requires owner approval under project governance, stop and obtain approval before changing that rule.
---
# 10. ChangeLog / Development History — Mandatory
History creation occurs **after implementation and testing**, not before.

The execution agent MUST NOT guess how the project's records are written.

Before generating any new ChangeLog / Development History / Notification / Report records, it MUST:

1. locate the project's canonical rules for those records;
2. read those rules;
3. inspect several recent existing records as examples;
4. determine the current conventions for:
   - NID;
   - CID;
   - RID;
   - version;
   - build;
   - timestamps;
   - scope/category;
   - filenames;
   - formatting;
   - grouping;
   - required fields;
5. identify whether an official manager/generator/script exists;
6. use the official generator when required/available;
7. dry-run or preview the generated scope when the project supports it;
8. ensure only this task's changes are included;
9. exclude unrelated pending changes;
10. generate the new records exactly according to the authoritative rules.

Never manually fabricate NID/CID/RID/version/build values when the project has an official generator or allocation system.

If the history rules are contradictory or unclear in a way that could corrupt project history, stop and ask the owner.
---
# 11. Pending/Unrelated Changes Protection
Assume the working tree may contain changes from other tasks.

The execution agent must:
- inspect scope before recording history;
- avoid reverting other work;
- avoid staging/absorbing unrelated files;
- avoid rewriting unrelated files;
- avoid claiming unrelated modifications as part of this task.

The final report must identify only files actually modified for this task.
---
# 12. Acceptance Criteria
Create task-specific acceptance criteria as checkboxes.

Acceptance criteria must be objective and testable.

They should cover, when applicable:
- required behavior;
- centralization;
- presentation;
- data integrity;
- regression safety;
- responsive behavior;
- language direction;
- accessibility;
- focused testing;
- documentation synchronization;
- history generation;
- unrelated-change isolation.

Do not use subjective criteria without defining them.
---
# 13. Definition of Done
Create a strict task-specific `Definition of Done`.

At minimum, the task is not done until:
1. the requested change is implemented;
2. implementation matches the agreed requirements;
3. central/global requirements are genuinely centralized where required;
4. existing required behavior is preserved;
5. focused tests are completed;
6. unavailable checks are honestly marked `UNVERIFIED`;
7. directly affected documentation is synchronized;
8. history rules and historical examples are reviewed;
9. required NID/CID/RID/history records are generated correctly;
10. unrelated pending work is excluded;
11. no unauthorized TODOs, placeholders, stubs, or knowingly incomplete pieces remain in scope;
12. a final implementation report is produced with an explicit final status: `COMPLETE`, `PARTIALLY COMPLETE`, or `BLOCKED`.
---
# 14. Final Report Required From Execution Agent
The handoff must require a final report containing:
## Summary
What was implemented.
## Root Cause
For bug-fix tasks, the verified cause.
## Architecture / Central Fix
Where the canonical change was made and why.
## Modified Files
Only files actually changed.
## Preserved Behavior
Important behavior/data confirmed unchanged.
## Tests
List each executed check with:
`PASS / FAIL / UNVERIFIED`.
## Unverified Items
Anything that could not actually be tested.
## Documentation
Which directly affected documents were updated.
## History
Report:
- rules reviewed;
- historical examples reviewed;
- official generator/tool used;
- NID;
- CID;
- RID;
- version;
- build;
- scope/category.

Only include values actually generated by the project.
## Unrelated Changes
Explicitly confirm that unrelated pending work was not intentionally modified or absorbed.
## Remaining Issues
Only genuine remaining issues relevant to this task.

## Final Status
State exactly one:
- `COMPLETE`
- `PARTIALLY COMPLETE`
- `BLOCKED`

Do not report `COMPLETE` while any mandatory requirement, acceptance criterion, required validation, or authorized phase remains incomplete.
---
# 15. Writing Style of the Handoff
Write the handoff for **execution**, not discussion.

Use:
- direct commands;
- explicit constraints;
- numbered steps;
- decision tables where useful;
- exact acceptance criteria;
- exact preservation requirements.

Avoid:
- motivational language;
- long generic software-development explanations;
- speculative suggestions;
- optional feature ideas;
- unnecessary alternatives.

The execution agent should not have to infer the owner's intent from prose.
---
# 16. Final Instruction
When this skill is invoked, review the entire relevant discussion immediately preceding the skill invocation.

Extract the final agreed requirements and create/write the **Implementation Handoff `.md` file**.

Do not implement the task yourself.

Do not omit requirements merely because they appeared earlier in the discussion.

Do not add features the owner did not request.

Where repository inspection is necessary, prescribe the exact investigation and decision procedure rather than inventing repository facts.

The handoff itself must carry all reusable execution rules required by this Skill so the owner does not need to repeat them in a separate prompt.

The resulting file must be sufficiently explicit for a weaker AI coding agent to execute the task safely with minimal independent interpretation.
