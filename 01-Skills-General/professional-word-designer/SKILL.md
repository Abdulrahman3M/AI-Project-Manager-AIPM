---
name: professional-word-designer
description: Create professional Microsoft Word research papers, articles, reports, books, theses, educational materials, and long-form publications through an evidence-controlled research-to-Word pipeline with claim/source traceability, academic structures, citation systems, purpose-driven visuals, native Word features, large-document chapter packages, and publication QA.
---

# Professional Word Designer — v5.1.0

Professional Word Designer is a **research, editorial, academic-publication, Word-production and release-QA Skill**. It does not merely decorate prose. For research-heavy work it controls the chain from Document Contract and evidence discovery through claim verification, academic synthesis, citation formatting, native Word construction, rendered-page inspection and final release.

## Mandatory entry route

For every substantial research/publication document:

1. Read `references/document-contract-v5.md` and create the Document Contract.
2. Read `references/research-to-word-pipeline.md`.
3. Read `references/normative-example-contract.md`; consult `examples/NORMATIVE_EXAMPLES.md` for every applicable requirement.
4. Read `references/visual-explanation-system.md` and `references/enterprise-visual-design.md` before choosing any visual or visual direction.
5. Select a documented pattern from `references/template-atlas.md`; choose one `style-profiles/*.json` profile unless Template Fidelity Mode controls the design.
6. For Arabic-first or materially bilingual output, read `references/rtl-hardening.md` and pass its multi-layer structural audit plus rendered-page checks.
7. If the target is **100 pages or more**, or is clearly too large for one stable file, read `references/large-document-architecture.md` and default to Chapter Package Mode unless the owner explicitly requires a single DOCX.

The 26 illustrated visual examples remain authoritative for visual grammar. v5 adds **124 fine-grained normative examples**, yielding **150 examples total**. Run `python scripts/validate_example_coverage.py`; coverage must be 100%.

## Canonical research-to-Word sequence

1. **Document Contract** — exact purpose, audience, research question, language/locale, length, citation style, evidence threshold, outputs, template and large-document mode.
2. **Research Plan** — questions/subquestions, scope, inclusion/exclusion, freshness, source classes, search channels and stopping criteria.
3. **Source Discovery** — find candidates with tools actually available; discovery is not acceptance.
4. **Source Acceptance & Quality** — classify authority, directness, recency, applicability and limitations.
5. **Source/Evidence Ledger** — assign stable `SRC-...` IDs and verified metadata.
6. **Claim–Evidence Matrix** — assign `CLM-...` IDs to consequential claims and link exact support/contradiction.
7. **Contradiction & Gap Analysis** — normalize scope; preserve real disagreement and missing evidence.
8. **Academic Document Mode** — Research Paper, empirical report, literature review, thesis chapter, technical report, white paper, policy brief, case study, educational chapter, journal manuscript, book chapter, etc.
9. **Academic Structure Router** — build purpose-driven hierarchy from type + audience + question.
10. **Outline and drafting** — substantive natural prose; no filler or fabricated experience.
11. **Literature Synthesis** when applicable — synthesize across evidence; do not serialize source summaries.
12. **Citation Style Engine** — APA 7, IEEE, Vancouver, Chicago Notes/Bibliography, Chicago Author-Date, MLA 9, Harvard-style author-date, or verified CSL/Zotero route.
13. **Front matter / glossary / acronyms / math / index** when the document type warrants them.
14. **Visual, table and figure intelligence** — apply the deterministic visual router; retain provenance/data.
15. **Word implementation** — real styles, fields, notes, captions, bookmarks, RTL/LTR behavior, sections, table semantics and editable structures.
16. **Research QA Dashboard** — claims, sources, gaps, citations, duplicates, metadata and example coverage.
17. **DOCX structural QA** — run available audits.
18. **Field refresh** in a capable Word engine when available; field XML alone is not proof of refreshed results.
19. **Page-by-page render QA** — inspect every page at readable size and repair defects.
20. **Release Package** — deliver requested documents plus required audit/reproducibility artifacts; report PASS/FAIL/UNVERIFIED accurately.

A downstream phase must never erase upstream uncertainty.

## v5 capability map

### Research and evidence
- Research Intelligence Layer — `references/research-intelligence.md`
- Research Plan — `references/research-plan.md`
- Source Quality Model — `references/source-quality-model.md`
- Reference Metadata & CSL/BibTeX/RIS interchange — `references/reference-metadata-interchange.md`
- Claim–Evidence Matrix — `references/claim-evidence-system.md`
- Contradiction & Gap Analysis — `references/contradiction-gap-analysis.md`
- Citation-safe originality/attribution review — `references/citation-safe-originality.md`
- Reproducibility Package — `references/reproducibility-package.md`

### Academic authoring
- Academic Document Modes — `references/academic-document-types.md`
- Academic Structure Router — `references/academic-structure-router.md`
- Literature Review Engine — `references/literature-review-engine.md`
- Citation Style Engine — `references/citation-style-engine.md`
- Academic Front Matter — `references/academic-front-matter.md`
- Native Math & Equations — `references/math-equations.md`
- Glossary, Acronyms and Subject Index — `references/glossary-acronyms-index.md`
- Journal Submission Mode — `references/journal-submission.md`
- Reviewer/Revision Workflow — `references/review-revision-workflow.md`
- Editorial Consistency Analyzer — `references/editorial-consistency.md`

### Word production and layout
- Enterprise Visual Design System — `references/enterprise-visual-design.md`
- Professional Template Atlas — `references/template-atlas.md`
- Tool Landscape & Adoption Rules — `references/tool-landscape.md`
- Existing native Word implementation — `references/word-implementation.md`
- Advanced Word features — `references/advanced-word-features.md`
- Long-document layout — `references/long-document-layout.md`
- Template Fidelity Mode — `references/template-fidelity.md`
- Tables & Figures Intelligence — `references/tables-figures-intelligence.md`
- Visual Explanation System — `references/visual-explanation-system.md`
- Multilingual/RTL — `references/multilingual-localization.md`
- RTL Hardening & Bilingual QA — `references/rtl-hardening.md`
- Accessibility — `references/publishing-accessibility.md`

### QA and release
- Research QA Dashboard — `references/research-qa-dashboard.md`
- Normative Example Contract — `references/normative-example-contract.md`
- Release Package v5 — `references/release-package-v5.md`
- Existing release/render gates remain mandatory and complementary.

## Large documents — Chapter Package Mode

If the estimated or rendered document is **>=100 pages**, default to:

```text
Publication/
├── 00-Index.docx
├── 01-Front-Matter.docx
├── 02-Chapter-01.docx
├── 03-Chapter-02.docx
├── ...
├── 90-References.docx
├── 91-Appendices.docx
└── chapter-manifest.json
```

`00-Index.docx` is a Word navigation document. When supported, each chapter title is a **relative external hyperlink** that opens its chapter DOCX. Generate it with `scripts/build_chapter_index.py`. Keep the complete package together so relative links remain valid. Do not claim cross-file dynamic page numbers or embedded master-document behavior unless a verified Word workflow actually provides it.

Every chapter gets its own structural/render QA; then the complete package receives terminology, numbering, reference and consistency QA.

## Normative examples — anti-improvisation rule

Every v5 normative rule has a stable `REQ-...` ID and at least one mapped `EX-...` example. An example contains: scenario, correct execution, incorrect execution and acceptance evidence. If a rule and an example appear to conflict, the explicit owner instruction and authoritative requirement win; update the example rather than improvising a third behavior.

Do not release v5 work with uncovered requirements. `scripts/validate_example_coverage.py` must report 100%.

## Runnable v5 tools

- `scripts/validate_example_coverage.py` — 100% requirement/example coverage gate.
- `scripts/check_claim_coverage.py` — detects unsupported critical/major claims.
- `scripts/validate_reference_metadata.py` — baseline source-ledger metadata validation.
- `scripts/deduplicate_references.py` — reports possible duplicates without destructive merging.
- `scripts/research_qa.py` — aggregates baseline research QA.
- `scripts/check_document_consistency.py` — baseline exact long-paragraph duplication scan for text exports.
- `scripts/validate_chapter_manifest.py` — validates chapter IDs/order/files.
- `scripts/build_chapter_index.py` — creates a Word Index with relative external hyperlinks to chapter DOCX files.
- `scripts/audit_docx.py --require-rtl` — checks Arabic WordprocessingML direction layers; it supplements, never replaces, Word Desktop and visual verification.
- Existing `build_document.py`, `audit_docx.py`, `render_and_audit.py`, visual validators, comparison and HTML companion tools remain available.

These scripts are deterministic baseline utilities. They do **not** replace human/source verification, a qualified language editor, real journal instructions, a capable Word field updater, real Zotero/CSL processing, or final visual review.

## Machine-readable contracts

Use `schemas/` for:
- Document Contract
- Research Plan
- Source Ledger
- Claim–Evidence Matrix
- Citation Record
- Chapter Manifest
- Example Coverage
- Research QA

Sample fixtures live in `examples/`. Demonstration facts are never real research evidence.

## Core release blockers

Block a clean PASS if any of the following remains unresolved:
- fabricated or materially unsupported claim;
- unsupported critical/major claim;
- citation/source mismatch;
- fabricated reference metadata;
- material contradiction hidden rather than analyzed;
- required example coverage below 100%;
- unlicensed/unsourced factual visual;
- broken chapter manifest/index in Chapter Package Mode;
- fake Word-native feature claim;
- unreadable/clipped/broken rendered page;
- material RTL/accessibility failure;
- claimed field refresh or tracked changes that did not actually occur.

## Absolute limits

Never invent sources, authors, DOI/URL/page numbers, quotations, statistics, datasets, routes, licensing, institutions, logos, authorship, ethics/funding statements, peer-review status, native Zotero fields, Track Changes, editable Office objects, field-refresh proof, plagiarism/AI-detector results or publication acceptance. Use an explicitly labeled fallback or mark the feature UNVERIFIED when tooling cannot prove it.

## Installation

Copy the **entire** `professional-word-designer` folder. Python utilities require Python 3.10+; DOCX creation uses `python-docx`; some existing tools also use `lxml`; gallery regeneration may use `cairosvg`; full render QA requires a compatible DOCX renderer. Run `python -m pytest tests -q` plus `python tests_check.py` where dependencies are available.
