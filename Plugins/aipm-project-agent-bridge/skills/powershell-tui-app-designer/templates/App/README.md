# {{AppName}}

A PowerShell terminal (TUI) application generated from the *PowerShell TUI App Designer* skill.

Run (Windows PowerShell 5.1, PowerShell 7 on Windows, PowerShell 7 on Linux/macOS):

```text
Windows:   {{AppId}}.bat            (or: powershell -NoProfile -File .\Start-{{AppId}}.ps1)
Linux:     ./{{AppId}}.sh            (or: pwsh -NoProfile -File ./Start-{{AppId}}.ps1)
Version:   Start-{{AppId}}.ps1 -Version
Demo/CI:   Start-{{AppId}}.ps1 -ScriptedInput '04{Enter}05'
Tests:     tests/Run-Tests.ps1
```

Every option is a two-digit number (`01`, `02` ...); type the number or use the arrow keys and Enter; `Esc` goes back; `Ctrl+C` quits.
Icons are chosen automatically (emoji, simple symbols or plain text); override with `{{ENVPREFIX}}_ICONS=emoji|symbol|ascii`.
Settings and the log live in the per-user data folder (`%APPDATA%\{{AppId}}` on Windows, `~/.config/{{AppId}}` on Linux; override with `{{ENVPREFIX}}_DATA_DIR`).

## Modern Design Options

The generated app ships with a configurable interactive design wizard under **Customize interface**. Choose any of 20 functional layout presets, arrow/number/hybrid/search navigation, emoji/symbol/ASCII/none icons, rich/subtle/no colors, and muted/shaded/inline/panel/off descriptions. Your selection is stored per user. The generator also accepts `-Preset`, `-Navigation`, `-IconMode`, `-ColorMode`, and `-DescriptionStyle`.
