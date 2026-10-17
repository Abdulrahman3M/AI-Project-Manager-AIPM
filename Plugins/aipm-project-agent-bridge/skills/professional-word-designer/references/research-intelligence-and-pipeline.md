# Research Intelligence and End-to-End Publication Pipeline

This framework runs before Word styling. It describes required research controls; it does not claim browsing, DOI resolution, citation formatting, or document generation is automatically available. Use tools actually available and report what was checked.

## Ordered pipeline

| Stage | Required record | Example |
|---|---|---|
| Document Contract | audience, purpose, question, scope, locale, length, citation style, outputs | 6,000-word review, English, APA 7, 2018–2026 |
| Research Plan | questions, search concepts, date range, inclusion/exclusion rules | Search urban heat AND tree canopy; include peer-reviewed city studies |
| Discovery and verification | query, venue, search date, access level, metadata status | Abstract available; full text inaccessible |
| Evidence Ledger | source record, findings, methods, caveats and locator | S014 supports association, not causation |
| Claim–Evidence Matrix | stable claim IDs mapped to sources and qualifiers | C-012 → S014/Table 2; retain “associated with” |
| Synthesis and gap analysis | agreement, disagreement, limitations, unanswered questions | Measures differ across studies; comparison remains tentative |
| Structure router and outline | document mode, section hierarchy, claim and figure plan | Review article: methods, thematic synthesis, limitations |
| Draft and citation QA | prose, style/version, source mapping, metadata exceptions | DOI mismatch flagged, not guessed |
| Word production and QA | editable DOCX, structural/render results | All 18 pages rendered and inspected, if actually done |
| Release package | requested files and verification report | DOCX plus ledger only if requested |

**Worked example.** For a policy report, record jurisdiction and currentness date, search official law and government guidance, map each legal claim to an exact section, draft, check the citation style, render the DOCX, and report provisions that could not be verified. A search snippet is not a verified source.

## Contract and research plan

Capture document mode, audience, purpose, question, intended decision or learning outcome, jurisdiction, time cut-off, included/excluded populations and topics, expected depth, language/locale, citation style/version, source access, supplied template/corpus, split-file requirements, privacy and rights constraints, and material assumptions.

Search logs record actual query, venue, date, result count when shown, and access status. Distinguish not searched, not found, and inaccessible. Use primary sources when they best answer the question. News may be a discovery lead rather than evidence for technical findings.

**Worked example.** “Compare two drug labels” is incomplete without country, product strength, label dates, target audience and source hierarchy. If sources cover different jurisdictions, do not silently merge them.

## Source ledger and uncertainty

Assign stable IDs such as S001. Record title, creator, publisher/venue, dates, DOI/URL and verification status, edition, locator, source type, language, access level, methods/document type, supported and contradicted claim IDs, limitations, corrections/retractions, and rights status for quoted or visual material. Preserve original metadata alongside normalized citation fields.

Use statuses: verified, partially verified, conflicting, not verified, inaccessible, or retracted/superseded. Describe quality in words based on directness, methods, relevance, recency, independence, integrity and access. Do not invent a universal certainty score.

**Worked example.** Metadata verified but abstract only means the methods remain unverified. Do not write as though the full paper was appraised.

## Research QA dashboard

Report actual counts for questions answered/partly/unanswered; sources by type and access; claims supported/qualified/contested/unsupported; stale evidence; missing metadata; duplicate references; unresolved gaps; citation exceptions; and incomplete Word/render gates.

**Worked example.** “38 claims mapped; 31 supported, 5 qualified, 2 removed; all 18 pages inspected” is acceptable only if those counts derive from the actual records. Never reuse sample counts.

## Full workflow example

For a 30-page review, define population, intervention, comparison, outcomes and date cut-off; log actual database searches and screening; check corrections; extract results and limits; map claims; synthesize by theme and method; choose Review Article mode; approve outline; draft; validate references; build DOCX; render every page; check structural and visual gates; package only requested companions. An unverified outcome cannot be charted as fact.
