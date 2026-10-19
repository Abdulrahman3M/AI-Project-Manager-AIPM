# Flicker-Free PowerShell TUI Architecture

> Reusable, Skill-Owned Implementation Prompt | PowerShell TUI App Designer v1.1.0 | 2026-10-19

Design or upgrade the PowerShell TUI using a **Flicker-Free PowerShell TUI Architecture** combining **ANSI In-Place Rendering + Differential Updates + Centralized TUI Renderer**.

## Agent Instructions

1. Inspect the actual repository, branch, open repair PRs, README, AGENTS.md, architecture, tests, and terminal capability detection. Preserve all existing features; integrate unfinished, verified fixes instead of overwriting them.
2. Make a single **central Renderer** the exclusive owner of terminal writes, positioning, styled segments, frame buffers, and cursor restoration. Input owns keys, Theme owns colors and icon tiers, menu controllers own selection state. Never let business logic emit console escape sequences.
3. Compose each logical frame into ordered, independently styled line segments, retaining **semantic foreground/background roles**, colorful standalone Emoji icons, Symbol/ASCII fallback icons, optional numeric choices, selection markers, muted descriptions, and keyboard hints. Preserve established layouts and Title Case static strings.
4. Use **ANSI In-Place Rendering** in verified VT-capable interactive terminals: position cursor with CSI row;column H, update content in place, clear only stale trailing characters with CSI K, and never use Clear-Host or CSI 2J for each arrow press. Hide cursor during redraw if supported and always restore it in a finally path. An alternate screen is optional and must also be restored.
5. Use **Differential Updates**: compare the next logical frame with the prior committed frame by row **including complete visible text and every style segment**; repaint only changed rows (for a simple adjacent selection, normally the old and new selected rows). Compare the actual rendered encoding, not only plain text. Clear rows removed from a shorter frame.
6. Keep the screen-frame comparison in a centralized controller. Invalidate/reconcile the cached frame on initialization, explicit full transition, terminal resize, icon-tier/theme change, unexpected write, or output-mode change. A full **in-place** redraw is acceptable then; do not blank the terminal on ordinary arrow navigation. During a blocking input wait, detect resize without requiring a key; preserve workflow state and remove stale rows on the next committed frame.
7. Handle Unicode display widths, surrogate pairs, combining characters, Emoji sequences, wrapped rows, terminal right-edge auto-wrap, small terminal dimensions and changed viewport sizes conservatively. If width/truncation is uncertain, use a known-safe row mode or fall back to a complete in-place frame. Avoid splitting grapheme clusters or measuring UTF-16 length as terminal columns.
8. For Windows PowerShell 5.1, PowerShell 7 on Windows, Windows Terminal and legacy conhost, choose ANSI only when actually supported. Use safe legacy cursor positioning and padding without emitting raw ANSI into a non-VT host. When positioning is unsupported, use a documented full-redraw fallback. In redirected/headless/test modes output readable plain text with **no ANSI**.
9. Preserve deterministic capture/test sinks; tests should exercise row-delta decisions, unchanged-frame zero writes, re-styling with equal text, frame shrink, resize invalidation, full transitions, cursor restoration on exceptions, rapid Up/Down, and redirected output. Static checks alone are insufficient evidence of a real flicker-free terminal.
10. Do not change installation, file operations, CLI compatibility, icon colors, descriptions or keyboard behavior as an incidental rendering fix. Update tests, documentation, changelog and versions according to each repository's rules. Run CI and physical terminal visual checks where possible, marking unexecuted checks UNVERIFIED.
11. Use feature branches/PRs and re-check current main before merging. Never force-push over other work or declare a merge successful without GitHub confirmation. Protected integrity-baseline hashes require separate explicit owner authorization.
12. For every new or existing TUI, audit resize/frame lifecycle before coding: complete frame ownership, blocking waits, idle resize observation, state preservation, shrink cleanup, redirected behavior, and terminal restoration. Apply the reusable implementation and tests in `references/Resize-And-Frame-Lifecycle-Reliability.md`; do not make a screen-specific resize patch when the shared input/renderer boundary is the defect.
13. Resize is an internal event, not a user action. Input waits for either a key or viewport change with a bounded, non-zero poll; the screen recomposes from the same state, and unchanged polls cause no render writes. Include the last committed viewport in the wait so an intervening resize is not lost.
14. For a broken Windows Terminal launcher, inspect the actual process boundary and parse the command line with `CommandLineToArgvW` or an equivalent real parser. Specifically test quoted paths ending in `\`; do not blame Unicode or trust an echoed command. Prefer the smallest safe argument-vector repair, then run a child probe that proves the entry script and forwarded arguments arrived intact. See `references/Windows-Terminal-Launcher-Diagnostics.md` and `examples/09-Windows-Launcher-ArgumentProbe.ps1`.
15. Keep proof levels separate: a parser probe proves argument splitting only; a fake terminal must parse and execute the child to prove launch behavior; only a real Windows Terminal run proves native host behavior. Report missing host evidence as UNVERIFIED.

## Acceptance Criteria

- Fast repeated arrows never invoke Clear-Host or CSI 2J along the ordinary navigation path.
- An unchanged frame writes **zero rows**, and selection changes repaint only actually modified rows where practical.
- Colors, independently styled icons, selected backgrounds, muted hints and descriptions remain intact.
- Screen changes, smaller/larger frame content and terminal resize produce no stale text.
- Resizing while input is idle is noticed within the configured bounded poll, without a key press, and preserves the current selection/text.
- A launcher regression test proves both parsed arguments and child execution; native Windows Terminal behavior is reported separately.
- Redirection and legacy consoles remain readable, and normal shutdown/errors restore terminal state.
- All executed tests show evidence; unsupported/untested terminal setups are listed as UNVERIFIED.

## Architecture Overview

```text
Input -> Selection/Menu State -> Logical Frame -> Centralized Renderer
                                             |     Compare old/new rows + style
                                             |     VT: CSI H + changed rows + CSI K
                                             |     Legacy: safe cursor + padding
                                             |     Redirected: plain text output
                                             +-> fallback / invalidate on resize or transition
```

Treat ANSI In-Place and Differential Updates as **complementary**, not competing, technologies. ANSI is the cursor/control mechanism; differential rendering is the policy deciding which rows to send.
