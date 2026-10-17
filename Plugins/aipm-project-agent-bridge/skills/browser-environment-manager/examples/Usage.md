# Windows Examples

Run commands from the Skill's root in a PowerShell 5.1+ window. No administrative elevation is required.

```powershell
.\scripts\Browser-Environment.ps1 -Action Create -Name AI-Agent-Browser -Browser Edge -CdpPort 9222 -CreateShortcut
.\scripts\Browser-Environment.ps1 -Action Status -Name AI-Agent-Browser
.\scripts\Browser-Environment.ps1 -Action Start -Name AI-Agent-Browser
.\scripts\Browser-Environment.ps1 -Action Connect -Name AI-Agent-Browser -NavigateTest
.\scripts\Browser-Environment.ps1 -Action Repair -Name AI-Agent-Browser -CreateShortcut
```

Chrome, explicitly chosen:

```powershell
.\scripts\Browser-Environment.ps1 -Action Create -Name Chrome-Agent-Test -Browser Chrome -CdpPort 9223 -CreateShortcut
```

Use separate names and CDP ports per simultaneously running environment. A repeated Create request fails deliberately instead of overwriting or adopting existing data; use Start/Repair/Connect for existing environments.

For a locally installed MCP-capable agent, use an existing session bridge with arguments like:

```text
npx -y chrome-devtools-mcp@latest --browser-url=http://127.0.0.1:9222
```

This command presupposes Node/npx, local connectivity, and the agent's MCP registration. It does not modify the default operating-system browser. To see a suggested prompt, open `PROMPT.md`.

Reset after explicit informed approval:

```powershell
.\scripts\Browser-Environment.ps1 -Action Reset -Name AI-Agent-Browser -ConfirmReset
```

Reset archives the old directory, without force-ending any processes or touching the normal browser. The backup still holds private information and must be handled carefully.
