# Measurement And Reconstruction

## Geometry And Scale

Identify the actual content viewport, excluding browser chrome, device frames, editor margins and unrelated screenshot borders. Record crop offsets. A full-page image height is document height, not viewport height. For stitched inputs, map overlap anchors and remove duplicate sticky headers from the reconstruction plan; retain originals for evidence.

Measure several independent anchors (container edges, logo bounds, heading baseline, card columns). Infer relationships rather than treating every rectangle as absolutely positioned. Distinguish fixed sidebar width from flexible content width, max-width from viewport width, and surface padding from parent gaps. Do not convert the screenshot width into a max-width without evidence of a centered capped container.

Treat antialiasing, JPEG artifacts, OS rendering, browser zoom and image resampling as measurement uncertainty. Sample flat interior color patches at multiple points; avoid edges, text antialiasing and compressed halos. A sampled composited pixel is not necessarily the authored CSS color. Recover overlay alpha only with sufficient foreground/background evidence; otherwise record a measured composite and inferred implementation.

## Typography Checklist

1. Reproduce legible copy verbatim, including punctuation, case, Arabic diacritics and numerals. Record uncertain text rather than inventing content.
2. Verify font file availability and successful loading. Check the requested weight exists and is not synthesized; inspect variable font axes when applicable.
3. Match text box width, font family/face, size, weight, line-height, tracking and baseline, in that order. Use wrap points as evidence.
4. Inspect letters with distinguishing shapes and both Arabic/Latin fallbacks. Preserve Arabic joining; avoid arbitrary letter spacing on Arabic text.
5. Resolve incorrect metrics before adding manual line breaks or absolute positions. Explicit source line breaks are different from wrapping.
6. When exact font identity is unavailable, name the selected fallback and show the residual. Exact font attribution requires a source, not visual confidence.

## Asset And Icon Contract

Record role, original path/source, dimensions, fit mode, crop/object-position, transparency, resolution sufficiency and usage status. Keep logos sharp and aspect-correct. Do not infer transparent backgrounds from a checkerboard embedded in an image. Match supplied images without replacing them merely because a generator is available.

Use object-fit/object-position or CSS backgrounds according to meaning. Avoid stretching imagery or cropping off important reference details. Prefer a dedicated asset crop over reusing a full screenshot as a UI background. Controls/text stay code-native; screenshot-as-page is a failure even when its pixel diff is zero.

Use one coherent icon system; compare shape, stroke, viewBox padding and optical alignment. Small carets, status dots and separators are part of the inventory. Custom SVG may be appropriate for a simple observed shape; do not redraw a complex logo from imagination.

## Responsive And RTL Rules

Multiple reference widths provide constraints, not proof of all intermediate widths. Check just below/above observed layout transitions and a narrow text-dense state. Preserve semantic order when columns collapse. Avoid desktop fixed heights that clip translated text.

Set direction intentionally at the appropriate scope. Prefer padding-inline, margin-inline, inset-inline and text-align:start/end. Mixed email addresses, Card IDs and URLs need isolation. Test tab order, long Arabic labels, diacritics, bilingual numbers and dropdown alignment. Follow explicit project text-size requirements; if they conflict with exact source typography, disclose the conflict and apply the governing rule.

## Existing Application Boundary

Inspect owner components before editing. Reuse business handlers, component contracts, selectors required by tests, routes and state flows. Scope overrides to the target surface; a global token change may alter unrelated screens. Record the before state and check immediate dependents. Do not replace a functioning app with a static mock simply to match a screenshot.
