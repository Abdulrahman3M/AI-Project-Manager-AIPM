---
name: powershell-tui-app-designer
description: Designs, builds, updates, diagnoses, and tests professional PowerShell terminal applications across Windows PowerShell 5.1 and PowerShell 7, including resize-aware frame lifecycle, launchers, configurable navigation, packaging, and release. Use for new or existing interactive apps, not unrelated shell scripts.
---

# PowerShell TUI App Designer (v1.1.0)

You are following an EXECUTABLE METHODOLOGY. Work through the phases IN ORDER. Each phase has: **Do** (steps), **Gate** (checks that must all pass), **If it fails**. You may not start phase N+1 until every Gate item of phase N is satisfied with evidence (a command you ran and its result). Do not skip, merge or reorder phases. Do not invent facts: inspect first.

Files you will use (relative to this skill folder):
`templates/App` (working scaffold) - `scripts/*.ps1` (generators and validators) - `examples/*.ps1` (small patterns) - `references/*.md` (rules; open the one named in each phase) - `assets/` (illustrations only) - `Prompts/Flicker-Free-PowerShell-TUI-Architecture.md` (reusable engineering prompt).

## Hard rules (apply in every phase)

1. **Configurable input.** Numbering is OPTIONAL, not mandated. Respect the user's choice of arrows, numbers, hybrid or search. Keep Classic Numbered as one selectable preset.
2. **Single owners.** Only Renderer writes to the screen, only Input reads keys, only Theme knows colors/glyphs, only Platform knows the operating system.
3. **ASCII-only source files.** Build glyphs from code points. (Windows PowerShell 5.1 reads BOM-less files as ANSI.)
4. **No `Invoke-Expression`, no shell strings from user input.** External programs run from argument arrays.
5. **Both editions, both systems.** No PowerShell-7-only syntax, no `$IsWindows` outside Platform, no hard-coded paths or separators.
6. **Never overwrite, delete, install or download without asking.** Source/input files are never modified.
7. **Honest reporting.** Results are PASS, FAIL or UNVERIFIED (could not run here, with the reason). A check that did not execute is never PASS.
8. **Do not guess.** If two valid options exist and the choice changes the product, write the options and ask the owner; otherwise pick the documented default and say so.
9. **Complete-frame and resize-aware rendering.** Every visible row (including help, validation, key hints, and editable-input context) belongs to a committed frame. While real interactive input is pending, detect width/height changes without requiring a key and return an internal Resize event; recompose from the same screen state. For interactive arrows, never call Clear-Host or ANSI 2J on every key or poll. Render in place using differential rows and clear obsolete rows centrally. Keep semantic colors, independently colored icons, Emoji/Symbol/Ascii tiers, and muted readable hints and descriptions intact; test resize and rapid navigation without blank frames. Preserve redirected plain output.
10. **Title Case UI text.** Write every static, user-visible application string in English Title Case: titles, headings, menu choices, prompts, help, status, validation, success, warning and error messages. Preserve proper nouns and acronyms; leave user-provided or dynamic content, code identifiers and source snippets unchanged.
11. **Reliability applies to new and existing apps.** For every create, extend, update, repair, or review task, audit the current frame lifecycle and idle resize behavior. Fix verified missing behavior at the shared renderer/input boundary, not one menu at a time, and preserve the app's selected navigation and active workflow state.

---


## Flicker-Free Architecture (mandatory for new interactive TUI work)

Load `Prompts/Flicker-Free-PowerShell-TUI-Architecture.md` and `references/Architecture.md` before changing renderer, menu navigation or visual styles. Implement **ANSI In-Place Rendering + Differential Updates + Centralized TUI Renderer** together when the host supports interactive VT output. A frame owns every visible row, including prompt/help/error/hints and the initial editable row. Compare text AND per-segment styling; a changed selection should normally touch only the previously and newly selected rows. Preserve semantic colors, separately colored Emoji/Symbol/ASCII icons, muted hints and descriptions, and existing numeric/keyboard conventions. Cache only committed screen frames; invalidate/reconcile on resize, layout/host/theme/icon-tier changes or explicit screen transitions. Input waits for key OR viewport change and returns a bounded internal Resize event without busy-spinning; the screen recomposes while preserving selection, typed text, and workflow state. Avoid per-arrow/poll `Clear-Host` or ANSI CSI 2J; use a documented legacy cursor/padding fallback and readable redirected output. Restore cursor and alternate screen in `finally`. Run differential-row, stable-frame, shrink, idle-resize, stale-prompt, accessibility, scripted and real-terminal tests. Do not claim visually verified flicker-free output without an interactive terminal test. See `references/Resize-And-Frame-Lifecycle-Reliability.md`.

## Phase 0 - Inspect the environment and the request

**Do**
1. Run `scripts/Test-TuiEnvironment.ps1` (add `-Json` if you need to parse). Record platform, PowerShell version/edition, interactive or redirected, terminal facts, suggested icon tier.
2. List which of `pwsh` (7.x) and `powershell` (5.1) exist. Decide which you can execute tests with; everything else will be UNVERIFIED locally and needs CI or a human.
3. If a project folder already exists: read its README/AGENTS/rules files, folder layout, `VERSION`, tests, launchers. Reuse what exists; do not create duplicates of modules that already do the job.
4. For new and existing apps alike, record renderer/input ownership, committed-frame boundaries, direct screen writes, blocking key waits, resize behavior, and prompt/input state preservation. Read `references/Resize-And-Frame-Lifecycle-Reliability.md` before changing those areas.
5. Write down the request in your own words: users, tasks, platforms, external tools, constraints.

**Gate**
- [ ] Environment facts recorded. - [ ] Executable editions listed. - [ ] Existing rules/structure read (or "greenfield" stated). - [ ] Request restated in <= 10 lines.

**If it fails**: stop and report what is unknown; do not proceed on assumptions about the platform.

## Phase 1 - Plan before code

Open `references/Checklists.md` (A) and `references/Architecture.md`.

**Do**
1. Before planning, follow `references/Interactive-Design-Wizard.md` to gather only unknown design preferences. Offer the twenty designs from `references/Modern-Presets.md` and `references/Design-Preview-Gallery.md`; skip questions the user has answered.
2. Define the TASKS (each = one workflow: goal, inputs, outputs, external tools).
3. Draft the menu in the selected interaction mode; icons and descriptions are customizable, and Exit stays accessible. Record the selected window host; default to Windows Terminal on Windows if the owner skips or omits the question.
4. For each task list its questions (prompt, help, example, validation, default, choices) as data (see Architecture section 5).
5. List dependencies (external programs, files, network) and what happens when each is missing.
6. List what is OUT of scope.
7. Choose names: app display name, `AppId` (letters, digits, hyphens), environment prefix (UPPER_SNAKE).

**Gate**
- [ ] Preset/navigation/icon/color/description/window-host preferences recorded or explicitly delegated; Windows Terminal is the Windows default. - [ ] Menu draft matches the chosen mode. - [ ] Questions listed as data for every task. - [ ] Dependency table with a "missing" behavior per row. - [ ] Out-of-scope list. - [ ] Names chosen.

**If it fails**: finish the plan first. Code written before this gate is discarded if it conflicts.

## Phase 2 - Decide the architecture

Open `references/Architecture.md`, `references/Cross-Platform-Compatibility.md`, and `Prompts/Flicker-Free-PowerShell-TUI-Architecture.md`.

**Do**
1. Adopt the layering and module catalogue unchanged unless a rule forces a deviation; write each deviation and its reason in a `docs/Architecture.md` of the new project.
2. Decide which logic is pure (goes in Core, unit-testable) and which is screen code (TUI).
3. Decide platform support matrix (Windows PS 5.1, Windows PS 7, Linux PS 7) and write it in the README plan.
4. Decide the per-user data folder name and the persistent settings (keep them few).

**Gate**
- [ ] Module list with one responsibility each. - [ ] Support matrix written. - [ ] Pure/screen split stated for each task.

## Phase 3 - Scaffold

**Do**
1. `pwsh -File scripts/New-TuiProject.ps1 -Name "<Display Name>" -Path <folder> -RunTests` (or `powershell -File` on Windows PowerShell).
2. Run `scripts/Test-TuiProject.ps1 -Path <folder>`.
3. Start the generated app with `-Version`; test a scripted exit using keys suited to the selected navigation mode (the default Hybrid starter accepts `-ScriptedInput '05'`).
4. Configure the Windows launcher for the selected host: use Windows Terminal when selected (including the default) and a standalone Console window only when selected. Check for Windows Terminal before launch; if unavailable, explain the fallback to the native Console host. Preserve native terminal behavior on non-Windows systems.
5. Initialize version control; commit the scaffold as a separate first commit.

**Gate**
- [ ] Generator printed "Created". - [ ] Generated tests: 0 FAIL. - [ ] Test-TuiProject: "0 failed". - [ ] `-Version` prints the version. - [ ] Non-interactive start without `-ScriptedInput` exits 2. - [ ] Windows launch behavior matches the selected host, with the documented unavailable-host fallback.

**If it fails**: do NOT edit around the failure. Read the failing rule/test, fix the cause in the generated project or report a skill defect.

## Phase 4 - Platform layer

Open `references/Cross-Platform-Compatibility.md`.

**Do**
1. Keep `Core/Platform.psm1`; add only OS facts you need (e.g., `Find-Executable` for your tools).
2. Implement dependency detection for each external tool: find, run `--version`, parse capabilities from the tool itself, show keyboard-selectable dependency choices (`Install it for me` only after explicit authorization, `I will install it myself`, `Exit`) using the chosen navigation mode.
3. Per-user settings/log folder via `Get-AppDataDirectory`; tests override it with `<PREFIX>_DATA_DIR`.
4. Launchers: keep the generated `.bat` (CRLF) and `.sh` (LF, executable); change only names/arguments. If Windows Terminal launch behavior is designed, reported broken, or changed, read `references/Windows-Terminal-Launcher-Diagnostics.md`; prove argument parsing and child execution rather than trusting a displayed command string.

**Gate**
- [ ] No OS check outside Platform (`Test-TuiProject` C5 passes). - [ ] Each dependency has a tested "present", "missing", "broken" path. - [ ] Launchers start the app from a folder with spaces.

## Phase 5 - Design the UI system

Open `references/TUI-Design-Rules.md` and `references/Unicode-and-Emoji-Handling.md`.

**Do**
1. Add icons your screens need to `Get-IconTable` with ALL THREE forms (Emoji, Symbol from WGL4, Ascii). Support Emoji in Windows Terminal when the selected font renders them; retain symbol and ASCII fallbacks.
2. Define success/warning/error/info wording patterns (what + why + next).
3. Design each screen on paper: header, context, question, options, footer; typed questions with help + example + validation.
4. Decide the first-run icon question (offer emoji once in unrecognized Windows consoles, remember the answer) and the Settings entry.

**Gate**
- [ ] Every enabled icon has 3 fallback forms; Windows Terminal Emoji rendering is supported with symbol and ASCII fallbacks.
- [ ] Static user-facing strings follow English Title Case. - [ ] Every screen documented with selected navigation and contextual feedback. - [ ] Every typed question has help, example, validator.

## Phase 6 - Build

Open `references/Coding-Conventions.md`. Build ONE task at a time, smallest first.

**Do** (repeat per task)
1. For both a new app and every change to an existing app, audit the shared frame/input lifecycle against `references/Resize-And-Frame-Lifecycle-Reliability.md`; record gaps before code.
2. Write the pure functions (Core) and their unit tests FIRST.
3. Write the screen code using only `Show-Menu`, `Show-Confirm`, `Show-Notice`, `Read-ValidatedInput` and Renderer roles. Every interactive screen passes the last committed viewport to the central resize-aware input wait.
4. Run external programs only through `Invoke-External` with an argument array; apply a timeout; handle `Started=$false`.
5. Add the task to the main menu with its description.
6. Run the unit tests and `Test-TuiProject` after EVERY task.

**Gate (per task)**
- [ ] New functions have tests (PASS). - [ ] `Test-TuiProject`: 0 failed. - [ ] Screen driven through `-ScriptedInput` end to end without error. - [ ] Selection labels, help and tests match the chosen interaction mode.
- [ ] A Resize event recomposes the same screen without changing selection, query, partial number, typed text, or workflow state.

**If it fails**: fix before starting the next task. Never accumulate failing tasks.

## Phase 7 - Errors, logging, cancellation

Open `references/Error-Handling.md`.

**Do**
1. Classify each failure mode (expected / environmental / unexpected / cancellation) and give each a mechanism.
2. Add messages in the what + why + next form; add "Show technical details" where raw output helps.
3. Make long tasks cancellable (`Esc` then confirm); kill child processes on cancel and in `finally`.
4. Log unexpected errors and environmental failures; mask secrets everywhere.
5. Verify terminal restoration after a forced failure.

**Gate**
- [ ] A forced failure exits 1, restores the terminal, prints the message after leaving the alternate screen. - [ ] Missing-dependency path exits/returns with the documented code. - [ ] No raw exception text is shown to users.

## Phase 8 - Test on every claimed environment

Open `references/Testing-Strategy.md`.

**Do**
1. Run `scripts/Invoke-TuiTests.ps1 -Path <folder>` (runs every installed edition; reports "NOT RUN" for missing ones).
2. Add static, flow, process-smoke and launcher tests for everything you built. Assert idle resize delivery, stable polls without redraw, frame growth/shrink, stale prompt removal, and state preservation during resize.
3. Set up CI for the claimed matrix (copy the workflow in Testing-Strategy section 3) and read its results; a platform without a run is UNVERIFIED.
4. When something fails in one environment only, follow Testing-Strategy section 4 (isolate, prove, fix the root cause, regression test).

**Gate**
- [ ] 0 FAIL on every environment you claim. - [ ] Every UNVERIFIED item listed with reason and the human steps to verify. - [ ] No test was skipped or loosened to pass.
- [ ] Windows Terminal resizing is checked with no key press; prompt resize and later screen transition are checked separately. Native visual checks are not inferred from scripted tests.

## Phase 9 - Documentation

**Do**
1. README: purpose, requirements per platform, install, run (`.bat`/`.sh`), keys, exit codes, troubleshooting, license, support matrix with what was verified.
2. `docs/Workflows.md` (every task, every question), `docs/Architecture.md`, `docs/Testing.md`.
3. Actual screenshots must come from the REAL running app with capture provenance. Original illustrative design mockups are allowed only if clearly labeled as illustrations, never as verified screenshots.
4. In-app help is the screen's help line + example; the docs do not replace it.

**Gate**
- [ ] A new user can install and run from the README alone. - [ ] Every claim in the docs is backed by a test or a stated manual check. - [ ] Links resolve.

## Phase 10 - Versioning and changelog

Open `references/Packaging-and-Release.md` sections 1-2.

**Do**
1. `VERSION` = Semantic Version. Start at `0.1.0` unless the owner states otherwise; `1.0.0` only when the criteria in section 1 are met.
2. Keep `CHANGELOG.md` with `[Unreleased]`; add user-relevant entries as you go.
3. Show the version in the header/About and `-Version`.

**Gate**
- [ ] VERSION, README badge, About screen and CHANGELOG agree (a test checks).

## Phase 11 - Package and release

Open `references/Packaging-and-Release.md` sections 3-6 and `references/Checklists.md` (E).

**Do**
1. Build the package with `scripts/New-TuiPackage.ps1` from the final merged commit.
2. Inspect contents; extract into a folder with spaces; run `-Version` and a scripted start; record SHA-256.
3. Write release notes with verified facts only (features, requirements, quick start, known limitations).
4. Tag `vX.Y.Z` and publish the release (through the project's allowed mechanism); then verify the tag, the release page and the asset checksum exist.

**Gate**
- [ ] Package verified. - [ ] Tag and release verified to exist. - [ ] Notes contain only verified claims.

## Phase 12 - Final cleanup and report

Open `references/Checklists.md` (F).

**Do**
1. Remove temp files, logs, caches; search for secrets, tokens, personal data and absolute local paths.
2. Run `Test-TuiProject` and the full tests one last time on the final commit.
3. Write the final report: what was built, per-environment PASS/FAIL/UNVERIFIED counts, run ids/commits, UNVERIFIED items with human steps, known limitations, release links.

**Gate**
- [ ] No secrets/paths. - [ ] Final test numbers recorded per environment. - [ ] Report lists every UNVERIFIED item. Status is COMPLETE only if every requirement is verified; otherwise PARTIALLY COMPLETE with the exact remainder.

---

## Conflict rules

- A project's own rules files (AGENTS.md, CONTRIBUTING, owner instructions) override this skill; say which rule you followed.
- If two skill rules conflict, the one in "Hard rules" wins.
- If a rule cannot be satisfied on the platform (for example a glyph that the terminal cannot draw), use the next fallback tier; never drop the option or its description.

## Things you must NOT do

- Do not write colors, glyphs or `$IsWindows` outside Theme/Renderer/Platform.
- Do not use undocumented keyboard shortcuts, `Read-Host` in modules, `Invoke-Expression`, or non-ASCII source.
- Do not report PASS for unexecuted tests, hide failing tests, or loosen assertions to get green.
- Do not publish, install, download or delete without the explicit approval the project rules require.
- Do not copy the reference application's domain code; copy only the principles.

## Interactive modern design policy

Numbers are never required unless selected. Classic Numbered is preserved as an option. Select preset, navigation (arrows/numbers/hybrid/search), icons (emoji/symbol/ascii/none/auto), colors (full/subtle/none/auto), description appearance (muted/shaded/inline/panel/off), window host and other layout preferences via `references/Interactive-Design-Wizard.md`. On Windows, Windows Terminal is the default when host selection is skipped, unanswered or absent. Use the standalone Console window only when selected. Provide Windows Terminal Emoji support with symbol and ASCII fallbacks, and write all static user-visible application strings in English Title Case. Give the user a clear textual preview, or respect stated defaults without extra questions. See `references/Modern-Presets.md` and `references/Design-Preview-Gallery.md`. Generator flags: `-Preset`, `-Navigation`, `-IconMode`, `-ColorMode`, `-DescriptionStyle`. The generated sample application has a Customize interface wizard. Do not claim that selecting a visual preset automatically implements unrelated backend features like AI chat, file management or analytics. Never copy original product branding or domain logic.
