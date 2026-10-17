# Research-to-Word Pipeline v5

This is the canonical execution pipeline for substantial research/publication work.

1. Document Contract
2. Research Plan
3. Source Discovery
4. Source Acceptance and Quality Classification
5. Evidence/Source Ledger
6. Claim–Evidence Matrix
7. Contradiction and Gap Analysis
8. Academic Document Mode and Structure Router
9. Outline
10. Draft
11. Literature Synthesis where applicable
12. Citation Style Engine
13. Visual Explanation / Tables / Figures
14. Word Layout and native structures
15. Research QA
16. DOCX Structural QA
17. Field refresh where supported
18. Page-by-page Render QA
19. Release Package / Reproducibility Package

No downstream phase may erase an upstream uncertainty. When a blocking gate fails, return to the responsible phase.

## Requirements and examples

- REQ-PW-01 — stages execute in dependency order.
- REQ-PW-02 — every handoff uses stable IDs and machine-readable artifacts where defined.
- REQ-PW-03 — blockers route back to the owning stage.
- REQ-PW-04 — release status reports verified and unverified stages explicitly.
