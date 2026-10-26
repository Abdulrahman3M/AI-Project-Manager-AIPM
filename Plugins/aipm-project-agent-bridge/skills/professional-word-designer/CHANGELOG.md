## [1.0.0] — AIPM Release Baseline

- Reset the Skill release line to 1.0.0 for independent AIPM development after project completion.

# Professional Word Designer — Changelog

## [1.1.0] — 2026-10-26

- Added an enterprise visual-design system and a 36-pattern Professional Template Atlas spanning executive, strategy, research, instructional, commercial, operational, editorial and bilingual documents. Each pattern specifies its visual grammar, appropriate components, and failure modes rather than shipping third-party templates or copyrighted assets.
- Added a documented tooling landscape synthesized from public documentation for `python-docx`, `docx`, `@office-kit/docx`, Docxtemplater, Pandoc, Quarto, LibreOffice/UNO, Mammoth, MarkItDown and Arabic-first DOCX projects. The Skill now routes tools by capability, records their limitations, and requires safe handling of untrusted documents.
- Added Arabic-first and mixed Arabic/English RTL hardening: Word settings, defaults, sections, visual-table order, paragraph direction, run direction, logical alignment, punctuation/isolation rules, regression strings, structural audit and real-render verification requirements.
- Upgraded the bundled DOCX baseline builder and auditor to implement and verify the RTL layers, including table visual order, complex-script language, section direction and Word theme language.
- This is an additive capability release. Research findings are attributed in `references/tool-landscape.md`; no third-party code, templates, images, logos, or proprietary modules were copied into the Skill.

## 5.0.0 — 2026-10-04

- Expanded the Skill from advanced Word design into a full evidence-controlled Research-to-Word publication workflow while keeping the Professional Word Designer name.
- Added the 21 approved capability areas: Research Intelligence, Claim–Evidence Matrix, source-quality evaluation, citation-style engine, Academic Document Modes, Research-to-Word Pipeline, literature review/synthesis, reference metadata validation, CSL/BibTeX/RIS interchange, academic front matter, native math/equation rules, glossary/acronyms/index, long-document layout, template fidelity, journal submission, reviewer/revision workflow, reproducibility package, editorial consistency analysis, citation-safe originality review, tables/figures intelligence and Research QA Dashboard.
- Added Document Contract v5, Research Plan, contradiction/gap analysis, Academic Structure Router and explicit release-package contracts so the pipeline is operational rather than a list of features.
- Added the owner's **100+ page Chapter Package Mode**: long publications default to separate chapter DOCX files plus `00-Index.docx` and `chapter-manifest.json`; the new index builder writes relative external Word hyperlinks to chapter files.
- Added the owner's strict **example-for-every-requirement** policy. v5 contains 124 new fine-grained normative examples across 31 domains plus the existing 26 illustrated visual examples, for 150 examples total.
- Added machine-readable JSON schemas for Document Contract, Research Plan, Source Ledger, Claim–Evidence Matrix, Citation Records, Chapter Manifest, Example Coverage and Research QA.
- Added deterministic validators for example coverage, claim coverage, reference metadata, duplicate-reference reporting, chapter manifests, baseline research QA and baseline document consistency.
- Added v5 sample research plan, source ledger, claim matrix and chapter manifest plus regression tests including Word Index external-link inspection.
- Retained all prior Word, visual, multilingual, accessibility and page-render gates; unsupported native Word/Zotero/CSL/Track Changes behavior remains explicitly non-fabricable.

## 4.0.1 — 2026-10-04

- Clarified that icons, educational images, annotated photos, and diagrams can be added while preparing articles and other Word documents when they improve understanding.
- Kept the existing visual decision, evidence, licensing, accessibility, and rendered-page review requirements; this release clarifies the existing capability without changing its behavior.

## 4.0.0 — 2026-10-04

- Renamed the Skill from `editorial-word-designer` / **Editorial Word Designer** to `professional-word-designer` / **Professional Word Designer**.
- Reframed the canonical description around creating professional Microsoft Word documents for research papers, articles, reports, books, educational materials, and long-form publications with structured content, professional formatting, visual elements, references, and publication-ready document design.
- Updated current Skill instructions, templates, package archive path, validation expectations, documentation, registry references, and plugin integration to the new identity.
- Preserved the existing research, visual-explanation, editable Word, multilingual, accessibility, and release-QA capabilities. The identifier/path rename is a breaking change, so the major version advances to 4.0.0.

## 3.1.0 — 2026-10-04

- Corrected concept-map connector routing: edges end at node boundaries, never cross central text, and render behind labels and boxes.
- Made diagram collision rules mandatory in the Visual Explanation System and Word page-render QA; introduced `scripts/validate_diagram_geometry.py` and regression testing.
- Synchronized master, plugin copy, and SVG documentation reference. Repository root-path modernization is tracked separately in the project Change Log.

## 3.0.0 — 2026-10-04

- Added deterministic Visual Explanation System with icon/photo/schematic/process/decision/mindmap/table/chart/timeline/map/no-visual routing, required educational justification and visual provenance.
- Added **26 original numbered visual demonstrations** in both editable SVG and PNG plus explicit WHEN/PASS/FAIL playbook and machine-readable coverage JSON.
- Adopted four external **concepts** (Anthropic render+inspect, gertalot design tokens, Quarto source-once publishing, Zotero managed bibliography) without copying third-party code/assets.
- Implemented ten requested improvements as executable baseline tools and/or documented optional playbooks.
- Added source contract, accessibility/publishing guide, advanced Word matrix, integration notes, eight release gates, strict skill routing and reproducible tests.

## 2.0.0 — 2026-10-03

- Added Word TOC field requirements, running headers/footers, numbered in-text citations and bibliography, RTL/LTR callouts, code, multilingual proofreading, visual component standards and QA.

## 1.0.0 — Initial design

- Introduced article/research editorial layout, cover, diagrams, icon-led education, natural editorial writing, end references and page visual inspection.
