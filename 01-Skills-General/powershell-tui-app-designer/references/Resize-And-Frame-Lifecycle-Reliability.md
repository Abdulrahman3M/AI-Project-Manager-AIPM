# Resize And Frame-Lifecycle Reliability

Use this reference for **every new, existing, updated, repaired, or reviewed interactive PowerShell TUI**. It turns two recurring user-visible failures into a central architecture and repeatable tests:

- Resizing an idle window changes the layout only after a key is pressed.
- Old prompts, typed paths, hints, or validation lines remain visible after the screen changes.

The supplied FFmpeg User Manager evidence showed both symptoms. Its reusable lesson is architectural, not application-specific: every visible row must belong to a committed frame, and the input wait must be interruptible by a viewport change.

## 1. Diagnose Before Editing

| Symptom | Immediate cause to verify | Common architectural cause |
|---|---|---|
| Layout changes only after Up/Down/Enter | Input is blocked waiting for a key while the terminal dimensions change | The wait loop cannot emit an internal resize event |
| Old input prompts or error rows survive a screen transition | Those rows were printed outside the frame that the renderer owns | Screen helpers write directly, or the frame cache never recorded the prompt/hints |
| Resize makes stale rows appear or wrap | The new frame is composed against old dimensions or old rows are not cleared | Viewport is not part of the committed-frame identity |
| Resizing clears typed text or changes selection | The resize path restarts the workflow instead of recomposing from its current state | Screen state and render lifecycle are coupled |
| CPU rises while the app is idle | The input loop polls without sleeping | Unbounded busy-wait rather than a bounded wait |
| Every key flashes a blank screen | The normal navigation path uses `Clear-Host` or CSI `2J` | Full-screen erase is incorrectly used for differential updates |

Before fixing, trace every screen write and key wait. Record which module emits each visible row, whether it is in the pending or committed frame, where width/height are read, and whether the input wait blocks. Do not assume a screenshot proves the root cause; reproduce it or make a minimal deterministic test.

## 2. Required Invariants

1. **Renderer owns all visible output.** Menus, prompts, validation, dialogs, and workflows compose text/segments; they do not write directly to the terminal.
2. **One complete logical frame per screen.** Include title, body, every option, help, examples, key hints, current validation feedback, and the initial editable-input row before committing it.
3. **Input owns keys and idle resize observation.** While a real interactive screen waits, it can return either a normalized key or an internal `Resize` event within the documented polling bound.
4. **Resize is not a user action.** Recompose the current screen with its current selection, search query, partial number, wizard step, typed text, validation state, cursor position, and cancellation semantics preserved.
5. **One central resize path.** Menus and prompts consume the same input event and renderer lifecycle. Do not add per-screen timers or independent `SizeChanged` handlers.
6. **No repaint on unchanged polls.** Compare the current viewport and committed frame; an idle poll that sees no change performs no screen write.
7. **Resize repaints in place.** Invalidate/reconcile the row cache once, repaint the new frame, and erase obsolete rows centrally. Do not blank the terminal with `Clear-Host` or CSI `2J` on each key or polling tick.
8. **Redirected and scripted runs are deterministic.** They do not inspect interactive dimensions or emit cursor-control sequences. Scripted input can inject a `Resize` event without waiting or sleeping.
9. **Restoration is unconditional.** Cursor visibility, colors, alternate screen, and Ctrl+C settings are restored in `finally` even after an exception during redraw.

## 3. Central Event And Frame Lifecycle

```text
Menu / Prompt / Dialog composes full state
  -> Renderer begins pending frame
  -> Renderer writes the complete logical frame and commits it
  -> Renderer returns the viewport snapshot for that committed frame
  -> Input waits for key OR compares live viewport with that snapshot
       key    -> normalized user event
       resize -> internal Resize event (width, height)
  -> screen keeps its state and composes again
  -> Renderer diffs rows/styles; resize invalidates once and paints in place
```

In the scaffold, `Complete-UiFrame` returns a `{ Width, Height }` snapshot. Interactive screens pass it to `Read-AppKey -SinceViewport`. `Read-AppKey` uses a bounded 100 ms wait by default (configurable in the 25-500 ms range): it checks queued keys, observes the viewport, then sleeps. It returns `Resize` when the width or height changes. The number is a latency/CPU tradeoff; do not use a zero-delay loop.

```powershell
while ($true) {
    Clear-Ui
    # Compose every visible row from the existing $state, including input and hints.
    Write-UiLine $state.Title 'Title'
    Write-UiLine ('> ' + $state.Text) 'Normal'
    Write-UiLine 'Enter Confirm   Esc Cancel' 'Dim'
    $frameViewport = Complete-UiFrame

    $event = Read-AppKey -SinceViewport $frameViewport
    switch ($event.Name) {
        'Resize' { continue } # Same state; the next pass recomputes layout.
        'Esc' { return $null }
        'Enter' { return $state.Text }
        'Char' { $state.Text += $event.Char }
        'Backspace' { if ($state.Text.Length -gt 0) { $state.Text = $state.Text.Substring(0, $state.Text.Length - 1) } }
    }
}
```

The generated `Menu.psm1` and `Prompt.psm1` are the canonical consumer examples. Keep render state local to the screen flow and pass it explicitly; a resize branch must not reset it.

## 4. Frame Ownership, Diffing, And Resize Layout

- A pending frame is not committed until every visible line has been composed. Do not print an extra help block after `Complete-UiFrame`.
- A typed-input keystroke may update the active input row, but that row, its cursor model, and surrounding prompt must be represented by the current frame. When any other screen is drawn, the next committed frame owns and removes the old rows.
- Compare the rendered row, including style segments, not just plain text. A color-only change is a change.
- A stable frame produces zero changed rows. An adjacent selection move should ordinarily touch only the old and new selected rows.
- On a width/height transition, the renderer plans a full in-place repaint for the new logical frame and clears rows that existed only in the old frame. Use cursor addressing plus clear-to-end/clear-row as appropriate. Avoid clearing the entire display first.
- Recompute layout, clipping, wrapping, and vertical pagination from the new viewport. Keep the selected item visible when fewer rows fit; do not silently remove options or force a different navigation mode.
- Do not split grapheme clusters, surrogate pairs, combining sequences, or emoji ZWJ sequences. UTF-16 `.Length` is not terminal cell width. If reliable width is unavailable, prefer a conservative layout/fallback.
- Treat very small/unavailable dimensions safely. Use an existing documented minimum-size or compact-screen branch; never allow negative widths or row indices.
- A renderer that wraps rows must model physical rows, not only logical strings, or choose a safe no-wrap/clipped mode near the terminal's right edge.

The scaffold's pure `Get-UiFramePlan` makes the important policy testable: same viewport + same styled rows -> no output; changed viewport -> repaint rows in the union of old/new frame lengths. Keep the painting implementation centralized in `Renderer.psm1`.

## 5. Input Event Pattern And Test Seams

`Read-AppKey` accepts an injectable viewport provider, key-availability provider, key reader, and waiter for deterministic tests. Production callers omit those parameters. Tests must prove event behavior with real template code, not only inspect source text.

```powershell
$probe = @{ Width = 80; Height = 24 }
$readViewport = { [pscustomobject]@{ Width = $probe.Width; Height = $probe.Height } }.GetNewClosure()
$advanceViewport = { param($Milliseconds) $probe.Width = 100 }.GetNewClosure()
$event = Read-AppKey -SinceViewport ([pscustomobject]@{ Width = 80; Height = 24 }) `
    -ViewportProvider $readViewport -KeyAvailableProvider { $false } `
    -Waiter $advanceViewport -PollIntervalMs 25
if ($event.Name -ne 'Resize' -or $event.Width -ne 100) { throw 'Resize event was not observed.' }
```

The scaffold's scripted-input token `{Resize}` is an internal test event, not a keyboard shortcut for end users. Examples such as `'{Down}{Resize}{Enter}'` verify that a menu retains selection, while `'{Resize}'` between typed characters verifies that a prompt retains its buffer.

## 6. Failure Patterns And Repairs

| Bad implementation | Why it fails | Reusable repair |
|---|---|---|
| `ReadKey($true)` is the only wait operation | The thread sleeps indefinitely until a key arrives | Poll `KeyAvailable` at a bounded interval and compare current dimensions with the last committed frame snapshot |
| Resize detection starts after reading a fresh baseline inside the wait | A resize between frame commit and wait start is missed | Pass the viewport returned by the renderer for the frame just displayed |
| Menu handles only keys and lets `Resize` fall through as a command | Selection can move or the event can be misinterpreted | Treat `Resize` as a no-op state transition followed by normal composition |
| Prompt redraws its heading, then separately uses `Write-Host`/`Read-Host` | Prompt/hints escape frame ownership and leave stale lines | Compose the prompt and input row together; use the centralized input/editor API |
| Resize handler reinitializes screen state | Search text, numeric buffer, selection, or typed path is lost | Keep UI state outside the render loop and only recompute layout |
| `Clear-Host`/CSI `2J` on every key or poll | Blank flashes and unnecessary terminal I/O | Use ANSI changed-row painting; invalidate only when the viewport or screen/layout identity changes |
| Diff cache is retained across a viewport change | Old geometry and physical wrapping become invalid | Include width/height in the frame identity and repaint once from the new frame |
| Poll loop has no sleep | CPU spins while idle | Use a short bounded wait; instrument tests to prove unchanged polls do not render |
| A screenshot or static regex is the only test | It cannot prove that resize arrived without a key or that frame state survived | Use injected dimensions and scripted event tests, then run real-terminal checks separately |

## 7. Required Automated Checks

Use observable behavior and retain existing tests. Add focused tests for:

1. Width-only and height-only changes; unchanged dimensions do not produce `Resize`.
2. `Get-UiFramePlan`: stable viewport/frame -> zero rows; style-only changes -> changed row; viewport growth/shrink -> complete old/new row reconciliation.
3. Interactive wait with an injected viewport transition and no available key -> `Resize` before a key, with new width/height attached.
4. Scripted mode remains immediate and can deliver `{Resize}` deterministically without sleeping or console access.
5. Menu resize preserves selection, pending numeric input, and search query; prompt resize preserves text including spaces and Unicode.
6. Leaving a typed prompt or validation-error screen for another screen removes old prompt/help/input/error rows from the new committed frame.
7. No redraw on unchanged idle polls; no blank-screen command on ordinary key movement or resize; obsolete rows are cleared on shrink.
8. Windows PowerShell 5.1 and PowerShell 7.x syntax/runtime compatibility, including strict mode and scripted flows.

The skill's own `scripts/Test-SkillPackage.ps1` must verify the linked reference and generated template contract. `scripts/Test-TuiProject.ps1` remains the generated-project structure/syntax gate; it does not by itself prove resize behavior.

## 8. Real-Terminal Verification

Automated tests prove event/state/render decisions, not physical paint quality. On each claimed host/runtime, manually:

1. Open a menu in Windows Terminal; resize wide -> narrow -> wide without pressing a key. Confirm layout changes within the configured polling bound and the selected item stays selected.
2. Resize during a text prompt after typing a long path with spaces and Unicode. Confirm text and cursor semantics remain usable and the prompt wraps/clips correctly.
3. Enter an invalid value, correct it, accept it, navigate away, then open another workflow. Confirm no old hints, typed text, validation rows, or duplicated screens remain.
4. Repeat rapid navigation through resize. Confirm no blank flash or accumulating rows.
5. Exercise the supported legacy console fallback; force an exception and confirm cursor/colors/alternate screen are restored.
6. Run a redirected/scripted session and confirm it has readable plain output, no cursor sequences, and no dimension polling.

Report each host as `PASS`, `FAIL`, or `UNVERIFIED` with terminal, PowerShell version, window sizes, action sequence, and evidence. Do not claim flicker-free visual success from a buffer sink or source review alone.
