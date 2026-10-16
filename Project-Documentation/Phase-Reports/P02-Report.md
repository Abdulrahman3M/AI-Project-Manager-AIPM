# P02 Phase Report

## Status

PASS — Windows storage acceptance verified within the limits below.

## Delivered

- Canonical `Shared-Project-State-Manager` initialization and pointer-only registry entries; existing state roots, traversal aliases, legacy `Shared-Project-State` collisions, platform-contained projects, and reparse components are rejected.
- New `State-Manifest.json` uses schema `1.1`, including `tasks` and `diff_fingerprint`; `Project-Manifest.json` remains `1.0`.
- Real Windows ACL denial leaves no partial state/access-probe tree and preserves an existing registry. Real junction tests verify rejection before redirected writes.

## Historical Focused Evidence

`python -m unittest Tests.test_p02_state_storage -v`: 10/10 passed with the authorized Windows fixture capability during P02 acceptance. This is a historical focused run, not the fresh full-suite count.

## Acceptance Evidence

Fresh Windows acceptance on 2026-10-16, after the final review fixes:

- `python -m unittest discover -s Tests -v`: final default sandbox run reported `Ran 73 tests in 29.547s`, `FAILED (failures=3)`, exit 1, zero skips. The two P02 junction cases and P05 guard-reparse case failed at fixture creation: `UNVERIFIED: Windows junction creation failed:  Access is denied.`; the other 70 tests passed.
- The same command with the authorized scoped Windows fixture capability reported `Ran 73 tests in 20.598s`, `OK`, exit 0, zero skips. Real junction rejection, ACL denial/restoration, live/dead child-process identity, and resource-guard child contention were exercised.
- Final focused P03 run: `python -m unittest Tests.test_p03_engine -v`, 20/20 passed in 6.026s. Focused P05 run with the authorized junction capability: `python -m unittest Tests.test_p05_continuity Tests.test_p05_hardening -v`, 25/25 passed in 12.359s; the subsequent full suite verifies the final integrated code.
- Invalid caller metadata is rejected before pending intent or recovery writes, and proposed manifest/event data is validated before publication. The final guard path is canonical/reparse/boundary checked before opening it; corrupted-pending checks and persistent resource guards remain intact.
- `python Core-Engine/aipm.py health`: exit 0; `{"schema_version": "1.0", "status": "PASS", "service": "aipm-core", "command": "health"}`.
- Direct `import aipm` with invalid `sys.argv`, guarded `ArgumentParser.parse_args`, `subprocess.run`, `subprocess.Popen`, and `os.system`: exit 0, no import output or guarded action; callable `aipm.main`.
- `git diff --check`: exit 0. Post-suite `.test-workspace` entry count: 0; disposable fixtures were removed. See the final review fix report for RED/GREEN evidence, the corrected intermediate integration failure, and final commit checks.

## Validation Limits

The non-Windows PID fallback, actual OS PID reuse, power-loss durability, and multi-process Core Engine writer serialization were not proven. PID reuse uses an injected changed identity; live/dead Windows identities and resource-guard contention use real child processes. POSIX `flock`/`renameat2` paths were not executed on Windows. Direct file-symlink creation remained unavailable (`WinError 1314`) even with the scoped capability; the guard regression uses an actual Windows directory junction and a narrowly modeled redirected file open, proving reparse rejection before any open and unchanged target/no lease, not a live file-symlink traversal. A passing local suite does not establish these untested properties.
