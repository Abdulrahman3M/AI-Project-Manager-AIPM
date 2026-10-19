## [1.0.0] — AIPM Release Baseline

- Reset the Skill release line to 1.0.0 for independent AIPM development after project completion.

# Changelog

## [1.1.0] - 2026-10-19

- Added idempotent registration of the owner-authorized `AI-Agent-Browser` Edge data-directory reference when manager metadata is missing; profile data is never copied, moved, or reset.
- Added normalized command-line parsing, explicit CIM/TCP permission statuses, parent-PID listener binding, bounded reconnect startup verification, and sanitized verification states.
- `Connect` now starts the verified dedicated environment once when it is not running, while refusing ambiguous, non-loopback, or foreign-listener conditions.

## [1.0.1] - 2026-10-11

- Expanded troubleshooting guidance with 36 symptom, evidence, and safe-response examples, including sandbox-denied localhost/CDP and blocked process-inspection cases.
- Clarified the difference between endpoint reachability, process ownership, profile verification, navigation, and screenshot verification.

## [1.0.0] - 2026-10-11

- Introduced safe Windows Edge/Chrome environment creation, launch, status, connection and archive-first reset.
- Added central configuration, desktop shortcut generation, listener/process identity checks and optional CDP new-tab test.
- Added portable connect-and-verify prompt, compatibility, examples, troubleshooting and tests.
- Firefox documented as unsupported pending a separate BiDi/Marionette adapter.
