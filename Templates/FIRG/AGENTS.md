# Fork Intelligence & Regression Guard

FIRG protects project fixes in any software project, including projects without a literal fork. These instructions apply to FIRG and explicitly delegated project-wide workflows, without overriding unrelated project rules.

Read root governance, this file, README and integration policy, relevant ledger/registry entries, then affected code and tests. Registry JSON files are the sole canonical fix data; FIX-HISTORY.md is the mandatory generated human index. Never edit it independently.

Review incoming functional changes before touching the protected target. Preserve provenance, IDs, authors, evidence and existing entries; never invent facts. Use only PASS, FAIL or UNVERIFIED for test results. Keep problem and expected behavior to 1–3 informative sentences each. Preserve rejected fixes; use evidenced superseded/reverted transitions with rationale and references. Record implemented fixes only after actual testing; provisional reviews may precede integration. Follow native history rules separately. Limit scope to affected components and justified dependencies; no subagents without owner authorization.

For a completed commit, use `commit-status` to distinguish documented and undocumented commits. When the owner requests documentation, use `document-commit` with the actual commit and factual problem, cause, expected behavior, implementation, rationale and related notes. The generated report is a readable snapshot of the canonical record; update both when correcting a documented fact. Unknown causes or unavailable evidence must be identified honestly. The optional local post-commit prompt works only where the hook is installed and an interactive terminal is available; hooks can be bypassed.
