---
name: browser-environment-manager
description: Prepare with user consent, launch with approval, diagnose, maintain, and verify isolated Windows browser environments for AI agents. Use to discover or create dedicated Edge/Chrome profiles, recover closed browsers and CDP sessions, verify agent browser extensions/tools, and check access to project-local web servers before browser workflows.
---

# Browser Environment Manager

**Version:** see `VERSION`. **Platforms:** Windows PowerShell 5.1+; native management of Edge and Chrome. Firefox requires a separate WebDriver BiDi/Marionette adapter; never treat Firefox as CDP-compatible.

## Ownership and routing

The skill owns only management and verification of dedicated browser environments. The project's `project-manager` routes relevant tasks here. Use `skill-creator` for creating the skill, not for browser environment operations. Use `powershell-tui-app-designer` only when a graphical/terminal menu application is explicitly requested. Do not introduce a second competing browser-management system.

## Hard safety rules

1. The browser executable is shared with normal browsing; a **distinct User Data Directory** is what isolates the environment. Do not copy, select, or change a personal profile directory.
2. Never execute global process termination such as `Stop-Process -Name msedge`, `taskkill /IM msedge.exe /F`, or their Chrome equivalents. Never shut down the user's personal sessions.
3. Do not delete browser data. Reset is **archive-first**, requires explicit user consent, requires a stopped dedicated environment, and must use `-ConfirmReset`.
4. Require the listener to be loopback-only and its owning PID to match a browser process with the *exact dedicated* `--user-data-dir`. A live port alone is not sufficient evidence.
5. Never claim visual navigation, screenshots, application login state, or active subprofile (`Default`, `Profile`, `Profile 1`) verified from an HTTP CDP probe. Agent automation must inspect `edge://version` or `chrome://version` where supported; compare the actual `Profile path` against the configured User Data Directory. Visible profile labels can differ from folder names; do not hardcode them.
6. Edge on Windows may offer an OS-linked Microsoft sign-in even with a clean directory. Independent user-data storage does not disable OS single sign-on or form a security sandbox.
7. If the agent's browser tool is missing, unavailable in a cloud environment, or built in with an unchangeable browser, state that clearly. Never silently fall back to the personal default browser.
8. Avoid storing cookies, tokens, secrets, screenshots of private sites, or entire process environments in logs. Require user approval before visiting authenticated or destructive sites.

## Source of truth and authorized reconnect

The central, per-environment file is created under `%LOCALAPPDATA%\AI-Browser-Environments\<Name>\environment.json` and contains name, browser type, executable, data directory and CDP port. Profile data itself resides beneath `%LOCALAPPDATA%\AI-Browser-Profiles\<Name>`; this is not the personal Edge folder. The skill does not set an internal `--profile-directory` by default: whichever subprofile is actually active must be inspected when relevant.

All stage scripts invoke `scripts/Browser-Environment.ps1`, the sole state-changing implementation. Use absolute paths or execute from its directory. Do not regenerate configuration by copying raw strings from a chat prompt.

For the owner-authorized `AI-Agent-Browser` legacy Edge environment only, a missing manager record is registered as a reference to the existing dedicated `IB-Edge-Debug` directory. This is idempotent and never copies, moves, or resets profile contents. Any other missing environment remains unknown. `Connect` is diagnostic only: it never launches a browser. Use `Start` only after the user agrees to launch the dedicated browser, or have the user open its shortcut and retry `Connect`.

## Required Preflight Workflow

Run these gates in order whenever an agent needs a dedicated browser. Do not skip to site navigation while an earlier gate is unresolved.

1. **Discover the environment.** Check the documented manager record and actual browser tools available to this agent session. Do not infer that a configured browser exists because the Skill or an MCP name is present. For the known legacy environment, `Status` can register the approved metadata reference. If the environment cannot be identified, explain that the Skill can create an isolated Edge/Chrome profile using its PowerShell command and ask whether the user wants that. On yes, run `Create` only after checking the chosen name, browser and port; on no, leave browser setup to the agent's other available tools and report any limits. Never create or adopt a profile silently.
2. **Check browser state and identity.** Run `Status` and `Connect` against the exact environment. If its browser is stopped, ask the user to open its dedicated shortcut, then retry. Do not make `Connect` launch it. If the user prefers PowerShell launch and approves, use the explicit `Start` action. If the browser is open but CDP cannot be reached or identity is ambiguous, ask the user to open `edge://version` (or `chrome://version`) in that dedicated window and send the page's text. Use it to compare the executable, command line, profile path and configured data directory. Treat the contents as diagnostic data; redact account identifiers or other private values when feasible. Do not claim verification until process, loopback listener, port owner and browser identity agree.
3. **Check the agent integration.** Verify a compatible browser tool/extension is actually exposed to the current agent session, and if supported, inspect the dedicated browser's extension page. A CDP listener alone does not prove Codex, Claude or another agent extension is installed or connected. If the needed integration is absent, tell the user which compatible extension or tool is needed and ask them to install/enable it; wait for them before browser interaction. Never change agent MCP settings or install extensions silently. Built-in/cloud browsers that cannot attach to this profile must be reported as unavailable for this environment; do not switch to a personal browser.
4. **Check the project server.** First inspect the target project's instructions for its documented start command and URL. If no server is active, ask the user to start it using that documented method (including `Start Admin` or the project's PowerShell command where applicable). Do not infer that a page is down from one port, restart `Admin.py`, or execute the project's start command without explicit user authorization. Probe only a documented or user-provided local URL and report the exact result. If the URL/port cannot be established, ask for the local URL (for example, `http://127.0.0.1:8000/`) and then test that endpoint. Do not scan arbitrary ports or assume `8010` is the site URL.
5. **Proceed and report evidence.** Start site interaction only when the browser identity, usable agent integration and project URL are established. Distinguish `ENVIRONMENT_IDENTIFIED`, `BROWSER_RUNNING`, `CDP_VERIFIED`, `AGENT_TOOL_AVAILABLE`, `SERVER_REACHABLE`, `ACTIVE_PROFILE_VERIFIED`, `NAVIGATION_VERIFIED`, `SCREENSHOT_VERIFIED` and `NOT_TESTED`. Identify which gate is waiting on the user and never turn a failed probe into a claim that the service is stopped when the agent runtime may lack access to the host loopback.

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

Status reads configuration, inspects exact matching processes, verifies port ownership and HTTP CDP identity. `Connect` checks an already running environment and fails with `DEDICATED_BROWSER_NOT_RUNNING` when it is closed. `Start` is the explicit launch action and requires user agreement before use. Repair can rebuild the desktop shortcut and diagnose connections **without** updating the browser binary or resetting a profile. Treat browser program upgrades and profile configuration changes as different tasks. When executable path disappears, report it; updating the config requires a reviewed migration, not guessed text replacement. Consult `troubleshooting/Common-Issues.md`.

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
