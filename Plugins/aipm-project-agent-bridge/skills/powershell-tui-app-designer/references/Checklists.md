# Checklists

Copy the relevant list into your working notes and tick it with evidence (command + result).

## A. Planning gate (phase 1)
- [ ] Target users and platforms written down (Windows/Linux, PS 5.1/7).
- [ ] Task list with the data each task needs and the external tools it calls.
- [ ] Selected navigation and layout are recorded; Classic Numbered remains optional.
- [ ] Out-of-scope list written (no GUI/web/database/telemetry unless required).
- [ ] Decisions needing the owner listed; none are guessed.

## B. Scaffold gate (phase 3)
- [ ] `scripts/New-TuiProject.ps1` ran; generated tests pass (`-RunTests`).
- [ ] `scripts/Test-TuiProject.ps1` reports 0 failed rules.
- [ ] Entry script `-Version` prints the version; non-interactive start exits 2.

## C. Screen gate (phase 6)
- [ ] Selected navigation is tested; description placement and icon display match preferences.
- [ ] Every question has help; every typed question has an example and validation.
- [ ] Success/Warning/Error/Info use the shared icons and roles.
- [ ] Works with `NO_COLOR=1` and with `<APP>_ICONS=ascii`; no output wider than the window.

## D. Compatibility gate (phase 8)
- [ ] No OS check outside Platform; no 7-only syntax; ASCII-only source.
- [ ] Paths built with Join-Path and used with -LiteralPath.
- [ ] Launchers: `.bat` CRLF, `.sh` LF + exec bit; run from a path with spaces.
- [ ] Tests executed on each claimed environment; UNVERIFIED items listed.
- [ ] Idle interactive resize returns an internal event without a key press; unchanged polls do not repaint.
- [ ] Menu selection/search/number state and prompt text/cursor/validation survive resize; frame shrink removes stale rows.
- [ ] Windows Terminal launch parsing and child execution are separately tested where that launcher path is used; native terminal checks are labeled separately.

## E. Release gate (phase 11)
- [ ] `VERSION`, README badge, CHANGELOG, About screen agree.
- [ ] Package built from the final commit, contents inspected, extracted into a folder with spaces, `-Version` OK, SHA-256 recorded.
- [ ] Release notes only state verified facts; known limitations listed.
- [ ] Tag and release verified to exist after publishing.

## F. Final cleanup (phase 12)
- [ ] No secrets, tokens, personal data or absolute local paths in any file.
- [ ] No temp files, logs, `dist/` content or caches in the package.
- [ ] README explains install, run, keys, exit codes, troubleshooting.

## G. Design v2
- [ ] User choices collected conversationally or explicitly delegated.
- [ ] All twenty presets selectable including Classic Numbered.
- [ ] Arrows-only omits numbers; numbers/hybrid/search tested.
- [ ] Muted/shaded explanatory rows and icon-free/no-color fallbacks are usable.
