# TUI Design Handoff

## Status

Design Contract Ready; Runtime UI Implementation Not Included In P07.

## Design Source

- `Visual-References/Task-Dashboard-Mockup.png` — default information hierarchy and selected project card.
- `Visual-References/Command-Palette-Mockup.png` — search and action selection.
- `Visual-References/Assistant-Console-Mockup.png` — conversation mode.
- `Visual-References/Icons-Terminal-Reference.svg` — documentation-only semantic glyph illustration.

## Implementation Routing

The next authorized UI implementation must use the original `powershell-tui-app-designer` Skill and pass its exact 13 phase gates. Use this Skill's screen contract and QA matrix as added acceptance criteria; do not treat P07 as implementation or terminal evidence.

## Handoff Requirements

1. Read `Tui-Screen-Contract.json`, `Intelligent-TUI-Design-Contract.md`, AIPM Project Rules, and the original TUI designer Skill.
2. Build only from verified Core Engine data; show missing and stale values as `Unknown`.
3. Preserve Title Case actions with descriptions, selected shading and marker, keyboard shortcuts, semantic text statuses, and verified progress counts.
4. Keep source `.ps1`/`.psm1` ASCII-only; centralize Renderer, Input, Theme, icons, and Platform capability detection.
5. Add style-aware diff tests proving zero writes for unchanged frames and bounded writes for focus moves. Do not clear the full screen per key.
6. Record PowerShell edition, terminal host, dimensions, color tier, output mode, and screenshots for live acceptance. Do not claim no-flicker before those runs.

## Known Limits

The supplied PNGs are references, not console screenshots. P07 provides no actual TUI renderer, no provider installation, and no ChatGPT-to-Windows bridge. These operational items remain unverified or out of scope.
