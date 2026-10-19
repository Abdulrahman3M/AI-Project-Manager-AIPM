# TUI Design Rules

Use in SKILL.md phase 5 (design) and phase 6 (build). Every rule has a testable form; the template's tests already cover most of them.

## 1. Navigation is configurable

When Numbers or Hybrid navigation is selected, including with the optional Classic Numbered preset, selectable options are shown as

```text
  NN  Icon  Name
      One-line description: what it does, when to use it, what to expect.
```

* `NN` is two digits, zero-padded: `01`...`09`, `10`, `11`...`99`, `100` and beyond (never truncated).
* Arrows, numbers, hybrid and search are all allowed. Numeric labels are only shown in number/hybrid modes. Exit and Back remain accessible. `Esc` = Back; `Ctrl+C` = quit.
* In Numbers/Hybrid mode only, typing digits selects: `05` selects option 5 at once; a prefix of a longer number (`1` in a list of 12) waits for the next digit; `Enter` accepts what was typed or the highlighted item. Arrow keys move the highlight (wrap around).
* Descriptions are configurable: muted indentation, shaded indentation, inline, selected panel or off. A disabled option stays visible, dimmed, and its description line becomes the reason ("Needs the X filter, which is not in this build.").
* Confirmations use the selected navigation mode, without mandatory numeric prefixes.

## 2. Screen anatomy (top to bottom)

1. **Header** (once per screen): icon + application name + version on the main screen; icon + task title elsewhere.
2. **Context** (optional): one dim line saying what this screen is for; a "Source" panel when the screen refers to a chosen file/object.
3. **Question or list**: the prompt, then its help line (dim), then options. Typed questions add `Example: ...`.
4. **Feedback** (only when needed): a validation/error line directly above the input.
5. **Footer**: show only enabled controls: arrows where supported, Enter to select, number ranges only in Numbers/Hybrid, search hint in Search, and Esc to go back.

Redraw logical frames in place without clearing the physical screen on every key; never rely on scrollback for state. In ANSI mode use cursor-home (CSI H), write the new frame, and erase only stale trailing content (CSI J); preferably update only changed lines. Full clear (CSI 2J) is reserved for transitions or initial setup. In legacy mode use safe cursor positioning where possible and a clearly documented fallback. Never blank the screen between arrow presses. Resize is an input event: detect it while waiting without a key, then recompute the viewport-dependent menu window and redraw from the same state. See `Resize-And-Frame-Lifecycle-Reliability.md` for the shared lifecycle contract.

## 3. Message semantics (same words, same icons, same roles everywhere)

| Kind | Icon name | Role | Use for | Wording |
|---|---|---|---|---|
| Success | `Success` | Success | an action finished | past tense, say what exists now ("Saved C:\...") |
| Warning | `Warning` | Warning | allowed but risky/slow/large | say the risk and what the app does anyway |
| Error | `Error` | Error | an action failed or input is invalid | what happened + why + what the user can do next |
| Info | `Info` | Info | neutral facts | one or two sentences |

Never show a raw exception to the user; log it (see Error-Handling.md) and show a plain sentence.

## 4. Forms (typed input)

Prompt, help (what it is, allowed range/format), example, then `> ` with the typed text. Validation runs on Enter; the message appears above the input and clears on the next keystroke; the typed text is kept so the user edits instead of retyping. `Esc` cancels. Prefer choices over typing; offer `Custom...` as the LAST option of a list when free values are legitimate, with its own validated prompt and limits stated in the help.

## 5. Confirmations

Ask before: overwriting, deleting, installing/downloading, stopping a running job, leaving unsaved work. Never overwrite silently: collisions always offer `Replace it`, `Choose another name`, and `Cancel` using the configured navigation. Say exactly what will change.

## 6. Progress

Long work shows: a bar (`[#####-----] 50%`), percent, elapsed time, current stage name, and how to cancel (`Esc`, then confirm). Redirected output prints one plain line per step (no carriage returns, no escape codes). Finish with a result screen: success/failure, output path, size, and numbered next actions (`01 Open folder`, `02 Run again`, `03 Main menu`).

## 7. Help, settings, about

* **Help**: every question has a help line; there is no separate manual that the screen depends on.
* **Settings** screen: each setting is a selectable choice with optional description and shows the current value in the title; changes apply immediately and are remembered; a "Reset to defaults" option exists when there is more than one setting.
* **About**: name, version (from `VERSION`), platform, PowerShell edition, icon tier, data folder path, license line.

## 8. Layout and responsiveness

* Query the size with `Get-TerminalSize` on every redraw (users resize), and ensure an idle wait returns control when dimensions change; otherwise a redraw-on-key implementation will remain stale after resize. Normal >= 80 columns, wide >= 120, narrow < 60.
* Narrow: drop description indentation and wrap, never truncate selection labels or numbers when enabled; Short window (< 20 rows): show a window of the list around the selection and a scroll indicator (`more above/below`).
* Never print wider than the window - wrap or shorten with an ellipsis, not by clipping.

## 9. Color

Colors exist only as ROLES in Theme (`Title`, `Heading`, `Normal`, `Dim`, `Selected`, `Number`, `Key`, `Success`, `Warning`, `Error`, `Info`, `Description`). Screens call `Write-Ui -Role`. Never write `-ForegroundColor` or ANSI codes outside Theme/Renderer. `NO_COLOR` disables color; the UI must stay fully usable without it (state is never conveyed by color alone: the selected row has a `>` marker, errors have an icon and the word).

For colorful Emoji plus semantic role colors, render icons in their own styled segment, independent of selected-row backgrounds and the muted description role. Preserve Emoji/Symbol/Ascii fallbacks, NO_COLOR, text labels and non-color cues. Never remove icons or descriptions to cure flicker; repair the renderer instead.

## 10. Accessibility and copy

* Keyboard only; no mouse dependence; no timing-dependent input; no flashing.
* Consistent order of keys and wording across screens. Plain words: verbs for actions ("Convert", "Save"), no jargon without a one-line explanation.
* Screen-reader friendly output: no box-drawing as the only separator for information, no decorative repetition; icons are additional, never the only carrier of meaning (the label is always present).
* One language per UI (English by default); do not mix.

## Modern preset contract

The twenty layouts in `Modern-Presets.md` separate visuals from navigation; refer to `Interactive-Design-Wizard.md`. No layout forces numbers. Keep muted explanatory copy legible and indented; faint background shading must gracefully fall back without color. Preserve keyboard accessibility.
