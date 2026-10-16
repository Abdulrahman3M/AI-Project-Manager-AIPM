# P03 Phase Report

## Status

PASS — command, recovery, and CLI acceptance verified within the limits below.

## Delivered

- Typed command envelopes, revision conflict rejection, validated contiguous immutable event history, and idempotent replay.
- Recoverable event/manifest commits use `History/Pending-Commit.json`; recovery validates command-specific fields and preserves invalid evidence rather than silently rewriting it.
- Schema `1.0` reads supply defaults without writing; accepted mutations upgrade state to `1.1`. Git observations share the revisioned command seam.
- Import-safe CLI entry point and structured JSON health, registry, inspect, state-read, and invalid-input results.

## Historical Focused Evidence

`python -m unittest Tests.test_p03_engine -v`: 19/19 passed during P03 acceptance. This is a historical focused run, not the fresh full-suite count.

## Acceptance Evidence

Fresh Windows acceptance on 2026-10-16, after P05 review acceptance:

- `python -m unittest discover -s Tests -v`: default sandbox run reported `Ran 71 tests in 42.735s`, `FAILED (failures=2)`, zero skips. Both failures were real junction fixture creation: `UNVERIFIED: Windows junction creation failed:  Access is denied.`; ACL fixtures and remaining tests passed.
- The same command with the authorized scoped Windows fixture capability reported `Ran 71 tests in 20.700s`, `OK`, exit 0, zero skips. Real junction rejection, ACL denial/restoration, live/dead child-process identity, and resource-guard child contention were exercised. Fixture denial was resolved by capability, without changing source or tests.
- `python Core-Engine/aipm.py health`: exit 0; `{"schema_version": "1.0", "status": "PASS", "service": "aipm-core", "command": "health"}`.
- Direct `import aipm` with invalid `sys.argv`, guarded `ArgumentParser.parse_args`, `subprocess.run`, `subprocess.Popen`, and `os.system`: exit 0, no import output or guarded action; callable `aipm.main`.
- `git diff --check`: exit 0. Pre-edit `git status --short --branch`: `## main`. Post-suite `.test-workspace` entry count: 0; disposable fixtures were removed. See the Task 5 implementation report for final document and commit checks.

## Validation Limits

The non-Windows PID fallback, actual OS PID reuse, power-loss durability, and multi-process Core Engine writer serialization were not proven. PID reuse uses an injected changed identity; live/dead Windows identities and resource-guard contention use real child processes. POSIX `flock`/`renameat2` paths were not executed on Windows. A passing local suite does not establish these untested properties.
