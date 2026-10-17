# Document Contract v5 — mandatory intake and publication contract

The Document Contract is the authoritative task specification for every substantial document. It is completed before research or writing and remains the controlling source of truth unless the owner changes it.

## Required fields

- document type and intended use;
- title/topic and research question;
- audience and assumed knowledge;
- language, locale, direction and spelling standard;
- expected length or page target;
- citation style;
- evidence threshold and freshness requirements;
- allowed and prohibited source classes;
- required sections, front matter and appendices;
- visual policy and accessibility constraints;
- template/profile requirements;
- output package;
- collaboration/review requirements;
- large-document strategy;
- unresolved assumptions.

## Decision rules

- Use explicit owner instructions over defaults.
- Apply defaults only to nonessential omissions; record them.
- Do not silently convert an academic paper into a magazine article, or vice versa.
- If the requested size is likely to reach 100 pages or more, set `large_document_mode=true` unless the owner explicitly requires one DOCX.
- If a supplied DOCX/DOTX is authoritative, set `template_fidelity_mode=true`.
- Every material change to the contract must be reflected in downstream research plan, structure and QA.

## Requirements and examples

- REQ-DC-01 — contract exists before substantive drafting.
- REQ-DC-02 — owner constraints are copied exactly, not normalized away.
- REQ-DC-03 — defaults are labeled as defaults.
- REQ-DC-04 — large-document and template modes are explicitly resolved.

See `examples/NORMATIVE_EXAMPLES.md` for the corresponding examples and `schemas/document-contract.schema.json` for the machine-readable form.
