# Research Intelligence Layer

This layer controls research before prose generation. It prevents source collection from becoming an unstructured list of links.

## Workflow

1. Convert the Document Contract into research questions and subquestions.
2. Define scope, date range, jurisdiction/domain, inclusion/exclusion criteria and evidence threshold.
3. Build a Research Plan before broad source collection.
4. Discover candidate sources using tools actually available.
5. Prefer primary/official/original evidence when feasible.
6. Capture source metadata and source-quality classification in the Source Ledger.
7. Extract only claims actually supported by the source.
8. Build the Claim–Evidence Matrix.
9. Detect contradictory findings, missing evidence, stale evidence and coverage gaps.
10. Stop research when the evidence threshold and coverage target are satisfied or report the unresolved gap.

## Research status labels

`VERIFIED`, `SUPPORTED-WITH-LIMITATION`, `DISPUTED`, `UNVERIFIED`, `OUT-OF-SCOPE`.

Never upgrade a status merely because several secondary sites repeat the same unsourced statement.

## Requirements and examples

- REQ-RI-01 — every research run begins with explicit questions and scope.
- REQ-RI-02 — source discovery is separate from source acceptance.
- REQ-RI-03 — research stops by evidence criteria, not arbitrary source count.
- REQ-RI-04 — unresolved evidence gaps survive into the final limitations/report.
