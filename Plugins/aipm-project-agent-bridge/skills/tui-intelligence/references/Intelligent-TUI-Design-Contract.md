# Intelligent TUI Design Contract

## Reference And Status

The supplied Task Dashboard, Command Palette, and Assistant Console mockups are design references. They are not captures of a working terminal. This contract preserves their navy/cyan/mint hierarchy in cell-based layouts and requires honest recording of host limits.

## Screen Hierarchy

- Header: `AI Project Manager`, `Task Dashboard`, current project and truthful local status, and `AIPM vX.Y.Z`.
- Portfolio: project cards with icon, Title Case name, readable secondary explanation, verified progress and completed/total count.
- Detail: active project, current task/phase, blocker, agent or handoff only when reported, test badges for Passed/Failed/Unverified, and safe actions.
- Help dock: `Up/Down Navigate`, `[1–9] Shortcuts`, `Enter Open`, `Esc Back`, `/ Search`, `F1 Help` when those inputs are implemented.

At 120+ columns use a portfolio/detail split. At 80–119 columns use a compact split or stacked layout. Below 80 columns use one-column focus, wrapping and paging. Below usable dimensions show a plain resize notice; at height under 20 keep Back and Exit reachable.

## Choice, Color, And Icons

Every choice retains a readable muted description below or beside its label. The selected item uses a shaded panel plus `>` (or equivalent text marker); color alone is never the focus or status signal. Use semantic roles from `../../../UX-TUI/theme.json`. Use the central icon table in `../../../UX-TUI/semantic-icons.json`; terminal icons are text glyphs only, with a tested Symbol/ASCII fallback. PNG/SVG files remain documentation assets.

## Navigation And Modes

The default is Task Dashboard. Settings may expose Command Palette and Assistant Console with an immediate preview. Use arrows, Enter, Esc, optional Tab, stable number shortcuts, `/` Search, `?`/F1 Help, and a safe `q` exit. Numeric shortcuts apply only to the active panel and pause during text entry.

## Renderer And Truth

Only the Renderer writes console frames. Compose logical rows with style runs; use ANSI cursor positioning plus differential rendering on verified VT hosts. A style-aware unchanged frame must produce zero writes; an arrow move normally changes only the old/new focus rows. Do not call `Clear-Host`, `Console.Clear()`, or CSI `2J` for each key. Invalidate cache on resize/theme/host changes; clear shortened suffixes and restore the cursor in `finally`.

Use 24-bit color only when probed, nearest 16-color roles when available, and clear textual cues under `NO_COLOR`. Redirected output is readable line-oriented text without ANSI. Keep PowerShell source ASCII-only. Test resize, row shrink, narrow screens, multi-cell glyphs, cursor restoration, repeated keys, redirect, and no-op/differential writes.

Progress is verified completed weight divided by known positive total weight. Blocked, failed, missing-weight, and unverified work cannot count as complete. Missing data is `Unknown`, not `0%`. Agent, phase, and handoff time remain unknown unless Core provides verified values.

## Evidence Gate

Unit or synthetic tests may verify frame decisions, but they do not prove absence of physical flicker. Claim visual parity only after capturing and recording real Windows Terminal runs with PowerShell 5.1 and 7.x, host/color mode, dimensions, and input scenario. Otherwise use `UNVERIFIED`.
