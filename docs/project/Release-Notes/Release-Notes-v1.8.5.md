# AIPM v1.8.5 Release Notes

## Browser Environment Preflight And Recovery

- **Environment discovery:** Added a consent gate before creating a dedicated Edge/Chrome profile when no configured environment can be identified.
- **Closed browser recovery:** `Connect` now reports that the dedicated browser is closed and waits for the user to open it; the explicit `Start` action remains available after agreement.
- **Identity diagnostics:** Added `edge://version` / `chrome://version` guidance for cases where the browser is open but its process, profile, listener or CDP identity cannot be verified.
- **Agent integration:** Requires the agent to verify that a compatible browser extension/tool is exposed and asks the user to add it when missing.
- **Local server gate:** Requires project-documented startup instructions or a user-provided URL, supports documented `Start Admin` / PowerShell workflows, and does not restart `Admin.py` automatically or assume a fixed port.
- **Orchestration and documentation:** Updated the `project-orchestrator` catalog to `browser-environment-manager` `1.1.2` (`project-orchestrator` `1.0.8`) and refreshed the General Skills index.

## Versions And Local Distributions

- Platform and TUI versions are synchronized at `1.8.5`; TUI runtime behavior did not change.
- The Browser Environment Manager Skill is `1.1.2`; the Project Agent Bridge is `1.2.3`.
- ChatGPT/Codex, Claude Code, and Google Antigravity packages are rebuilt and locally validated; packages remain uninstalled and unpublished.
- This is an unpublished repository update. No GitHub push, tag, or Release was created.
