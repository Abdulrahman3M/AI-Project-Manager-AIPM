# Design system — professional research and educational Word

This is a responsive *editorial framework*, not a mandatory template. Research seriousness comes before color or card density. Specific user and institutional guidelines override defaults.

## 1. Document and page architecture
- Default A4 portrait, margins typically 2.0–2.5 cm. For bookbinding or extensive notes, account for gutter and print trim. Use landscape section **only** when a diagram or comparison needs it.
- For longform: minimalist cover (topic, useful subtitle, date/author/organization **only if provided**), optional short abstract or learning outcomes, real TOC, introduction, clear Heading 1–3 sections, occasional well-justified teaching components, conclusion, optional glossary/appendix, complete bibliography.
- Keep an even typographic rhythm; generous but disciplined white space. Avoid repeated title cards, ornamental empty pages and giant icons.
- Use Word paragraph styles for **all** headings, paragraphs, captions, quotations, callouts and references. Never simulate indent or alignment with chains of spaces.

## 2. Typography and direction
- Typical Latin body: 10.5–12 pt; Arabic body: 12–14 pt as needed for font; heading 1: 19–24 pt, heading 2: 14–18 pt. For Russian, select a Cyrillic-complete face and verify every glyph.
- Maintain appropriate line spacing (~1.25–1.45 subject to font). Avoid fully justified text where narrow columns or Word's Arabic justification introduce visibly unnatural rivers or stretched ligatures.
- A high-legibility neutral, one principal accent, one secondary accent and purpose-specific warning colors; maintain accessible contrast. Check grayscale legibility. Avoid novelty fonts and emoji as critical icons.
- For Arabic: set correct RTL paragraph direction and, where supported, complex-script language. English/Latin acronyms, URLs, DOI and code are isolated LTR runs rather than manually reordering characters.

## 3. TOC — strict specification
- A long report's contents page uses a real Word TOC built from **Heading 1–3**, not manually typed lines. Recommended navigation: TOC instruction `TOC \o "1-3" \h \z \u` (the native OOXML `w:instrText` contains these field switches with ordinary single backslashes).
- Style **TOC 1/2/3** separately. Each entry has its proper heading indentation, a right-aligned tab with a **dot leader** and the matching page number at the physical opposite edge of the content line. In RTL documents, verify the actual tab placement and reading order in the renderer and in Word; don't assume English defaults work when mirrored.
- Hyperlink TOC labels to actual heading bookmarks if supported by the chosen generator and editor. Refresh fields after all pagination-sensitive changes; audit page numbers and random links. Provide the Word-specific fallback **References → Update Table → Update entire table** if field caches remain stale. Do not label a static TOC auto-updating.
- Omit cover/page numbers from visible body numbering when requested via separate sections; validate page numbering after section changes.

## 4. Header, footer, logo
- Use a `different first page` section or blank cover header/footer. For body pages, subtle rule, running document title, and **current Heading 1 text** using a real `STYLEREF` field *when supported and tested*. If field behavior is unreliable for the target editor or RTL, use explicitly separated chapter sections and synced section headers, and verify on each page.
- Put actual `PAGE` fields in the footer (optionally PAGE of NUMPAGES if requested), consistent with section page-number scheme; for Arabic, test numerals and alignment visually.
- Logos are **optional supplied/authorized assets**; never hallucinate an institutional logo. Use small uncluttered placement, adequate padding, and alt text when meaningful.

## 5. Native note/callout color tokens
Use editable **one-cell border-controlled Word tables** or robust paragraph shading/border when available. Preserve text as selectable and allow box to flow across pages when necessary. Colors below are defaults, not hard institutional standards.

| Semantic block | Suggested fill | Side stripe | Icon | Usage |
| --- | --- | --- | --- | --- |
| General information | #EDF5FF | #2B65A2 | outline information | Supporting context or definition |
| Important note (amber example) | #FFF2E0 | #C43E32 | outline exclamation/circle | Reader attention; requested amber + red stripe |
| Practical tip | #ECF7F1 | #2C7954 | outline lightbulb | Actionable guidance |
| Warning | #FFF0EE | #B3342A | outline triangle | Real risks, not normal facts |
| Example | #F3F4F6 | #727A88 | outline book | Illustrative scenario |

**Directional rule:** keep the colored vertical side stripe on the right for RTL blocks and on the left for LTR blocks. Arabic box icons/headings/text start on the right; mirror interior spacing. If mixed-language box contains a separate full code snippet, the snippet itself remains LTR. Don't rely on color alone: add a plain-text label and a small coherent icon.

## 6. Visual placement and captions
- Visuals should break up difficult concepts where they are discussed, not cluster at random. Add numbered `Figure N — ...`/localized captions and a short source note below each sourced graphic.
- Use native editable Word tables for comparisons and Word chart objects if feasible and data is real. Prefer compatible SVG/vector assets if target Word validates; otherwise high-resolution PNG at actual printed size. Maintain a text-readable alternative and editable diagram source on request.
- Mind maps: legible central idea and generally <=5–7 main branches per page; split sprawling maps instead of shrinking all text.
- Ornament: restrained title underline, rule, abstract corner motif. Do not overshadow scientific images, prose, citations or table labels.

## 7. End-matter
- Numbered bibliography in citation-number order for the default numeric style, hanging indent where it improves scanning; preserve DOI or stable URL as real hyperlinks when possible.
- Figure credits and data notes live with their figures or in a clearly cross-referenced credits section. Optional glossary defines technical terms with original-language spellings where useful.
