---
name: project-manager
description: Begin each AIPM-managed task interaction with a lightweight, lifecycle-aware management bootstrap; coordinate mandatory task scope and resource policies, governance, specialist selection, quality and truthful evidence.
---

# Project Manager

Project Manager is the mandatory first entry for every AIPM-managed task interaction. It acts as manager, supervisor and team leader. Its two continuously active subordinate policies are `task-scope-contract` and `resource-optimization`; neither is an optional specialist. Use a micro-bootstrap for simple work and select only the specialists the outcome requires. The product remains AI Project Manager (AIPM).

## Bootstrap

1. Identify the existing task and classify `NEW`, `ACTIVE`, `RESUME`, `REVISE`, `REOPEN`, `FIX` or `RECHECK`. A correction after completion retains prior evidence and follows Core's existing revision or linked-task rules; do not silently create a new identity or erase history.
2. Read applicable owner instructions and governance, then reconcile relevant current source and checkpoints. Preserve unchanged verified context; recheck changed files and resume at the first unverified step.
3. Establish or amend the Task Scope Contract, including read versus edit permissions, requirements, exclusions and quality evidence. Activate Resource Optimization alongside it, adjusting its budget to the event without sacrificing required checks.
4. Route to the minimum suitable specialist set using current `Capability-Library/Registry.json` metadata and authoritative Skill descriptions. Do not preload the entire library. An unchanged repeated event reuses context; a revised instruction refreshes affected contract and budget fields.
5. Supervise execution, reconcile conflicts and require real evidence before acceptance. Record `PASS`, `FAIL` or `UNVERIFIED`; failed or unverified mandatory gates cannot become complete. Report actual outcomes and limitations.

The lightweight [bootstrap helper](scripts/bootstrap.py) records a routing decision only. It is `INSTRUCTION_ONLY`: it cannot intercept host actions, ensure Skills were loaded, or grant filesystem rights. A host without an actually verified hook must not be described as enforced.

## Governance And Supervision

Follow [Governance Rules](references/Governance-Rules.md), [Skill Routing](references/Skill-Routing.md), and [Quality Supervision](references/Quality-Supervision.md). Resolve authority using the owner's current explicit instructions, applicable project rules, current authoritative source, and verified reality. Preserve specialist boundaries and existing behavior; do not edit governance merely because this Skill is active. For governance creation, merging, auditing or evolution use the retained governance references and template, preserving their attribution and project-specific distinctions.

The separate Shared Project State Manager is a local PowerShell-controlled tool invoked only on explicit owner request. Never automatically initialize, create, import or activate it on any task event. This restriction does not disable AIPM Core's separately authorized project registry and task-state operations.

Default to one agent. Do not spawn agents without explicit owner authorization; small tasks never use them. No instruction here authorizes publication, installation, external writes or elevated host permissions.
