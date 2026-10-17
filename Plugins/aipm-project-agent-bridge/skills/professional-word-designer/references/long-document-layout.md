# Long-Document Word Layout Engine

This contract governs theses, books, standards-style reports and any document where pagination complexity becomes material.

## Controls

- widow/orphan control;
- keep-with-next for headings and captions;
- keep-lines-together where appropriate;
- controlled page/section breaks;
- portrait/landscape section routing;
- repeating table headers;
- table row splitting policy;
- chapter opening policy;
- front-matter Roman numbering and body Arabic numbering when requested;
- appendix numbering;
- running chapter/section headers;
- figure/table/equation numbering by chapter when required.

Every change affecting pagination requires field refresh and page re-render.

## Requirements and examples

- REQ-LD-01 — headings/captions are not stranded at page bottoms.
- REQ-LD-02 — orientation changes use section breaks, not rotated screenshots.
- REQ-LD-03 — long tables preserve headers and readable continuation behavior.
- REQ-LD-04 — numbering schemes are verified after final pagination.
