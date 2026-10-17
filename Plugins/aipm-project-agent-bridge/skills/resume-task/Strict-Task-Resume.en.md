<!--
Version: 1.4.0
Type: Strict Task Resume — English Execution Prompt
Related Skill: resume-task
Updated: 2026-10-13
-->

# Strict Task Resume — English

Use this prompt to continue an interrupted task from its last VERIFIED state. It preserves all existing Resume Task recovery, safety, side-effect inspection, step verification, two-pass auditing and cross-agent provisions, with explicit continuity enforcement.

## Copy-and-paste prompt

```text
You are resuming an existing unfinished task after an interruption of ANY kind, including usage/quota/token/rate limits, exhausted context, session expiry, timeouts, crashes, network failures, tool errors, manual pauses, and transfer between AI agents or models. You may be the original agent or a different agent working on code, documents, data, design, research, or other authorized work. Your assignment is to FINISH THE ORIGINAL TASK, not restart it, simplify it, change its scope, or merely describe next steps.

OPTIONAL CONTEXT (use only if provided):
- Original task / objective: [OPTIONAL — paste or point to the original request]
- Approved plan / specification: [OPTIONAL — link or path]
- Project / workspace: [OPTIONAL — path or location]
- Previous progress report / checkpoint: [OPTIONAL — paste or path]
- Special constraints / acceptance criteria: [OPTIONAL]
- Known interruption reason / last attempted operation: [OPTIONAL — do not assume it is a usage limit]
- Handoff / external side effects / output locations: [OPTIONAL — provide identifiers or accessible references only]

MANDATORY OPERATING RULES

0. APPLY THIS PROMPT GENERALLY WITHOUT IMPORTING THE SOURCE PROJECT'S RULES
   This prompt may be used in any project or workspace. Follow the active task's instructions, project-specific governance, approved plans, and tool permissions. Do not apply Universal AI ToolKit rules, naming conventions, approval requirements, or assumptions to another project solely because this prompt came from that repository. The prompt defines a reusable continuation method and grants no permissions.

1. RESTORE THE ORIGINAL CONTRACT
   Reconstruct the original objective, all deliverables and acceptance criteria, approved plans and decisions, applicable project instructions, execution sequence, and safety/permission boundaries from the actual conversation and available project records. Preserve the original scope and quality bar unless a newer authorized instruction explicitly changes them. Never invent missing requirements, decisions, or completed work.

2. INSPECT STATE AND LOCATE THE INTERRUPTION
   Independently inspect current artifacts and state: files and diffs, branches/commits, checkpoints and task lists, execution/test reports, and running operations where accessible. Treat prior progress claims as leads, not proof. Identify the last VERIFIED completed step, the exact interrupted step, and its remaining acceptance conditions. Preserve valid work and avoid duplicates, conflicts, or destructive actions.

3. VERIFY THE INTERRUPTED STEP FIRST
   Before advancing to any dependent step, determine whether the interrupted operation actually finished. Inspect its outputs and side effects and perform safe, relevant checks. If incomplete, finish only the missing portion and verify it. If it may still be running, inspect its status instead of starting a duplicate. If retrying may repeat an external or irreversible effect, inspect state first and obtain any required authorization.

4. APPLY A VERIFICATION GATE AFTER EVERY STEP
   For each remaining step: (a) define its required outcome and acceptance evidence; (b) confirm prerequisites are verified; (c) execute it; (d) inspect the actual result against the criteria; (e) correct failures and rerun affected checks; and (f) mark it VERIFIED only when evidence passes. Do not proceed to a dependent step based on an attempt, optimistic report, unchecked log, or assumption. If evidence is unavailable, mark the step UNVERIFIED or BLOCKED, explain the exact gap, and do not claim completion.

5. CONTINUE SAFELY AND WITHIN SCOPE
   Complete authorized work using original methods, architecture, naming, formatting, conventions, and constraints. Make routine decisions autonomously; do not repeatedly ask for settled approvals. Do not overwrite unrelated changes, perform destructive actions, expose secrets, publish/deploy, incur costs, or make irreversible external changes unless specifically authorized. Ask only when essential context, access, or authorization genuinely blocks safe progress. Continue independent safe work that does not depend on a blocked step.

6. AUDIT THE WHOLE TASK IN TWO PASSES
   After implementation, audit all original requirements, including work completed before the interruption.
   Pass A — Requirement coverage and correctness: map every requirement and deliverable to the final artifact and evidence; check names, paths, formats, constraints, completeness, edge cases, and internal consistency. Confirm nothing was omitted or silently downgraded.
   Pass B — Integration, regression, and quality: run appropriate tests, builds, lint/type checks, inspections, previews, or domain-specific validation supported by the environment. Review integration with untouched components and relevant reliability/security risks. Fix issues and rerun affected checks. Clearly distinguish checks performed from checks unavailable or skipped.

7. REPORT EVIDENCE-BASED STATUS
   End with a compact, complete report containing:
   - Original objective and what was recovered from evidence;
   - Last verified checkpoint, exact step resumed, and how its state was checked;
   - Work completed and important changes;
   - Requirement-by-requirement acceptance results;
   - Checks actually run and observed outcomes;
   - Remaining gaps, limitations, blockers, risks, or approvals;
   - One final status: COMPLETE, PARTIALLY COMPLETE, or BLOCKED.

Use COMPLETE only when all requirements are satisfied and mandatory checks pass. Use PARTIALLY COMPLETE when meaningful work is complete but requirements or checks remain open. Use BLOCKED when no safe authorized progress can continue without a specific missing input, access, resource, or approval. Support the status with evidence.

8. SUPPORT ALL INTERRUPTION CAUSES AND AI AGENTS
   Apply these SAME original requirements and verification gates regardless of whether execution stopped from usage limits, context exhaustion, session expiry, a crash, network/tool failure, timeout, manual pause, or a model/agent handover. Continue with the current agent's real capabilities and permissions while preserving the original user's scope and existing outputs. If the previous agent's private context is inaccessible, recover what you can from the supplied task, approved records, checkpoints, artifacts, and actual external state; never claim to remember unavailable conversations or hidden reasoning. A Prompt does not bypass product quotas, restore lost context, or grant tool permissions. If access is still restricted, report the specific blocker accurately.

9. USE PORTABLE CHECKPOINTS AND AVOID DUPLICATE EFFECTS
   When interruption is foreseeable and the task/environment permits it, save a concise, agent-neutral checkpoint: authoritative task source, unchanged requirements/decisions, validated completed steps with evidence, interrupted step and acceptance criteria, files/IDs/versions, partial writes or possible external side effects, next safe action, remaining dependencies, and mandatory final checks. Do not store secrets or sensitive user data.
   After any interruption, compare checkpoint claims against the current artifacts, tests, version-control state and external results before acting. For non-idempotent actions (sending, payment, publication, deployment, deletion or migration), check whether they already completed and use existing transaction or idempotency identifiers where available. Do not blindly replay operations. Checkpoints and summaries are hints, not proof. Preserve original acceptance gates and use accurate UNVERIFIED/BLOCKED labels for inaccessible evidence.

10. STRICT CONTINUITY AND QUALITY INVARIANTS
   An interruption alone never changes the original requirements, approved implementation plan, project architecture, applicable governance, naming, code conventions, testing depth, documentation, sequencing, security, performance, or acceptance thresholds. Treat all of these as continuing obligations. Do not infer permission to refactor, switch libraries, downgrade quality, compress tests, omit deliverables or choose a new strategy merely because limits or connectivity interrupted execution. Follow any later explicitly authorized change without treating it as a violation of continuity. When tooling or resources differ across agents, adapt only the mechanics necessary to fulfill the same approved outcome, without unapproved scope or safety changes.
   Before any write, reconcile the original contract, the real working tree/external state, and durable checkpoint evidence. Label items VERIFIED, IN_PROGRESS, UNVERIFIED, FAILED or BLOCKED. Preserve all correct prior work; do not duplicate side effects. Continue the original task by execution, not by paraphrasing it. If mandatory verification cannot be performed, record the limitation and never report COMPLETE.

EXECUTION ORDER (STRICT):
Recover context -> Inspect actual state -> Identify interruption point -> Verify/repair interrupted step -> Execute and verify each remaining step -> Perform both final-audit passes -> Report evidence-based status.

START NOW. First inspect the original task context and actual workspace state; then do the work. Do not stop at a plan or ask me to repeat information already accessible. If critical context or artifacts are inaccessible, identify exactly what is missing rather than pretending to recover it.
```

## Guidance

- Skill: [`resume-task`](SKILL.md); concise variant: [`Short-Prompt.md`](prompts/Short-Prompt.md).
- Arabic equivalent: [`Strict-Task-Resume.ar.md`](Strict-Task-Resume.ar.md).
- This prompt cannot bypass service limits or retrieve inaccessible context.
