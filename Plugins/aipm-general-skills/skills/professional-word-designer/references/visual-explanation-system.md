# Visual Explanation System for Word Documents — Normative v3.0

**MUST READ for EVERY content-bearing visual.** This is a deterministic editorial decision system, not a quota. Rendered illustrations in `assets/visual-examples/` are normative examples of component **type, visual hierarchy, direction, and information density**; substitute real content and valid evidence, never copy example statistics as facts. The selection algorithm takes precedence over a designer's decorative preferences.

## 1. Visual selection algorithm (execute per candidate passage)

1. Write the reader's exact learning task as an action: *identify*, *see appearance*, *follow sequence*, *compare*, *understand cause*, *locate relationships*, *interpret measured data*, *apply code*, or *none*. If task is `none`, use **no visual**.
2. Identify the content's shape: a short atomic cue, visible real-world subject, sequential actions, branching decision, non-linear concepts, comparable attributes, observed numeric values, temporal events, executable/literal code, or contextual warning.
3. Apply decision table below in order. **Never use a decorative icon as a substitute for content that needs a figure**. A paragraph may need no visual; a concept map must not imply causality or direction unless the source supports it.
4. For each planned visual, record `learning_goal`, `visual_type`, `trigger`, `source/data ledger IDs`, `asset license`, `caption`, `alt_text`, `editability`, `RTL/LTR layout`, `Word fallback`, `review_status` in the Visual Register. Unfilled required fields block delivery.
5. Pair each visual with a sentence that introduces it; place it at or immediately after the relevant passage; add a meaningful caption; keep figure/caption together.
6. Read the page image at 100% to confirm figure legibility and no caption drift. Test absence: if removing the visual does not lower comprehension, remove it.

| Reader task / qualifying condition | **MUST select** | **MUST NOT** | Reference example |
|---|---|---|---|
| One recognisable action or category requiring rapid scanning; at most one phrase | Small consistent **icon with adjacent text** | Icon alone for crucial content; photo replacement | `04-icon-rule` |
| Appearance of an actual object, anatomical location, interface control, material, place or device is the learning objective | Annotated **instructional photo/screenshot** with permission and credits | Fabricated photo as factual proof; unlabelled stock image | `05-annotated-image` |
| Spatial construction, anatomy, conceptual component arrangement where photos obscure critical parts | **Labeled educational illustration** | Unexplained dramatic artwork | `06-illustration` |
| Actions have a fixed start and ordered steps | **Sequential flowchart** | Mind map; decorative arrows | `07-process-flow` |
| Choice changes the next action (if/else, diagnosis, classification) | **Decision diagram** with explicit branching conditions | Non-labelled branching | `08-decision` |
| The question is how a central concept relates to several subtopics, without implying a timeline | **Mind map / concept map**, labels on each edge if semantics matter | Use when sequence matters | `09-mindmap` |
| Items are being evaluated on **the same named criteria** | **Comparison table**; comparison cards only if <=4 criteria and visual scanning is beneficial | Distorted bars with no common baseline | `10-comparison` |
| Authentic measured quantities, time series or proportions, with source, units and sample | Appropriate **chart** (bar/line/dot), honest zero baseline for bars | Generated numbers; 3-D distortion; unlabeled axes | `11-data-chart` |
| Chronological milestones, exact dates, or phases | **Timeline** | Flowchart if events are not action steps | `12-timeline` |
| Geographically situated facts or route | **Map** only with verified geographic data, labels and license | Unverified route or guessed coordinates | `13-map` |
| Call out a caveat, important detail, safety caveat, short worked example | Native Word **callout box**, optional semantic icon | Replacing complete explanation with warning icon | `14-callouts` |
| Literal short command/function/identifier in prose | **Inline Code** character style and bidi isolation | Screenshot of text/code | `15-inline-code` |
| Multi-line source code requiring preserved spaces/newlines | Editable **Code Block** paragraph/table with optional syntax emphasis | Screenshot of code | `16-code-block` |
| Reader needs direct navigation, cross-reference or deep linking | Native Word **TOC / bookmark / caption REF / hyperlinks** | False clickable static label | `02-toc`, `17-cross-reference` |
| Question can be explained succinctly as text with no structural ambiguity | **No image/icon/diagram** | Decorative filler, mandatory visual count | `18-no-visual` |

## 2. Precise routing and tie-breaks

- REAL APPEARANCE outranks generic illustration; choose an annotated instructional photo when trustworthy/authorized, else draw a clearly labeled schematic and **state it is schematic**.
- PROCESS outranks MIND MAP if order or decision path is consequential.
- MEASURED DATA must be sourced; when numeric evidence is absent, use conceptual comparison **without charts, percentages or fabricated scales**.
- Avoid simultaneous icon + image + chart for the **same small fact**; consolidate into one teaching component.
- In lengthy sections, prefer a single legible visual over four tiny ones. For labels below printable minimum, increase figure size or simplify and place detail in caption.
- Default illustration style: clean 2D vector, muted navy/teal highlights, no fake shadows, 1–2 accent colors, high contrast, no watermark or made-up authority logos.
- For genuine photos, capture/obtain usage rights, keep image provenance including file/author/license/source. No unlicensed web-image harvesting.
- For icon sets, pick one family per document, equal optical size and line weight; always include adjacent label and add alt text only if informative. Decorative icons get empty alt text rather than redundant narration.
- For chart data: a source-ledger ID, units, observation date, data table or CSV, and an explanatory caption are mandatory.
- For maps: use verified spatial data and mark routes and distances as illustrative if not verified; check geographic licensing.

## 3. Word-native vs companion interactivity

DOCX may use **live Word chart objects**, actual image alt text, heading navigation, native tables, hyperlink/bookmark navigation, real fields (TOC, PAGE, SEQ, REF) and editable elements when the generator supports them. DOCX **does not execute webpage JavaScript charts**; deliver a static Word counterpart and a clearly separated accessible HTML/InfoBank interactive companion when requested. Use `scripts/export_html_companion.py` only as a small interactive demonstration, not as a full Word conversion. Label static graphics honestly.

## 4. Bidi, sizing and accessibility contracts

- Arabic: `w:bidi=1`, right-side callout stripe, right-to-left arrow flow when culturally appropriate and semantically accurate, preserve English names/functions inside directional runs. English/Russian default LTR. A copied screenshot with English-only UI must be localized or clearly identified as an original UI screenshot.
- Letter/A4 report: figure fits text width; typical body 10.5–11.5 pt, figure title at least 9 pt and internal annotation roughly >= 9 pt at printed size. Do not use a minuscule multi-column chart.
- Alt text: explain the educational information **not** generic 'picture of' or duplicate nearby words; for complexity, include equivalent prose or accessible data table.
- Captions: `Figure N — What it proves or explains. Source: ...` localized per document. For altered/synthesized graphics identify: `Adapted from [n]` or `Diagram prepared from [n]`.
- Native tables: header flags and repeating rows, clear cell order; use real styles, not screenshot tables.

## 5. Deterministic validation contract

Before inserting a visual assert all:
`educational_gain=true`, `matching_type=true`, `asset_rights_verified=true_or_original=true`, `provenance_present_if_factual=true`, `caption_present=true`, `alt_or_decorative_flag=true`, `direction_test_passed=true`, `legibility_test_passed=true`, `not_redundant=true`. If any fail, repair or **omit**. Record the decision and reason in `Visual Register` (example `examples/visual-register.json`).

## Diagram geometry and no-overlap release gate (mandatory from v3.1.0)

- Route connectors to the **outer boundary** of a node, NEVER from or through its text center. Orthogonal/elbow connectors are preferred when a straight line would cross a label or another node.
- Draw edges behind shapes and labels (SVG z-order: edges first, then nodes, then text). Preserve a visible separation between a connector and every other unrelated node.
- For mind maps and all charts, maintain an explicit bounding-box ledger for boxes and text. Reject layouts with line/arrow crossings through protected node rectangles or text bounds; inspect the **final rendered output**, not only the SVG source.
- For Arabic/Russian/English, expand text bounds after actual text shaping, fonts and bidi layout. When words wrap or labels grow, reroute connectors; do NOT shrink important text below readable size.
- Before DOCX delivery render every page. An agent must correct line/label occlusion, clipped arrows, illegible connectors and figure/caption breakup, then rerender; a passed SVG unit test alone never guarantees Word renderer output.
- Run `python scripts/validate_diagram_geometry.py` and the diagram regression test. The numbered example `09-mindmap.svg` is normative for lines terminating at node boundaries.
