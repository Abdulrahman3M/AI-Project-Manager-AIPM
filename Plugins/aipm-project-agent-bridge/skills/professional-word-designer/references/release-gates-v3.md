# Release Gates v3 — stop on serious failure

1. **Sources:** evidence ledger factual claims verified; source use/license tracked; citations in body map to real bibliography; visuals with quantities have units/source/date. BLOCK if fabricated or material unsupported claims.
2. **Content:** human-readable, subject-appropriate, no filler, editorial pass and proofread per language, terminology glossary checked, no unverifiable original authorship claim. BLOCK if meaning changed in translation.
3. **Navigation:** headings real, TOC is real field for longform, dot-leader **render verified after field update**; captions and references refresh verified; page fields present. If no refresh engine, report pending field refresh, not PASS.
4. **Visualization:** visual register complete; each figure type selected by decision table; no arbitrary decorations; 100% legibility; sufficient contrast; RTL semantics; truthful caption and editability label.
5. **Accessibility:** alt text for useful figures, semantic tables, reading order inspection, accessible description for complex figures. Auto audit baseline + independent manual pass.
6. **Rendering:** all pages PNG; zero cut off, orphaned caption, bizarre line wraps, collapsed bidi, missing font glyphs; inspect full-size, record QA report; re-render on correction.
7. **Format integrity:** DOCX opens, expected fields/shapes/styles/sections retained, no bogus Zotero fields, no macros or remote code. No half-implemented interactive Word claims.
8. **Artifacts:** tests execute; generate signed-off report with verified/unverified and platform/tool requirements; requested DOCX/HTML companion only, except sample gallery stored in Skill distribution.

The included `scripts/audit_docx.py` and `scripts/render_and_audit.py` cover a *subset* of these requirements; they cannot automate fact checking, copyright clearance, translated prose quality, actual Word field refresh or aesthetic review. Their PASS alone does not certify all 8 gates.
