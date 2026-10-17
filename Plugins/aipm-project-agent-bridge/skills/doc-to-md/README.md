# Doc to MD — v1.0.0

Offline-first, original Python-powered **conversion + quality-audit Skill** built for AI agents that must understand user-supplied files without trusting an incomplete extraction.

**Input → Markdown + machine-readable audit → verification decision.** The goal is **reliable AI comprehension**, not pixel-perfect reproduction. No Microsoft MarkItDown code or MarkItDown dependency is present.

## Features

- Native parsers for `.txt`, `.md`, `.log`, `.rst`, `.yaml`, `.yml`, `.toml`, `.json`, `.jsonl`, `.csv`, `.tsv`, `.html`, `.htm`, `.xhtml`, `.xml`, `.docx`, `.pptx`, `.xlsx`, `.epub`, `.zip`.
- Optional local PDF (`pymupdf`), legacy `.xls` (`xlrd`), image OCR (`tesseract`), and media transcription (`faster-whisper` with a pre-existing local model).
- Arabic, Russian and other Unicode handled as UTF-8. Tabular literal `NA`, `NULL` and leading zeros not coerced to NaN by a data-frame layer. Formulas retained as source expressions, not evaluated.
- Per-document SHA-256 provenance, per-object counters, safety controls on archives and XML, explicit error codes and fail-closed `PASS`/`REVIEW`/`BLOCK` decisions.
- Page, sheet and slide markers; original files never overwritten. `--allow-review` does not falsify the audit status.
- No network services, LLM keys, model downloads, paid endpoints or MarkItDown dependency.

## Quick Start

```bash
python scripts/doc_to_md.py "input.docx" -o "output.md"
python scripts/doc_to_md.py "input.pdf" -o "output.md" --ocr-lang ara+eng
python scripts/doc_to_md.py "recording.wav" --audio-model-local "C:/models/faster-whisper-small"
python -m unittest discover -s tests -v
```

Sample output names: `output.md` and `output.md.audit.json`.

**Exit codes:** `0` clean PASS or explicitly allowed REVIEW; `2` REVIEW needs manual source verification; `3` BLOCK prevents confident use. For a missing file, unsafe output path, or CLI misuse `argparse` exits with `2`.

**Installing optional parsers in a project-specific environment:** `python -m pip install pymupdf pillow xlrd faster-whisper`; install Tesseract and relevant OCR language packs separately. Only install needed extras after reviewing their licenses/security and resource cost.

## Quality And Known Limitations

The engine is intentionally conservative: multi-column PDFs, scanned text, editable mathematical equations, merged table cells, charts, incomplete speaker notes, formula caches, OCR language detection, reading order and EPUB spine can be ambiguous. A `REVIEW` or `BLOCK` finding is **expected behavior**, not a successful lossless conversion. See [Coverage And Limits](references/Coverage-And-Limits.md) before relying on results. Exact 100% fidelity for arbitrary files is impossible to promise.

## Structure

- `SKILL.md`: agent instructions, trigger rules, verification and escalation.
- `scripts/doc_to_md.py`: original CLI implementation.
- `tests/test_doc_to_md.py`: offline synthetic regression tests.
- `references/Coverage-And-Limits.md`: current capabilities, failure-mode defenses, limits and backlog.
- `VERSION`, `CHANGELOG.md`: independent Skill SemVer and development history.

## Attribution

Microsoft's [MarkItDown project](https://github.com/microsoft/markitdown) and [public issues](https://github.com/microsoft/markitdown/issues) were used as **comparative requirements research** (format list and common failure categories). No implementation code, assets, tests, or documentation were copied or adapted. MarkItDown remains Microsoft's separate MIT-licensed work; this Skill follows the Universal AI ToolKit's repository license. This is **not an external-derived Skill** or registered fork.
