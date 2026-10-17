# Advanced Word Feature Matrix and Implementation Playbooks

| Feature | Method | Hard pass check | Illustrated sample |
|---|---|---|---|
| Cover + introduction | Separate first-page header; hero title, subtitle, author as provided | Clean render, no invented affiliation/logo | `01-cover` |
| Automatic TOC | Real `TOC \\o "1-3" \\h \\z \\u` + heading styles; leader dots | Field present; **cached page numbers only after compatible Word refresh** | `02-toc` |
| Running chapter header | `STYLEREF "Heading 1"` where verified or fixed section header | Repeats accurate current section; no title on cover | `03-header-footer` |
| Page numbers + footer | PAGE and optional NUMPAGES field with user-provided logo only | Field XML and page display | `03-header-footer` |
| Inline citations | `[n]` linked to evidence ledger; reuse ID for same source | No orphaned/mismatched in-text number | `19-citation` |
| Bibliography | Complete traceable entries, DOIs/URLs where available | Every used ID listed; no unreferenced filler | `20-bibliography` |
| Callout styles | Native single-cell Word table, cell shading + RTL/LTR stripe border | Correct stripe side, editable words, headings | `14-callouts` |
| Icons / image | One family; source/rights record; adjacent explanatory label | Semantic justification & alt text | `04-icon-rule`, `05-annotated-image` |
| Flow / mind map | Prefer editable shapes if reliable, else high-resolution source SVG/PNG with source | Text legible at 100%, data source/caption | `07-process-flow`, `09-mindmap` |
| Tables/charts | Native where feasible, CSV source for quantitative data | Axis, units, truthful scales | `10-comparison`, `11-data-chart` |
| Figure/table TOC | Caption with `SEQ Figure`, table with `SEQ Table`; actual `TOC \\h \\z \\c Figure` if verified | Cross-refs and compiled list after refresh | `21-list-of-figures` |
| Internal REF | Bookmark each figure number, insert REF/PAGEREF fields | References resolve after refresh | `17-cross-reference` |
| Accessibility | Real heading levels, table header marking, image alt, reading order | `audit_docx.py` no critical failures; human check | `22-accessibility` |
| Code | Word Code Inline and Code Block custom styles; isolate bidi | Spaces/newlines preserved, copyable | `15-inline-code`, `16-code-block` |
| Multilingual | Per-language editorial edition + language metadata where supported | Independent language terminology QA, mirrored callout | `23-multilingual` |
| Interactive material | Real separate accessible HTML companion and static Word summary | Equivalent data and explicit file-type labels | `24-html-companion` |
| Review mode | Save original/revised, paragraph diff; native comments only with proper tooling | No destructive rewriting, verify XML when tracking | `25-review-diff` |
| Full QA | Render full DOCX with all pages; inspect page images | No clipping, missing captions or orphan headers | `26-render-qa` |

## Semantic design rules

Every example has **PASS**, **FAIL** and **selection trigger** in `examples/ILLUSTRATED_PLAYBOOK.md`. Visual examples are deliberately schematic design references, NOT factual source illustrations. They must never be copied as research evidence.
