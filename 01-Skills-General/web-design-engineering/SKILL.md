---
name: web-design-engineering
description: Design, build, review, or improve production web interfaces with subject-specific art direction, responsive accessible implementation, purposeful motion, and rendered evidence. Use for websites, landing pages, product surfaces, design systems, or UI quality reviews; not for backend-only work.
---

# Web Design Engineering

## Purpose And Boundary

Create web interfaces that are useful, distinctive for their subject, and demonstrably robust. This Skill combines art direction with engineering discipline; it never substitutes a fashionable visual style for a product decision, nor a source-code check for rendered evidence.

Use the smallest route below that covers the request. Preserve the repository stack, established design system, real content, and behavior unless the owner requests a change. A supplied brand, Figma frame, screenshot, accessibility target, or existing component library takes precedence over all defaults.

Do not use this Skill for backend-only work, to install packages, or to claim a browser, build, accessibility audit, or production deployment that was not actually run.

## Routing

| Request | Read | Deliver |
| --- | --- | --- |
| New page, new product, or major redesign | [Art Direction](references/Art-Direction.md), [Design System](references/Design-System.md), [Responsive Layout](references/Responsive-Layout.md) | A one-page design brief before implementation, then the working surface |
| Existing page or component refinement | [UI Review](references/UI-Review.md) and only the relevant system/layout guide | Narrow fixes with before/after evidence |
| Figma, screenshot, or visual reference fidelity | [Reference Fidelity](references/Reference-Fidelity.md) | A measured fidelity plan and rendered comparison |
| Motion or interaction work | [Motion And Interaction](references/Motion-And-Interaction.md) | State-aware, interruptible interaction behavior |
| Accessibility, localization, or responsive QA | [Quality Gates](references/Quality-Gates.md) | Findings with PASS, FAIL, or UNVERIFIED evidence |

Read [Research Synthesis](references/Research-Synthesis.md) when explaining why this Skill makes a particular tradeoff or updating the Skill itself.

## Common Workflow

1. **Understand the surface.** Inspect the affected route, components, tokens, assets, dependencies, existing tests, and any visual reference. Identify audience, page job, primary action, actual content, critical states, required viewports, themes, and locales. Make a bounded assumption only when its absence does not materially change identity or scope.
2. **Choose a direction deliberately.** For new or substantially reshaped UI, record a compact design brief using [the template](templates/Design-Brief.md): thesis, content hierarchy, role-based tokens, type roles, layout principle, signature element, motion intent, and accessibility constraints. Reject any choice that could have been made for an unrelated product.
3. **Build with the local system.** Reuse available primitives and tokens. Add only the smallest missing token or component. Encode semantics in HTML before ARIA; use native controls before custom roles. Keep copy specific, sentence case, actionable, and consistent across controls, confirmation, empty, loading, and error states.
4. **Make every state usable.** Cover default, hover, focus-visible, active, disabled, loading, empty, error, success, long-text, narrow-width, zoomed-text, and reduced-motion states that apply. Color alone must never carry status. Ensure interactive targets, focus order, labels, and escape/cancel behavior are intentional.
5. **Verify the rendered result.** Run the relevant project checks, then inspect the current build in a browser whenever it is available. Check representative wide and narrow widths, all changed themes/locales, keyboard paths, and relevant data extremes. Source inspection cannot replace this gate.
6. **Report only evidence.** Use [the report template](templates/UI-Verification-Report.md). Mark an item `UNVERIFIED` if the needed runtime, device, assistive technology, or asset is unavailable.

## Design Decision Rules

- Begin from the subject and page job. A banking workflow needs readable risk and status hierarchy; an editorial product needs typographic pacing; a creative portfolio may place more expressive weight in media. Do not start from a generic card kit or a trend name.
- Spend visual intensity in one memorable, content-relevant place. Surround it with disciplined spacing, contrast, and hierarchy. Remove decorative marks that neither orient, communicate, nor support an interaction.
- Treat typography as a system: explicit display, body, and utility roles; readable measure; intentional weights and leading; resilient wrapping for translated strings, long names, URLs, and user text. Do not rely on a particular word wrapping at a particular width.
- Use containers, borders, and elevation when they clarify grouping, ownership, density, or interaction—not merely as ornament. Repeated items may be cards; unrelated hierarchy should not become nested cards.
- Avoid generated-looking defaults unless the brief calls for them: unexplained gradient washes, identical rounded cards, decorative numbered labels, arbitrary accent-word styling, generic icon-only controls, and animation applied uniformly to every element.
- Treat dark mode, mobile layouts, and imagery as scope decisions. Preserve existing support; add them for new work when requested or when the product contract requires them. Never fake imagery or pretend a generated asset exists.

## Engineering Invariants

- Use a token layer rather than scattering raw values. Start from [the token contract](templates/Design-Tokens.json); adapt it to the existing stack rather than forcing a framework.
- Keep layout fluid: intrinsic sizing, `minmax`, logical properties, content-driven breakpoints, safe wrapping, and no hidden essential text. Test at browser zoom or text scaling where practical.
- Maintain visible `:focus-visible`, sufficient non-color cues, semantic headings/landmarks, form labels and errors, native keyboard behavior, and a reduced-motion alternative that retains comprehension.
- Motion must explain an action or state change. It should be concentrated, interruptible, performant, and disabled or simplified under `prefers-reduced-motion`; never trap focus or delay feedback.
- For reference fidelity, reproduce observable structure and behavior, not brittle pixel values. Do not copy protected assets, code, or branding without authorization.

## Deterministic Helpers

The helpers use only Python's standard library and do not install packages or contact the network.

- `python scripts/validate_design_brief.py path/to/brief.json` validates a design-brief handoff against the supplied schema.
- `python scripts/build_token_css.py templates/Design-Tokens.json path/to/tokens.css` emits a portable CSS variable layer.
- `python scripts/check_html_contract.py path/to/page.html` checks a static HTML baseline for title, language, viewport, landmarks, heading order, image alternatives, and obvious focus-style omissions. It is advisory; it is not a substitute for browser and assistive-technology testing.

Run `python -m unittest discover -s tests -v` after changing these helpers or templates.

## Safe Completion

Do not expand a visual request into a replatform, dependency migration, brand rewrite, analytics change, or deployment without authorization. State the exact viewports, states, browser checks, and automated checks performed; list remaining limits. Follow [Quality Gates](references/Quality-Gates.md) before declaring a UI task complete.
