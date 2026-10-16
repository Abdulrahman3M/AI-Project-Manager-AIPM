---
name: tui-intelligence
description: Design, Specify, Review, And Verify Accessible PowerShell Terminal Interfaces With Evidence-Based Progress, Readable Choice Descriptions, Semantic Color, Keyboard Navigation, Responsive Layout, And Differential Rendering.
---

# TUI Intelligence

## Purpose And Boundaries

Act as the terminal UX architect and accessibility reviewer for AIPM Intelligent TUI work. Translate the approved reference screens and contracts into a testable screen design, renderer contract, QA plan, and handoff.

This is a design Skill, not a running TUI, host bridge, ChatGPT installation, or permission grant. Do not claim that a terminal was rendered, that a plugin is installed, or that ChatGPT text can access Windows files. Keep all status and progress grounded in verified Core Engine data; use `Unknown` where evidence is absent.

## Required Sources And Routing

1. Read the approved mockup(s), the local `UX-TUI/Intelligent-TUI-Contract.md`, AIPM rules, relevant host capability matrix, and the preserved `powershell-tui-app-designer` Skill.
2. Follow that original Skill for implementation and its exact 13 phase gates. This Skill supplements its methodology; it does not replace or rewrite it.
3. Treat raster mockups as documentation references, never as terminal images. Match information hierarchy, relative emphasis, palette roles, descriptions, focus, and progress within tested terminal capabilities.
4. Use only host capabilities listed as implemented and tested. Package-format compatibility is not an installation or runtime guarantee.

## Design Procedure

1. Build a view model from verified project state. Separate present, missing, stale, and unverified values.
2. Design `Task Dashboard` as the default, with `Command Palette` and `Assistant Console` as selectable modes. Include project portfolio, active project/task, phase, blockers, tests, handoffs, and status counts only when supported by data.
3. Give every action a Title Case label and a concise, readable muted description. Keep the description visible for selected and unselected choices; use wrapping, detail rows, or paging on narrow terminals.
4. Use the approved palette and layered panel/selected backgrounds. Keep selection identifiable by a visible marker and text, even under `NO_COLOR`.
5. Specify Up/Down and appropriate Left/Right navigation, Enter, Esc, Tab where useful, stable `[1–9]` shortcuts, `/` Search, `?`/F1 Help, and safe exit. Scope numbers to the active menu and disable shortcuts during text entry.
6. Require one Renderer for output/cache, one Input layer for key events, a Theme for semantic colors/icons, and a Platform capability probe. Use ANSI in-place positioning plus style-aware differential rows. Unchanged frames write zero bytes; never clear the screen for each key.
7. Define resize/cache invalidation, stale suffix clearing, cursor restoration, redirected/NO_COLOR text output, narrow/short layouts, multi-cell glyph safety, and a tested fallback tier.
8. Calculate progress only as verified completed weight divided by a known positive total. Exclude blocked and unverified work; otherwise show `Unknown`, never an invented zero or percentage.
9. Produce the screen contract, design handoff, QA report, keyboard/test matrix, and screenshot provenance manifest. Mark interactive or visual behavior `UNVERIFIED` unless exercised on the named host and PowerShell version.

## Visual And Accessibility Invariants

- Use readable semantic roles: Background `#101923`, Panel `#172635`, Selected `#203447`, Text `#F0F5FA`, Muted `#AAB9C9`, Accent `#8ED3FF`, Success `#46C89A`, Warning `#F2B45C`, Error `#F16F7B`.
- Preserve color meaning with visible text: Passed, Failed, Blocked, and Unverified are never distinguished by hue alone.
- Use independent semantic icon and text segments with Emoji → Symbol → ASCII fallback selected by tested platform facts or explicit user preference. Keep `.ps1`/`.psm1` source ASCII-only and construct optional code points at runtime.
- Show a progress bar, verified count, and status when known and space permits. On redirected output, provide the same factual information in readable plain text with no ANSI escapes.
- Do not remove explanations, focus indicators, evidence counts, or progress merely to fit a plain one-line menu.

## Required Output

Start from the templates in `references/`: `Tui-Screen-Contract.json`, `Tui-Design-Handoff.md`, `Tui-QA-Report.md`, `Keyboard-And-Test-Matrix.md`, and `Screenshot-Manifest.json`. Keep source image provenance distinct from a real console screenshot. Add test results, exact host/PowerShell details, limitations, risks, and the next authorized action.

## Safe Completion

Do not edit imported Skills or write into managed/external project folders. Do not install or publish provider packages. Request owner input only for a genuine scope, security, or design conflict; otherwise record a bounded assumption and continue. Follow [the AIPM TUI Design Contract](references/Intelligent-TUI-Design-Contract.md).
