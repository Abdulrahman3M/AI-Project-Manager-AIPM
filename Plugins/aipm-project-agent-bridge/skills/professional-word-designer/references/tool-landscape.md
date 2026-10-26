# Tool Landscape And Adoption Rules

This is a curated research synthesis, current as of 2026-10-26. It informs tool selection; it does not vendor, copy, install, or endorse any project. Pin versions, review licenses, test the exact target format, and do not run converters on untrusted documents without isolation.

| Tool / source | Useful capability | Material limit or risk | Adoption rule |
| --- | --- | --- | --- |
| [python-docx](https://github.com/python-openxml/python-docx) | Python DOCX creation, styles, tables, sections and header/footer preservation | API coverage is incomplete; low-level OOXML is sometimes necessary | use for controlled native builds, then audit XML/render |
| [dolanmiu/docx](https://github.com/dolanmiu/docx) | Node/TS DOCX generation and template patching | output still needs Word/render checks | use for JS-native documents and tested placeholders |
| [@office-kit/docx](https://github.com/office-kit/docx) | ECMA-376-focused open/edit/serialize API | pre-1.0 API may change | pin and regression-test before production |
| [Docxtemplater](https://github.com/open-xml-templating/docxtemplater) | editable placeholders, loops and conditions | several useful modules are paid; template design still governs quality | use only licensed modules and validate every expansion |
| [Pandoc](https://pandoc.org) | source-to-DOCX conversion and reference-doc workflows | conversion is not pixel-perfect | use a controlled reference DOCX and render QA |
| [Quarto Word output](https://quarto.org/docs/output-formats/ms-word.html) | reproducible scholarly publishing | no automatic visual parity guarantee across outputs | use when source-first publishing is desired |
| [LibreOffice / UNO](https://www.libreoffice.org) | headless conversion and an independent renderer | differs from Word Desktop | treat as a renderer, not Word proof |
| [Mammoth](https://github.com/mwilliamson/python-mammoth) | semantic DOCX-to-HTML inspection | intentionally ignores much visual styling; unsafe input needs sanitization/isolation | use for content/structure checks, never visual fidelity |
| [MarkItDown](https://github.com/microsoft/markitdown) | broad file-to-Markdown extraction for LLM analysis | not intended for high-fidelity human output; inherits process I/O privileges | use narrow converters and treat output as evidence aid |
| [Zotero](https://www.zotero.org/support/word_processor_integration) | real managed citations/bibliography in Word | requires real desktop integration | never fake Zotero fields |
| [Arabic Word Production](https://github.com/Bannovich/arabic-word-production) | Arabic/bilingual DOCX models and structural audit ideas | alpha; renderer differences remain | adopt only its documented concepts after local tests |
| [claude-arabic-docs](https://github.com/muhmoosa/claude-arabic-docs) | identifies Word RTL settings/defaults/section/run layers | project-specific claims need independent validation | implement OOXML layers and verify in actual Word |
| [arabic-docx-skill](https://github.com/alahmadics/arabic-docx-skill) | Arabic RTL helper/audit concepts | small, third-party project; do not treat as universal proof | use as a research reference, not a dependency |
| [Canva Docs templates](https://www.canva.com/docs/templates/) | broad categories and visual inspiration | assets, licensing and export behavior are platform-specific | derive category and hierarchy ideas only; never copy design assets |

## Selection flow

1. Existing owner template with approved placeholders: template engine or native editor; preserve styles and validate output.
2. New structured DOCX: `python-docx` or Node `docx` plus low-level OOXML only where required.
3. Source-first scholarly document: Quarto/Pandoc with an approved reference DOCX.
4. Semantic extraction/review: Mammoth or MarkItDown in a constrained environment; never regard extraction as layout proof.
5. Arabic-first delivery: use the multi-layer rules in `rtl-hardening.md`; Word Desktop verification is the highest available compatibility evidence.

The public-source observation behind this Skill is simple: tools solve different layers. Template engines fill content, generators construct OOXML, converters extract/translate, and renderers reveal failures. No single tool replaces semantic authoring, license review, RTL engineering and page-by-page human inspection.
