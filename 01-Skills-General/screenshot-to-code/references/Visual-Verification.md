# Visual Verification

## Capture Contract

Record image hash, source revision, reference ID, browser/version, OS, CSS viewport, raster dimensions, DPR, zoom, light/dark theme, locale/direction, scroll offset, capture type and exact interaction state. Unknown fields remain unknown. Compare images only after these conditions are aligned or the remaining environment differences are disclosed.

Wait for document fonts, image decode and a stable page. Inspect network/resource failures and console errors. Network idle alone is unsuitable for pages with polling or streaming. Use project-specific readiness signals; do not rely on a blind sleep. Freeze animations/video at the same observed frame only for a controlled static comparison, and test live behavior separately. Do not disable motion to conceal a broken interaction.

Use an authorized supported browser tool; host policies determine whether a plugin, connector, local automation or manual capture is available. Do not attach to personal sessions or install tools merely because a third-party Skill recommends them.

## Comparison Layers

| Layer | Inspect | Typical Cause |
| --- | --- | --- |
| Coverage | All visible regions, all references, below-fold sections | Incomplete source inventory |
| Structure | Columns, hierarchy, grouping, scroll and sticky states | Wrong layout model |
| Geometry | Container edges, section heights, anchors, gaps | Wrong max-width, padding or sizing |
| Typography | Face, baseline, wrapping, weight, Arabic shaping | Missing font or wrong text metrics |
| Assets | Crop, scale, sharpness, transparency, icons | Missing/wrong asset or object-position |
| Surface | Fill, border, gradient, shadow, radius | Token/compositing mismatch |
| Behavior | Actual outcome of click, keyboard and focus | Inert controls or changed handlers |

Review crops at native scale as well as full-page composition. A blank background can dominate a global score. Add independent regions for critical header, primary action, content panel, footer and high-detail controls as applicable.

## Diagnostic Semantics

`compare.py` computes changed pixels when the maximum absolute RGB channel difference exceeds `--threshold` (default 8 on the 0–255 scale). Mean absolute error uses all channels and all selected pixels, including those below that threshold. These are reproducible low-level metrics, not perceptual or semantic scores. Alpha is composited against white and reported; recapture unusual transparent exports on a comparable background.

Masks use exclusive raster coordinates, merge by union, require reasons, and cannot cover the entire image. Raw global and per-region metrics remain visible; unmasked metrics are additional. Never change the threshold or mask to make a failing result appear acceptable. Treat missing images, fonts, text, controls or states as independent blockers even if total error is low.

Do not resize, align or blur images automatically before the main comparison. Such transformations can erase true errors. If a diagnostic normalization is useful, keep the originals and label the normalized result separately.

## Repair Ledger

Track each issue as region → expected evidence → observed mismatch → severity → likely owning file/token → attempted correction → new capture → resolved/residual/regression. Prioritize root causes that explain several regions, not dozens of unrelated pixel nudges. Keep immutable per-round artifacts or at least the final and best previous round in the project's approved evidence area.

Three rounds is a default resource budget, not a claim of convergence. If the same issue persists without improvement, inspect assumptions (DPR, font, assets, crop and layout model). Report evidence limits or missing inputs rather than promising an exact result.

## Acceptance Gates

- Implementation: source compiles/runs with the appropriate project checks.
- Fidelity: fresh comparable captures cover every supplied reference; no material unresolved layout, font, copy, asset or control mismatch; minor differences explained.
- Interaction: replay actual intended state transitions and inspect outcomes. Cursor, hover rules and button presence are insufficient.
- Responsive: no unintended overflow/clipping at tested widths; supplied breakpoint references matched; inferred layouts labeled.
- Accessibility: semantic controls, labels, keyboard access and visible focus checked; disclose contrast conflicts and any automated/manual coverage limits.

Return PASS only for checks actually performed. Helpers returning exit 0 never grant these gates. A missing browser capture means fidelity UNVERIFIED even if source tests pass.
