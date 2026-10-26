---
name: project-orchestrator
description: Select and coordinate specialist Skills when the user asks for help choosing a Skill, the request spans multiple capabilities or workstreams, or project-level supervision is needed. Analyze the requested outcome and deliverable before routing; send execution instructions or handoff documents for another AI agent to create-strict-implementation-handoff. For a clear single-specialist deliverable, invoke that specialist directly without adding orchestration overhead. Use project-governance-manager and shared-project-state-manager as foundational assistants when applicable to substantial work.
---

# Project Orchestrator

## Role

Act as a **Manager, Supervisor, and Team Leader at the same time**.

This Skill coordinates multi-capability work and helps select Skills when requested or genuinely needed. For an unambiguous single deliverable, route directly to the narrow specialist rather than making orchestration a mandatory extra step.

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

## 3. Foundational Assistants

Two Skills provide foundational support for substantial orchestration where relevant.

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

For a narrow, single-step specialist request, do not activate these assistants unless project rules, existing state, or risk level make them relevant.

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

- Route analysis to a specialist only when an active catalog entry explicitly covers the analysis deliverable; do not refer to removed or unavailable Skills as installed.
- If an analysis is followed by a requested execution-ready handoff, use `create-strict-implementation-handoff` to author it. Writing a handoff does not authorize starting the implementation.
- For browser-related work, use `browser-environment-manager` only when isolated browser environment setup or repair is actually in scope.
- `token-optimization` is optional SUPPORT on substantial work; requirements, safety, governance and verification outrank token reduction.
- Default to a single agent; spawning subagents or multi-agent teams requires explicit owner approval. Efficient batching of independent reads within one agent is allowed.

---

### 4.1 Current Skill Catalog — Mandatory Routing Source

Before choosing a Skill, consult this catalog. It is the Orchestrator's routing summary for the active AIPM Capability Library.

The catalog must remain synchronized whenever any Skill is added, removed, renamed, updated, version-bumped, or materially changes scope. `Capability-Library/Registry.json` is the AIPM source of truth for active Skill slugs and versions; use each Skill's own `SKILL.md` for authoritative behavior and triggers. If this summary conflicts with either source, treat it as stale and reconcile it before relying on it.

| Skill | Current Version | Primary Function | Choose It When |
|---|---:|---|---|
| `audio-timing-author` | `1.0.0` | Produce transcript-aligned SRT and structured timing JSON from audio. | Accurate sentence/word synchronization is required. |
| `browser-environment-manager` | `1.1.0` | Create, diagnose and maintain isolated Edge/Chrome environments for agents. | Dedicated browser profiles, CDP/MCP connections, or browser-session troubleshooting are in scope. |
| `create-strict-implementation-handoff` | `1.0.0` | Author a strict execution-ready handoff without executing its underlying implementation. | The requested deliverable is a handoff, implementation task file, execution prompt, or instructions/brief for another AI agent to implement/change/repair. A generic README or explanatory Markdown is not enough. |
| `doc-to-md` | `1.0.0` | Convert user-supplied files into evidence-audited Markdown. | Extracting or analyzing supplied document contents is the task. |
| `powershell-tui-app-designer` | `1.2.1` | Design, build, update and test interactive PowerShell terminal applications. | A new or existing PowerShell TUI, wizard, menu, or input/render lifecycle is in scope. |
| `professional-word-designer` | `1.1.0` | Produce evidence-controlled professional Word publications. | The requested artifact is a substantial Word document or publication. |
| `project-governance-manager` | `1.0.0` | Create, audit and maintain AI-agent governance rules. | `AGENTS.md`, rule hierarchy, or project governance needs work. |
| `project-orchestrator` | `1.0.5` | Select and coordinate a minimum set of Skills/workstreams. | The user requests Skill selection, the task spans capabilities, or orchestration/supervision itself is needed. Do not add it as overhead for a clear single-specialist deliverable. |
| `resume-task` | `1.0.0` | Recover and finish interrupted work from verified current state. | Work is resuming after interruption, loss, timeout, or agent handoff. |
| `screenshot-to-code` | `1.0.0` | Reconstruct screenshots as editable frontend code with regional rendered verification. | Screenshot-to-code, exact visual matching, RTL recreation, or screenshot discrepancy repair is requested. |
| `shared-project-state-manager` | `1.0.0` | Preserve verified cross-agent/task state and handoffs. | Work is substantial, long-running, risky, or must survive session/agent changes. |
| `token-optimization` | `1.0.0` | Reduce avoidable context and repetition without dropping quality gates. | Lightweight efficiency support is useful for substantial work. |
| `tui-intelligence` | `1.0.0` | Specify and evaluate accessible terminal interaction and visual behavior. | TUI accessibility, navigation, information hierarchy, or visual interaction needs design/review. |

| `web-design-engineering` | `1.0.2` | Design and verify distinctive accessible web interfaces. | Original design, redesign, or broader web-interface engineering is requested. |

### 4.2 Deliverable-First Routing

The requested outcome and deliverable determine routing; file extension or a keyword alone does not. Consult `references/Skill-Selection-Protocol.md` before selecting Skills. When the owner asks for a Markdown file, prompt, task brief, or instructions that another AI agent will use to implement/change/repair work, assign `create-strict-implementation-handoff` as the LEAD authoring Skill and do not begin that implementation unless separately requested. Generic README, notes, explanation, or project documentation route by their actual purpose instead. This routing rule lives here so the imported handoff Skill's protected source content remains unchanged.

### 4.3 Explicit Owner Skill Selection

If the owner explicitly names a Skill, treat that Skill as selected and do not replace it through automatic routing.

If another Skill appears better suited:

1. keep the owner's named Skill as the active choice;
2. recommend the alternative briefly and explain the advantage;
3. wait for owner approval before substituting or adding it.

Preserve an explicitly named Skill. If another Skill seems better suited, explain the fit and obtain approval before substituting or adding it. Do not force Orchestrator-first routing for a clear specialist deliverable.

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

Follow `references/Skill-Selection-Protocol.md`. Confirm a gap against the active registry, then search trusted online sources when web access is available and discovery can materially help. Evaluate fit, maintenance, provenance, license, security, permissions and compatibility before recommending a candidate. Search or discovery does not authorize downloading, installing, executing, granting permissions, or adding dependencies. If online search is unavailable, use the base agent's native capabilities only when it can perform and verify the work competently; otherwise state the limitation and safe next step. Do not create a permanent Skill unless the owner asks for or approves that work.

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
- Use `project-governance-manager` as foundational support when governance is relevant to the task.
- Use `shared-project-state-manager` as foundational support for substantial work and never ignore relevant existing shared state.
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

For substantial orchestration, start with governance and shared-state awareness, then select the minimum necessary specialist Skills, construct the Team Map, execute through controlled workstreams, apply Supervisor gates, and maintain resumable state. For a narrow specialist deliverable, route directly and do not add orchestration steps.

The success criterion is:

**The owner should be able to request the outcome without needing to manually choose, order, supervise, and coordinate a large collection of Skills.**

## Automatic Skill Discovery and Selection

Use the deliverable-first routing and capability-gap process in `references/Skill-Selection-Protocol.md`.

- **audio-timing-author v1.0.0** — Use for audio/transcript synchronization work that requires accurate SRT sentence timing and structured sentence/word JSON timing metadata while preserving authoritative transcript text and excluding unspoken speaker labels from the timeline.

## Risk, Verification, Concurrency and Recovery

- Classify each task LOW, MODERATE or HIGH risk and secure approvals before sensitive or destructive changes.
- Define measurable acceptance criteria; distinguish PASS, FAIL, NOT-RUN and UNVERIFIED with actual evidence.
- Inspect current state immediately before edits and reconcile drift instead of overwriting concurrent work.
- Run independent workstreams in parallel only when their writes do not overlap; designate an integration owner.
- Keep resumable checkpoints and diagnose failures before bounded retries.
- Respect each active project's own governance; do not import this toolkit's rules into unrelated projects.
