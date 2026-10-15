# Four external approaches — concrete adaptation without copying code

| Public approach | Strong idea adopted | Local implementation/reference | Not falsely promised |
|---|---|---|---|
| [Anthropic public DOCX skill](https://github.com/anthropics/skills/tree/main/skills/docx) | Create → render → inspect → repair and OOXML-aware QA | `scripts/build_demo.py`, `scripts/audit_docx.py`, `scripts/render_and_audit.py`, `tests/` | We do not copy or bundle their code; no full comment/tracked-change engine shipped |
| [gertalot/docx-skill](https://github.com/gertalot/docx-skill) | Reusable editorial visual identity and type-system discipline | `style-profiles/*.json`, visual tokens, gallery, fonts are system installed | No external brand or copyrighted templates embedded |
| [Quarto](https://quarto.org/docs/output-formats/ms-word.html) | Source-of-truth publishing and reproducible cross-format concepts | `examples/sample-brief.json`, `scripts/export_html_companion.py`, Word visual fallback | No Quarto runtime or arbitrary MD→DOCX parity promised |
| [Zotero](https://www.zotero.org/support/word_processor_integration) | Managed research citations and updated bibliographies | `references/research-and-editorial.md`, `scripts/audit_docx.py`, `examples/sample-sources.json`; Zotero integration checklist below | Fake Zotero citation fields must never be generated |

## Optional Zotero route

- If Zotero desktop + Word integration exists, insert citations **using the real Zotero plugin within Word** and select the user-designated style (APA, IEEE, Vancouver etc). Then refresh the bibliography via Zotero before delivery and test the document in Word.
- If unavailable, create verifiable numbered citations and bibliography from source ledger. State they are **not live Zotero fields**. Do not mislabel them as editable Zotero objects.

## Optional Quarto route

- If Quarto is installed and source starts as Markdown/QMD, use a `reference-doc` to control styles, then export DOCX, verify OOXML fields and visuals, render every page. Check HTML and DOCX figure numbering/citations independently. Do not claim perfect equivalence without parity test.

## Editing and collaboration

- For existing DOCX, preserve original and produce revised DOCX + content-diff summary (`scripts/compare_versions.py`). If genuine tracked edits/comments are demanded, use verified OOXML-capable tooling (e.g., the host's trusted DOCX toolchain) and validate both XML semantics and visible layout. A diff text file is **not** Word Track Changes.
