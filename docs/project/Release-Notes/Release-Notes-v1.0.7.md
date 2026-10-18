# AI Project Manager v1.0.7 — Development Update Notes

> This is a repository development update. It is not a GitHub Release, does not create a Git tag, and does not include a source ZIP or Release asset.

## Highlights

- Added a Core-enforced AIPM installation boundary. A managed project root, registry file, registry backup, or restore source that overlaps the AIPM installation is rejected before Core writes occur.
- Added the project registry lifecycle to the Core CLI and Intelligent TUI. On first interactive use, the owner can approve the default `%LOCALAPPDATA%\AI-Project-Manager\registry.json` location or select a different external `registry.json` path.
- Added Registry Management actions to view, register, unregister, back up, restore, and switch the selected registry. Registration creates only AIPM-owned operational state after confirmation. Unregistering deletes no project files. Restore checks an optional SHA-256 sidecar and creates a pre-restore safety backup.
- Added an explicit owner-authorization rule to `AGENTS.md`: ordinary use of AIPM on another project never authorizes edits to the AIPM installation.

## Verification

- Registry isolation and administration tests cover self-registration rejection, overlap rejection, initialization, registration, pointer-only removal, backup/restore, and checksum tamper rejection.
- The full Core and TUI regression suites are recorded in the Support Matrix after the final validation run for this update.

## Boundaries

- The Core guard protects supported AIPM operations. It cannot prevent a separately authorized process or AI host from writing directly to the AIPM files; use host workspace isolation or Windows ACLs for that operating-system boundary.
- No Skill or Prompt content changed. The three multi-host distributions were rebuilt at `1.0.7` to synchronize catalog metadata; they are not represented as installed or runtime-tested. The independently versioned legacy Bridge remains `1.0.6` because its content did not change.
- The latest published GitHub Release remains `v1.0.2`.
