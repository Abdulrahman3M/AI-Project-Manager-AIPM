# AIPM v1.5.9 Release Notes

## Legacy Task Commit Recovery

- **Task Creation Fix:** AIPM now reconciles the documented legacy task normalizations with the historical event stream before completing a pending commit. Creating a new task no longer fails with `STATE_COMMIT_FAILED` merely because an older task stored `verification` as text or used `COMPLETED` instead of `COMPLETE`.
- **Integrity Preserved:** The compatibility path accepts only those two legacy representations. Any other mismatch between task history and the state manifest remains blocked.
- **Regression Coverage:** Added an automated test for creating a follow-up task after normalizing a legacy verification value.

## Distribution

Version `1.5.9` is an unpublished repository update. No Skill or Prompt content changed, so Plugin versions remain unchanged. No GitHub Release or tag was created.
