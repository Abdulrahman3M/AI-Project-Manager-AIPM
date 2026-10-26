# Quality Gates

## Before Implementation

- Scope, audience, page job, source of truth, and target surface are known or explicitly bounded.
- Existing stack, tokens, components, tests, and repository rules were inspected.
- Major new UI has a design brief; fidelity work has an observation/unknowns ledger.

## Before Completion

- Automated checks relevant to changed code pass, or failures are reported with their cause.
- Current rendered UI is inspected when rendering is available.
- Required widths, themes, locales, states, and data extremes are checked.
- Keyboard path, visible focus, landmarks/headings, form labels/errors, non-color cues, and reduced-motion behavior are covered where applicable.
- No clipped essential text, accidental horizontal scrolling, dead control, missing image alternative, focus trap, or contrast regression remains in the tested scope.
- Final report distinguishes evidence from assumptions and `UNVERIFIED` items.
