# AIPM v1.5.8 Release Notes

## Resilient Task State Normalization And Self-Healing

- **String Verification Normalization (`INVALID_STATE` Fix):** Added defensive normalization in `CoreEngine._validate_task_record` (`domain.py`) to handle string-based `verification` values written by external AI agents or legacy tools. The engine automatically transforms string entries into structured dictionaries (`{'result': ..., 'evidence': ...}`) with inferred results (`PASS`, `FAIL`, or `UNVERIFIED`), preventing unhandled `StateError: Invalid Task Evidence` and `BLOCKED: INVALID_STATE` errors when reading project tasks.
- **Loose Status Override Normalization:** Normalized informal status override representations, translating `'COMPLETED'` to canonical `'COMPLETE'`, and converting dynamic statuses (`'BLOCKED'`, `'IN-PROGRESS'`) to `None` so AIPM Core dynamically computes task status from blockers and verification states without rejecting the record.
- **Managed Project State Recovery:** Restored and repaired divergent `State-Manifest.json` and event logs in registered managed projects (`Info Bank` and `Language Learning Hub (LLH)`), ensuring seamless task browsing and execution.
- **Automated Regression Coverage:** Added unit test coverage in `test_task_artifacts.py` verifying that string-based verification values and non-standard status overrides self-heal into compliant structures on read.

## Distribution

Version `1.5.8` is an unpublished repository update. No Skill or Prompt content changed, so Plugin versions remain unchanged.
