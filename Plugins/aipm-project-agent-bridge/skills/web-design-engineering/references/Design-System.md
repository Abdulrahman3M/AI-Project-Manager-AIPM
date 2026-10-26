# Design System

Use tokens by role, not by visual accident. A small system is preferable to an elaborate unused one.

## Minimum Token Families

- Color: canvas, surface, raised surface, text, muted text, border, primary action, destructive action, success, warning, focus.
- Type: display, body, utility; size, weight, line-height, tracking; never encode semantic importance solely as a smaller or lighter font.
- Space: a small scale that permits dense and spacious compositions without arbitrary values.
- Shape and elevation: separate tokens for controls, panels, and overlays when the hierarchy actually differs.
- Motion: duration and easing roles for feedback, reveal, and overlay; reduced-motion behavior is part of each component contract.

## Component Contract

Before adding a reusable component, document its semantic root, inputs, states, keyboard behavior, focus behavior, empty/error/loading behavior, responsive behavior, and non-color status cues. Start with `templates/Component-Contract.md`.

Do not impose a new component library, replace an existing token architecture, or add a webfont dependency merely to satisfy this Skill.
