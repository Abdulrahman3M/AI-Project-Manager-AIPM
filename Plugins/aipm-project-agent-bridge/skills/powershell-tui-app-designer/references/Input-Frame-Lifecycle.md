# Managed Input And Frame Lifecycle

Use this reference when building or changing an interactive form, path prompt, wizard, retry flow, result screen, or **Run Again** workflow. It complements [Resize And Frame-Lifecycle Reliability](Resize-And-Frame-Lifecycle-Reliability.md): that reference owns viewport changes and frame diffing; this one owns the input editor's relationship to the committed frame.

## Failure Pattern

The supplied Input/Frame Lifecycle bundle documents three related observations in a Windows Terminal application:

1. A path typed beside a prompt appeared near the bottom of the terminal instead of on the prompt's input row.
2. After a successful operation, the typed path remained below the result screen.
3. On **Run Again**, the prior path remained while a new input session began elsewhere.

Treat these as a lifecycle defect to reproduce, not as a request to add `Clear-Host`. The screenshots establish the visible symptoms. The attached handoff attributes them to cursor ownership and frame-cache divergence, but unless the target application's source and tests are inspected, treat that explanation as a diagnostic hypothesis—not independently verified implementation evidence.

## Two Independent Failure Conditions

| Condition | What happens | Evidence to inspect |
|---|---|---|
| **Cursor is not re-established for the active editor** | Frame painting, clearing, wrapping, or a prior screen leaves the physical cursor elsewhere; a line editor writes at that incidental position. | Record the cursor row/column after frame commit and immediately before each live edit. Check Enter, validation retry, Browse, Back, completion, resize, and Run Again. |
| **Visible text and committed renderer cache diverge** | An editor writes text outside the renderer, but the renderer's cached row still describes the old frame. A later diff decides that row is unchanged and leaves the physical text behind. | Compare the physical write path with the frame's pending/committed rows. Determine who invalidates or reconciles the cache after every edit and exit. |

Either condition can misplace or retain text; both can occur together. A repaint, clear-screen command, or cursor adjustment alone is not a complete repair if ownership and cache state remain split.

## Preferred Contract

Keep one screen renderer and one input owner. For generated apps, use the existing key-event `Input.psm1` + `Prompt.psm1` loop: store the current value in workflow state, compose the prompt and value into the same frame, accept one normalized key, update state, and let the renderer commit the next frame. Do not call `Read-Host`, `Console.ReadLine()`, `Write-Host`, or `Console.Out.Write()` from a managed screen to get an independent live editor.

For an existing application that requires a separate line editor, first inspect whether that host/editor can be integrated without taking ownership away from the renderer. If it cannot, redesign the boundary so there is an explicit editor lease with all of these properties: the intended row/column is established by the renderer; the edit result and cursor state return to the screen owner; the physical row is reconciled into or invalidates the renderer cache before another diff; and exit/transition does not emit an unmanaged newline. Do not invent a local per-screen workaround. If the contract cannot be made reliable, report the limitation and use the existing key-event editor or another supported interaction pattern.

### Frame And State Invariants

- A committed frame includes the prompt, help/example, validation feedback, key hints, and the visible input value.
- The active editor's logical insertion point is explicit. For cursor-driven editors, position it at the prompt's designated row/column after every frame commit and resize. For key-event editors, redraw the changed value through the renderer; never rely on the physical cursor to echo text.
- Only the renderer writes screen rows. Only the input layer reads keys. A screen/workflow owns the input buffer and passes it into rendering as data.
- A changed value must be reflected in the renderer's committed state, or the cache must be deliberately reconciled/invalidated before another diff. Keep both representations consistent.
- A transition commits a complete replacement frame and clears obsolete trailing rows centrally. No managed input path may leave an unmanaged newline, duplicate prompt, or orphaned error row.
- Preserve the user's navigation, locale, accessibility, and layout choices. The path labels below describe result semantics; they do not mandate a language or visual redesign.

## State Transition Contract

| Event | Input buffer | Cursor/layout | Frame/cache |
|---|---|---|---|
| Character or Backspace | Update only the active field | Recalculate logical insertion point | Render the current value through the central renderer and commit/reconcile it |
| Resize while waiting | Preserve partial text and validation state | Recompute the designated row/column from the new viewport | Invalidate/reconcile once, redraw, and preserve workflow state |
| Enter with valid input | Return the accepted value to the workflow | Retire the editor cursor | Commit the next complete screen; remove obsolete prompt rows |
| Enter with invalid input | Keep the value only if the established retry UX does so | Reposition within the same prompt | Render validation feedback and input together; do not append a separate unmanaged error line |
| Esc/Back | Cancel the active field; do not leak it into another workflow | Retire the editor cursor | Commit the previous/next complete frame and clear obsolete input rows |
| Browse | Suspend the current field with value retained only if the workflow defines that behavior | Re-establish the prompt row on return | Render the browse result/return transition centrally; never leave two prompt copies |
| Success/result | Keep paths in structured operation state, not in transient editor output | No old editor cursor | Render the result and any real source/destination context as deliberate result rows |
| Run Again | Start a new run with its specified default/history only; do not implicitly inherit the prior buffer | Establish the new prompt's row | Replace the result frame and clear residue from the earlier run |

If the application intentionally prefills a field or retains history, make that behavior explicit in workflow state and test it. An accidental visual remnant is never a valid prefill.

## Structured Result Context

For file operations, carry source and destination paths from structured workflow/result data. Never recover them by parsing a shell command or scraping rendered rows. Use the scaffold helper inside a result frame:

```powershell
Clear-Ui
Write-UiLine 'Completed Successfully' 'Success'
Write-ResultPathContext -InputPaths @($sourcePaths) -OutputPath $destinationPath
$frameViewport = Complete-UiFrame
```

`Write-ResultPathContext` writes `Input:` and each supplied source path, then writes `Output:` only when a real output path is available. It does not clear or commit the frame; the calling result screen owns those operations. For estimates, network workflows, or results with no file paths, omit unavailable fields—never fabricate a path. Preserve all source values; apply the app's established wrapping/clipping behavior visibly and accessibly.

## Diagnosis And Repair Workflow

For a reproducible defect in an existing app:

1. Capture the exact interaction sequence and target host/runtime. Reproduce it before changing code.
2. Trace screen writes, key reads, frame begin/commit, cursor movement, dimensions, and cache invalidation across the shared input/renderer boundary.
3. Determine which of the two failure conditions above is present; verify both independently. Check shorter replacement frames, direct writes, implicit line endings, and repeated runs.
4. Record the intended state transitions and structured result fields. Preserve current behavior not implicated in the defect.
5. Add deterministic regression tests first. Make the smallest central-boundary repair, then run the focused tests and the app's required suite.
6. Inspect the final diff and test output. Treat source review, scripted tests, and real-terminal visual checks as separate evidence.

For a new app, define this contract in the Phase 1 screen/state plan and architecture before building screens. For an existing app, audit the shared boundary and every consumer before patching the displayed screen.

## Required Regression Coverage

Adapt the applicable checks; do not loosen existing renderer, resize, accessibility, or launcher tests:

1. The active input value is part of its committed frame and appears on the intended row; if a real editor cursor is shown, the cursor is restored to its designated row/column.
2. A live edit updates or reconciles the frame cache. The next repaint can replace/erase the edited value correctly.
3. Replacing a taller frame with a shorter one erases stale prompt, help, hint, validation, and input rows.
4. Enter, Esc/Back, Browse, and validation retry produce no unmanaged newline, duplicate editor, or orphaned row.
5. **Run Again** with a different path shows only the new run's value unless explicit prefill/history is part of the UX.
6. Result context uses structured data, labels all available `Input:` sources and the real `Output:` value, and omits unavailable paths.
7. Resize while input is pending preserves partial text and workflow state while recomputing layout/cursor ownership.
8. Scripted and redirected sessions remain deterministic and do not emit cursor-control sequences.

Use real template behavior for deterministic tests, not source-string matching alone. The bundled template tests cover sequential input frames and result-path presentation; extend the target application's tests for its specific Browse, validation, and repeat-run flow. A buffer test does not prove physical cursor placement or flicker behavior.

## Real-Terminal Acceptance

On each claimed terminal/runtime, type a long path with spaces, trigger validation, use Browse if available, complete the operation, and choose **Run Again** with a different path. Resize while a field is active without pressing a key. Confirm the prompt and value stay associated, no prior row remains after each transition, and the result shows only real structured paths. Record terminal name/version, PowerShell edition/version, actions, and evidence. If interactive testing is unavailable, mark this check `UNVERIFIED` and provide the exact steps; never infer visual success from a screenshot, source review, or buffer test.
