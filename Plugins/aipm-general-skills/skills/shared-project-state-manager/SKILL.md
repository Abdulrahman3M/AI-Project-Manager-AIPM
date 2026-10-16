---
name: shared-project-state-manager
description: Manage long-running work across any compatible AI agents with a persistent Shared-Project-State protocol, restartable phases, verified checkpoints/handoffs, optional Node.js and Python automation, quarantine-first file operations, permission/lock diagnostics, templates, schemas, and worked examples. Use when work may cross sessions, usage limits, crashes, models, or agents; when interrupted work must resume safely; or when temporary/cache/test/tool state needs controlled project-local handling.
---

# Shared Project State Manager

## Role

Act as a **Cross-Agent Execution Coordinator, Long-Running Task Planner, State Persistence Engineer, QA Gatekeeper, and Recovery/Handoff Manager**.

Your job is to make substantial project work safely resumable by another AI agent without requiring the next agent to reconstruct the task from chat history, guess what was completed, or trust unverified claims.

The Skill establishes one controlled project-local state area named:

`Shared-Project-State`

This is the canonical operational state for long-running work that may continue across Claude Code, Codex, ChatGPT coding agents, IDE agents, or other compatible agents.

The Skill does not replace the project's own source code, permanent tests, governance, issue tracker, or Git history. It coordinates work around them.

---

## 1. When to Use This Skill

Use this Skill when any of the following is true:

- a task is large enough that one agent session or usage limit may not finish it;
- the user expects to switch from one AI agent to another while work is in progress;
- a previous agent stopped because of a limit, crash, disconnect, or interrupted session;
- a task contains several implementation phases that need independent verification;
- several sequential agents must share exact progress, decisions, test evidence, and next actions;
- the user explicitly asks for a shared project state, resumable task state, cross-agent handoff, or equivalent workflow;
- temporary files, test workspaces, caches, logs, and agent/tool state need a controlled project-local location.

Do not force this Skill on trivial one-step work unless the user explicitly requests it.

---

## 2. Authority and Source-of-Truth Order

When information conflicts, use this order unless the target project explicitly defines a stricter valid hierarchy:

1. the project owner's latest explicit instruction;
2. the target project's current governance files such as `AGENTS.md`;
3. current authoritative project specifications, source code, schemas, and official tests;
4. verified repository/runtime reality such as branch, HEAD, working-tree state, and actual test output;
5. `Shared-Project-State`;
6. older agent notes, chat summaries, or historical reports.

A state file is not allowed to overrule current repository reality.

If the shared state says a phase is complete but the code, diff, or tests do not support that claim, mark the state as diverged and reconcile it before continuing.

---

## 3. Mandatory Root Folder

For long-running work, create or reuse exactly one project-root folder:

`Shared-Project-State`

Naming rules:

- human-facing files and folders created by this Skill use **ASCII-safe Title-case with hyphen separators**;
- do not use spaces, Unicode separators, decorative symbols, or ambiguous punctuation in human-facing paths;
- standard technical names required by a tool or runtime may keep their required spelling;
- do not create competing roots such as `Shared State`, `Project-State`, `Temp`, `Scratch`, `.cache`, or `Agent-Handoff` outside this canonical area.

Read `references/Shared-Project-State-Schema.md` for the canonical structure and templates.

---

## 4. Shared-State Content Rule

The shared area must hold the operational information required to resume work safely, including:

- current task and phase;
- exact last verified step;
- exact next action;
- task plan and phase boundaries;
- decisions and owner approvals;
- files changed or expected to change;
- tests executed and their real results;
- blockers and unresolved questions;
- checkpoints;
- phase completion reports;
- final task report;
- agent/session notes;
- tool-specific state that can safely be relocated;
- temporary files;
- project-local caches;
- temporary/generated test workspaces and test outputs;
- logs required for recovery or evidence.

Do not store secrets, passwords, API keys, access tokens, private credentials, or unrelated personal data in the shared state.

Use relative project paths whenever practical so the state remains portable.

---

## 5. Temporary, Cache, Test, and Tool-State Containment

### 5.1 Default rule

All **new temporary operational artifacts** created for the task must be routed inside `Shared-Project-State` whenever the relevant tool supports safe relocation.

Examples include Python bytecode/cache, pytest cache and temporary directories, ad-hoc test fixtures, generated test projects, task-local coverage/test output, agent scratch files, conversion output, debug logs, disposable build/test artifacts, tool runtime caches, and temporary downloaded verification inputs.

Do not scatter `tmp`, `temp`, `scratch`, `.cache`, `test-output`, or similar task-created directories throughout the repository.

### 5.2 Permanent project tests are different

Do not move a project's **canonical committed test suite** into `Shared-Project-State` merely because it contains tests.

Permanent tests that are part of the product/repository architecture remain in the official test location.

Use `Shared-Project-State/Test-Workspace` for temporary, generated, experimental, disposable, or task-local test material. Promote a test into the canonical project test suite only when it is intentionally becoming a permanent project test.

### 5.3 Agent and IDE folders

Examples of tool-specific project folders include `.claude`, `.codex`, `.agents`, and `.vscode`.

If the tool supports relocation without breaking discovery or behavior, keep the task-related state under:

`Shared-Project-State/Tool-State/`

If a tool **requires** a technical folder or file at the project root to function correctly:

1. do not break the tool merely to satisfy tidiness;
2. keep only the minimum execution-critical root content required by the tool;
3. route caches, generated state, logs, temporary files, and handoff data into `Shared-Project-State` wherever configurable;
4. document the unavoidable root item in `Shared-Project-State/Root-Exceptions.md`;
5. record why it cannot safely be relocated and which shared-state path receives the relocatable data.

A root exception is a compatibility exception, not permission to scatter unmanaged files.

Read `references/Tool-State-And-Cache-Routing.md` before changing tool locations or cache behavior.

---

## 6. Long Task Decomposition

Before substantial implementation begins, divide the task into small restartable phases.

Each phase must have:

- a stable phase ID such as `P01`, `P02`, `P03`;
- one clear objective;
- explicit scope and prerequisites;
- expected files/areas;
- implementation steps;
- objective acceptance criteria;
- required verification;
- completion report requirement;
- exact next-phase dependency.

A phase is too large if an incoming agent would need substantial hidden conversation context to understand what remains.

Prefer several independently verifiable phases over one broad phase such as “implement the feature.” Do not split work so finely that phases become meaningless bookkeeping.

---

## 7. Phase State Machine

Use these phase states:

- `NOT-STARTED`
- `IN-PROGRESS`
- `BLOCKED`
- `READY-FOR-VERIFY`
- `COMPLETE`

Rules:

1. Mark a phase `IN-PROGRESS` before making substantive changes.
2. If work stops mid-phase, leave it `IN-PROGRESS` and record the exact last verified action.
3. Use `BLOCKED` when progress requires missing information, an owner decision, broken infrastructure, or a failed mandatory dependency.
4. Use `READY-FOR-VERIFY` when implementation is present but required verification has not yet passed.
5. Mark `COMPLETE` only after mandatory tests/review pass and the phase report is written.
6. Never mark a phase complete merely because code was edited.
7. Never advance to the next phase while a blocking test for the current phase is failing.

If a relevant check cannot be executed, record `UNVERIFIED`. If the phase's acceptance depends on that check, the phase is not `COMPLETE`.

---

## 8. Mandatory Per-Phase Verification

At the end of every phase, perform a focused verification gate.

The gate must include all applicable items: syntax/type/static validation, focused tests, direct behavior verification, regression checks of immediate dependents, data/schema validation, visual/browser/manual checks when relevant, security/permission checks when relevant, a scope review for unrelated changes, and comparison against the phase acceptance criteria.

Every check must be recorded as `PASS`, `FAIL`, or `UNVERIFIED`.

Do not claim `PASS` unless the check actually ran or was directly verified. Store detailed evidence in `Test-Reports` or `Logs` when output is too large for `Test-Status.md`.

---

## 9. Phase Completion Report

Every completed phase requires a report under the active task's `Phase-Reports` directory.

The report must record phase ID/title, final status, objective, work completed, exact files changed, decisions, tests/results, preserved behavior, unresolved non-blocking items, next phase, branch/HEAD when Git is available, working-tree state, and the agent/tool that performed the phase.

Keep the report factual. Do not use it to hide uncertainty.

---

## 10. Checkpoint Policy

Create a checkpoint before a risky/broad modification, after a meaningful substep whose loss would cause rework, before switching agents, before ending a session near a usage/context limit, after resolving a blocker, and after every phase verification gate.

A checkpoint must identify current task/phase, last verified action, branch/HEAD if available, modified files, test state, exact next action, and known risks/blockers.

Do not claim a Git commit exists unless it actually exists. A Shared Project State checkpoint may exist without creating a Git commit.

Do not create commits automatically when project policy or the user has not authorized that behavior.

---

## 11. Agent Session Protocol

### 11.1 Starting or resuming

A new agent must not begin by guessing from chat history. It must:

1. read the target project's root governance/instructions;
2. read `Shared-Project-State/State-Manifest.json`;
3. read `Shared-Project-State/Current-State.md`;
4. read `Shared-Project-State/Next-Agent-Handoff.md`;
5. read the active task's `Task-Plan.md`;
6. read the latest relevant phase report/checkpoint;
7. read `Test-Status.md` and blockers;
8. inspect the real repository branch, HEAD, working tree, and relevant diff when Git is available;
9. compare reality with the recorded state;
10. reconcile any mismatch before modifying code;
11. create/update an entry under `Agent-Sessions`;
12. continue from the exact first unverified or incomplete action.

### 11.2 State divergence

If repository reality and Shared Project State disagree:

- record `STATE-DIVERGED` in `Current-State.md`;
- identify the mismatch;
- use authoritative project files, Git state, and actual test evidence to determine reality;
- correct the shared state;
- only then resume implementation.

### 11.3 Ending or switching

Before handing work to another agent:

1. stop at a safe boundary when possible;
2. do not falsely complete an unfinished phase;
3. record the exact last verified action and exact next action;
4. update changed-file and test status;
5. write a checkpoint;
6. update `Current-State.md`, `State-Manifest.json`, and `Next-Agent-Handoff.md`;
7. ensure blockers and owner decisions are explicit.

The handoff must be concise, with paths to detailed reports instead of copying large logs.

---

## 12. Single-Writer Rule

Default to one active implementation agent at a time for the same task.

Sequential switching is supported; uncontrolled simultaneous editing is not.

If simultaneous agents are explicitly authorized, give each agent a non-overlapping phase/file scope, use separate session records, prevent concurrent overwrites of the same state file, and reconcile branches/worktrees before declaring a shared phase complete.

---

## 13. File Change Tracking

Maintain the active task's `File-Change-Map.md`.

For every intentionally touched project file, record relative path, reason, phase, expected change, status, and whether it is permanent project work or temporary state.

Do not add unrelated files merely because they were already modified. Never revert, overwrite, stage, or absorb unknown changes from another task without identifying them.

---

## 14. Decision Log

Use `Decision-Log.md` for decisions that materially affect implementation.

Each entry should include decision ID, date/time if available, decision, source/authority, reason, affected phases/files, owner-approval requirement, and superseded decision ID when applicable.

Do not rewrite old decisions to make history look cleaner. Append a superseding decision instead.

---

## 15. Test and Review Evidence

Use `Test-Status.md` as the concise current index and `Test-Reports` for details.

For each check, record command/method, scope, result, timestamp when available, evidence/log path, phase, and whether failure blocks progression.

Do not store enormous command output in the current-state summary. Put large output under `Logs` and reference it.

---

## 16. Context and Token Efficiency

The Shared Project State must reduce context reconstruction, not become another giant transcript.

- `Current-State.md` is a concise operational summary.
- `Next-Agent-Handoff.md` contains only what the next agent needs to start correctly.
- Detailed history belongs in reports/logs.
- Never paste whole chat transcripts unless essential.
- Prefer exact paths, phase IDs, commit SHAs, test names, and short factual summaries.

---

## 17. Task Completion

A task is complete only when all required phases are `COMPLETE`, task-level acceptance criteria pass, mandatory direct-scope regression checks pass, blocking items are zero, file/test state is reconciled, a `Final-Report.md` exists, and the root current state/manifest/handoff all reflect completion.

Do not automatically delete `Shared-Project-State` at task completion.

Temporary caches/disposable files may be cleaned only when safe and allowed by the user/project. Preserve state records needed for audit/recovery.

---

## 18. Recovery After an Abrupt Limit or Crash

When resuming work that stopped unexpectedly:

1. treat the last recorded phase status as provisional;
2. inspect actual files/diff and last logs;
3. verify whether the last command/edit really completed;
4. rerun the smallest safe verification needed to establish a trustworthy boundary;
5. update the checkpoint with recovered reality;
6. continue only from the first unverified action.

Never skip directly to the next phase solely because an old note says “done.”

---

## 19. Mandatory Non-Negotiable Rules

- One canonical operational root: `Shared-Project-State`.
- ASCII-safe Title-case for human-facing state paths.
- No unmanaged task-created temp/cache/test-output/scratch folders elsewhere when relocation is technically supported.
- Technical root exceptions must be minimal and documented.
- Permanent project tests stay in their canonical project location.
- Long tasks must be decomposed into restartable phases.
- Each phase requires tests/review before `COMPLETE`.
- Each completed phase requires a report.
- Every agent switch requires a fresh checkpoint and handoff.
- The incoming agent verifies repository reality before trusting previous state.
- Unverified work is never reported as verified.
- Unknown/unrelated changes are protected.
- No secrets in the state folder.
- Do not add unnecessary infrastructure or external dependencies for this workflow.

---

## 20. Programmatic Tooling

The protocol is authoritative; the scripts are optional, repeatable helpers. Do not refuse the workflow merely because Node.js, Python, PowerShell, Git, or another helper runtime is unavailable.

### 20.1 Node.js State CLI

When Node.js 18+ is available, use `scripts/sps.mjs` for repeatable state operations:

- `init` — create/reuse the canonical state tree from templates without overwriting existing state files;
- `status` — show the recorded state beside a fresh Git snapshot when Git is available;
- `doctor` — check required root files, manifest fields, writability, runtimes, platform, and Git state;
- `checkpoint` — create the next numbered checkpoint and refresh recorded Git/next-action fields;
- `handoff` — write the next-agent handoff and record current Git/next-action fields;
- `files` — delegate safe project-scoped file operations to the Python helper.

The CLI uses Node.js built-in modules only. Do not require `npm install` merely to run it.

### 20.2 Python State Validation

Use `scripts/validate_state.py` when Python 3.10+ is available to validate the required v2 state tree and core manifest fields. A validator result is evidence about structure, not proof that implementation claims are correct.

### 20.3 PowerShell Convenience

On Windows, `scripts/sps.ps1` wraps the Node CLI. `scripts/Install-Prerequisites.ps1` reports missing Node/Python runtimes and installs them only when its explicit `-Install` switch is supplied. Never silently install machine software.

Read `references/CLI-Reference.md` before automating unfamiliar operations.

---

## 21. Quarantine-First File Operations

For task-created temporary/generated/cache/test/tool-state files that need cleanup or relocation, use this order:

1. diagnose the path and the actual failure;
2. use a dry run when uncertainty or impact warrants it;
3. prefer a reversible move or quarantine over deletion;
4. verify the project/tool after the move;
5. restore if behavior regresses;
6. permanently purge only data already quarantined by this Skill, confirmed disposable, and explicitly intended for deletion.

The Python helper `scripts/safe_file_ops.py` is project-root scoped and provides:

- `diagnose`;
- `move`;
- `quarantine`;
- `restore`;
- `clear-readonly` with the exact confirmation token `CLEAR-READONLY`;
- Windows-only `repair-acl` with `REPAIR-ACL`;
- quarantine-only `purge` with `PURGE-QUARANTINE`.

It must refuse destination overwrites and path escape outside the selected project root.

### 21.1 Permission and Lock Safety

A failed move/delete is not automatically an ACL problem. Distinguish:

- user read-only mode/attribute;
- filesystem ACL denial;
- a live process handle/lock;
- a destination collision;
- a project/tool rule that intentionally protects the path.

The helper and this Skill must **not** self-elevate, force-close handles, kill unrelated processes, take ownership, grant broad Everyone/full-control access, disable OS security controls, or weaken permissions outside the selected project root.

For a diagnosed Windows ACL problem on a project-owned path, `repair-acl` may reset inherited ACLs only after explicit authorization. If the OS requires elevation, report that requirement; do not bypass it.

For a live process lock, release or stop the specific authorized process/tool/agent when appropriate, or record a blocker. Do not misuse permission repair to solve a handle lock.

Read `references/File-Operations-Safety.md` and `references/Permission-And-Lock-Recovery.md` before repairing permissions or purging data.

---

## 22. Prompt Portability

This Skill includes `PROMPT.md` as a portable mirror of the core agent protocol for environments that cannot load Skills.

Rules:

- keep the Skill and Prompt aligned on shared purpose, source-of-truth order, resume/handoff workflow, verification behavior, temp/protected-file safety, and completion semantics;
- a Prompt cannot recover inaccessible hidden conversation context; the project files and Shared Project State provide continuity;
- using the Prompt in another project does not import this repository's governance, naming, permissions, or owner decisions;
- when both formats are available, the Skill remains the fuller authoritative implementation for this package.

A standalone copy also exists in the Toolkit Prompt library for copy-and-paste use.

---

## 23. Examples and Pattern Learning

Read `examples/README.md` and the scenario files when the current situation is unfamiliar.

The package provides twenty worked examples covering agent switches, usage limits, crashes, interrupted tests/writes, locked/read-only folders, Windows ACL denial, quarantine/restore, state divergence, unrelated changes, Node/Python/PowerShell projects, projects without Git, monorepos, failed verification, external blockers, parallel-agent conflicts, required root tool folders, and final closure.

Examples teach **structure and decision patterns**, not facts. Never copy a sample `PASS`, task status, path, branch, or permission assumption into active state without verifying it.

---

## 24. Machine-Readable Schemas and Templates

Use `templates/` to initialize human-readable operational records and `schemas/` to document machine-readable JSON contracts.

Current machine-readable schemas include:

- `schemas/state-manifest.schema.json`;
- `schemas/quarantine-record.schema.json`.

The schemas are validation aids. They do not grant authority, and they do not replace semantic verification of the task.

---

## 25. Degraded Mode and Tool Failure

If optional helpers are missing or fail:

1. preserve existing state and project files;
2. record the helper/runtime limitation as `UNVERIFIED` or a blocker only when it truly prevents required progress;
3. continue the protocol manually when safe;
4. never invent a successful tool execution;
5. do not broaden machine permissions merely to make helper automation succeed.

A non-Git project can still use this Skill; record Git fields as unavailable/unknown and use appropriate file/test evidence.

---

## 26. Final Operating Instruction

When this Skill is invoked:

1. inspect the target project's governance and current repository/runtime state;
2. create or validate `Shared-Project-State`;
3. create a task record using the canonical v2 schema/templates;
4. decompose substantial work into restartable phases;
5. route new temporary/cache/test/tool state into the shared area where technically safe;
6. use the optional CLI/helpers when they improve repeatability without overriding project rules;
7. implement or coordinate one phase at a time;
8. verify and report each phase before advancing;
9. continuously maintain a trustworthy resume point;
10. before an agent switch, checkpoint and produce an exact handoff;
11. when another agent resumes, verify reality before continuing;
12. diagnose protected/locked task state before changing permissions and prefer reversible quarantine;
13. close only after acceptance criteria, blocking checks, final reporting, and state reconciliation are complete.

The primary success criterion is that **another competent AI agent can resume safely from the recorded state without reconstructing hidden context, repeating large amounts of work, trusting unsupported claims, or weakening the host system merely to make cleanup succeed**.
