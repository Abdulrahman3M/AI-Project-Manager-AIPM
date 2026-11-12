---
name: task-scope-contract
description: Maintain the mandatory AIPM task scope, evidence-based reads, bounded retries and quality contract throughout every task lifecycle event under Project Manager supervision.
---

# Task Scope Contract

Activate after Project Manager for every task interaction, including simple, active, resumed, revised, reopened, correction and regression work. Remain active with Resource Optimization. This policy records decisions; it grants no filesystem permissions and cannot intercept host actions.

## Intelligent File Scope Control

Move progressively through **Targeted Discovery** (names, manifests, symbols), **Focused Inspection** (relevant files and ranges), **Dependency Expansion** (verified import, call, configuration or test edges), and **Broad Investigation** (only when evidence shows narrower levels are insufficient). Every read needs an articulated relation to the task or its verification. Never impose an arbitrary file-count limit; a documented dependency chain may span any necessary number of files. Read permission does not authorize an edit.

## Task Scope Definition

Maintain a compact contract containing task identity, lifecycle event, scope revision, requirements, acceptance criteria, allowed read paths, authorized edit subset, excluded paths, preservation rules, evidence and required tests. Reconcile it with live state and owner changes; do not silently replace prior evidence or create an unrelated task. Respect host, project and owner permissions independently of this contract.

Use the [contract template](references/Contract-Template.md) when a written record is useful; no persistent state is created merely by invoking this policy.

## Read Tracking

Record path, reliable revision or hash, inspected ranges, reason and observation time without retaining source contents or secrets. Reuse trustworthy unchanged evidence; invalidate on change. Flag a redundant full reread, allow changed content to be rechecked, and mark identity `UNVERIFIED` when it cannot be established reliably. Resolve paths and guard traversal and symlinks where host access controls permit.

## Bounded Retry

Record the previous operation, outcome, new hypothesis or changed evidence, attempts and limit. Do not blindly repeat identical failures. Permit a bounded transient retry when its cause is recorded; escalate persistent failures. Fixing the cause may justify rerunning a required test.

## Scope Expansion

Expand only when a demonstrated task dependency or verification need justifies it. Record the cause and revise the contract. Broad investigation requires evidence that narrower approaches are insufficient, not a fixed file-count threshold. Never treat read scope as write authorization.

## Quality Contract

Map each acceptance criterion to required actual tests or direct evidence, preserving safety and existing behavior. Required checks outweigh time and token budgets. Record `PASS`, `FAIL` or `UNVERIFIED`; a blocking failure or missing required evidence prevents completion. Evidence references must be checked against actual output, not fabricated or inferred from a file's existence.

## Verification Assistance

For weaker models break work into atomic steps, state expected versus actual, preserve invariants, provide executable checks and negative cases, and stop when evidence or authority is missing. Never lower acceptance criteria to fit a budget or promise equal model quality.

## Compliance & Evidence

Keep a minimal, privacy-aware ledger of read reasons, expansions, retries, checks and observed outcomes. The optional [scope checker](scripts/scope_check.py) does not enforce host access. Its lexical edit match is not authorization; `edit_preflight` rejects Windows reserved names, short-name aliases and trailing-dot or trailing-space aliases, checks existing path metadata and returns only `PROVISIONAL_MATCH`, because a path can change before use. Its `REPORTED_PASS` result means every required result was reported as passing; it is not a verified `PASS` or permission to complete a task. Independently inspect each result and required test before recording `PASS`. Label the host capability `INSTRUCTION_ONLY` unless a real interception mechanism has been tested.
