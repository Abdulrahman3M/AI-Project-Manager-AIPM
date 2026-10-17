# Meaning-driven visual components and InfoBank companion guidance

## A. Choose the right visual form

| Reader question | Best first choice | Production rules |
| --- | --- | --- |
| What does this term mean? | Definition callout + small line icon | One concise idea and exact terminology |
| What should I be careful about? | Important note or warning box | Semantically justified severity, non-color label |
| How does this work? | Numbered steps or flowchart | Consistent arrow direction, readable at print scale |
| How are these ideas connected? | Mind map / concept map | Clear center, selective branches, no misleading implied causal edges |
| How do A and B differ? | Native comparison table | Balanced comparable attributes, source notes |
| What happened when? | Timeline | Grounded dates and no invented chronology |
| What does the object/process look like? | Labeled educational illustration | Legible labels, meaningful anatomy/parts with verified terminology |
| What does the evidence quantify? | Sourced, labeled chart | Actual numeric data, axes/units/sample/period when applicable |
| What command or markup should I use? | `Code Inline` or `Code Block` | Literal correct code; LTR even in Arabic article |

## B. Visual evidence and accessibility
- Plan each visual with `purpose`, `source IDs`, `visual type`, `key labels`, `caption`, `alt text`, `language`, `editable version needed?`, `location` and `companion needed?`.
- Every graph needs an identified underlying dataset: units, dates, population/period if relevant, and caveats on aggregation; never design a pretty chart from invented numbers. Use explanatory annotations without obscuring uncertainty.
- A mind map is a visual organization aid; distinguish known hierarchical categories from hypothesized relationships and never claim causal evidence solely through arrows.
- Icon set should be stylistically uniform in stroke thickness, size and use; use appropriate icon color and text labels. No scatter of unrelated emoji, photos or repeated purely decorative images.
- Place images close to the corresponding explanations with numbered, localized figure captions and credits. Recreate diagrams from legitimate sources with attribution; comply with licenses for reused images and assets.

## C. Interactive-looking Word versus interactive HTML
**Possible inside DOCX:** clickable TOC, bookmarks, references and external links; editable tables and perhaps native Word chart/data workbooks when built and tested; static maps, step diagrams, decision trees, concept maps and infographics.

**Not equivalent inside DOCX:** executing InfoBank's JavaScript visualization library, filtering a graph on hover, unrestricted drag-and-drop node editing, browser-specific 3D and interactive state. Do not label a still image or a clickable reference as a fully interactive graph.

If a separately requested interactive edition will be published in **InfoBank**, create a companion HTML/JavaScript component following the project's actual library/version and security/accessibility conventions. The skill must not guess a third-party library or mutate an InfoBank project without access to its configuration. Establish visual parity between the Word version and the interactive companion: same facts, labels, units, warnings and source credits. Maintain text alternatives, keyboard support and the ability to print/export a static fallback.

## D. Source and editable-asset manifest (when companions are supplied)
- Include only requested or materially useful extra deliverables such as `assets/figure-01.svg`, `assets/figure-02.mmd`, `assets/data-chart.csv`, or `companion/interactive-example.html`; each companion documents which Word figure it corresponds to.
- Captions should be informative: “Figure 3 — Stages of X ...”; “Source: [4]”; “Adapted from [5] with permission” only when permission exists. Include tool attribution when contract/licensing requires it, rather than invented original authorship.
