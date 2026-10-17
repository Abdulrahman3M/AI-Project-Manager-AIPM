# Quality gates — block release if any applicable requirement fails

**Gate 0 — deliverable contract**
- [ ] Reader, subject, output language(s), scope, desired length, user/institution style requirements and deliverable(s) respected; all requested features routed to a real implementation, with unsupported ones clearly distinguished.
- [ ] No made-up author qualifications, organizational branding, interviews, photos, licenses, examples presented as real experience, or quality claims.

**Gate 1 — content and genuine human-quality editing**
- [ ] Introduction explains what matters to the reader; all sections follow a logical teaching progression; conclusion synthesizes instead of repeating the outline.
- [ ] Every paragraph contributes: explanation, evidence, comparison, cause, example, limitation or synthesis. No generic AI boilerplate, repetitive sentence rhythms, fabricated anecdotes, content padding or artificial enthusiasm.
- [ ] Each source-derived and consequential fact has appropriate evidence. Claims with incomplete sourcing are explicitly qualified or withheld; dates and data limits are correct.
- [ ] Technical vocabulary is precise and consistent; calculations, names, data, captions and illustrative code are correct.

**Gate 2 — traceable references**
- [ ] All numbered in-text reference markers map to a real bibliography entry; repeated sources reuse the same number, citation order follows the selected style, and the bibliography contains no phantom works.
- [ ] Sourced paragraphs have appropriately placed markers (one source at paragraph end may suffice; split evidence if multiple claims need different support). Transitions and original illustrative text are not burdened with meaningless fake citations.
- [ ] Direct quotations have authentic wording, attribution and page/locator where needed. Figure/chart data sources, rights and source notes are recorded; URLs/DOIs are verified when tools permit.
- [ ] References section ends the research or appears in the location required by the institution, with consistent formatting and useful links.

**Gate 3 — editable Word structure, not a visual mockup**
- [ ] Real Word Heading styles and outline levels; native text, tables, appropriate section/page breaks and caption structure; no full-page flattening.
- [ ] When TOC required: actual field exists; TOC 1–3 style, dot leaders, page numbers and clickable labels if supported; entry-page accuracy checked after final pagination, or explicitly marked as requiring update in Word.
- [ ] Running chapter header behaves as claimed (`STYLEREF` or clearly disclosed section-header fallback), first-page behavior is intentional, footer has `PAGE` field, page number sequence and authorized optional logo are checked.
- [ ] Native editable callouts use the correct color, non-color label and **right accent in Arabic RTL / left in English or Russian LTR**; no stray cut-off borders or overflow.
- [ ] If requested: `Code Inline` style and block code box preserve literal syntax, indent and LTR direction in RTL document; code is selectable, not merely a screenshot.
- [ ] Footnotes, links, bookmarks, alt text, chart objects or companion diagram source have been implemented as claimed, not visually faked.

**Gate 4 — visuals and pedagogy**
- [ ] Every icon, comparison table, chart, diagram, mind map or educational photo answers an identifiable learning question. Unnecessary visuals removed.
- [ ] Chart values/axis labels/time period/units match actual source data; mind maps don't assert unsupported relationships; arrow direction corresponds to the document language and logic.
- [ ] Images/diagrams have readable labels, figure numbers and captions, source credits and meaningful alternative text. Asset licensing and quality checked.
- [ ] If interactive HTML companion requested, separately verify that it works with the actual target InfoBank/library environment. The Word graphic is clearly identified as static or natively editable, not false JavaScript interactivity.

**Gate 5 — multilingual and direction**
- [ ] Every delivered language edition has distinct grammar/idiom/terminology/caption/reference/TOC check; no promise of native proofreading unless completed.
- [ ] Arabic heading, tables, note borders, layout and mixed English technical terms render in correct RTL/LTR order. Latin URLs, DOI, quotes, inline code and code blocks preserve literal characters.
- [ ] English spelling variety, Russian idiomatic case/grammar/Cyrillic support and local punctuation reviewed as appropriate. No silent change to source meaning, qualifiers, quantities or cross-language citation IDs.

**Gate 6 — visual and structural release test**
- [ ] Render the final DOCX **all pages to images** in a real Word-compatible tool; examine every page at readable/100% zoom. Do not merely check the cover and random pages.
- [ ] No overlap, missing glyphs, clipped line, weak contrast, distorted graphic, unintentional blank page, orphan heading, broken table, overflowing citation, unbalanced note or hidden code text.
- [ ] Check cover; every TOC spread; first/last page of each chapter; changes in running headers and actual page numbering; every chart/callout/code box; source section.
- [ ] Automated structural check/spot checks agree with visible output: heading fields/cross-references/bookmarks where promised, all cited source IDs present and figures/data recorded. If field caches or target Word editor haven't been tested, state the limitation.
- [ ] After a fix that changes pagination or content, repeat field update + render + full inspection. The final file matches the final inspection, not an earlier intermediate.

## Required release-note format
- Actual file(s) delivered and document language(s).
- Features **verified**: TOC status, running header behavior, real page-number fields, source style, visuals, optional code components.
- Any unfinished QA, unavailable tools, non-native Word limitations or needed `Update Field` action; no success claims for unchecked items.
