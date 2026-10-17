# File Operations Policy

## Default

- Diagnose before changing permissions.
- Prefer reversible `move` or `quarantine` over deletion.
- Never overwrite an existing destination silently.
- Keep every helper operation inside the declared project root.
- Do not self-elevate, force-close other processes, take ownership, or disable security controls.
- Clearing read-only attributes or repairing Windows ACL inheritance requires explicit confirmation.
- Permanent deletion is allowed only for an item already quarantined by the tool and requires `PURGE-QUARANTINE` confirmation.

## Permission / Lock Failure

When an operation fails:

1. record diagnostics;
2. distinguish read-only, ACL, or process-lock symptoms;
3. retry only when safe and bounded;
4. use elevated permissions only when the project owner has authorized the operation and OS policy requires it;
5. never weaken permissions outside the project root.
