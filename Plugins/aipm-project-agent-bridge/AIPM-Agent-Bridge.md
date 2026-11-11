# AIPM Project Agent Bridge

## Purpose

For every AIPM-managed task event, start with `project-manager`, then keep `task-scope-contract` and `resource-optimization` active while selecting only relevant specialists. Reconcile revised and reopened work with current source and prior evidence.

## Operating Boundary

This guidance is INSTRUCTION_ONLY: the package does not enforce host invocation, install or publish itself, start a session, or grant project access. Host permissions remain authoritative. The separate Shared Project State Manager is invoked through local PowerShell only on explicit owner request; AIPM Core state remains separately permission-gated.

## Agent Workflow

1. Run the lightweight Project Manager bootstrap and read applicable project rules.
2. Establish scope and resource policies; reuse unchanged verified context.
3. Query AIPM Core for authoritative project state only where the host adapter supports it.
4. Route to the smallest relevant specialist set, verify outcomes and preserve evidence.
5. Keep unsupported host operations permission-gated and fail-closed.
