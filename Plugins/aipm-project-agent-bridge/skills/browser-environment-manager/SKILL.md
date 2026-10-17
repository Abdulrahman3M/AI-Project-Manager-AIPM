---
name: browser-environment-manager
description: Create, launch, diagnose, maintain, repair, and verify isolated Windows browser environments for AI agents. Use for dedicated Microsoft Edge or Chrome profiles, CDP ports, browser screenshot workflows, MCP browser connections, avoiding personal profiles, and recovery from browser session/port issues.
---

# Browser Environment Manager

**Version:** see `VERSION`. **Platforms:** Windows PowerShell 5.1+; native management of Edge and Chrome. Firefox requires a separate WebDriver BiDi/Marionette adapter; never treat Firefox as CDP-compatible.

## Ownership and routing

The skill owns only management and verification of dedicated browser environments. The project's `project-orchestrator` routes relevant tasks here. Use `skill-creator` for creating the skill, not for browser environment operations. Use `powershell-tui-app-designer` only when a graphical/terminal menu application is explicitly requested. Do not introduce a second competing browser-management system.

## Hard safety rules

1. The browser executable is shared with normal browsing; a **distinct User Data Directory** is what isolates the environment. Do not copy, select, or change a personal profile directory.
2. Never execute global process termination such as `Stop-Process -Name msedge`, `taskkill /IM msedge.exe /F`, or their Chrome equivalents. Never shut down the user's personal sessions.
3. Do not delete browser data. Reset is **archive-first**, requires explicit user consent, requires a stopped dedicated environment, and must use `-ConfirmReset`.
4. Require the listener to be loopback-only and its owning PID to match a browser process with the *exact dedicated* `--user-data-dir`. A live port alone is not sufficient evidence.
5. Never claim visual navigation, screenshots, application login state, or active subprofile (`Default`, `Profile`, `Profile 1`) verified from an HTTP CDP probe. Agent automation must inspect `edge://version` or `chrome://version` where supported; compare the actual `Profile path` against the configured User Data Directory. Visible profile labels can differ from folder names; do not hardcode them.
6. Edge on Windows may offer an OS-linked Microsoft sign-in even with a clean directory. Independent user-data storage does not disable OS single sign-on or form a security sandbox.
7. If the agent's browser tool is missing, unavailable in a cloud environment, or built in with an unchangeable browser, state that clearly. Never silently fall back to the personal default browser.
8. Avoid storing cookies, tokens, secrets, screenshots of private sites, or entire process environments in logs. Require user approval before visiting authenticated or destructive sites.

## Source of truth

The central, per-environment file is created under `%LOCALAPPDATA%\AI-Browser-Environments\<Name>\environment.json` and contains name, browser type, executable, data directory and CDP port. Profile data itself resides beneath `%LOCALAPPDATA%\AI-Browser-Profiles\<Name>`; this is not the personal Edge folder. The skill does not set an internal `--profile-directory` by default: whichever subprofile is actually active must be inspected when relevant.

All stage scripts invoke `scripts/Browser-Environment.ps1`, the sole state-changing implementation. Use absolute paths or execute from its directory. Do not regenerate configuration by copying raw strings from a chat prompt.

## Create

Prerequisite: a local Windows PowerShell session. Default is Edge, environment `AI-Agent-Browser`, port `9222` (configurable); the name is an ASCII hyphenated identifier. **Create does not adopt existing data**, and refuses a previously existing environment, profile root, or occupied port.

```powershell
& .\scripts\Browser-Environment.ps1 -Action Create -Name AI-Agent-Browser -Browser Edge -CdpPort 9222 -CreateShortcut
```

Read returned config path and verify the shortcut is desktop-scoped; startup success needs CDP verification, not merely `Start-Process`. To choose a different port/browser, specify `-CdpPort` / `-Browser Chrome`. Never launch multiple browser instances against the same User Data Directory.

## Maintain & Repair

```powershell
& .\scripts\Browser-Environment.ps1 -Action Status -Name AI-Agent-Browser
& .\scripts\Browser-Environment.ps1 -Action Repair -Name AI-Agent-Browser -CreateShortcut
& .\scripts\Browser-Environment.ps1 -Action Start -Name AI-Agent-Browser
```

Status reads configuration, inspects exact matching processes, verifies port ownership and HTTP CDP identity. Repair can rebuild the desktop shortcut and diagnose connections **without** updating the browser binary or resetting a profile. Treat browser program upgrades and profile configuration changes as different tasks. When executable path disappears, report it; updating the config requires a reviewed migration, not guessed text replacement. Consult `troubleshooting/Common-Issues.md`.

For explicit user-requested archive-first reset only:

```powershell
& .\scripts\Browser-Environment.ps1 -Action Reset -Name AI-Agent-Browser -ConfirmReset
```

Confirm from the user that the data loss/archiving is intended; keep a backup until the user verifies. Do not call Reset as a generic repair technique.

## Connect & Verify

```powershell
& .\scripts\Browser-Environment.ps1 -Action Connect -Name AI-Agent-Browser -NavigateTest
```

The command verifies configured process, localhost listener ownership, browser signature and endpoint. With `-NavigateTest`, uses the CDP discovery endpoint to create a new `https://example.com` tab, *not* an MCP screenshot. Do not misreport this as complete visual validation.

For actual interaction and screenshot: connect the **agent's own available** compatible tool (for example Chrome DevTools MCP `--browser-url=<verified-endpoint>`), inspect active profile path, navigate, interact and capture screenshot. If the browser tool is absent, report `CDP_VERIFIED / AGENT_TOOL_UNAVAILABLE / SCREENSHOT_NOT_RUN`. The user's environment URL is local to the Windows host; remote/cloud runtimes cannot assume the same `127.0.0.1` is accessible.

Read and offer `PROMPT.md` for portable agents without this Skill. Do not silently install software, change MCP settings, or impersonate working browser tools.

## Reference and testing

- `references/Browser-Compatibility.md` — Edge, Chrome, Firefox, DevTools MCP and security limits.
- `examples/Usage.md` — first creation, reuse, repairs, launch and agent integration.
- `troubleshooting/Common-Issues.md` — port mismatch, auto-sign-in, profile label mismatch and missing agent tools.
- `tests/Test-Static.py` — dependency-free structural/security regression checks; **not** a substitute for Windows PowerShell integration tests.
- `tests/Test-Windows.ps1` — non-destructive native diagnostics for an explicitly named environment.

## Completion report

Always separate: `CONFIGURED`, `BROWSER_RUNNING`, `CDP_VERIFIED`, `ACTIVE_PROFILE_VERIFIED`, `NAVIGATION_VERIFIED`, `SCREENSHOT_VERIFIED`, and `NOT_TESTED`. Identify the browser tool actually used. Never imply that a profile is isolated solely because its visible display name says AI Agent.
