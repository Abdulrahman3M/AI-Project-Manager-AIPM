# Evidence Modes And Scenarios

The original screenshot remains the visual authority in both modes. A browser-inspected reference adds evidence; it does not replace the screenshot or prove that the local implementation works.

## Mode Selection

| Mode | When to use | Evidence allowed | Required report |
| --- | --- | --- | --- |
| Screenshot-only (default) | No explicit browser opt-in; browser is unavailable, unverified or unnecessary | User-supplied screenshots and the target project's files/assets | Screenshot dimensions/hash, observed versus inferred facts, and any unknowns |
| Authorized browser inspection | The user has explicitly opted in for an identified page and the host verifies the approved agent-connected browser | Visible page content, visible-element DOM/computed styles and geometry, already loaded asset metadata, and user-authorized visible states | Page/URL scope, browser/tool, time, viewport/DPR, visible state, evidence provenance, and limits |

Ask before any browser action, using the exact prompt in the parent Skill. A supplied URL alone does not authorize navigation. The user may instead open the page in an approved agent-connected browser. If the user declines or the host cannot verify the browser identity/permission, proceed in screenshot-only mode.

Browser inspection does not authorize sign-in, entering credentials, access-control bypass, reading cookies/storage, hidden or private data, backend source, private APIs, another origin, or side-effecting actions. Do not use the user's personal browser/profile. Do not download or reuse third-party assets without separate permission and license review. If any boundary is unclear, stop inspection and keep working from screenshots.

Use the screenshot and the page only to establish observable client-side facts. Label each record SCREENSHOT, AUTHORIZED_BROWSER, INFERRED, or UNKNOWN; do not describe an inference as a measurement. Record current page and viewport so a second page or state is not silently treated as the same reference.

## Screenshot-Only Scenarios

1. **One desktop image, unknown CSS scale:** Preserve the original raster and dimensions. Record CSS viewport/DPR as unknown, calibrate only from justified anchors, and do not claim a known browser viewport.
2. **Desktop and mobile images:** Register each as a distinct viewport reference. Implement and compare both; do not infer that a tall image is a phone layout or merge alternate designs.
3. **Arabic with a mixed-direction identifier:** Preserve the exact Arabic copy and visible English ID. Use lang/dir, isolate the ID, and report shaping or glyph uncertainty.
4. **Custom font missing from the screenshot/project:** Mark the exact face unknown. Check available project fonts, select a disclosed fallback only if needed, and do not call typography exact.
5. **A dynamic control appears in one state:** Reproduce the visible state. Treat unseen open/closed, hover, loading, and error states as NOT_RUN unless supplied or requested; do not invent their appearance.
6. **Screenshot ends partway down a page:** Reconstruct the visible crop and any explicitly requested extension only. Do not add a guessed footer, section, interaction, or hidden page.

## Authorized Browser Scenarios

- **Consent granted for one public page:** Verify the approved browser identity and exact URL, inspect only visible client-side facts for that page, then return to the target project to implement and test its own output.
- **Consent declined or capability uncertain:** Perform no reference-site navigation or inspection. Continue with the supplied image and mark browser-derived facts UNKNOWN.
- **The page exposes login, private account data, or a blocked state:** Do not sign in, bypass access controls, or inspect private content. Ask for a safe screenshot/reference or continue with the evidence already supplied.

These are operating examples, not executed browser tests. Report NOT_RUN for any scenario not actually exercised.
