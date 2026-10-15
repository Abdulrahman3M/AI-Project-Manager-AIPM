# Research QA Dashboard

Before release, generate a compact evidence/quality status report.

## Minimum metrics

- total claims;
- critical/major claims;
- supported, disputed and unverified claims;
- source count by class;
- stale/limited sources;
- citation orphans;
- bibliography orphans;
- duplicate references;
- missing metadata;
- unresolved contradictions/gaps;
- examples coverage percentage;
- chapter-manifest status when applicable;
- structural DOCX audit;
- render-review status;
- field-refresh status.

Metrics describe recorded evidence; they are not a quality score invented from arbitrary weights.

## Requirements and examples

- REQ-QD-01 — dashboard counts come from machine-readable ledgers.
- REQ-QD-02 — blocking failures are visually distinct from informational warnings.
- REQ-QD-03 — no composite “research quality score” is invented without a defined validated model.
- REQ-QD-04 — final release status reflects unresolved blockers.
