# Browser Compatibility and Trust Boundaries

## Edge (default)

Windows executable usually under `%ProgramFiles(x86)%\Microsoft\Edge\Application\msedge.exe`; alternatives are detected. `--user-data-dir` selects a data root distinct from the personal default. `--remote-debugging-port` exposes DevTools Protocol; always prefer `--remote-debugging-address=127.0.0.1`. `edge://version` displays the actual command line and active profile path. Browser account sign-in can still be suggested or silently linked to a Windows account; creating a new data directory is **not** an OS-account firewall.

## Google Chrome

Equivalent Chromium flags, but Chrome 136+ requires a **non-default** `--user-data-dir` for the remote debugging switch to be respected. Use `chrome://version` and a Chrome-specific executable. Chrome for Testing is another automation-oriented distribution but is not silently installed by this Skill.

## Firefox

Do **not** apply Chromium CDP or Chrome DevTools MCP semantics to Firefox. Mozilla documents Marionette and WebDriver BiDi. Firefox support requires an explicit provider adapter with a separate lifecycle, dedicated profile and test suite. This version deliberately reports Firefox unsupported rather than a false success.

## CDP versus MCP

CDP is a local browser debugging protocol; an MCP server is a **tool bridge for an agent**. A successful HTTP `/json/version` probe indicates DevTools is responsive but does not mean agent tool exposure or screenshot capability exists. The Chrome DevTools MCP `--browser-url` option requests connection to an existing browser; agent configuration varies, and third-party Chromium browser compatibility should be tested.

## Security rules

The debugging endpoint grants strong browser control to any local process able to connect. Avoid sensitive accounts; never expose via firewall/NAT/public forwarding. Do not store authentication material in environment JSON or prompts. Dedicated data roots separate browser storage, not the operating-system user account or OS credentials.

## Official references

- [Microsoft Edge DevTools Protocol](https://learn.microsoft.com/en-us/microsoft-edge/devtools/protocol/)
- [Microsoft Edge and Chrome DevTools MCP](https://github.com/MicrosoftDocs/edge-developer/blob/main/microsoft-edge/web-platform/devtools-mcp-server.md)
- [Chrome DevTools MCP — existing browser](https://github.com/ChromeDevTools/chrome-devtools-mcp/blob/main/docs/advanced-usage.md)
- [Chrome remote debugging security change](https://developer.chrome.com/blog/remote-debugging-port)
- [Firefox remote protocols](https://firefox-source-docs.mozilla.org/remote/index.html)
