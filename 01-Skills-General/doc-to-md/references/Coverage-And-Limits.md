# Coverage, Failure Modes, And Quality Limits

## Format Support

| Input | Baseline behavior | Unresolved/explicit audit risk |
|---|---|---|
| TXT/MD, JSON, XML | Local UTF-8 and structured text; reject XML entity declarations | Plaintext has no layout validation; XML representation is structural, not reconstructed source bytes |
| CSV/TSV | Preserve string literals and explicit empty cells | Original column widths and multiline CSV cell presentation require cross-check |
| HTML | Convert basic headings, paragraphs, links, lists, image alt and inline emphasis | Merged/complex tables, relative URLs, CSS and semantic layout may not survive; REVIEW |
| DOCX | Parse document paragraphs, heading styles, lists, simple tables, OMML presence | Merged cells, math rendering, hyperlinks, images, comments, headers/footers, textboxes, tracked changes need visual inspection |
| PPTX | Extract text from slides and notes; sort by shape geometry | Grouped shapes, charts, diagrams, text flow and same-row ordering are approximate; REVIEW |
| XLSX | Extract string and numeric raw values, formulas and sheet tables without pandas coercion | Sheet names, styled cell displays, rows/columns, merges, number formats, charts, formulas/cache validity need comparison |
| XLS | Optional xlrd; preserve nominal rows/cells | Numeric formatting/cell styles may be lost; REVIEW |
| PDF | Optional local PyMuPDF; preserve page markers, column detection | Tables, floating figures, equation text, mixed RTL/LTR, reading order, footnotes, cross-column text need visual review |
| Scan/Image | Optional local Tesseract and language data; PDF scanned pages can be rendered/OCR'd | OCR output always REVIEW; unrecognized characters, tables and diagrams demand source check |
| Audio/Video | Optional offline faster-whisper model; timestamps per segment | Speaker identity, word exactness, punctuation, music/noise, language recognition need verification |
| EPUB | Extract HTML chapters | Current filename-order approximation is **not spine-aware**; REVIEW |
| ZIP | Iterate supported members, reject path traversal/symlinks and zip bomb limits | Unknown subformats and failed members trigger BLOCK |
| YouTube URL | No automatic download/network capability | Not implemented in current reference engine. Prefer authorized, downloaded local audio/video input |

## Failure Modes Observed In Public MarkItDown Issues

The issue links below are research inputs, not evidence of the same bug in our implementation and **not a claim of fixes**. Each maps to an explicit regression or risk gate:

- [#2580 PDF form page causing column interleaving](https://github.com/microsoft/markitdown/issues/2580): detect columns and require visual sequence verification, page-scoped not whole-document order state.
- [#2565 OCR PDF glued columns](https://github.com/microsoft/markitdown/issues/2565): OCR always REVIEW, especially embedded images and multiple columns.
- [#2571 PPTX same-row order](https://github.com/microsoft/markitdown/issues/2571): test geometry sort, warn it is approximate.
- [#2569 unexpected shape aborts conversion](https://github.com/microsoft/markitdown/issues/2569): skip/review unsupported members without executing them; archive member failure gets explicit BLOCK.
- [#2573 DOCX OMML delimiter arguments](https://github.com/microsoft/markitdown/issues/2573), [#1512 missing equations](https://github.com/microsoft/markitdown/issues/1512): retain visible math markers and require original comparison instead of silently claiming mathematical fidelity.
- [#2532 Excel float precision](https://github.com/microsoft/markitdown/issues/2532), [#2498 literal NA/NULL changes](https://github.com/microsoft/markitdown/issues/2498): preserve raw XML strings and avoid pandas inference; assert representative digits/strings in tests.
- [#2536 HTML caption/colgroup header](https://github.com/microsoft/markitdown/issues/2536): flag complex HTML table parsing; do not claim it is repaired.
- [#2500 relative HTML links](https://github.com/microsoft/markitdown/issues/2500): issue explicit warning for base URL; no automatic fetch.
- [#2343 scanned PDF OCR detection](https://github.com/microsoft/markitdown/issues/2343): scanned pages handled page-by-page, missing OCR is BLOCK.

## Quality Decision Rules

- **PASS:** source and output hashes reported, no known missing required output or parser ambiguity found. Not a completeness certification.
- **REVIEW:** detected uncertainty, possible formatting loss, OCR/transcription, approximated geometry or cached formula. Must review original content.
- **BLOCK:** unsupported format, critical dependency missing, unsafe/corrupt archive/XML, exhausted limits, failed member, empty result or fundamental extraction error.
- **Quality gate:** run offline unit tests + representative real-world golden documents (Arabic mixed RTL, columns, scans, numeric fidelity, vector diagrams, tables, equations). Reject regression in reading order and numeric strings; never certify without golden corpus evidence.
- **Human oversight:** legally important or verbatim outputs require original comparison even on PASS; high-severity findings block unsupervised downstream use.

## Security And Privacy

No shell invocation with user-provided filenames; external executables get argument lists, `subprocess` timeouts apply to OCR; XML DOCTYPE/ENTITY prohibited; ZIP traversal and symlinks rejected, member/file/total size and nesting depth limited. The script does not run Office macros or remote downloads. For hostile content, execute in sandbox with CPU/memory constraints, ensure optional third-party parsers are updated, and keep outbound network blocked. The baseline archive/resource limits are not a replacement for OS-level sandboxing.

## Known Work Remaining

1. Build a layout-graph OCR/PDF parser preserving page coordinates and text-to-image linkage with robust RTL/LTR reading-order goldens.
2. Build native table extraction (merged cells, nested tables, spans) instead of lossy Markdown pipes.
3. Implement complete OMML-to-MathML/LaTeX with semantic verification and page-image math review.
4. Resolve OOXML relationships for hyperlinks, sheet names, hidden objects, speaker-notes shape ownership, grouped shapes, chart data and slide master content.
5. Preserve EPUB spine/nav, semantic HTML table layouts and relative link targets.
6. Add explicit optional YouTube/media ingestion with URL allowlisting, SSRF defenses, pinned executables, consent and offline-first policy.
7. Add byte-level source-to-output page coverage and screenshot-diff tools, realistic benchmark corpus, CI gates and measured accuracy thresholds.

**Release truth:** v1.0.0 is a tested foundation, not a verified all-feature parity engine. A review finding is honest degradation, not a solved layout defect.
