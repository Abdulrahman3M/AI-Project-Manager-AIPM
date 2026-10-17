---
name: token-optimization
description: Optimize unnecessary token/context consumption across analysis, strict implementation handoff Markdown and implementation. Apply independent, lightweight support without dropping requirements, safety, tests or verification; prevent redundant reads, repeated output and unnecessary multi-agent fan-out.
---

# Token Optimization

## Role
An independent, reusable **SUPPORT** Skill, not part of brainstorming and not an alternative handoff writer or executor. Its lightweight controls should remain active across significant analysis, handoff and implementation tasks. Full loading is selective; repeatedly loading the complete Skill for trivial tasks defeats efficiency. This cannot change actual model quota accounting or guarantee any percent savings.

## Precedence
Correctness → owner-approved requirements → safety/governance → tests/evidence → architecture → context/token efficiency. Never sacrifice higher priorities to save tokens. Preserve every constraint, negative requirement, acceptance criterion, data integrity and relevant test. Do not make unmeasured claims of reduced consumption.

## Explicit owner permission for agent fan-out
Do not use multi-agent teams, spawned subagents, or parallel agent execution without explicit owner authorization, even when agents could work independently. Ask once when materially useful; otherwise stay single-agent. This does not prohibit batching independent tool calls within the same agent.

## Continuous Controls
- **Inspect selectively:** read index/manifest, authoritative candidate files and necessary ranges before expanding. Reuse unchanged, trustworthy evidence; refresh if files/state change.
- **Compact state:** maintain objectives, owner decisions, invariants, evidence refs, open issues and work status in small, lossless checkpoints. Avoid repeated full history, logs and superseded drafts.
- **Reason proportionally:** target hard unknowns and failure paths. Record candidate options, key tradeoffs and the chosen design; do not repeatedly explore ruled-out ideas.
- **Use tools deliberately:** batch independent lookups, avoid duplicate queries and repeated full-file dumps; bound retries with a new hypothesis/evidence per retry.
- **Single-agent default:** do not spawn parallel/multi-agent runs solely for speed or token savings; use them only for genuinely independent work when authorized, and account for fan-out overhead.
- **Outputs:** concise user summary, but fully complete required artifact. Replace repeated boilerplate with precise references where the downstream document stays self-contained.
- **Testing:** focus directly impacted code/tests plus any broader checks mandatory under project rules; never skip verification to save cost.
- **Claims:** report measured calls/input/output tokens or agent counts only if tools expose them; otherwise describe the optimizations applied without numerical claims.

## Stage 1 — Analysis
Use `deep-brainstorming` or other chosen analysis Skill. Prioritize verified evidence, competing causes and material alternatives; record recommendation with concise rationale. Preserve an exact requirement/evidence transfer packet, not a speculative summary.

## Stage 2 — MD Handoff
The existing `create-strict-implementation-handoff` owns creation of `IMPLEMENTATION-HANDOFF_<Project>_<Task-Name>.md`. Ensure compact **without loss**: full mandatory scope, evidence/confidence, architecture, no-change constraints, sequence, edge cases, tests and acceptance criteria. Do not implement.

## Stage 3 — Execution
The separately authorized executor reads the MD and applicable governance, scopes file edits, makes bounded changes, verifies affected workflows and records resumable milestones. Avoid identical retries, unnecessary tool rounds or repeated copying of unchanged large context. Complete required documentation and audits.

## Interoperability
The project orchestrator invokes this as a lightweight independent SUPPORT policy for substantial tasks. It can assist any Skill; do not duplicate this entire policy in other Skills. Direct owner Skill selection still governs. Local project rules supersede cost optimizations.

## Exit Check
Was each read/call/agent necessary? Was the MD complete? Were edge cases, tests and verification maintained? If token usage was not measured, state `not measured` rather than claiming savings.
