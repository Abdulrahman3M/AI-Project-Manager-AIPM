# Responsive Layout

Design from the content outward. Treat breakpoints as a response to an actual layout failure, not a list of device names.

## Required Checks

- No horizontal scroll caused by normal content, including long identifiers and translated labels.
- Essential text can reflow under zoom, text scaling, and browser spacing overrides.
- Navigation, tables, filters, and comparison data have an intentional narrow strategy: reflow, prioritize, disclose, or permit a clearly labeled scroll region.
- Touch targets and spacing remain usable where touch is in scope; hover-only information has a focus/tap alternative.
- Use logical CSS properties so RTL layouts are not an afterthought. Test real RTL strings when localization is in scope.

Prefer `max-inline-size`, `minmax()`, `clamp()`, flex/grid wrapping, container-aware components, and content limits. Avoid fixed heights for user-generated or translated text.
