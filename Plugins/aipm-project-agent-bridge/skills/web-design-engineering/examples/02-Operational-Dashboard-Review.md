# Example: Operational Dashboard Review

| Finding | Evidence | Smallest correction | Validation |
| --- | --- | --- | --- |
| Status depends on green/red dots | Text labels disappear in compact view | Keep a written status beside each dot and expose it in the row name | Inspect default, high-contrast, and screen-reader name |
| Filter chips overflow at 360px | Last controls are off-screen with no discoverable scroll | Wrap filters, or add a focusable “More filters” disclosure | Keyboard and narrow-width render |
| Hover-only action has no visible focus | Keyboard user cannot discover it | Add `:focus-visible`, an accessible name, and a focusable control | Tab path and screenshot |
| Every card animates on refresh | Data changes feel slow and reduced motion still moves | Restrict motion to changed rows and show stable reduced-motion state | Refresh and `prefers-reduced-motion` |
