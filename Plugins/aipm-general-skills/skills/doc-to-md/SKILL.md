---
name: doc-to-md
description: Convert locally supplied files, Office documents, PDFs, scans, tables, presentation slides, EPUBs, images and recordings to evidence-audited Markdown for AI understanding. Use whenever an AI agent needs to read, extract, index, quote, or analyze the contents of user-provided files. Preserve structure and provenance, audit conversion losses, reject unsafe formats and do not treat uncertain output as authoritative.
---

# Doc to MD

An **original implementation** in the Universal AI ToolKit. It is informed by public format requirements and observed conversion-failure categories, **not copied, forked, modified or imported from Microsoft MarkItDown**. Its executable reference implementation is `scripts/doc_to_md.py`. MarkItDown is neither a runtime nor a dependency.

## Critical Contract

1. Only process the user's supplied or expressly authorized files. No network calls or paid AI calls. Do not install software or send private content to third parties without permission.
2. Use the **narrowest available native reader** when a platform directly supplies trusted file text/page images. If using the bundled offline CLI, execute it and inspect the JSON audit, **not just the Markdown**.
3. Preserve source untouched. Separate Markdown and `.md.audit.json` outputs, including source SHA-256, Markdown SHA-256, issue codes and coverage counters.
4. `PASS` means no *detected* risk, **never proof of perfect fidelity**. `REVIEW` means the AI must consult original page/slide/cell media before making high-confidence claims. `BLOCK` means no usable assured extraction; do not infer content.
5. Never silently discard known unparsed equations, charts, images, tables, slide elements, speaker notes, OCR text, transcription, hyperlinks, layout uncertainty, hidden sheets, or suspicious decoding. Create a finding and, where important, keep an explicit placeholder in Markdown.
6. For PDFs with multi-column or complex layouts, compare extracted reading order with source-page view; for Word mathematical objects, compare original formulas; for Excel, protect raw numbers, formulas, cell types and zero padding; for presentations compare slide geometry, grouped shapes and notes.
7. Do not rephrase original text, fabricate missing characters, normalize away source facts or claim a source is complete based on output length alone. Preserve Arabic/Russian/other Unicode faithfully. Distinguish source content from AI annotations.
8. On partial failures, report failed sections and recovery options. Do not hide `REVIEW`/`BLOCK` by passing `--allow-review`; that option modifies only the exit code and never changes the audit status.
9. Never execute embedded Office macros, HTML scripts, archive members, documents, or links. Enforce archive bounds and reject unsafe paths. Do not resolve untrusted URLs automatically.
10. For legal, medical, financial, archival or verbatim requirements, **require original-source comparison** even when the converter emits `PASS`.

## Workflow

1. Identify file extension, volume, sensitivity, expected exactness, and available local converters. Compare to `references/Coverage-And-Limits.md`.
2. Run from an isolated environment: `python scripts/doc_to_md.py /path/input.pdf -o /path/output.md`. Optional: `--ocr-lang ara+eng`, `--audio-model-local /models/whisper`, `--allow-review`, `--overwrite`.
3. Read both output files. If exit code `3` / status `BLOCK`, do not rely on generated Markdown. If exit code `2` / status `REVIEW`, inspect source and correct/re-extract with a suitable alternative. Exit `0` / `PASS` still requires task-appropriate spot checks.
4. Validate for missing sections/pages/slide counts, expected numeric strings, table cells, equations, scripts, OCR confidence and embedded objects. Compare page ranges against source; do not announce completeness without evidence.
5. Deliver Markdown, companion audit, and precise qualifications. For AI ingestion, include references to original source, page/sheet/slide markers, plus a warning list. Never discard the audit.

## Optional Tools And Setup

- Core: Python 3.10+ standard library (no cloud costs).
- PDF: locally installed `pymupdf`.
- OCR: locally installed Tesseract command and target language packs; Pillow optional for image metadata.
- Audio/video: locally installed `faster-whisper` plus **existing local model directory**; may additionally require FFmpeg for non-WAV decoding. The bundled implementation never downloads models.
- Legacy XLS: locally installed `xlrd`.
- HTML, CSV/TSV, DOCX, PPTX, XLSX, EPUB, XML, JSON/JSONL, text and ZIP: baseline adapters do not require additional packages.
- Dependencies are **optional per format**, not installed automatically. Missing capabilities trigger `BLOCK` findings.

## Test And Release Gate

Run `python -m unittest discover -s tests -v`, then run independent fixtures from each required format. If exact content preservation cannot be verified, mark the Skill experimental for that format and keep a blocking or review finding. A green synthetic test suite is **not** equivalent to corpus-level coverage.

## Boundaries

The v1.0.0 reference engine is a cautious functional foundation, **not** a perfect all-format replacement. Native complex PDF table topology, high-fidelity OMML-to-LaTeX, rich PowerPoint charts/grouped geometry, Excel display formatting and formula recomputation, EPUB spine fidelity, HTML merged tables and automatic YouTube fetching need further implementations. The current engine flags many of these, but does not fully resolve them. Never claim the full upstream feature set or universal accuracy without format-specific test evidence.

Read `README.md` for commands, `references/Coverage-And-Limits.md` for the explicit support matrix and risk register, `tests/` for regressions and `CHANGELOG.md` for release history.
