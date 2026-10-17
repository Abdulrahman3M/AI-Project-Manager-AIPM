<!--
Version: 1.0.1
Name: RichViz
Type: Task Resumption and Verified Continuation Prompt
Related Skill: shared-project-state-manager
Updated: 2026-10-08
-->

# RichViz

Resume and complete the task already assigned in this conversation or project. The task may have been interrupted because of usage limits, a session ending, a context limit, a tool failure, or another interruption.

Treat this as a continuation of the original assignment, not as a new task. Preserve its original scope, intent, requirements, constraints, standards, priorities, and requested deliverables. Do not simplify, reinterpret, silently drop, or replace any requirement.

## 1. Establish the Authoritative Task

Before taking action:

1. Read the complete original user request and all subsequent user clarifications or corrections available in the conversation.
2. Inspect the applicable project instructions, plans, handoffs, acceptance criteria, decisions, and repository or workspace guidance.
3. Identify the authoritative sources for the task. Follow their precedence rules. User instructions and explicit user decisions take precedence over agent-authored notes, assumptions, summaries, and plans.
4. Build a concise requirement checklist covering:
   - required outcomes and deliverables;
   - constraints, standards, and prohibited actions;
   - dependencies and ordering;
   - required validation and acceptance criteria;
   - any unresolved decisions that genuinely block safe or correct execution.

Do not rely on a previous agent's summary as proof that a requirement was satisfied. Verify it against the original request and current project state.

## 2. Reconstruct the Last Verified Checkpoint

Determine the latest task step that is demonstrably complete. Do not resume from the last step that was merely started, discussed, planned, attempted, or reported as underway.

Inspect the strongest available evidence, in this order where applicable:

1. Current files, application state, database state, or other task artifacts.
2. Version-control state: working-tree diff, staged changes, commits, branches, and relevant history.
3. Test, build, validation, deployment, or other execution results.
4. Durable task records such as a plan, checklist, handoff, progress log, checkpoint file, or session notes.
5. Conversation messages and tool outputs that clearly show completed work.

Use timestamps only as supporting evidence; a recent timestamp alone does not prove completion. Confirm that outputs exist, are coherent, and satisfy the applicable requirement. Distinguish these states explicitly:

- **Verified complete:** the result exists and has been checked against its requirement.
- **Implemented, not verified:** changes exist, but adequate verification is missing.
- **In progress or partial:** some work exists, but the step's completion criteria are not met.
- **Not started:** no reliable evidence of execution.
- **Blocked:** progress depends on a specific missing input, access, decision, or external condition.

Create a checkpoint table with each requirement or work item, its evidence, status, and next action. If no durable checkpoint exists, reconstruct one from the artifacts and records; do not assume that nothing was completed.

## 3. Handle Partial and Uncertain Work Safely

For every item that was in progress, partially completed, or implemented but not verified:

1. Inspect the actual current state before editing or rerunning anything.
2. Identify completed substeps and preserve valid work.
3. Identify incomplete, inconsistent, duplicated, or failed substeps.
4. Resume at the smallest incomplete substep that can be safely continued.
5. Avoid overwriting user changes, repeating irreversible actions, duplicating deliverables, or discarding valid partial work.
6. Before retrying an operation that may have external side effects, check whether it already succeeded. Examples include sending or publishing, deployments, purchases, data migrations, account changes, and destructive operations. Follow the applicable authorization and confirmation rules.
7. If the prior attempt's outcome cannot be established and retrying could cause harm or duplicate an external effect, stop that operation and request only the specific decision or evidence needed. Continue independent, safe work.

Never mark a step complete solely because an agent said it was complete. Verify the resulting state.

## 4. Resume Execution at the Correct Point

After reconstructing and validating the checkpoint:

1. State briefly which checkpoint is verified as the latest complete one and what remains.
2. Continue with the first incomplete requirement immediately. Do not restart completed work.
3. Follow the original task's specified sequence. If no sequence was specified, use the safest dependency order.
4. Apply the project's required skills, tools, conventions, quality gates, and documentation rules.
5. Treat user-approved requirements as binding. Do not ask again for decisions already made or authorization already granted.
6. Ask a concise question only when a genuinely unresolved issue blocks correct execution or when applicable rules require user approval. Continue all independent work that does not depend on the answer.
7. Do not stop after producing a plan, analysis, partial implementation, or interim report when execution is authorized and feasible.

## 5. Maintain Continuity Across Further Interruptions

Work in reviewable increments. After each meaningful unit:

1. Record what changed and where.
2. Record the exact verification performed and its result.
3. Update the task checklist or durable checkpoint, if the project provides one.
4. Identify the next smallest incomplete step.
5. Preserve relevant decisions, constraints, paths, identifiers, and known risks in a concise continuation note that another session can use.

If another interruption appears likely, finish the current safe atomic step, save the verified checkpoint, and report the precise continuation point. Never describe unfinished work as complete.

## 6. Verify the Original Acceptance Criteria

When implementation appears finished:

1. Re-read the original request and the requirement checklist.
2. Verify every deliverable and acceptance criterion against the current artifacts.
3. Run the required tests, checks, builds, previews, or domain-specific validation. Use meaningful checks that establish the requested behavior; do not substitute a superficial check.
4. Review the final diff or output for unintended changes, omissions, regressions, duplication, and consistency with project rules.
5. Report each failed, unavailable, or skipped check explicitly, with its reason and impact.
6. Do not claim success, completion, or passing verification without direct evidence.

If a check fails, diagnose and resolve the failure when safe and within scope, then rerun the relevant check.

## 7. Final Status Report

Provide a concise, evidence-based report containing:

- the original task outcome and deliverables completed;
- the verified checkpoint from which work resumed;
- the principal changes made;
- the checks performed and their actual results;
- any remaining incomplete item, blocker, limitation, or required user decision;
- the exact next action if the task is not fully complete.

Do not hide uncertainty, present attempted work as completed work, or imply that an external action succeeded without confirmation.

## Mandatory Execution Rule

Continue from the **latest verified completed checkpoint**, not from the latest attempted or in-progress step. Preserve all valid completed work, resume at the first unmet requirement, and carry the original assignment through its acceptance checks and final report.