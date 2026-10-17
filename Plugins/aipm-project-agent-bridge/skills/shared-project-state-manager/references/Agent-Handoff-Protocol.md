# Agent Handoff Protocol

This reference defines a vendor-neutral handoff between any two AI agents, models, IDE assistants, or resumed sessions.

## Outgoing Agent

Before stopping: verify the last completed action; update task/phase status without falsely completing work; capture branch, HEAD, working tree, relevant files, tests, blockers, and owner decisions; write a checkpoint and handoff; state the exact next action; list work that should not be repeated; point to large reports rather than pasting them.

## Incoming Agent

Read active project governance, the manifest/current state/handoff/task/latest checkpoint/tests/blockers/decisions, then inspect Git/runtime/files directly. Confirm whether the interrupted operation actually completed. If state and reality differ, mark `STATE-DIVERGED`, reconcile, and only then continue from the first incomplete or unverified action.

## Required Handoff Fields

- task ID/title and phase/status;
- outgoing and intended incoming agent;
- exact last verified action and exact next action;
- branch/HEAD/working-tree state when Git exists;
- intentionally modified files;
- tests/checks and real outcomes;
- blockers/risks and owner decisions;
- do-not-repeat items and report/log paths.

## Interrupted Commands

A command shown in a transcript is not proof it completed. Inspect outputs and side effects. For external or irreversible operations, inspect state before retrying to avoid duplicate effects.

## Single-Writer Default

Only one agent should normally write the same task/state at a time. Parallel agents require distinct scopes and an explicit reconciliation step.
