---
name: resume-task
description: Resume and finish interrupted tasks for any AI agent after usage limits, context exhaustion, session loss, timeout, crash, failure, or takeover. Reconstruct accessible task details, preserve progress, verify actual state before repeating actions, and complete every remaining requirement.
---

# Resume Task — Strict Task Resume

## Mission

Finish the original task from its latest evidenced state. Preserve the user's scope, requirements, deliverables, decisions, constraints, project governance, sequence, and quality bar. Verify the interrupted operation before advancing; gate each subsequent step; audit the complete task and report only evidence-backed outcomes.

This is a general-purpose Skill for any project, repository, workspace, organization, or standalone task; its source location in Universal AI ToolKit does not restrict where it may be used. It applies to code, documents, data, research, design, and external workflows. Adapt the evidence and validation method to the artifact. Follow the active task's governing instructions, project-specific rules, approved plans, and tool permissions. Do not import Universal AI ToolKit rules or assumptions into another project merely because this Skill came from that repository. The Skill provides a reusable continuation method; it does not replace any governing specification or grant permissions.

## Non-negotiable rules

1. **Preserve the original contract.** Use the user's original request and later clarifications, available approved plans, project rules, and actual artifacts. New authorized user instructions amend older ones. Never fabricate missing requirements or prior decisions.
2. **Evidence beats claims.** A former agent's completion message, checkbox, checkpoint, or test summary is a lead, not proof. Verify relevant claims against current state and trustworthy results.
3. **Interrupted step comes first.** Do not begin a dependent step until the interrupted step passes its acceptance checks.
4. **Inspect before replay.** Check state before repeating external mutations, messages, publishing, deployments, purchases, migrations, destructive actions, or operations that may still be running.
5. **Gate every step.** Define the outcome, execute, inspect against acceptance criteria, correct failures, rerun affected checks, then mark VERIFIED. Attempted work is not verified work.
6. **Stay within authorized scope.** Continue routine, reversible work autonomously. Follow project approval rules for high-impact actions. Do not create unapproved side effects or silently change scope.
7. **Report uncertainty accurately.** Missing context, inaccessible systems, skipped checks, and unresolved results remain explicit. Never claim full success without evidence.

## Workflow

### 1. Reconstruct the task contract

Identify the objective, every deliverable and acceptance criterion, dependencies/order, constraints and prohibited actions, relevant approvals, and applicable quality gates. Read the project's current governance (for example, AGENTS.md) and invoke the project's required Skill-routing or governance process. Treat summaries and agent notes as secondary evidence.

Build an internal requirement ledger. If an essential input is missing, do safe discovery and ask only for that specific blocker; continue independent work.

### 2. Inspect actual state

Inspect deliverables and current state before editing: files and diffs, version-control state, branches and commits, checkpoints, test/build/validation results, partial writes, failures, and running operations where accessible. Preserve user and teammate changes. Record each work item with its requirement, evidence, status, missing check, and next safe action.

Use these status labels:

- **VERIFIED** — result exists and current evidence satisfies its acceptance criteria.
- **IN_PROGRESS** — work started; acceptance is not yet met.
- **UNVERIFIED** — completion is plausible or claimed but evidence is insufficient.
- **FAILED** — an observed acceptance check failed.
- **BLOCKED** — progress requires unavailable context, access, resources, or authorization.

Identify the latest VERIFIED step and the exact interrupted step. Timestamps and recollection are supporting clues only.

### 3. Verify or repair the interrupted step

Inspect its output and side effects. If complete, verify all its acceptance criteria. If partial, preserve valid work and finish only the missing portion. If a process may still be active, inspect its status instead of duplicating it. If it failed, diagnose and make the smallest authorized correction. If retrying risks irreversible or duplicate effects, inspect the external state and obtain required approval. If evidence is inaccessible, mark UNVERIFIED/BLOCKED and do not advance dependent work.

**Gate:** The interrupted step is VERIFIED before any dependent successor starts.

### 4. Execute remaining steps with strict gates

For each remaining step, in the original dependency order:

1. Confirm prerequisites are VERIFIED and resources/permissions exist.
2. State internally what “done” means and what evidence will prove it.
3. Perform the smallest coherent authorized action, following project conventions.
4. Inspect the actual result, not just the tool response or a progress claim.
5. Fix deficiencies and repeat affected verification. Recheck earlier results if changes could invalidate them.
6. Mark VERIFIED only when all mandatory criteria pass; otherwise retain FAILED, UNVERIFIED, or BLOCKED and stop dependent work.
7. Save concise durable checkpoints when the project supports them, recording facts, evidence, and the next safe action.

Independent safe work may continue around a blocker only if it does not assume the blocked step succeeded or violate the original sequence.

### 5. Perform a two-pass final audit

Do not stop after implementation.

**Pass A — Requirements and correctness**

- Re-read the original request and map every requirement and deliverable to the final artifact and evidence.
- Check names, locations, formats, scope, constraints, completeness, edge cases, internal consistency, and requested outputs.
- Confirm no requirement was omitted, replaced, duplicated, or silently downgraded.

**Pass B — Integration, regression, and quality**

- Run suitable tests, builds, lint/type checks, data validation, rendering/previews, link checks, or direct functional inspection available for the domain.
- Review interactions with related and untouched components, unexpected changes, regressions, and relevant reliability/security risks.
- Fix defects and rerun affected checks. Distinguish actual passes from manual review, unavailable checks, and skipped checks.
- If a mandatory check cannot run, state why and do not report COMPLETE.

### 6. Report final status

Provide a concise evidence-based report containing the recovered objective and sources, verified checkpoint and exact resumed step, changes made and locations, requirement-by-requirement outcomes, checks performed and actual results, and remaining limitations/blockers/approvals. Choose exactly one status:

- **COMPLETE** — every deliverable and mandatory acceptance check is satisfied with evidence.
- **PARTIALLY COMPLETE** — meaningful work is done, but a requirement/check remains open or unverified.
- **BLOCKED** — safe authorized progress cannot continue because a specific input, access, resource, or approval is missing.

Do not say “all tests pass” unless all relevant required tests were actually run on the final state.

## Limit-aware and cross-agent continuation

- **Universal trigger:** Use after any stop or takeover, especially token/usage/quota/rate limits, context exhaustion, timeouts, crashes, network disconnections, tool failures, and manual pauses. Apply to coding and non-coding tasks alike.
- **Protect the contract:** Recover the exact original objective, constraints, approved decisions, acceptance tests, artifacts, and later authorized amendments. Do not lose details because a new model or agent is taking over.
- **Prepare before a predictable cutoff:** When feasible and permitted, save a concise portable checkpoint with original task source, requirements ledger, evidence-backed VERIFIED steps, current incomplete step, possible side effects, next safe action, remaining work, and final checks. Prefer compact evidence references over full transcripts. Never save secrets.
- **Recover after an abrupt cutoff:** Inspect accessible messages, task files, version control, logs, test outputs and any checkpoint. Reconcile recorded state against live artifacts. Do not pretend to recover inaccessible conversations, hidden reasoning, or unavailable files.
- **Avoid duplicate mutations:** Check if the interrupted operation already succeeded, especially for external sends, payments, publication, deployments, deletions, migrations, and remote API calls. Reuse idempotency identifiers when available, not blind replay.
- **Across AI agents:** Express handoffs in platform-neutral text and file locations. The receiving agent uses only actually available tools and permissions and follows the active project's rules—not rules of this Skill's source repository.
- **Efficient but complete:** Do not restart or rerun expensive completed work without reason. Verify existing evidence, recover missing portions, then run all mandatory final checks. Missing mandatory verification prevents a COMPLETE verdict.
- **Limit boundary:** This Skill does not bypass quotas, guarantee agent memory, restore inaccessible context, or run in the background.

See [Recovery Playbook](references/Recovery-Playbook.md), [Checkpoint Example](examples/Task-Checkpoint.json), and optional [read-only validator](scripts/validate_checkpoint.py).

## Checkpoint template

When a durable checkpoint is useful and permitted:

```markdown
# Task Continuation Checkpoint
- Original objective and authoritative source:
- Applicable instructions, decisions, and constraints:
- Workspace/repository and relevant artifact versions:
- VERIFIED steps with evidence:
- Exact interrupted/current step and acceptance criteria:
- Partial actions or possible side effects:
- Latest actual check results and failures:
- Next safe action; actions that must not be repeated:
- Remaining ordered work:
- Final audit still required:
- Missing access, context, or approvals:
```

Do not create a project note solely for this template if the user or project disallows it.

## Safe boundaries

- Do not use destructive reset/clean actions to erase unknown changes or conflicts.
- Do not repeat external effects without checking whether they already succeeded.
- Do not expose secrets or personal data in checkpoints/reports.
- Do not add dependencies, incur costs, publish/deploy, send messages, or make permanent changes that need approval unless authorized by the original task or current user.
- Follow platform and project rules; this Skill grants no permissions or capabilities.
- If verification is unavailable, use a defensible alternative when possible and keep the required result UNVERIFIED/BLOCKED.

## Relationship to project state and other Skills

Use the active project's shared-state, orchestration, governance, testing, or domain-specific Skills when their triggers and governing rules apply. This Skill provides the resumption and verification gates; it does not replace a project's broader state-management system. If the user explicitly names another Skill, follow the active project's routing precedence and do not silently substitute. Apply this Skill's general workflow across projects while keeping each project's own rules, vocabulary, approval process, and tooling separate.

## Strict Task Resume — Bilingual Prompts

Use [English](Strict-Task-Resume.en.md) or [Arabic](Strict-Task-Resume.ar.md) for strict, paste-ready resumption. Both retain original requirements, verified checkpoint recovery, safety gates and quality standards. The legacy [full prompt](PROMPT.md) and [short prompt](prompts/Short-Prompt.md) remain available for backward compatibility. This Skill remains canonically identified as `resume-task` to avoid breaking routing and existing imports; **Strict Task Resume** is its new human-facing combined name.
