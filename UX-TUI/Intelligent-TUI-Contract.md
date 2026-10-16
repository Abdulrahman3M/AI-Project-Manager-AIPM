# Intelligent TUI Contract

This contract adopts the owner-approved dashboard, Command Palette, and Assistant Console reference images as cell-layout guidance, not bitmap terminal content. Its complete skill-level checklist and test matrix live in `../01-Skills-General/tui-intelligence/references/`.

## Required Outcomes

- Use the semantic roles in `theme.json` and one icon map in `semantic-icons.json`; select true-color/16-color/ASCII tiers only after host checks.
- Keep Title Case labels, a visible `>` focus marker, selected-panel shading, and a readable muted explanation for every selected and unselected choice.
- Provide Task Dashboard as default, plus Command Palette and Assistant Console modes; support arrows, Enter, Esc, `/` Search, `?`/F1 Help and stable numbers when implemented.
- Keep passed/failed/blocked/unverified text, evidence counts, and progress bars when data is known. Derive progress only from verified weighted work; otherwise show `Unknown`.
- Use a single renderer with in-place positioning and style-aware differential rows; identical frames write zero bytes and a key press never triggers a full-screen clear.
- Wrap/page narrow screens, honor `NO_COLOR` and redirected output, avoid clipped descriptions, restore cursor/terminal state, and document what could not be tested.

No renderer is delivered in P07. Real Windows Terminal visual/no-flicker behavior remains `UNVERIFIED` until captured and tested under PowerShell 5.1 and 7.x.
