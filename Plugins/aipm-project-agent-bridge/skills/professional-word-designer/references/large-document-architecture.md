# Large Document Architecture — 100+ pages

When the target is 100 pages or more, or the content is clearly too large/risky for one stable Word file, default to **Chapter Package Mode** unless the owner explicitly requires a single DOCX.

## Package structure

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

File names may adapt to owner convention, but stable ordering is mandatory.

## Word Index file

`00-Index.docx` contains:
- publication title and metadata;
- chapter list in reading order;
- optional description/page estimate/status;
- **external relative hyperlinks** to each chapter DOCX when supported;
- instructions that the package must remain together for relative links to resolve.

A normal Word hyperlink can target another DOCX. The included `scripts/build_chapter_index.py` creates a DOCX index with relative external relationships. This is preferred over claiming unsupported embedded multi-document behavior.

## Cross-chapter rules

- chapter IDs and filenames are stable after citation/cross-reference freeze;
- shared glossary, reference strategy and numbering policy are defined in the manifest;
- do not create fragile cross-file page-number references unless a verified Word workflow supports them;
- references may be per chapter or centralized according to the contract;
- every chapter receives independent render QA plus package-level consistency QA.

## Threshold

Use the actual rendered page count when available. Before rendering, a planning estimate may trigger the mode; label it as an estimate.

## Requirements and examples

- REQ-LA-01 — estimated/final >=100 pages defaults to Chapter Package Mode.
- REQ-LA-02 — every chapter appears exactly once in the manifest and Index.
- REQ-LA-03 — Index hyperlinks use relative chapter paths when possible.
- REQ-LA-04 — chapter package receives both per-file and package-level QA.
