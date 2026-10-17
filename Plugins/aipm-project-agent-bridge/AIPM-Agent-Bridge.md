# AIPM Project Agent Bridge

## Purpose

Use this local package to orient an AI agent to an AI Project Manager (AIPM) project. Start with the project rules, use AIPM Core as the authority for project state, and select an included Skill only when it matches the requested work.

## Operating Boundary

This package does not install itself, publish itself, start a background session, or grant access to local project files. The host must explicitly provide the project workspace and any required permissions.

## Agent Workflow

1. Read the project rules and current phase/checkpoint.
2. Query AIPM Core for authoritative project state where the host adapter supports it.
3. Select the smallest relevant included Skill and preserve project evidence.
4. Keep unsupported host operations permission-gated and fail-closed.
