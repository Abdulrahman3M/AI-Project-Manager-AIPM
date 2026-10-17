# Claim–Evidence Matrix

Every consequential factual claim must be traceable to evidence before final publication.

## Claim record

Each claim has:
- stable `claim_id`;
- exact normalized claim;
- section/heading destination;
- importance: critical / major / minor;
- evidence status;
- one or more supporting source IDs;
- contradictory source IDs when present;
- qualification/uncertainty;
- citation placement;
- reviewer status.

## Rules

A source ID is not enough: record which proposition the source supports. A paragraph containing materially different claims may require multiple claim records. Derived calculations identify their input sources and method. Editorial transitions need no forced citation.

Critical and major claims with status `UNVERIFIED` block publication unless the document explicitly presents them as unresolved and that treatment is appropriate.

## Requirements and examples

- REQ-CE-01 — critical/major factual claims have stable IDs.
- REQ-CE-02 — each supported claim maps to the exact source proposition.
- REQ-CE-03 — contradictory evidence is preserved, not silently discarded.
- REQ-CE-04 — unsupported critical claims block clean-release status.
