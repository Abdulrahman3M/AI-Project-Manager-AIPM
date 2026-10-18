# Example File Operations Policy

Adapt these rules to the real project and its owner instructions.

## Default

- Inspect and diagnose before changing permissions or files.
- Prefer reversible moves or quarantine over permanent deletion.
- Never overwrite an existing destination silently.
- Keep helper operations within the authorized project root.
- Do not self-elevate, force-close unrelated processes, take ownership, or weaken security controls.
- Require explicit owner confirmation for destructive or externally visible actions.

## Permission Or Lock Failure

1. Record the exact error and affected path.
2. Determine whether the cause is read-only state, ACL policy, or a process lock.
3. Retry only when safe and bounded.
4. Request authorization before elevated operations when required.
5. Never weaken permissions outside the authorized project root.

## Quarantine And Purge

Record the original path, reason, timestamp, and recovery location before quarantine. Permanent deletion requires an explicit owner decision and confirmation; do not assume quarantine means permission to purge.
