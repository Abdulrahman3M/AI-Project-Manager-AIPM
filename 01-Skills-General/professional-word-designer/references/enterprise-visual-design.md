# Enterprise Visual Design System

This system turns a Word document into a credible corporate artifact without making it look like a presentation squeezed onto paper. It is a design decision system, not a collection of copied templates.

## 1. Design contract

Before styling, record audience, decision to support, reading environment, brand assets supplied by the owner, print/digital target, page size, accessibility needs, language direction and template family. Never invent a logo, brand palette, certification mark, client name, photograph, or performance statistic.

Choose one art direction: **quiet executive**, **editorial insight**, **technical precision**, **warm education**, or **premium proposal**. Use one type family per script, one primary accent, one supporting neutral, and semantic colors only for status. A visual system is successful when a reader can scan title, key decision, section hierarchy, callouts, data and next action in seconds.

## 2. Corporate page grammar

| Layer | Professional default | Guardrail |
| --- | --- | --- |
| Cover | restrained title, short subtitle, owner-supplied identity, one purposeful image/shape | no invented logo; no decorative stock image without a license record |
| Navigation | real heading styles, TOC, running header, page field | never type page numbers or a faux TOC |
| Executive signal | short summary, decision box, KPI/metric panel when verified | do not turn every paragraph into a card |
| Sections | numbered H1, short intro, stable spacing and thin rule/icon cue | never use manual spaces for alignment |
| Evidence | native table/chart, figure caption, source/data note | charts need real data and a readable text alternative |
| Closing | decision, recommendation, next actions, references/appendix | distinguish recommendation from fact |

## 3. Visual components

- **Icon-led section marker:** use a single licensed, stylistically consistent line-icon family. Icons reinforce labels; they never replace text or convey status by color alone.
- **Quote or insight panel:** short verified quotation, author/source/context, generous white space, 1–2 quotation marks as a quiet motif. Do not quote anonymous web copy or fabricate attribution.
- **Inline literal/code token:** for text such as `هذا النص كمثال`, use the `Code Inline` character style: subtle neutral fill, 0.5–1 pt border, monospace font, protected LTR run for code/identifiers. It is not a quotation style.
- **Arabic quotation:** use Arabic guillemets `«…»` for prose quotations when the house style permits; keep the Arabic paragraph RTL, and isolate a foreign quote or URL as its own LTR run. Do not use code styling for ordinary prose quotes.
- **Callout:** semantic label + small icon + editable text in a one-cell table or shaded/bordered paragraph. Mirror stripe, padding and icon placement in RTL.
- **Evidence image:** only when it explains content. Include concise alt text, figure number, caption, source/rights note, and enough resolution for the printed size.
- **Process/timeline:** one reading direction, numbered stages, labels outside connectors, no crossing lines. Mirror the journey for RTL only when the meaning flows right-to-left.
- **Comparison:** use a native Word table with row headers; do not use screenshots of tables.

## 4. Type, space and grid

Use styles rather than direct formatting. Typical body size is 10.5–12 pt Latin and 12–14 pt Arabic; use a tested Arabic font with distinct Arabic and Latin glyphs. Limit body line length, avoid cramped multi-column pages, and keep a consistent baseline rhythm. Use white space to group related material; decorative rules and color blocks are accents, not containers for every idea.

Arabic documents require a mirrored layout: side stripe and section ornament on the right, paragraph and heading starts on the right, and logical rather than physical left/right alignment. A separate code block, command, URL, DOI, formula or file path remains LTR even inside an RTL page.

## 5. Image and asset rules

Prefer owner-supplied or original visuals. For external assets, record creator, source URL, license/permission, modification and intended figure. Do not use a trademark or brand logo merely because it is searchable. Decorative images must be removable without changing the factual meaning of the document.

## 6. Visual release gate

At 100% rendered-page review, check: hierarchy is visible; all text is selectable; no clipped elements; no unexplained blank page; icon/figure consistency; contrast and grayscale legibility; captions and source notes; correct RTL mirroring; and no visual obscures evidence. Mark Word Desktop verification separately from structural or LibreOffice verification.
