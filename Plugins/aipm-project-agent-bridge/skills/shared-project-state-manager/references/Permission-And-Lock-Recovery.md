# Permission And Lock Recovery

Use this sequence when Windows or another OS refuses a file operation.

## 1. Diagnose

```powershell
python .\scripts\safe_file_ops.py diagnose ".\Problem-Path" --project-root .
```

Check whether the path exists, is readable/writable, appears read-only, and—on Windows—the `icacls` output.

## 2. Read-Only Mode

If the target belongs to the project and only writability is wrong:

```powershell
python .\scripts\safe_file_ops.py clear-readonly ".\Problem-Path" --project-root . --confirm CLEAR-READONLY
```

## 3. Live Process Lock

If ACLs look valid, stop/release the specific authorized watcher/editor/agent/test process using the path. Use bounded retry if appropriate. If the holder is unknown, report the blocker instead of killing processes indiscriminately.

## 4. Windows ACL Problem

For a project-owned path, after authorization:

```powershell
python .\scripts\safe_file_ops.py repair-acl ".\Problem-Path" --project-root . --confirm REPAIR-ACL
```

This resets ACLs to inherited defaults and can remove custom explicit entries, so it is not a routine cleanup command. If elevation is required, the helper does not bypass it.

## 5. Ownership

The helper does not call `takeown`. Ownership repair is a separate explicit system-administration action.

## 6. Quarantine

Once operable, prefer quarantine over immediate deletion, validate the project, then restore or explicitly purge.
