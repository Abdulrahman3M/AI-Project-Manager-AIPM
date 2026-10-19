# Skill Selection Protocol

This protocol makes Skill routing intent-aware, evidence-based, and lightweight. The goal is to choose the right capability for the user's requested outcome—not to invoke the Orchestrator for every request or match Skills by keywords alone.

## 1. Parse the Request Before Selecting a Skill

Write a short internal task model with:

1. **Outcome:** what result does the user want?
2. **Work mode:** explain, inspect, diagnose, plan, author a handoff, implement, review, or publish?
3. **Deliverable:** what must exist at the end (answer, file, code change, handoff, release)?
4. **Recipient/use:** is the artifact for the user, the current agent, or another AI agent to execute?
5. **Constraints:** scope, platform, permissions, risk, and verification requirements.

Do not choose a Skill from a file extension, an isolated noun, or a superficial phrase match. A request to explain how to write a Markdown file is not necessarily a request to author one; a request for an `.md` handoff that another agent will implement is.

## 2. Consult the Active Catalog

- Use `Capability-Library/Registry.json` as the AIPM source of truth when it is available. In other environments, use the current installed Skill list and its authoritative descriptions.
- Ignore removed, excluded, stale, or merely historical Skills. Do not route to a Skill absent from the active catalog as if it were installed.
- Shortlist by the outcome and capability required, then read only candidate `SKILL.md` files needed to resolve ambiguity.
- Check prerequisites, platform fit, permission needs, output scope, verification method, and overlap before activation.

## 3. Deliverable-First Handoff Rule

Select `create-strict-implementation-handoff` as the **LEAD authoring Skill** when the user requests a document whose purpose is to transfer executable implementation instructions to another AI agent. Common phrasings include:

- “Create an implementation handoff/task file for another agent.”
- “Write a prompt/instructions/brief that tells an AI agent to implement, update, or fix this.”
- “Make an `.md` file the next agent can follow to perform this change.”
- “Prepare a strict execution plan/handoff; do not start the work.”

This Skill authors the handoff only. Do not implement the underlying task unless the user separately requests implementation. A generic README, project overview, meeting notes, explanation, tutorial, or reference document is **not** a handoff merely because it is Markdown or mentions an AI agent. Route those by their actual purpose. If the user's requested purpose is unclear and changes whether implementation is authorized, ask one concise clarifying question.

## 4. Candidate Ranking and Minimal Selection

For each candidate, assess:

| Criterion | Question |
|---|---|
| Outcome fit | Does the Skill directly produce or enable the requested result? |
| Trigger fit | Do its active description and instructions cover this request? |
| Scope fit | Can it do the work without taking on unrelated responsibilities? |
| Environment fit | Does it support the target OS, host, tools, and formats? |
| Safety fit | Are permissions, side effects, and approval requirements compatible? |
| Verification fit | Can the promised output be checked with available evidence? |
| Incremental value | Does it add a distinct capability not already covered? |

Choose the smallest sufficient set: one LEAD per responsibility, SUPPORT only for a distinct needed capability, and keep plausible alternatives inactive. A clear single-specialist task goes directly to that specialist. Use Project Orchestrator as LEAD only when selecting/coordination is requested or the work truly spans capabilities, phases, or supervision. Governance and shared-state Skills are foundational only when project rules, risk, or substantial continuity needs make them applicable.

## 5. Routing Examples

| User intent | Route | Boundary |
|---|---|---|
| “Write an `.md` prompt for another AI to implement this bug; don't implement it.” | `create-strict-implementation-handoff` — LEAD | Produce execution-ready handoff only; no product code changes. |
| “Create a README explaining how to install this tool.” | Route by documentation task or use native authoring | Do not invoke handoff merely because the output is Markdown. |
| “Explain how I can create a handoff.” | Answer/explain, optionally teach | The user asked for guidance, not a handoff artifact. |
| “Build a new PowerShell menu app with validated input.” | `powershell-tui-app-designer` — LEAD | Follow its full create/build/test workflow. |
| “Review this TUI's resize and typed-input lifecycle.” | `powershell-tui-app-designer` — LEAD; add `tui-intelligence` only for a distinct accessibility/interaction review | Inspect existing behavior and test; avoid unrelated redesign. |
| “Choose the right skills and coordinate a multi-phase migration.” | `project-orchestrator` — LEAD | Establish scope, roster, dependencies, and verification gates. |
| “Turn this attached PDF into reliable Markdown.” | `doc-to-md` — LEAD | Preserve provenance and report conversion uncertainty. |

If more than one Skill seems relevant, distinguish the user's deliverable from optional downstream work. Do not silently chain into work the user did not request.

## 6. No Suitable Skill: Online Discovery and Native Fallback

When the active catalog has no adequate Skill:

1. Re-check the active catalog and candidate descriptions to ensure the gap is real.
2. If web search or another trusted discovery source is available and useful, search for maintained Skills that cover the capability. Prefer primary/repository sources over reposts.
3. Evaluate capability fit, maintenance, provenance, license, security, requested permissions, platform compatibility, dependencies, and evidence of quality. Inspect the candidate instructions before recommending use.
4. Report findings and recommend a candidate. Discovery does not itself authorize downloading, installing, executing, granting access, or adding dependencies; obtain required owner/environment approval first.
5. If online search is unavailable, the base AI agent may perform the work using native capabilities only when it is competent to do so and can verify the result. Otherwise explain exactly what cannot be done and give the safest next step.
6. Do not invent a claim that a missing Skill is installed, or create a permanent Skill as an unrequested workaround. Skill creation requires an explicit request or approval.

If no safe verified route exists, mark the capability gap as UNVERIFIED/BLOCKED as appropriate rather than claiming success.

## 7. Explicit User Choice and Re-Evaluation

- If the user names a Skill, honor that choice. If a different Skill appears materially better, explain the reason and get approval before substituting or adding it.
- Re-evaluate selection only when the scope changes, evidence shows a candidate is unsuitable, or a new phase introduces a distinct capability.
- Keep a compact record of selected Skills and why when orchestration is substantial; do not create an orchestration report for trivial work unless requested.

## 8. Routing Quality Tests

When changing this protocol or its catalog:

- test exact registry/catalog slug and version parity;
- test that another-agent implementation Markdown routes to `create-strict-implementation-handoff`;
- test that generic Markdown does not automatically route there;
- test online discovery and unavailable-network/native-agent fallbacks;
- test that installation/execution remains approval-gated;
- inspect examples for false positives, removed Skill names, and claims exceeding actual platform support.
