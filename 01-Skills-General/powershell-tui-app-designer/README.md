# PowerShell TUI App Designer

| | |
|---|---|
| **Skill name** | `powershell-tui-app-designer` (display name: PowerShell TUI App Designer) |
| **Version** | 1.2.0 |
| **Purpose** | Teach an AI agent to design, build, update, diagnose, test, package and release professional PowerShell terminal applications, including resize-safe rendering, managed input/frame lifecycle, and Windows Terminal launcher diagnostics |
| **Compatibility** | Generated apps: Windows PowerShell 5.1 and PowerShell 7.x on Windows; PowerShell 7.x on Linux/macOS. Skill scripts: same |
| **Last updated** | 2026-10-19 |

## What this is

An **executable methodology**, not an essay. `SKILL.md` gives an agent 13 ordered phases (0-12), each with steps, a gate of checkable criteria and a failure rule. The rest of the package gives it the material it needs:

```text
PowerShell TUI App Designer/
  SKILL.md              the strict procedure (start here)
  README.md  VERSION    this file; version 1.2.1
  Prompts/              reusable engineering prompts (complete frame + resize lifecycle)
  references/           architecture, resize/input lifecycle, launcher diagnosis, testing and design rules
  scripts/              generator, validators, test runner, packager, self-check
  templates/App/        a complete working scaffold (the generator copies it)
  examples/             nine small, runnable patterns (+ Shared/TinyTui.ps1)
  assets/               illustrations of the style (not needed to apply the skill)
```

## What a generated application looks like

Menu navigation chosen independently from layout (arrows, numbers, hybrid or search), optional muted or shaded descriptions, flicker-free ANSI in-place rendering with differential changed-row updates and a centralized renderer for arrow navigation, validated forms with help and examples, confirmations with the configured keyboard mode, success/warning/error notices, icons in three tiers (emoji, single-column symbols, ASCII) chosen from facts about the terminal, safe external-command execution from argument arrays, a scripted-input mode for tests and CI, launchers for Windows (`.bat`) and Linux (`.sh`), a per-user settings file and log, a unit/UI test suite, and a package script. See `assets/`.

## Quick start

```powershell
# 1. look at the machine
pwsh -File scripts/Test-TuiEnvironment.ps1
# 2. create an app from the template and run its tests
pwsh -File scripts/New-TuiProject.ps1 -Name "Disk Helper" -Path ./disk-helper -RunTests
# 3. validate the project against the rules
pwsh -File scripts/Test-TuiProject.ps1 -Path ./disk-helper
# 4. run it
pwsh -File ./disk-helper/Start-DiskHelper.ps1
# 5. check this skill package itself
pwsh -File scripts/Test-SkillPackage.ps1
```

On Windows PowerShell 5.1 use `powershell -NoProfile -File ...` instead of `pwsh`.

## Scripts

| Script | Use |
|---|---|
| `New-TuiProject.ps1` | Generate a working project from `templates/App` (placeholders, CRLF/LF, exec bit) |
| `Test-TuiProject.ps1` | Validation gate: structure, ASCII-only, syntax, forbidden constructs, launchers, version (exit 1 on any failure) |
| `Test-TuiEnvironment.ps1` | Platform / edition / terminal / encoding / suggested icon tier (read-only) |
| `Invoke-TuiTests.ps1` | Run a project's tests under every installed PowerShell edition; "NOT RUN" is never a pass |
| `New-TuiPackage.ps1` | Build `<Name>-v<VERSION>.zip` (no tests/.git/dist) |
| `Test-SkillPackage.ps1` | Self-check of this package (links, privacy, syntax, generated project, examples) |

## Installing the skill

Copy the folder into your agent's skills location (for example `.claude/skills/`). Some loaders require the folder name to equal the `name` in the `SKILL.md` front matter: rename the folder to `powershell-tui-app-designer` in that case. The folder name `PowerShell TUI App Designer` is the display name used for the distributed archive.

## Historical v1.0.0 verification (archived)

The original v1.0.0 `scripts/Test-SkillPackage.ps1` (41 checks: structure, front matter, links, privacy, syntax, a generated project with its own 54-check test suite and validator, a scripted app session, the non-interactive refusal, the package script and all eight examples) was executed with these results:

| Environment | Result |
|---|---|
| Windows PowerShell 5.1 on a Windows runner | 41 of 41 checks passed |
| PowerShell 7 on a Windows runner | 41 of 41 checks passed |
| PowerShell 7 on Linux (GitHub runner) | all checks passed |
| PowerShell 7.4 on Linux (development machine) | 41 of 41 checks passed |

Historical v1 test note: Running it on Windows PowerShell 5.1 found two real defects that were fixed before that release: the `TernaryExpressionAst` type does not exist in 5.1 (the validator now compares type names), and child scripts need `-ExecutionPolicy Bypass` under 5.1's default policy.
Not verified in the historical manual checks: the appearance of icon tiers in Windows Terminal or the classic console, and macOS. Current `assets/` contains original illustrative SVG concepts, not captured application screenshots.

## Generalized engineering principles

The Skill preserves reusable terminal engineering practices, not any previous application's domain code, menu content or visual branding. Generalized lessons are in `references/General-Terminal-Engineering-Lessons.md`.

For every new or existing TUI, the methodology now requires an audit of frame ownership and idle resize behavior. `references/Resize-And-Frame-Lifecycle-Reliability.md` gives the state machine, reusable code pattern, fault table, test cases, and manual terminal checks. `references/Windows-Terminal-Launcher-Diagnostics.md` covers evidence-led diagnosis of argument merging, including quoted trailing-backslash paths, parser reconstruction, minimal repairs, and child execution proof. The scaffold implements resize events at the shared renderer/input boundary; `examples/09-Windows-Launcher-ArgumentProbe.ps1` is a Windows-only parser repro (not a native terminal test).

## Change history

| Version | Date | Changes |
|---|---|---|
| 1.2.1 | 2026-10-20 | Reconciled the package overview and embedded version references with the managed Input/Frame lifecycle release. |
| 1.2.0 | 2026-10-19 | Added managed input/frame lifecycle guidance, structured result-path context, and stale-input regression tests. |
| 1.1.0 | 2026-10-19 | Added reusable resize/frame-lifecycle engineering, shared input/renderer implementation, regression coverage, and Windows Terminal launcher argument diagnostics and parser probe. |
| 1.0.0 | 2026-10-18 | Reset the independent Skill release line to the AIPM-owned baseline. |
| 2.0.3 | 2026-10-14 | ANSI in-place frames, differential updates, centralized rendering prompt, semantic colors, Emoji fallbacks and Title Case |
| 2.0.1 | 2026-10-10 | Documentation consistency: selectable navigation, wizard guidance, corrected release history and non-screenshot asset provenance |
| 2.0.0 | 2026-10-10 | Interactive designer, 20 presets, configurable keyboard input and visuals, and generated design wizard |
| 1.0.0 | 2026-10-04 | Initial stable methodology, project scaffold, validation scripts, examples and illustrations |

## v2 interactive design

Twenty product-neutral design profiles preserve Classic Numbered and add modern styles. Users may select arrows, numbers, hybrid or search; icons, color and muted/shaded descriptions are independent choices. The generator accepts `-Preset`, `-Navigation`, `-IconMode`, `-ColorMode` and `-DescriptionStyle`. The generated app provides a Customize interface wizard. Profiles change presentation and interaction; they do not create application-domain services.

The previously documented 41-check environment results are historical **v1 results**, not v2 verification. v2 test results must be taken from current CI evidence.

Previous v1 PNG screenshots were removed; current SVGs are labeled illustrative, not verified real terminal captures. Consult assets/README.md for provenance.

## Historical v2 functional verification

GitHub Actions cross-platform matrix exercises Windows PowerShell 5.1, PowerShell 7 on Windows, and PowerShell 7 on Linux. The v2 checker includes generated Arrows and Search variants in addition to the default scaffold: **48 checks, 0 failures** in the completed successful run [38065211728](https://github.com/Abdulrahman3M/Universal-AI-ToolKit/actions/runs/38065211728). This validates scripted application flows, not the pixel-level appearance of each preset in an interactive terminal. v2.0.3 updates the host-selection, Emoji and Title Case design guidance plus static package checks; runtime modules are unchanged. Verify the v2.0.3 package checks through the current CI run before release. macOS remains unverified.
