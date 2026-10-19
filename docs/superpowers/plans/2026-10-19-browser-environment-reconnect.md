# Browser Environment Reconnect Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Reliably rediscover and reconnect the owner-authorized dedicated Edge environment after restart without ever adopting a personal browser profile.

**Architecture:** Keep `Browser-Environment.ps1` as the only state-changing entry point. It recognizes one narrowly scoped legacy environment by exact name, executable, data-directory, loopback endpoint, and port; any other configuration remains under the managed root. Process/listener/CDP gates remain fail-closed.

**Tech Stack:** Windows PowerShell 5.1, Python `unittest`, AIPM Capability Library and Plugin builder.

**Spec:** `D:/Test/02 │ Assistance Projects/AI Project Manager (AIPM) │ Archive/AIPM │ Stages Completed/AIPM │ Stages Completed │ 2026.10/IMPLEMENTATION-HANDOFF_AI-Project-Manager_Browser-Environment-Manager-Automatic-Reconnect.md`

## Global Constraints

- No personal browser profile, global process termination, reset, deletion, network-bound CDP, or alternate browser fallback.
- Adopt only the owner-authorized `AI-Agent-Browser` legacy path as a metadata reference; never copy or move profile data.
- Refresh protected capability baselines only through the confirmed CLI with a reason.
- Rebuild and validate ChatGPT/Codex, Claude Code, and Google Antigravity archives after Skill changes.

## Review Focus

- A missing registry with the authorized legacy directory must create metadata only, without recreating or copying it.
- A valid port owned by another process must never be connected to or killed.
- Child Edge processes must not be mistaken for independent root browsers.
- CIM/TCP permission failures must be explicit and must not be reported as a stopped browser.
- Profile-folder labels must never be hardcoded as the active profile.

### Task 1: Discovery And Identity Gates

**Files:** Modify `01-Skills-General/browser-environment-manager/scripts/Browser-Environment.ps1`; test `tests/Test-Static.py`.

- [ ] Write and run failing structural tests for authorized legacy discovery, normalized command-line parsing, explicit permission statuses, and parent/listener identity.
- [ ] Implement narrowly authorized metadata registration, process/listener checks, bounded auto-start verification, and sanitized status output.
- [ ] Run static and Windows test harnesses.

### Task 2: User Contract And Distribution Synchronization

**Files:** Modify Skill documentation/version/changelog; regenerate bridge; refresh the registry; update project and TUI release metadata; build and validate distribution archives.

- [ ] Document automatic reconnect, safe failure statuses, and the required external-agent profile/screenshot verification boundary.
- [ ] Update Skill, platform, TUI, and generated-plugin versions/changelogs through their approved workflows.
- [ ] Validate the capability registry, generated bridge, archives, and repository/GitHub synchronization.
