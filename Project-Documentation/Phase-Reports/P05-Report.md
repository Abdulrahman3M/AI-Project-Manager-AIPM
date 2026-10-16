# P05 Phase Report

## Status

PASS — Windows continuity and recovery acceptance verified within the limits below.

## Delivered

- Checkpoint/handoff records keep unknown token usage as `null` in `History/Checkpoints`, outside event history. Snapshots use unique destinations; `restore` restores `Current-State.md` only, without Git code rollback or wholesale transactional manifest restoration.
- Read-only Git observations cover branch, HEAD, staged/unstaged diffs, and untracked path/content; operational state is excluded. Persisted observations use injected `CoreEngine` revisions/events without changing task state.
- State-bounded quarantine/archive preserve hashes and immutable intent/audit metadata; restore validates records and destinations, refuses replacement, and retries interrupted moves/audit completion.
- Nonce-protected leases use OS process creation/session identity and persistent per-resource OS guards across acquire/release/recovery. Expired recovery refuses a live original owner or unknown identity; stale cleanup cannot delete a newly acquired lease. Malformed metadata raises domain errors.

## Historical Focused Evidence

`python -m unittest Tests.test_p05_continuity Tests.test_p05_hardening -v`: 24/24 passed in 30.669s during P05 review-fix acceptance. This is a historical focused run, not the fresh full-suite count.

## Acceptance Evidence

Fresh Windows acceptance on 2026-10-16, after P05 review acceptance:

- `python -m unittest discover -s Tests -v`: default sandbox run reported `Ran 71 tests in 42.735s`, `FAILED (failures=2)`, zero skips. Both failures were real junction fixture creation: `UNVERIFIED: Windows junction creation failed:  Access is denied.`; ACL fixtures and remaining tests passed.
- The same command with the authorized scoped Windows fixture capability reported `Ran 71 tests in 20.700s`, `OK`, exit 0, zero skips. Real junction rejection, ACL denial/restoration, live/dead child-process identity, and resource-guard child contention were exercised. Fixture denial was resolved by capability, without changing source or tests.
- `python Core-Engine/aipm.py health`: exit 0; `{"schema_version": "1.0", "status": "PASS", "service": "aipm-core", "command": "health"}`.
- Direct `import aipm` with invalid `sys.argv`, guarded `ArgumentParser.parse_args`, `subprocess.run`, `subprocess.Popen`, and `os.system`: exit 0, no import output or guarded action; callable `aipm.main`.
- `git diff --check`: exit 0. Pre-edit `git status --short --branch`: `## main`. Post-suite `.test-workspace` entry count: 0; disposable fixtures were removed. See the Task 5 implementation report for final document and commit checks.

## Validation Limits

The non-Windows PID fallback, actual OS PID reuse, power-loss durability, and multi-process Core Engine writer serialization were not proven. PID reuse uses an injected changed identity; live/dead Windows identities and resource-guard contention use real child processes. POSIX `flock`/`renameat2` paths were not executed on Windows. A passing local suite does not establish these untested properties.
