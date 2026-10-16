# Strict Execution Contract v3.0 — no undocumented improvisation

The sample is a constraint **on method and component grammar**, not a template for fabricating content. Each request has an explicit Document Contract and a release gate. When documents cannot be rendered or fields refreshed, report precisely what was validated and what remained unverified.

## Pipeline, inputs, evidence

1. Intake a `Document Contract`: title, audience, learning objectives, language and locale, expected length, output formats, data/reference availability, citation style, chosen style profile, illustration constraints, user logo/license. Apply defaults rather than ask nonessential questions.
2. Create `source-ledger.json` from **actually consulted** sources. Source entries include unique ID, title, creator/publisher, URL/DOI and retrieval date where appropriate. Never make up an author, URL, observation, reference or date. Quote carefully.
3. Build outline with real heading hierarchy; assign stable `heading_id` and `figure_id` and label each section's intended learning gain.
4. Draft and three-pass edit: (a) meaning/content, (b) natural editorial style, (c) native-level proofreading where possible. Natural writing is NOT a claim of human authorship or undetectability; prohibit synthetic personal testimony.
5. Generate `visual-register.json`; execute Visual Explanation System routing. Each visual gets independent teaching purpose, provenance and expected screenshot ID. Consult each specific numbered visual example before building.
6. Load **exact** `style-profiles/<profile>.json` design tokens; deviations need documented user or content justification. Keep all text editable where possible; never rasterize entire document pages.
7. Generate Word with real `Heading` styles, `PAGE`, `TOC`, `SEQ`, `REF` fields when relevant, semantic list/table structures, separate header/footer first page, correct RTL, caption number hierarchy, correctly formatted citations and bibliography. `python-docx` alone cannot update field results; open with a compatible field-aware Word engine if available and verify, otherwise mark `requires_field_refresh=true` explicitly.
8. Check structural integrity: field existence and type, source↔citation mapping, captions, alt text, internal relationships and headings. `scripts/audit_docx.py` performs a useful baseline, NOT an exhaustive scientific or accessibility audit.
9. Render **every page** using installed rendering tools; `scripts/render_and_audit.py` orchestrates previews and a QA report. Inspect every page at natural scale; fix, re-render and document pass/fail.
10. Only then publish files, report implemented features, unresolved limitations, test output and delivery paths. If generating HTML companion, validate its accessibility and data parity separately.

## Reproducible layout tokens / fixed defaults

- Profile `academic-research`: A4 210×297mm, 22mm horizontal margin, body 11pt, 1.24 line, navy #20324E, teal #247A7C, amber #FFF4E3. First page is cover only for substantial reports.
- `visual-textbook`: A4, body 11pt, 1.3 spacing, educational two-dimensional diagram preferred to decoration, ~20–24mm margins.
- `technical-guide`: A4, 10.5–11pt, dark code boxes, short step tables and decision diagrams.
- `infobank-style`: clear source breadcrumbs, strong RTL contrast, colored semantic callouts, web/Word content parity.
- Other rules in `references/design-system.md` / `references/multilingual-localization.md` supersede only where task specific.

## Deliverable matrix

| Intended feature | Source format | Word implementation | Required gate | If unsupported |
|---|---|---|---|---|
| Contents | Heading IDs | Real `TOC \\o` field, dot leaders | Field/visual audit | Static approximation clearly labeled |
| Running header | Major heading styles | `STYLEREF` or verified per-section fallback | Header spot check on every section | Disclose fallback |
| References | Source ledger and usage | Native text superscript or numbered `[n]`, bibliography | One-to-one crosscheck | Block fake references |
| Figures | Visual Register, editable svg/source | Sourced figure + SEQ caption; alt text | Visual/data/rights check | Omit if unlicensed |
| Interactive diagram | Tagged graph data | Static counterpart + companion HTML | Feature parity | Static-only and disclose |
| Languages | Per-language terminology glossary | RTL/LTR local editions, not naive literal translation | Independent proofreading + layout | Mark native proofread unavailable |
| Review changes | Original + revised DOCX | Compare changed paragraphs; OOXML comments/tracking via supported specialized tooling | Review visual+XML | Provide clean diff report, no false native claims |

## Tool boundaries

- Original public projects **inspire architecture only**: Anthropic's public DOCX skills (render-review cycle), gertalot's docx-skill (typography), Quarto (single-source publishing), Zotero (editable citations), and Microsoft native Word functions. We did **not bundle their code, templates, images, trademarks or proprietary content**.
- `scripts/` includes executable portable baseline utilities. Optional professional integrations (Zotero active citation fields, fully editable Excel-based charts, Word's exact TOC refresh, native tracked changes) are **integration specifications**, not claimed built-in implementation. Check app availability and do not downgrade silently.
- No agent may claim the generated prose is 100% human-made or guaranteed to evade AI detectors. Require accurate natural writing, attributable sources, evidence checks and transparent documentation.
