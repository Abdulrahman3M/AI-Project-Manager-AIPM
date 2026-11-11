# How To Validate And Execute

This guide is copied into each large offline handoff package. Use Python 3.10 or later; no third-party packages are needed. Run commands from the extracted package root. Inspect scripts before running an untrusted package. SHA-256 checks detect changed files, not malicious authorship.

## Before Sharing

1. Inspect the master and each ordered phase. Verify source evidence and owner decisions; label hypotheses and unknowns. Confirm each phase has its prerequisites, permitted scope, actions, checks and stop conditions.
2. Run `python scripts/handoff-lint.py . --profile ultra` (or `guided`/`standard` matching the selected profile). Exit 0 means no blocking structural finding; 1 means a finding; 2 means invalid input or I/O error. `--format json` produces machine-readable output; `--fail-on-warning` also blocks warnings. Review warnings. Lint cannot prove diagnosis or code correctness.
3. Run `python -m unittest discover -s tests -p "test_handoff*.py" -v`. For risky or complex work, a capable reviewer separately examines evidence, contradictions, scope, tests and decisions. Record Gate B as UNVERIFIED if unavailable.
4. From the authoring environment run `python <skill>/scripts/bundle-handoff.py <staging> <output.zip>`, then `python <skill>/scripts/handoff-lint.py --verify-package <output.zip>`. The helper adds missing support files and generates the manifest; do not edit it manually. Check the inventory for secrets or private paths. Choose an output path outside the staging tree that does not already exist.

## After Receipt

Before extraction, verify the ZIP using a trusted copy of `handoff-lint.py --verify-package <output.zip>`; inspect untrusted scripts before execution. Extract safely, run the document lint and tests above, and compare the manifest. If Python is unavailable, mark automatic checks UNVERIFIED and manually check the six stages and order, scope, preservation, source evidence, unique IDs and trace links, tests, stop rules, final status and package inventory. Do not claim checksum verification without actually running it.

## Execution

Read the master and applicable project instructions. Confirm repository snapshot, dirty state and source anchors. For high-risk ULTRA-STRICT work, read back scope, first unit, pass criterion and stop condition; stop on failure. Execute one ordered phase and unit at a time, run its specified checks, and record commands, evidence and PASS / FAIL / UNVERIFIED. If a baseline or assumption differs, stop the affected unit and report expected versus actual. On a failed test investigate within the stated bounds; consult the owner or stronger reviewer when the plan would change approved behavior, data, architecture or scope. Report COMPLETE, PARTIALLY COMPLETE or BLOCKED without treating lint as runtime verification.
