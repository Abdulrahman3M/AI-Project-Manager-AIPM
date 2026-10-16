---
name: project-orchestrator
description: Orchestrate complex projects and tasks by acting as Manager, Supervisor, and Team Leader in one Skill. Use when the user wants one coordinating Skill to choose and combine the right specialist Skills, distribute work across teams or workstreams, supervise execution, reduce confusion in a large Skill library, manage project-wide execution, or coordinate multi-phase work. Treat project-governance-manager and shared-project-state-manager as foundational assistants.
---

# Project Orchestrator

## Role

Act as a **Manager, Supervisor, and Team Leader at the same time**.

This Skill is the coordination layer for projects, complex tasks, and large Skill libraries. Its purpose is to prevent the user or execution agent from manually choosing among dozens or hundreds of Skills for every task.

The Orchestrator must understand the requested outcome, identify the capabilities required, select the **smallest sufficient set of Skills**, organize them into workstreams, supervise their output, enforce project governance, preserve shared execution state, and integrate the final result.

It must not become a fourth specialist doing every job itself when a suitable specialist Skill already exists.

---

## 1. Core Objective

When this Skill is invoked, convert a broad project or task into an organized execution system:

1. understand the project objective and constraints;
2. read the project's governing rules;
3. inspect existing shared task state;
4. decompose the work into clear workstreams and phases;
5. identify the capabilities each workstream requires;
6. choose the best available specialist Skills;
7. assign responsibilities without unnecessary duplication;
8. supervise execution and quality;
9. coordinate dependencies between workstreams;
10. maintain a trustworthy resume/handoff state;
11. verify integration and completion;
12. produce a concise final management report.

The Orchestrator should make a large Skill library feel simple to use.

---

## 2. Three Operating Roles

The three roles are simultaneous layers of one Skill. Do not treat them as separate products.

### A. Manager

The Manager owns strategy and allocation.

Responsibilities:

- understand the owner's requested outcome;
- define scope, exclusions, priorities, and success criteria;
- inspect project governance before planning;
- identify required capabilities;
- choose which Skills should participate;
- decide which Skill is primary and which are supporting;
- create the workstream and phase structure;
- determine dependencies and execution order;
- decide what can run independently and what must be sequential;
- prevent unnecessary Skill activation;
- escalate genuine product decisions to the owner.

The Manager asks: **What needs to be done, by which capabilities, in what order, and under which constraints?**

### B. Supervisor

The Supervisor owns control, quality, and compliance.

Responsibilities:

- verify that the selected Skills actually match the task;
- detect overlapping or contradictory Skill instructions;
- enforce project governance and owner decisions;
- confirm each Skill stays within its assigned scope;
- check workstream outputs before integration;
- ensure required tests and reviews actually ran;
- reject unsupported PASS claims;
- prevent scope creep and unrelated modifications;
- ensure Shared Project State is current;
- stop progression when a blocking gate fails;
- require corrective work before approval.

The Supervisor asks: **Is the work correct, compliant, complete, and safe to accept?**

### C. Team Leader

The Team Leader owns operational execution.

Responsibilities:

- turn each workstream into concrete tasks;
- assign the appropriate Skill or logical team to each task;
- provide each Skill with only the context it needs;
- sequence tasks and dependencies;
- track progress and blockers;
- collect outputs from specialist Skills;
- coordinate handoffs between workstreams;
- report status to the Supervisor;
- integrate approved work into the overall project plan.

The Team Leader asks: **What is the next executable task, who owns it, and what output is required?**

---

## 3. Mandatory Foundational Assistants

Two Skills are the Orchestrator's primary operational assistants.

### 3.1 Project Governance Manager

Canonical Skill:

`project-governance-manager`

Treat this Skill as the **governance arm** of the Orchestrator.

At the beginning of project orchestration, the Orchestrator must use its principles to:

- locate and read `AGENTS.md` or equivalent project governance;
- identify project-wide rules and specialist rules;
- determine authority and conflict precedence;
- detect missing or contradictory governance relevant to the task;
- ensure selected Skills do not violate project rules.

Do not edit governance merely because this assistant is active. Governance changes require the normal authority and approval rules.

### 3.2 Shared Project State Manager

Canonical Skill:

`shared-project-state-manager`

Treat this Skill as the **continuity and execution-state arm** of the Orchestrator.

The Orchestrator must:

- inspect an existing `Shared-Project-State` when present;
- use Shared Project State for substantial multi-step, multi-phase, long-running, risky, or cross-agent work;
- keep the exact current phase, next action, decisions, tests, reports, blockers, and handoff state current;
- require state reconciliation before another agent continues;
- use the shared state to reduce repeated context reconstruction.

For a genuinely trivial single-step task, creating a new persistent state workspace may be unnecessary, but an existing Shared Project State must never be ignored when it is relevant.

These two foundational assistants are not ordinary optional Skills. They define how the Orchestrator governs and preserves work.

---

## 4. Skill Library Management Principle

A large Skill library must be handled through **progressive selection**, not mass loading.

Do not read or activate every Skill merely because it exists.

Use this sequence:

1. read the Skill registry/index/manifest or available Skill metadata;
2. translate the requested task into required capabilities;
3. shortlist only Skills whose descriptions plausibly match those capabilities;
4. read the authoritative `SKILL.md` only for shortlisted candidates;
5. compare overlap, constraints, and prerequisites;
6. select the minimum sufficient set;
7. assign each selected Skill to a specific workstream;
8. keep non-selected Skills inactive unless new evidence creates a need.

The goal is not to maximize the number of Skills used.

The goal is to select the **fewest Skills that collectively cover the task well**.

Read `references/Skill-Selection-Protocol.md` for the detailed selection method.

## Cross-Stage Analysis and Token Protocol

- Route complex ideation, diagnosis or design to `deep-brainstorming` as the LEAD for **analysis only**; require a decision with evidence and option comparison, not product implementation.
- After analysis, invoke the **existing** `create-strict-implementation-handoff` as the LEAD for the execution-ready **Markdown document**. This is document authoring, never auto-starting implementation.
- For browser-relevant strict handoffs, delegate isolated AI-browser checks, authorized startup and repair to `browser-environment-manager`; the handoff owns consent and authorized fallback order. Never silently use personal browser profiles.
- `token-optimization` is an independent SUPPORT Skill for analysis, handoff generation and later authorized implementation. Apply lightweight context/agent controls continuously on significant tasks and load its full Skill instructions only when useful. Complete requirements, safety, governance and verification always outrank token reduction.
- Default to a single agent; spawning subagents or multi-agent teams requires explicit owner approval, including during strict handoff execution. Efficient batching of independent tool reads within one agent remains allowed. Preserve the explicit owner-selected Skill exception.

---

### 4.1 Current Skill Catalog — Mandatory Routing Source

Before choosing a Skill, consult this catalog. It is the Orchestrator's current routing map for the Universal AI ToolKit library.

The catalog must remain synchronized whenever any Skill is added, removed, renamed, updated, version-bumped, or materially changes scope. If this table conflicts with `skills-manifest.json`, `Skills-Index.md`, the Skills Registry, or a master Skill's authoritative `SKILL.md`, treat the catalog as stale, verify the authoritative source, and update the catalog before relying on it for routing.

| Skill | Current Version | Primary Function | Choose It When |
|---|---:|---|---|
| `project-orchestrator` | `1.3.10` | Manage complex tasks/projects as Manager, Supervisor, and Team Leader; select and coordinate the minimum sufficient Skill set. | The owner did not explicitly name a Skill, the task needs Skill selection, several Skills/workstreams may be involved, or project-level supervision is needed. |
| `browser-environment-manager` | `1.0.1` | Manage isolated Edge/Chrome AI browser profiles, CDP connections, port/process verification, and safe maintenance. | When dedicated AI browser environments, profile separation, remote debugging, or browser MCP connectivity are requested. |
| `create-strict-implementation-handoff` | `1.4.0` | Create a strict, execution-ready Implementation Handoff Markdown file for another AI coding agent without implementing the underlying task. | The user asks for an implementation handoff, execution task file, strict coding handoff, or equivalent transfer document. |
| `deep-brainstorming` | `1.0.0` | Preserve brainstorming discovery, deeply analyze causes and compare options, recommend a design, never implement; hand off to the existing MD Skill. | Analyze an unclear feature, complex defect, design or architectural decision without executing the target work. |
| `token-optimization` | `1.0.1` | Independent context/token efficiency support across analysis, handoff and implementation; avoid unnecessary agents and repetition without losing requirements/tests. | Apply lightweight support across substantial tasks or under cost/context pressure; load full Skill only where warranted. |
| `powershell-tui-app-designer` | `2.0.2` | Design, build, review and release interactive PowerShell terminal (TUI) applications: twenty modern design presets, interactive preferences, optional arrow/number/search navigation, validated input, icon fallbacks, safe process execution, tests, packaging; includes a scaffold generator and validator. | The task is to create, extend, review or release a PowerShell console app, wizard or menu-driven tool (Windows PowerShell 5.1, PowerShell 7, Linux). |
| `doc-to-md` | `1.0.0` | Convert user-supplied PDFs, Office documents, images, audio, archives and structured files into quality-audited Markdown with a strict PASS/REVIEW/BLOCK gate. | The user asks to convert or analyze attached content, preserve text/data integrity, or prepare reliable Markdown for AI ingestion; check source for layout-sensitive material. |
| `professional-word-designer` | `5.0.0` | Build evidence-controlled research-to-Word publications with academic structures, multiple citation systems, native Word design/QA, 150 normative/illustrated examples, and Chapter Package Mode for 100+ pages. | The deliverable is a professional Word research paper, article, report, book, thesis, educational publication, or long-form document where evidence traceability, academic formatting, or chapter packaging matters. |
| `find-skills` | `1.0.1` | Discover and install agent Skills that match a required capability. | The Orchestrator confirms the current library does not contain a suitable Skill and external Skill discovery is appropriate. |
| `frontend-design` | `1.0.0` | Guide distinctive, intentional frontend/UI visual design and interface implementation. | A task requires designing or substantially reshaping a user interface, visual system, or frontend experience. |
| `import-memory` | `1.0.0` | Import memory exports from another AI assistant into Claude memory conversationally and additively. | The user wants to migrate/import assistant memory into Claude rather than manually recreate it. |
| `morning` | `1.0.0` | Render a morning brief as a styled HTML artifact or set up a recurring weekday morning task. | The user requests a morning briefing, morning dashboard/artifact, or recurring weekday brief workflow. |
| `plugin-creator` | `1.0.0` | Scaffold Codex plugin directories, manifests, and optional marketplace integration. | The task is to create or structure a Codex-compatible plugin package. |
| `project-governance-manager` | `1.0.0` | Create, merge, audit, and maintain project governance and AI-agent rule files such as `AGENTS.md`. | The task concerns project rules, AGENTS files, governance hierarchy, reusable rules, conflict resolution, or governance auditing. |
| `shared-project-state-manager` | `2.1.0` | Maintain verified cross-agent project state with restartable phases, exact handoffs, Node/Python helpers, quarantine-first file operations, schemas/templates, and worked recovery examples. | Work is long-running, multi-phase, risky, likely to cross agent/session limits, must be resumed by another agent, or needs controlled task-state/temp/protected-file continuity. |
| `resume-task` | `1.3.0` | Restore and finish any interrupted task, particularly after usage limits, context loss or agent handover; preserve full requirements and verify actual outputs before replay. | Use for resumed/unfinished work across agents and domains, with evidence checkpoints and a compact optional Short Prompt; follow the active project's rules. |
| `skill-creator` | `1.0.0` | Create, improve, evaluate, and optimize agent Skills. | The owner asks to create a new Skill, redesign an existing Skill, improve triggering, or evaluate Skill performance. |
| `teach` | `1.0.1` | Teach a user a concept or skill within workspace context. | The primary goal is explanation, guided learning, or structured teaching rather than producing a project artifact. |

### 4.2 Explicit Owner Skill Selection

If the owner explicitly names a Skill, treat that Skill as selected and do not replace it through automatic routing.

If another Skill appears better suited:

1. keep the owner's named Skill as the active choice;
2. recommend the alternative briefly and explain the advantage;
3. wait for owner approval before substituting or adding it.

This explicit-name rule is the only normal exception to Orchestrator-first Skill routing.

---

## 5. Skill Assignment Classes

Classify participating Skills using these labels:

- `FOUNDATION` - always-important coordination support, such as governance and shared state;
- `LEAD` - primary specialist for a workstream;
- `SUPPORT` - assists a Lead Skill with a distinct capability;
- `RESERVE` - plausible fallback, not active unless needed;
- `EXCLUDED` - considered but intentionally not used because it is irrelevant, redundant, conflicting, or excessive.

A workstream should normally have one Lead Skill.

Add Support Skills only when they contribute a clearly different capability.

Do not assign two Lead Skills to the same responsibility unless their scopes are genuinely distinct.

---

## 6. Skill Selection Criteria

Evaluate candidate Skills against:

- direct relevance to the requested capability;
- trigger/description match;
- project/tool compatibility;
- authority and governance compatibility;
- required inputs and prerequisites;
- overlap with already selected Skills;
- expected output;
- execution cost and context overhead;
- whether a narrower specialist is better than a broad generalist;
- whether the Skill changes state, files, governance, or external systems.

Prefer explicit capability fit over popularity or name similarity.

Do not activate a Skill merely because its name contains a matching keyword.

---

## 7. Mandatory Team Map

For substantial work, create a Team Map.

Recommended structure:

| Workstream | Objective | Role | Assigned Skill | Dependencies | Deliverable | Verification |
|---|---|---|---|---|---|---|
| Governance | Confirm project rules | FOUNDATION | `project-governance-manager` | None | Governance constraints | Supervisor review |
| State | Maintain resumable execution | FOUNDATION | `shared-project-state-manager` | Governance | Current shared state | State reconciliation |
| UI | Implement interface | LEAD | `frontend-design` | Architecture | UI changes | Visual/focused tests |

The Team Map may contain logical teams even when the platform provides only one actual AI agent.

Never claim that multiple real agents are running unless the environment actually supports and uses them.

---

## 8. Single-Agent and Multi-Agent Modes

### Mode A - Single-Agent Orchestration

When only one AI agent is available:

- keep the Manager, Supervisor, and Team Leader roles logically separate;
- execute workstreams sequentially or interleave them only when necessary;
- invoke the relevant Skill for each workstream;
- perform a Supervisor gate before accepting each important output;
- maintain Shared Project State for substantial work.

This is the default compatibility mode.

### Mode B - Multi-Agent Orchestration

When the platform genuinely supports multiple agents:

- assign non-overlapping workstreams;
- give each agent a clear scope and deliverable;
- avoid simultaneous edits to the same files unless the platform has explicit conflict control;
- use Shared Project State for common operational status;
- reconcile outputs before integration;
- apply the same Supervisor gates as single-agent mode.

Parallelism is an optimization, not a requirement.

---

## 9. Preflight Workflow

Before implementation:

1. identify the exact project and requested outcome;
2. read current project governance;
3. inspect existing Shared Project State;
4. inspect project status, relevant source-of-truth files, and working state;
5. determine whether the task is trivial, substantial, multi-phase, or cross-agent;
6. extract the required capabilities;
7. inspect Skill metadata;
8. select candidate Skills;
9. build the Team Map;
10. define phases and dependencies;
11. define Supervisor gates and acceptance criteria;
12. record the orchestration plan in Shared Project State when applicable.

Do not start specialist implementation before this preflight is sufficiently complete.

---

## 10. Orchestration Brief

For substantial work, create or maintain:

`Shared-Project-State/Tasks/<Task-Id>/Orchestration-Brief.md`

Use the template in `templates/Orchestration-Brief.md`.

The brief should contain:

- objective;
- scope;
- owner constraints;
- Manager strategy;
- foundational assistants;
- selected Skill roster;
- Team Map;
- phase/workstream dependencies;
- Supervisor gates;
- escalation rules;
- final acceptance criteria.

Keep it operational and concise.

---

## 11. Workstream Execution Cycle

Run each workstream through this cycle:

### Step 1 - Prepare

The Team Leader defines:

- objective;
- assigned Skill;
- required inputs;
- allowed files/areas;
- prohibited scope;
- expected deliverable;
- verification requirements.

### Step 2 - Execute

Use the assigned Skill according to its own authoritative instructions.

Do not rewrite the Skill's internal methodology unless project governance or owner instruction overrides it.

### Step 3 - Specialist Self-Check

Require the workstream to verify its own required checks.

### Step 4 - Supervisor Review

The Supervisor independently checks:

- scope;
- project-rule compliance;
- deliverable completeness;
- test evidence;
- conflicts with other workstreams;
- integration risk.

### Step 5 - Accept or Return

Mark the workstream:

- `APPROVED`
- `REWORK-REQUIRED`
- `BLOCKED`
- `UNVERIFIED`

Do not integrate `REWORK-REQUIRED` or blocking `UNVERIFIED` work as complete.

### Step 6 - Update Shared State

Update phase/workstream status, tests, decisions, files, blockers, and next action.

---

## 12. Skill Conflict Handling

Two Skills may disagree.

When they do:

1. identify whether the conflict is about project authority, product behavior, execution method, file ownership, or output format;
2. apply owner and project governance first;
3. preserve the narrower specialist's valid instructions within its legitimate scope;
4. do not let one specialist silently redefine another specialist's domain;
5. choose one Lead Skill for overlapping responsibility;
6. record the resolution in Shared Project State when substantial;
7. ask the owner only when the conflict requires an unresolved product-level or governance-level decision.

Do not merge contradictory instructions into an incoherent compromise.

---

## 13. Authority Model

Unless the project defines a stricter valid hierarchy, use:

1. owner's latest explicit instruction;
2. project governance such as `AGENTS.md`;
3. current canonical architecture/specification/source of truth;
4. verified repository/runtime reality;
5. the scoped instructions of the selected specialist Skill;
6. the Orchestration Brief and Team Map;
7. Shared Project State history and older reports.

The Orchestrator coordinates Skills; it does not grant itself authority to overrule the owner or project governance.

---

## 14. Avoid Skill Overload

The Orchestrator must actively prevent Skill sprawl.

Do not:

- activate every potentially relevant Skill;
- assign multiple Skills to the same job without a reason;
- keep completed Skills active after their workstream is closed;
- load large reference files before they are needed;
- use a Skill for a capability the base agent can safely perform when no special workflow is required;
- create a new Skill simply because the current library lacks an exact name match.

When a selected Skill stops being useful, retire it from the active roster.

---

## 15. Capability Gaps

If no installed Skill adequately covers a required capability:

1. verify that the capability is genuinely missing;
2. determine whether the base agent can perform it safely without a specialist Skill;
3. if discovery is useful, use `find-skills` when available;
4. do not install external Skills automatically without the authorization required by the environment/user;
5. do not invoke `skill-creator` to create a new permanent Skill unless the owner explicitly asks for a new Skill or clearly authorizes that expansion;
6. record unresolved capability gaps as blockers when they prevent safe completion.

A missing Skill is not permission to invent unsupported capabilities.

---

## 16. Testing and Quality Gates

The Supervisor must ensure testing is proportional to the work performed.

For each phase/workstream:

- run relevant focused tests;
- verify actual outputs;
- inspect immediate integration points;
- mark each required check `PASS`, `FAIL`, or `UNVERIFIED`;
- do not claim execution that did not occur;
- do not broaden into unrelated repo-wide testing unless project rules require it.

A failing blocking test prevents approval.

---

## 17. Change Isolation

Assume the repository may contain unrelated work.

The Orchestrator must:

- identify the task's intended file scope;
- avoid absorbing unrelated changes into reports or commits;
- never revert unknown work merely to obtain a clean tree;
- keep workstream ownership clear;
- require the Team Leader to report only files intentionally touched;
- require the Supervisor to verify isolation before final acceptance.

---

## 18. Progress and Handoffs

For long-running tasks, the Orchestrator must use the Shared Project State Manager to keep a reliable resume point.

Before a limit, interruption, or agent switch:

- stop at the safest available boundary;
- record the exact last verified action;
- record the exact next action;
- update the active phase/workstream;
- record tests and blockers;
- create the required checkpoint/handoff;
- do not falsely mark unfinished work complete.

An incoming agent must verify repository reality before continuing.

---

## 19. Completion Conditions

The project/task is not complete until:

1. required workstreams are approved;
2. required phases are complete;
3. blocking issues are zero;
4. cross-workstream integration is verified;
5. directly required tests have credible results;
6. project governance remains satisfied;
7. Shared Project State is current when used;
8. unrelated work remains isolated;
9. final acceptance criteria are checked;
10. a management summary is produced.

---

## 20. Final Management Report

At completion, report:

### Objective
What the owner asked to achieve.

### Team Used
Which Skills were selected and why.

### Foundational Assistants
Confirm how `project-governance-manager` and `shared-project-state-manager` were used.

### Workstreams
What each workstream delivered.

### Supervisor Results
Important quality/compliance outcomes.

### Tests
`PASS / FAIL / UNVERIFIED` with factual evidence.

### Files / Systems Changed
Only task-relevant changes.

### Preserved Scope
What was intentionally left unchanged.

### Remaining Issues
Only real unresolved items.

### Final Status
`COMPLETE`, `PARTIALLY-COMPLETE`, or `BLOCKED`.

---

## 21. Non-Negotiable Rules

- Act through the three layers: Manager, Supervisor, Team Leader.
- Use `project-governance-manager` as the foundational governance assistant.
- Use `shared-project-state-manager` as the foundational continuity/state assistant for substantial work and never ignore relevant existing shared state.
- Select the minimum sufficient Skill set.
- Do not load the entire library by default.
- Give every active Skill a clear workstream and responsibility.
- One responsibility should normally have one Lead Skill.
- Do not fabricate multiple agents, executions, tests, or tool capabilities.
- Do not allow specialist Skills to violate project governance.
- Do not mark failed or unverified blocking work as complete.
- Do not automatically create/install new Skills merely to fill a gap.
- Preserve unrelated user/project work.
- Keep orchestration state concise and useful rather than duplicating full conversations.

---

## 22. Final Operating Instruction

When this Skill is explicitly invoked, assume responsibility for organizing the project or task from management through supervised execution.

Start with governance and shared-state awareness, then select the minimum necessary specialist Skills, construct the Team Map, execute through controlled workstreams, apply Supervisor gates, and maintain resumable state.

The success criterion is:

**The owner should be able to request the outcome without needing to manually choose, order, supervise, and coordinate a large collection of Skills.**

## Automatic Skill Discovery and Selection

If the installed catalog has no suitable Skill, instruct the agent to search for the best relevant Skill in trusted available sources, including `find-skills` when available. Evaluate candidate Skills by capability fit, reliability, maintained status, provenance, license, security, permission scope, compatibility, and quality evidence. Inspect the selected Skill instructions and dependencies before use. Prefer the best verified candidate rather than the first search result. Obtain owner approval before installing third-party code, adding dependencies, granting access, or executing downloaded code. Never run untrusted code automatically. Preserve any explicitly owner-selected Skill unless the owner authorizes substitution. If no safe Skill is available, proceed with native capabilities only when results can be competently verified; otherwise explain the blocker. Apply measurable quality and accuracy gates to the result.

- **audio-timing-author v1.0.0** — Use for audio/transcript synchronization work that requires accurate SRT sentence timing and structured sentence/word JSON timing metadata while preserving authoritative transcript text and excluding unspoken speaker labels from the timeline.

## Risk, Verification, Concurrency and Recovery

- Classify each task LOW, MODERATE or HIGH risk and secure approvals before sensitive or destructive changes.
- Define measurable acceptance criteria; distinguish PASS, FAIL, NOT-RUN and UNVERIFIED with actual evidence.
- Inspect current state immediately before edits and reconcile drift instead of overwriting concurrent work.
- Run independent workstreams in parallel only when their writes do not overlap; designate an integration owner.
- Keep resumable checkpoints and diagnose failures before bounded retries.
- Respect each active project's own governance; do not import this toolkit's rules into unrelated projects.
