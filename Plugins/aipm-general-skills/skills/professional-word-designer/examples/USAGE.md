# Quick reproducible execution examples

| Goal | Sample command / mandatory reference |
|---|---|
| Start a substantial research publication | `references/document-contract-v5.md` → `references/research-to-word-pipeline.md` |
| Review all fine-grained v5 examples | `examples/NORMATIVE_EXAMPLES.md` |
| Validate all 124 v5 requirements have examples | `python scripts/validate_example_coverage.py` |
| See all 26 pictured visual features | `assets/visual-examples/*.png` + `examples/ILLUSTRATED_PLAYBOOK.md` |
| Validate a claim matrix | `python scripts/check_claim_coverage.py examples/sample-claim-evidence.json` |
| Validate source metadata | `python scripts/validate_reference_metadata.py examples/sample-source-ledger-v5.json` |
| Find likely duplicate references | `python scripts/deduplicate_references.py <source-ledger.json>` |
| Aggregate baseline Research QA | `python scripts/research_qa.py --sources <sources.json> --claims <claims.json> --examples examples/EXAMPLE_COVERAGE.json --output research-qa.json` |
| Validate a chapter manifest | `python scripts/validate_chapter_manifest.py chapter-manifest.json --check-files` |
| Build the Word Index for a chapter package | `python scripts/build_chapter_index.py chapter-manifest.json --check-files` |
| Generate editable baseline DOCX | `python scripts/build_document.py --input examples/sample-document.json --output demo.docx --profile visual-textbook` |
| Verify actual Word structure | `python scripts/audit_docx.py demo.docx --require-toc --require-alt --json audit.json` |
| Render to page PNGs | `python scripts/render_and_audit.py demo.docx --output-dir rendered/` |
| Run tests | `python -m pytest tests -q` and `python tests_check.py` |

**Demo warning:** sample research/source/claim/chapter files are fixtures only. Replace every demonstration claim/source with real verified evidence. TOC/REF/SEQ/STYLEREF displayed values may require a compatible Word field refresh. Keep Chapter Package files together so relative links from `00-Index.docx` continue to resolve.
