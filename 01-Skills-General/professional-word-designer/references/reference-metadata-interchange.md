# Reference Metadata Validation and Interchange

## Metadata

Capture only verified fields: type, title, authors/organization, date/year, container/journal/publisher, volume/issue/pages, DOI, URL, ISBN/ISSN when relevant, retrieval date when style requires it, language and source ID.

Normalize DOI forms for comparison; preserve the canonical DOI value. Detect duplicates by DOI first, then strong metadata similarity. Never merge two distinct works merely because their titles resemble each other.

## Interchange

Support import/export planning for:
- CSL-JSON
- BibTeX/BibLaTeX
- RIS
- Zotero-managed records when real integration is available

Preserve unknown fields during round-trip when possible.

## Requirements and examples

- REQ-RM-01 — required metadata is validated by source type.
- REQ-RM-02 — DOI/URL is verified rather than guessed.
- REQ-RM-03 — duplicate detection preserves distinct editions/versions.
- REQ-RM-04 — interchange export never invents missing bibliographic data.
