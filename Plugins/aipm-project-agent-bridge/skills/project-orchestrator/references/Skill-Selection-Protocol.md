# Skill Selection Protocol

This reference defines how Project Orchestrator chooses Skills from a large library without creating context overload.

## Principle

Select by required capability, not by library size.

The Orchestrator should discover broadly from metadata but read deeply only for shortlisted Skills.

## Selection Pipeline

### 1. Capability Decomposition

Convert the task into capability statements, for example:

- project governance;
- state/handoff continuity;
- UI design;
- document generation;
- browser automation;
- database migration;
- testing;
- deployment.

Do not start with Skill names.

### 2. Metadata Scan

Use available lightweight sources such as:

- Skill registry;
- manifest;
- Skills index;
- plugin Skill list;
- installed-tool Skill descriptions.

Do not open every `SKILL.md`.

### 3. Candidate Shortlist

For each capability, shortlist Skills whose description/trigger clearly matches.

A candidate should have a reason such as:

- direct specialist fit;
- mandatory foundational responsibility;
- unique supporting capability;
- explicit owner request.

### 4. Deep Read

Read the authoritative `SKILL.md` only for shortlisted candidates.

Check:

- trigger conditions;
- scope;
- prerequisites;
- outputs;
- limitations;
- destructive/state-changing behavior;
- conflicts with project rules;
- overlap with other candidates.

### 5. Minimal Set Decision

Choose:

- mandatory FOUNDATION Skills;
- one LEAD per major workstream;
- SUPPORT Skills only for distinct missing capabilities.

Keep other plausible candidates as RESERVE rather than activating them.

### 6. Conflict Check

Look for:

- duplicated ownership;
- contradictory instructions;
- incompatible output formats;
- incompatible tool/environment requirements;
- one Skill modifying artifacts owned by another;
- different assumptions about source of truth.

Resolve before execution where possible.

### 7. Team Map

Record selected Skills against concrete workstreams.

Every active Skill must answer:

- What capability does it provide?
- What workstream owns it?
- What does it receive?
- What must it deliver?
- Who verifies it?
- When does its role end?

## Selection Heuristics

Prefer a Skill when it:

- directly matches the required outcome;
- has a narrower, better-defined specialist scope;
- provides a required workflow or validation discipline;
- is explicitly required by project governance or the owner.

Avoid selecting a Skill when it:

- only loosely matches by name;
- duplicates an already covered capability;
- adds large context without unique value;
- requires unavailable tooling;
- conflicts with the project's current architecture;
- is useful only for a future phase that has not started.

## Core Assistants

The Orchestrator treats these specially:

### project-governance-manager

FOUNDATION for interpreting project governance, authority, rules, and conflicts.

### shared-project-state-manager

FOUNDATION for continuity, phases, checkpoints, handoffs, and recovery on substantial work.

These two do not replace specialist Skills. They govern and preserve the work around them.

## Capability Gap Escalation

If no Skill matches:

1. verify the gap;
2. consider safe base-agent execution;
3. use `find-skills` when discovery is appropriate;
4. request authorization before installation when required;
5. use `skill-creator` only when the owner asks for or approves creation of a new permanent Skill.

## Anti-Overload Rule

A large library is not a reason to produce a large active team.

If five Skills can do the work but two are sufficient, use two.

If one specialist Skill covers a workstream completely, do not add extra Skills merely for reassurance.

## Re-Evaluation

Re-evaluate the roster only when:

- scope changes;
- a selected Skill proves incompatible;
- a new blocker appears;
- a new phase requires a capability not previously needed.

Do not repeatedly rescan the entire library after every small step.

## Automatic Skill Discovery and Selection

If the installed catalog has no suitable Skill, instruct the agent to search for the best relevant Skill in trusted available sources, including `find-skills` when available. Evaluate candidate Skills by capability fit, reliability, maintained status, provenance, license, security, permission scope, compatibility, and quality evidence. Inspect the selected Skill instructions and dependencies before use. Prefer the best verified candidate rather than the first search result. Obtain owner approval before installing third-party code, adding dependencies, granting access, or executing downloaded code. Never run untrusted code automatically. Preserve any explicitly owner-selected Skill unless the owner authorizes substitution. If no safe Skill is available, proceed with native capabilities only when results can be competently verified; otherwise explain the blocker. Apply measurable quality and accuracy gates to the result.
