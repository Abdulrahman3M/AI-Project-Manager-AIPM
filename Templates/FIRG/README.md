# FIRG — Fork Intelligence & Regression Guard

FIRG combines Git evidence, canonical `registry/*.json` fix records and the generated [master ledger](FIX-HISTORY.md) to support safe review of changes from any external source. Its commands require a usable Git repository rooted at the project directory. Existing history remains authoritative; it has not been backfilled. See [integration policy](policies/INTEGRATION.md) and [schema](schemas/fix-record.schema.json).

Run from the repository root with Python 3 and Git, without packages or network access:

```text
python FIRG/tools/firg.py validate --strict
python FIRG/tools/firg.py sync --check
python FIRG/tools/firg.py next-id --date 2026.11.04
python FIRG/tools/firg.py register --input path/to/verified-record.json
python FIRG/tools/firg.py sync
python FIRG/tools/firg.py commit-status
python FIRG/tools/firg.py document-commit --commit HEAD --problem "Problem" --cause "Known cause or unknown" --expected "Expected behavior" --implementation "Actual change" --rationale "Reason for approach" --notes "Related changes or none"
python FIRG/tools/firg.py intake --base BASE --head HEAD --source upstream --reference REFERENCE
python FIRG/tools/firg.py gate --base BASE --head HEAD --source upstream --review FIRG/reviews/REV-YYYY.MM.DD-NN.json
python -m unittest discover -s FIRG/tests
```

IDs use the verified issue date or registration date in the configured timezone (UTC by default) with `issue_date_known=false`. IDs never change when a date is corrected. `next-id` proposes only; registration uses exclusive file creation. Commit hashes must be full and locally resolvable. A record without a commit requires an immutable reference and explanation in `provenance_reason`. Preserve original and replacement provenance on rebases.

Record publication writes complete JSON to a temporary file before an exclusive atomic link; Windows falls back to an exclusive rename when hard links are denied. The temporary file uses the project state temporary directory when present, otherwise the registry directory. If the filesystem cannot publish atomically, the command fails without replacing an existing record. A report created before a publication failure is retained for review.

`commit-status` lists reachable commits as documented or undocumented. `document-commit` creates one canonical record and a Markdown report from facts supplied by the user; it never infers a cause or claims tests passed. Its initial test evidence is `UNVERIFIED` and must be updated with real evidence. AIPM offers this flow after commits made through its task interface. When the default local post-commit hook is available, FIRG also asks in interactive terminals after other Git commits. Hooks can be bypassed and non-interactive Git clients cannot present the prompt; use `commit-status` and `document-commit` for missed commits. AIPM does not replace an existing post-commit hook or a custom hooks path.

The included self-tests use an existing `Shared-Project-State-Manager/Test-Workspace` for disposable Git fixtures. Set `FIRG_TEST_WORKSPACE` to an existing authorized disposable directory to use another location. Tests skip if the selected directory is absent and do not create a shared-state installation when the owner declined it; skipped tests are unverified.

The gate requires explicit origin; unknown origin cannot pass functional changes. Review metadata is JSON for mechanical checking, and should be accompanied by a human-readable dated Markdown report describing commands, results, scope, actor, rationale and residual risk. Reviews must name exact resolved base/head SHAs and include `source`, `disposition`, `rationale`, `fix_ids`, `tests` and `reference`; every test has `name`, `command_or_reference`, `result`, `evidence`. Never approve unverified checks. Review candidates in an isolated worktree; record rejected/deferred reviews without claiming an integrated fix. A documented owner exception must identify scope, risk, actor and timestamp; it is not an automated pass.

Intake is read-only and does not execute arbitrary recorded commands. Reviewers execute relevant commands in the isolated candidate environment and record actual evidence. Path matching cannot prove semantic equivalence or complete coverage. Branch protection and CI execution are controlled by the owner; instructions cannot force every agent runtime to read them. Configure the FIRG check as required where appropriate.
