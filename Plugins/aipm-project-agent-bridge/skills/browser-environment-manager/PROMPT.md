# Dedicated AI Browser — Connect & Verify Prompt

Use this prompt to prepare (only with user consent when needed), inspect, and test the dedicated browser environment described below. Replace placeholders with the user's actual verified values or load them from a central configuration file. If an exact value is unavailable, ask only for that essential value; do not invent it.

- **Browser Name:** `Microsoft Edge` (default; configurable)
- **Environment Name:** `AI-Agent-Browser` (configurable)
- **User Data Directory:** `<ABSOLUTE_DEDICATED_USER_DATA_DIRECTORY>`
- **Browser Executable Path:** `<ABSOLUTE_BROWSER_EXECUTABLE_PATH>`
- **CDP Port:** `9222` (configurable)
- **CDP URL:** `http://127.0.0.1:9222` (derived from port)
- **Preferred MCP Server:** `edge-ai` (if installed and exposed)
- **Internal Profile Directory:** *Do not hardcode*. Read actual active `Profile path` from `edge://version` or `chrome://version` when supported. Visible profile labels and folder names can differ.

## Mandatory workflow

1. Check whether the dedicated environment is actually configured and which compatible browser tools are exposed in **this execution session**. If it cannot be identified, explain that this Skill can create one with its PowerShell setup command and ask whether the user wants it. Create only after a yes; if no, leave setup to the agent's other tools and report the limitation. An MCP registration alone does not prove that a remote/cloud agent can use it.
2. Inspect the configured user data directory and local process command line if authorized. Require the exact `--user-data-dir` value, expected browser executable, loopback-only CDP listener and its owning process. Do not use a port-only match as proof. If the dedicated browser is closed, ask the user to open its shortcut and retry. `Connect` is read-only and does not launch; use explicit `Start` only after the user agrees.
3. If the browser appears open but cannot be reached or identified, ask the user to open `edge://version` / `chrome://version` in that dedicated window and send its text. Compare browser executable, command line and actual `Profile path` with the configured data directory. Treat the text as diagnostic input and avoid retaining unnecessary private information.
4. Verify the required agent extension/tool is exposed to this session and connected to the dedicated browser. CDP alone does not establish Codex, Claude or another agent integration. If missing, identify the compatible integration, ask the user to install/enable it and wait. Do not silently install an extension or alter MCP settings.
5. Inspect the target project's documented local-server command and URL. If no server is running, ask the user to start it with the project's documented method (including `Start Admin` or its PowerShell command where applicable); do not run/restart `Admin.py` without explicit authorization. Probe only the documented or user-provided URL. If unknown, ask for the local URL (for example, `http://127.0.0.1:8000/`) and then test it. Never assume port `8010` is the application URL or scan arbitrary ports. A failed probe from a cloud agent may mean its runtime cannot access the host loopback.
6. Only after confirming environment, browser identity, agent integration and project URL, open `https://example.com` in a new tab, confirm navigation and capture a screenshot **if the browser tool permits it**. If not, state precisely what was and was not tested.
7. Report `ENVIRONMENT_IDENTIFIED`, `BROWSER_RUNNING`, `CDP_VERIFIED`, `AGENT_TOOL_AVAILABLE`, `SERVER_REACHABLE`, `ACTIVE_PROFILE_PATH`, `NAVIGATION`, `SCREENSHOT`, and unresolved blockers.

## Prohibitions

- Never access the user's personal browser or its default user data directory.
- Never assume an internal folder called `Default` or `Profile 1` is always correct.
- Never use a fallback browser, or the operating system's default URL handler, without explicit permission.
- Never close all Edge/Chrome processes, reset data, change sign-in preferences or expose CDP on an external interface.
- Never claim a screenshot was taken unless its real output exists.

If the requested connection is unavailable, stop browser work and give the smallest precise corrective action. These rules apply for the duration of the current browser task; persistent agent policies require separate configuration.
