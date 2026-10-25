# AIPM v1.5.10 Release Notes

## Diagnosable And Audited Task-State Recovery

- **Root Cause Reporting:** Task management now reports when committed task events and the state manifest do not agree, and explains which safe recovery path applies.
- **Guided Recovery:** For a pending task creation blocked only by additional valid task records missing from event history, Core can create a hash-verified backup, record those records in an explicit reconciliation event, and resume the pending creation. The TUI asks for confirmation before any write and reports the backup location.
- **Fail-Closed Integrity:** Repair remains unavailable if prior event replay conflicts with an existing task, the pending operation is not a task creation, or any task record fails validation. Those cases include a manual recovery recommendation.
## Distribution

Version `1.5.10` is an unpublished repository update. No Skill or Prompt content changed, so Plugin versions remain unchanged. No GitHub Release or tag was created.
