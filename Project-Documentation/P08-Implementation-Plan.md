# P08 PowerShell TUI Implementation Plan

## Goal And Approved Design

Build AIPM's first running PowerShell TUI in this repository. Use the approved Task Dashboard / Command Palette / Assistant Console references, with Task Dashboard as the default; hybrid arrows and stable numeric selection, Search, Help, Title Case labels, readable descriptions, semantic icons and selected shading. Preserve the P07 palette and icon maps, use the Core Engine as the only project-state source, and persist UI preferences only. The owner delegated ordinary design decisions and requested inline execution without subagents.

## Decisions And Boundaries

- Layout: Task Dashboard preset by default; all 20 neutral presets remain selectable under Settings, independently from the three AIPM modes.
- Interaction: Hybrid arrows/numbers, Enter, Esc, `/` Search, `?`/F1 Help, safe `q` exit; numbers are scoped to the visible menu.
- Icons/colors/descriptions: automatic Emoji → Symbol → ASCII fallback, theme semantic roles, shaded selected rows where supported, muted explanatory rows always visible; `NO_COLOR` remains usable.
- Host: Windows Terminal is the declared Windows default; native Console fallback is documented. PowerShell 5.1 and 7.x on Windows are targets; other runtimes are reported only when tested.
- Assistant Console is a local read-only surface; it does not claim an AI session or provider connection.
- Project/task data is read-only in P08. Unsupported agents, test counts, weights, or history are `Unknown`/`Unverified`; progress is never inferred from missing weights.
- No Universal AI ToolKit writes, external tests, install, publish, push, or P09/P10 work. Physical Windows Terminal captures are marked `UNVERIFIED` unless actually observed.

## File Map

- `Core-Engine/aipm.py`: add read-only `dashboard` and `catalog` projections; `dashboard` uses the existing Core Engine/registry, `catalog` reads the protected capability inventory without refreshing it. No parallel state writer.
- `Tests/test_p08_core_dashboard.py`: Core projection contracts, empty/malformed registry, registered projects, unreadable state, and catalog scope.
- `TUI/AI-Project-Manager/`: generated from the preserved TUI Skill template, then adapted as the AIPM application. Core modules handle platform, settings and process invocation; TUI modules own theme, input and differential rendering; App composes screens only.
- `Tests/test_p08_tui.py`: launch the actual app with in-repository fixtures under `.test-workspace`; assert modes, Core-derived state, safe unknowns, fallbacks, no-color/redirect, settings isolation and exit codes under available PowerShell editions.
- `UX-TUI/semantic-icons.json`: correct only icon code points whose fallback conflicts with the preserved WGL4/width rules; keep the provided references as illustrations.
- `README.md`, `CHANGELOG.md`, `VERSION`, app README/docs/changelog/license, and P08 report/checkpoint/handoff: document actual support, test evidence, limitations, provenance and next authorized phase.

## Architecture Gate

Dependencies point down only: `Start-AiProjectManager.ps1` parses `-Version`, `-ScriptedInput`, and the in-repo test registry override, then imports modules and restores the terminal; `Core/App.psm1` composes view models/screens and calls Core; `Core/AipmClient.psm1` invokes the Python CLI with argument arrays and timeouts; `Core/Platform.psm1`, `Settings.psm1`, `Log.psm1`, and `Process.psm1` own OS facts, UI-only per-user settings, safe logs, and external processes; `TUI/Theme.psm1`, `Input.psm1`, and `Renderer.psm1` exclusively own glyphs/colors, keys, and frame writes. `Menu.psm1`, `Dialog.psm1`, and `Prompt.psm1` consume those owners. Pure progress/status/formatting logic lives in the tested Core/App boundary; screen code never calculates unverified progress or writes state.

Declared platforms: Windows PowerShell 5.1 and PowerShell 7.x on Windows; PowerShell 7.x on Linux is declared only after CI or local Linux execution. This turn can run the first two on Windows; physical Windows Terminal/legacy-console checks require an interactive host.

The Skill's module catalog is retained, with one scoped adaptation: an `AipmClient` module is added so every project/capability read crosses AIPM's existing CLI/Core boundary; it owns no project state and adds no write command. AIPM visual roles and glyphs are loaded by Theme from `UX-TUI/theme.json` and `semantic-icons.json` instead of copying those values into screens. TUI settings are independent from Core state. The Assistant Console is guidance only, not an AI transport.

## Tasks And Verification

1. **Core Dashboard Projection** — Write and run failing `dashboard` CLI tests first. Implement a read-only Core projection returning each registered project's verified state, isolated per-project failures, and an explicit unregistered-registry result. Run `python -m unittest Tests.test_p08_core_dashboard -v`.
2. **Generated App Scaffold** — Generate only into the new `TUI/AI-Project-Manager/` folder with Task Dashboard/Hybrid/Auto/Panel defaults, run generated unit tests, `Test-TuiProject.ps1`, `-Version`, and redirected non-scripted refusal. Keep the existing Git repository; do not initialize a nested repository.
3. **AIPM Modes And Renderer** — Add failing tests before behavior changes. Integrate the app through Core's read-only dashboard command; implement the three modes, portfolio/detail, safe task/test/agent/timeline data, Skills & Plugins, Settings and Help; responsive layouts, choice explanations, full preset catalog, central semantic Theme/Input/Renderer, differential styled rows, plain redirected output, settings override under `.test-workspace`, and safe failure restoration. Run app tests under each installed PowerShell edition and `Test-TuiProject.ps1`.
4. **Docs, Package And Phase Record** — Document all workflows, architecture, command/exit contract and executed support matrix; build and inspect an in-repository ZIP, extract it under `.test-workspace` and verify `-Version` plus scripted exit. Do not tag or publish. Record real screenshots only if captured from an actual terminal; otherwise keep them `UNVERIFIED`. Run P02–P08 focused/integrated suites, capability-library validate (without refresh), Python compile, whitespace, license/Title Case/path checks; self-review the final diff.

## Review Focus

1. Missing or malformed registry must not be shown as a verified empty project or a false `0%`.
2. A corrupt project's state must not hide other valid projects; its state remains visibly `Unverified`.
3. Narrow and short terminals must retain descriptions, selection, status and reachable Help/Exit without clipping.
4. Style-only changes and removed rows must invalidate the correct output; an unchanged frame must produce zero bytes.
5. Redirected/`NO_COLOR` and a thrown screen error must avoid ANSI leaks and restore cursor/terminal state.

## Phase 0 Baseline

- Branch/HEAD: `main` / `cd87887310248a607265a9d832ffd7d08f791e54`; worktree was clean at start.
- Environment probe: Windows 11 build 26200, PowerShell 7.6.5; Windows PowerShell 5.1 executable is installed; WT launcher exists, but this run is redirected/non-interactive (`TERM=dumb`, `NO_COLOR`, no `WT_SESSION`).
- P07 focused suite: 16/16 passed. Integrated P02–P07: default run 97/100 because the three known junction fixtures report `Access is denied`; the previously authorized, repository-scoped junction run passed 100/100.
- Source TUI package and project rules were inspected; no existing AIPM renderer was present. The original designer Skill and P07 contracts remain unchanged.
