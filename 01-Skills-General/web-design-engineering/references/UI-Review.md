# UI Review

Review the smallest surface named by the request. Report findings by impact, affected state, evidence, and smallest safe correction.

| Lens | Questions |
| --- | --- |
| Purpose | Can a first-time user identify the page job and next action? |
| Hierarchy | Is scanning order clear before decorative detail? |
| Content | Are labels specific, actions consistent, and failure states actionable? |
| Layout | Are groups, ownership, density, wrapping, and overflow legible? |
| Interaction | Are states, focus, keyboard paths, cancellation, and feedback complete? |
| Accessibility | Are semantics, contrast, focus visibility, errors, status, and motion addressed? |
| Resilience | Does it survive narrow screens, zoom, long/RTL strings, no data, and slow data? |
| Evidence | Was the current rendered surface checked, rather than only its source? |

Use `templates/UI-Verification-Report.md` and classify each result as PASS, FAIL, or UNVERIFIED. Do not rewrite unrelated UI while fixing a focused finding.
