# Word production — implementation contract

This guide defines what must be present in the **actual DOCX package**, not merely in the rendered appearance. Use stable authoring tools appropriate to the agent environment (for example `python-docx` plus OOXML fields when needed), and verify resulting `.docx` in target Word-compatible renderer(s). Never report a feature as dynamic when only decorative text was produced.

## 1. Structural foundation
- Define real paragraph and character styles: `Title`, `Subtitle`, `Heading 1`, `Heading 2`, `Heading 3`, `Body Text`, `Caption`, `Quote`, `References`, `Callout Title`, `Callout Body`, `Code Inline`, `Code Block`, `TOC 1–3` as applicable. Assign the appropriate outline levels to headings.
- Use genuine section breaks for cover/body/landscape appendix or alternate page numbering. Set `different first page` where cover header differs. Set document and paragraph language and bidi properties for Arabic; don't fake RTL using only right alignment.
- Prefer native tables and lists, with explicit header rows and clear reading order. Handle row splitting and headings near page breaks (`keep with next`, `keep lines together`) thoughtfully.

## 2. Clickable, dot-led, numbered automatic Table of Contents
- Build the headings before building TOC. Insert an actual Word TOC field, using `w:fldChar begin`, `w:instrText` containing `TOC \o "1-3" \h \z \u`, a suitable field result/cached display where possible, and `w:fldChar end`; a safe supported alternative is a simple `w:fldSimple` field if the generator/target editor handles it. Add `w:updateFields` on open if supported.
- Style `TOC 1`, `TOC 2`, `TOC 3` with appropriate level indents and a **dot-leader tab stop** ending in correctly aligned page number at the physical page edge opposite the TOC label. RTL needs an actual render and update test; English/LTR tab logic cannot simply be reused untested.
- TOC text should link to chapter/section headings (`\h`); validate at least a sample of links. Updating fields can affect pagination: update field cache with a capable desktop Word editor or renderer where available, re-render, then manually cross-check random TOC entries against final pages. LibreOffice and Word may render certain fields differently; state which was tested.
- When no capable field updater exists: preserve a real TOC field and explicitly say **“Open in Word, right-click the contents page → Update Field → Update entire table.”** Do not promise accurate visible page numbers unless verified. A static navigable table is a fallback only when explicitly disclosed and requested/necessary.

## 3. Dynamic running headers/footers and numbering
- On cover: suppress body headers/footer if not requested. In body: use small actual `STYLEREF "Heading 1"` field for the current major section **only after testing** across chapter boundaries. An alternative is chapter section breaks with per-section static header text and deliberately controlled `Link to Previous` settings; never call that alternative dynamically updated.
- Footer page number is a `PAGE` field, not typed digits. Optionally use `NUMPAGES` or section-specific `SECTIONPAGES` with tested result. Add small authorized logo only when supplied. Choose page-number start, numeric script and placement according to brief and verify first, middle, and last pages.
- Running text may require a stable abbreviated section title separate from H1; prefer supported style references, not fragile per-page hardcoding. Keep rule lines subtle and away from text margins.

## 4. In-text citations, reference cross-links, figures
- For default bracket style, insert `[1]` / `[1, 2]` after the claim or supporting paragraph. Hyperlink citation numbers internally to matching bibliography bookmarks if target editor and format reliably preserve them. **Citation numbering remains stable** when the same source reappears.
- Where the authoring environment supports source management reliably, native citation/bibliography features may be used if they actually match the chosen academic style. Don't imply manually numbered links are editable citation-manager fields.
- Insert native caption paragraphs and, when feasible, `SEQ Figure`/table fields plus `REF` cross-references. Chart/table notes name their data source. Ensure caption numbering and cross-references update after edits.
- Give external links meaningful link text where accessibility calls for it; preserve full identifiers in references. Footnotes/endnotes, if requested, must be **real Word notes** and verified, not merely superscript text.

## 5. Native callouts, note blocks, direction
- Build callouts from native one-cell tables or stable paragraph shading and a **single thick vertical border** (not a floating image of a box). Avoid tables nested so deeply that editability or accessibility suffers. Apply padding, readable small headings and non-color labels/icons.
- Amber + red attention block example: pale amber background `#FFF2E0`, red vertical border `#C43E32`. Put accent border **right for RTL** (`right` table border), **left for LTR** (`left` border). The border position is driven by the containing block's language/direction, not the document's overall language if the block is fully in another language.
- For long note blocks, avoid splitting a heading from its first line. Verify that multi-page boxes don't truncate, float over the footer, or create large unexpected gaps.

## 6. Inline code and boxed code examples
- **Inline code (`Code Inline`)** is a character style, e.g. restrained neutral shading and clear monospaced font; preserve literal backslashes, HTML tags and special symbols. In Arabic prose, wrap the code run with correct **LTR direction/isolation** and appropriate punctuation separation. Do not place literal code inside smart typographic quotes unless the text is an actual quotation.
- **Block code (`Code Block`)** is a paragraph group or one-cell native table with light-gray fill, subtle border, sufficient inset, monospaced font, text selectable/copyable, and all lines LTR for languages such as HTML/CSS/JavaScript/Python. Add an optional small language label and a code caption when instructive. Disable unwanted auto-correction of punctuation, smart quotes and list autoformat where possible.
- Do not force a long code line past margins; wrap deliberately and mark wrapping if it changes semantics, or use a wider landscape appendix. Retain accurate indentation; avoid accidental tabs auto-converted to lists. Include a short human explanation or sample output if it teaches something.
- DOCX code is **display-only**; no macros, remote script loading, or suggestion that an HTML/JS code sample runs inside Word.

## 7. Word graphics versus full interactivity
- Word-native editable chart objects with underlying datasets are preferable when technically supported; verify external link/update behavior before promising live data. Native tables and simple arrow shapes can be edited in Word; an inserted PNG/SVG may not expose fully editable nodes.
- Charts exported as images are **static**. Clickable internal links, cross-references, figure links and external hyperlinks add navigation, not JavaScript interactivity. JavaScript-based pan/zoom, filtering or hovering belongs to a separate accessible HTML/InfoBank companion, **only** when explicitly requested, with a static/print-safe Word version and clear correspondence.

## 8. Editability, accessibility, metadata
- Keep textual body and components editable; avoid whole-page screenshot design. Provide source `.svg`/`.mmd`/diagram specification as a companion when visual editability is requested but native Word can't reliably preserve it.
- Add alt text to instructional visuals and table headers when tooling supports it; do not encode meaning solely by red/green. Use correct reading order and hyperlink labels. Avoid uncontrolled tab traps and decorative icons treated as instructional content without description.
- Don't invent author names, company logos, image licenses or source attribution in document properties or cover. If metadata scrubbing is requested, remove personal/tool metadata without falsifying factual authorship.

## 9. Post-build technical audit
- Inspect the DOCX XML/structure if necessary: TOC field exists; Heading 1–3 are styles and not just formatted normal text; field update request exists where needed; `PAGE` and `STYLEREF` are present **if claimed**; bookmarks and hyperlink targets resolve; source IDs align; RTL code block isolation is correct.
- Render *every* page to PNG. Inspect cover, TOC and its page numbers, section boundaries and changing running headers, all callout border sides, code symbols, all graphics, citations/endnotes, reference section and last page. Fix, regenerate and inspect every page again after material changes.

## 10. Reusable style template (optional)
When the user asks for repeated documents in exactly the same design, create a companion `.dotx` template **only if supported and explicitly requested**, with documented styles and reusable cover/TOC/callouts; verify a new test DOCX instantiated from it. A style guide alone is not a working Word template.
