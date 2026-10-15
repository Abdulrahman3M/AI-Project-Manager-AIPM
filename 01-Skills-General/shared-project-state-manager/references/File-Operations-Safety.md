# File Operations Safety

The file helper solves project-local cleanup and relocation problems without becoming a security bypass.

## Safety Order

1. Diagnose target/access state.
2. Dry-run when uncertainty matters.
3. Prefer reversible move or quarantine.
4. Repair the narrow problem only when necessary.
5. Reset Windows ACLs only for a project-owned path, only when explicitly intended, and only after diagnosis.
6. Verify the project/tool still works.
7. Purge only quarantined data confirmed disposable.

## Project Root Boundary

Every helper operation resolves against `--project-root` and refuses paths that escape it.

## Quarantine

`quarantine` moves a path to `Shared-Project-State/Quarantine/Items` and writes a recovery record under `Quarantine/Records`. `restore` refuses to overwrite an occupied original path.

## Destructive Cleanup

`purge` acts only on a path named by a quarantine record and verified to be under `Quarantine/Items`. It requires `--confirm PURGE-QUARANTINE`. There is intentionally no generic recursive-delete command.

## Permission Changes

`clear-readonly` requires `--confirm CLEAR-READONLY`.

`repair-acl` is Windows-only and runs `icacls <path> /inheritance:e /reset` (recursively for directories unless disabled). It requires `--confirm REPAIR-ACL`. It does not run `takeown`, grant Everyone/full control, self-elevate, or disable security controls.

## Locks

A permission error can be caused by a live process handle rather than ACLs. Release or stop the relevant authorized process/agent/tool, then retry. The helper uses only bounded retries and never kills processes or force-closes handles.

## Unknown Data

Do not quarantine or purge files just because they look temporary. Confirm they belong to the active task or are intentionally disposable.
