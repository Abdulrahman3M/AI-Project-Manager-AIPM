# Worked Examples

These twenty scenarios teach the expected Shared Project State patterns across agent/model switches, limits, crashes, verification failures, state divergence, temporary/protected files, permissions, non-Git projects, monorepos, and final closure.

## Index

1. [01-Claude-To-Codex-Handoff.md](01-Claude-To-Codex-Handoff.md) — Claude Code reaches its session limit after finishing P02; Codex must continue P03.
2. [02-Codex-To-Claude-Handoff.md](02-Codex-To-Claude-Handoff.md) — Codex completes a refactor phase and hands documentation/verification back to Claude Code.
3. [03-Session-Limit-During-Tests.md](03-Session-Limit-During-Tests.md) — An agent is cut off while a long test command is running.
4. [04-Crash-Mid-File-Write.md](04-Crash-Mid-File-Write.md) — The editor/agent crashes while rewriting a configuration file.
5. [05-Locked-Temporary-Directory.md](05-Locked-Temporary-Directory.md) — A task-created temp directory cannot be moved because a watcher still has a handle open.
6. [06-Read-Only-Generated-Files.md](06-Read-Only-Generated-Files.md) — Generated task artifacts were made read-only and cleanup cannot proceed.
7. [07-Windows-Acl-Access-Denied.md](07-Windows-Acl-Access-Denied.md) — A Windows temp folder has an ACL that blocks the current user despite being project-owned.
8. [08-Quarantine-And-Restore.md](08-Quarantine-And-Restore.md) — A folder is suspected disposable but the agent wants a reversible cleanup path.
9. [09-State-Divergence-After-Manual-Edit.md](09-State-Divergence-After-Manual-Edit.md) — The user manually edits files after the last agent handoff.
10. [10-Uncommitted-Unrelated-Changes.md](10-Uncommitted-Unrelated-Changes.md) — The working tree contains unrelated user changes before the task begins.
11. [11-Multi-Phase-Node-Project.md](11-Multi-Phase-Node-Project.md) — A Node application feature is split into schema, service, UI, and regression phases.
12. [12-Multi-Phase-Python-Project.md](12-Multi-Phase-Python-Project.md) — A Python project spans model, API, tests, and migration phases.
13. [13-PowerShell-Project.md](13-PowerShell-Project.md) — A Windows PowerShell utility is being modified across several sessions.
14. [14-No-Git-Project.md](14-No-Git-Project.md) — The project is a file-based folder with no Git repository.
15. [15-Monorepo-Task.md](15-Monorepo-Task.md) — One task changes only package A in a large monorepo.
16. [16-Failed-Verification-Gate.md](16-Failed-Verification-Gate.md) — Implementation is done but a blocking focused test fails.
17. [17-Blocked-External-Dependency.md](17-Blocked-External-Dependency.md) — A required external service is unavailable after all independent local work is complete.
18. [18-Parallel-Agent-Conflict.md](18-Parallel-Agent-Conflict.md) — Two agents accidentally modify the same state/source file concurrently.
19. [19-Required-Root-Tool-Folder.md](19-Required-Root-Tool-Folder.md) — A tool requires `.vscode` or `.claude` at the project root.
20. [20-Final-Closure-And-Retention.md](20-Final-Closure-And-Retention.md) — All phases pass and the task is ready to close.

## Reading Strategy

Use the nearest one or two examples as structural guidance. Do not copy task IDs, paths, test results, branch names, permissions, or completion states into a real project without verifying them.

## Interpretation Rule

Examples are educational patterns, not proof. Active owner instructions, active project governance, authoritative project files/tests, and verified repository/runtime reality outrank these examples.
