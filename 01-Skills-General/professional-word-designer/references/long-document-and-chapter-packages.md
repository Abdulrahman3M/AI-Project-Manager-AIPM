# Long Documents and Chapter Packages

## Routing trigger

A request of about 100 pages or more requires explicit chapter-delivery planning. The user may request chapters at any length. Clarify in the contract whether page estimates count body text or the whole package; otherwise use estimated body pages and record that assumption. A single DOCX remains valid when requested and manageable, but assess navigation, revision and rendering burden.

**Example.** A 130-page thesis collection triggers chapter planning. A 95-page report explicitly requested as parts is also split.

## Chapter continuity plan

Before drafting, define stable chapter IDs, titles, scope, boundaries, target length, heading levels, citation/reference policy, figure/table numbering, glossary/acronym policy, cross-chapter links, front/back matter ownership, language, style profile and filenames. Maintain a master outline and terminology/continuity ledger.

**Example.** CH03_Methods.docx owns sections 3.1–3.8, uses global figure numbers, and cites a shared bibliography. Do not reset figure numbering unless specified.

## Word Index with cross-file links

When separate DOCX chapters are made, create 00_Index.docx with ordered chapter title, scope/summary, exact filename and navigation link. Preferred implementation is a relative hyperlink to the sibling DOCX, with all files kept together. Word hyperlink relationships can support this, but activation varies by platform, security settings, URL encoding and moved/renamed files. Test every link in the target environment before claiming that a click opens the file. If unsupported or blocked, keep the index and exact filenames as a reliable manual-navigation fallback.

**Example.** Package 00_Index.docx, CH01_Introduction.docx and CH02_Evidence.docx in one folder; test each link after copying the final folder. If link testing is unavailable, disclose that the index lists filenames but links are unverified.

## Package and QA

Use stable sortable filenames; add a navigation block to each chapter when supported. Check missing/duplicate IDs, title/filename agreement, headings, broken links, citations, figure numbering, contradictory definitions, abbreviations, transitions, page count, stale summaries and per-file render QA. Deliver index and chapters together, preserving relative layout. Include PDF or ZIP only if requested or useful to the brief.

**Example.** If the index links to 03_Results.docx but the actual file is 03_Results_RevB.docx, the package fails until corrected.
