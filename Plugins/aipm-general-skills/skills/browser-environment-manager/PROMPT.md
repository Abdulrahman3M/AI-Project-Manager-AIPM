# Dedicated AI Browser — Connect & Verify Prompt

You are authorized to **inspect and test only** the already configured, dedicated browser environment described below. Replace placeholders with the user's actual verified values or load them from a central configuration file. If an exact value is unavailable, ask only for that essential value; do not invent it.

- **Browser Name:** `Microsoft Edge` (default; configurable)
- **Environment Name:** `AI-Agent-Browser` (configurable)
- **User Data Directory:** `<ABSOLUTE_DEDICATED_USER_DATA_DIRECTORY>`
- **Browser Executable Path:** `<ABSOLUTE_BROWSER_EXECUTABLE_PATH>`
- **CDP Port:** `9222` (configurable)
- **CDP URL:** `http://127.0.0.1:9222` (derived from port)
- **Preferred MCP Server:** `edge-ai` (if installed and exposed)
- **Internal Profile Directory:** *Do not hardcode*. Read actual active `Profile path` from `edge://version` or `chrome://version` when supported. Visible profile labels and folder names can differ.

## Mandatory workflow

1. Check which browser tools are actually exposed **in your current execution session**. A CLI list of registered MCP servers does not prove that a remote/cloud agent can use them.
2. Inspect the configured user data directory and the local process command line if authorized. Require the exact `--user-data-dir` value, expected browser executable, loopback-only CDP listener and its owning process. Do not use a port-only match as proof.
3. Connect to the already-running dedicated browser through the configured MCP/CDP adapter. Prefer reusing the verified session; **do not launch another browser**, create a new profile, or change browser settings without permission.
4. Retrieve CDP `/json/version`, compare the browser identity and endpoint. Inspect `edge://version` / `chrome://version` via your actual browser tool when supported and confirm the active Profile path is under the dedicated user data directory. If this cannot be inspected, report `ACTIVE_PROFILE_UNVERIFIED` and do not claim verified identity.
5. Only after verifying the correct environment, open `https://example.com` in a new tab, confirm navigation and capture a screenshot **if the browser tool permits it**. If not, report precisely what was and was not tested.
6. Report `MCP_TOOL`, `PROCESS_IDENTITY`, `USER_DATA_DIRECTORY`, `CDP_ENDPOINT`, `ACTIVE_PROFILE_PATH`, `NAVIGATION`, `SCREENSHOT`, and unresolved blockers.

## Prohibitions

- Never access the user's personal browser or its default user data directory.
- Never assume an internal folder called `Default` or `Profile 1` is always correct.
- Never use a fallback browser, or the operating system's default URL handler, without explicit permission.
- Never close all Edge/Chrome processes, reset data, change sign-in preferences or expose CDP on an external interface.
- Never claim a screenshot was taken unless its real output exists.

If the requested connection is unavailable, stop browser work and give the smallest precise corrective action. These rules apply for the duration of the current browser task; persistent agent policies require separate configuration.
