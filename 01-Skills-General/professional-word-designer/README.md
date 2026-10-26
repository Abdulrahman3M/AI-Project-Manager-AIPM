# Professional Word Designer — v5.1.0

**Professional Word Designer** is now a complete **research-to-Word publication system** for research papers, articles, reports, books, theses, educational materials and other long-form Microsoft Word documents. It combines evidence control, academic structure, citation management rules, native Word production, enterprise visual direction, reusable template patterns, multilingual/accessibility handling, long-document chapter packages and strict release QA.

## v5.1 enterprise visual and RTL upgrade

- Choose from 36 documented, original template patterns in `references/template-atlas.md`; adapt their hierarchy, spacing, typography, visual roles and guardrails rather than copying third-party template artwork.
- Use `references/enterprise-visual-design.md` for corporate-grade covers, executive summaries, callouts, icon systems, data displays, source-safe images and print-aware layout.
- For Arabic-first or mixed Arabic/English work, apply every required OOXML direction layer in `references/rtl-hardening.md`, then run `audit_docx.py --require-rtl` and inspect the rendered document in a capable Word engine.
- See `references/tool-landscape.md` for research-backed tool selection, security limits and non-fabrication rules.

## What v5 adds

v5 adds **21 major research/publication capabilities**, the owner's two new requirements, and the infrastructure needed to make those capabilities testable rather than descriptive. The capability surface includes Research Intelligence, Claim–Evidence Matrix, source-quality classification, multiple citation styles, Academic Document Modes, literature synthesis, metadata validation/interchange, front matter, native math rules, glossary/acronyms/index, long-document layout, template fidelity, journal submission, reviewer workflow, reproducibility artifacts, consistency analysis, attribution-safe originality review, table/figure intelligence, Research QA and a full Research-to-Word Pipeline.

### 150 normative examples

The existing **26 illustrated examples** remain unchanged for visual grammar. v5 adds **124 fine-grained normative examples** across 31 domains. Every v5 requirement has a stable `REQ-ID` and mapped example; `scripts/validate_example_coverage.py` must report **100%**.

### 100+ page Chapter Package Mode

For documents estimated or rendered at **100 pages or more**, the default is to split the publication into chapter DOCX files plus `00-Index.docx` and `chapter-manifest.json` unless the owner requires one file. The Index is a real Word document whose chapter titles can use **relative external hyperlinks** to open the chapter files. `scripts/build_chapter_index.py` implements this baseline.

## Core v5 pipeline

Document Contract → Research Plan → source discovery → evidence quality/ledger → Claim–Evidence Matrix → contradiction/gap analysis → academic structure → drafting/synthesis → citation engine → visuals/tables/math/front matter → Word layout → Research QA → DOCX QA → field refresh → rendered-page QA → release package.

## New machine-readable layer

`schemas/` contains contracts for document intake, research plan, source ledger, claims, citations, chapter packages, example coverage and Research QA. Sample fixtures are under `examples/`.

## New deterministic tools

- `validate_example_coverage.py`
- `check_claim_coverage.py`
- `validate_reference_metadata.py`
- `deduplicate_references.py`
- `research_qa.py`
- `check_document_consistency.py`
- `validate_chapter_manifest.py`
- `build_chapter_index.py`

They complement the existing DOCX builder/auditor, renderer, visual validators, version comparer and HTML companion.

## Existing strengths retained

- four design profiles;
- real Heading/TOC/PAGE/STYLEREF/SEQ/REF specifications;
- visual decision system with provenance/rights/accessibility;
- RTL/LTR and Arabic/English/Russian editorial handling;
- code/callout/table/figure patterns;
- full-page render inspection;
- honest disclosure when Word/Zotero/Quarto/native features cannot be verified.

## Quick start

1. Read `SKILL.md`.
2. Complete `references/document-contract-v5.md`.
3. Follow `references/research-to-word-pipeline.md`.
4. Use `examples/NORMATIVE_EXAMPLES.md` plus the 26 illustrated examples.
5. Run the applicable research validators, Word structural audit and page renderer.
6. For >=100 pages, use Chapter Package Mode and build `00-Index.docx`.

Run tests with `python -m pytest tests -q` and `python tests_check.py`.

## Technical limits

The Skill defines and validates a professional workflow; it does not magically provide a Word desktop automation engine, live Zotero plugin, journal database subscription, source full text, or human peer review. Never claim those capabilities unless the host environment actually supplied and verified them.
