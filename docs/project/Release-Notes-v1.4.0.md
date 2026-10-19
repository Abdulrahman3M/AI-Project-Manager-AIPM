# AI Project Manager v1.4.0

AI Project Manager v1.4.0 is the first source release after the published `v1.0.2` baseline. It brings the accumulated, previously development-only platform work together with the expanded PowerShell TUI App Designer Skill and refreshed capability distributions. The platform and PowerShell TUI versions are synchronized at `1.4.0`; the Skill is independently versioned at `1.1.0`.

## Highlights Since v1.0.2

### Safer Project And Registry Management

- Added Core-enforced self-protection so supported project, task, registry, backup, and restore operations cannot target or overlap the AIPM installation.
- Added guided Registry Management for choosing an external registry JSON path, connecting an existing registry, registering projects, viewing registered projects, creating checksummed backups, and restoring with a safety copy.
- Kept the registry outside the AIPM installation by default and documented that paths are references to local projects, not project copies.
- Made denied Windows ACL checks fail promptly: the access probe now uses one exclusive UUID path rather than Python's retrying temporary-file helper, which can loop when Windows reports a denied directory as writable.

### Task Context And Agent Handoffs

- Added independent task records, plans, checkpoints, blockers, verification notes, reports, handoffs, and task-scoped supporting-file controls under each managed project's `Shared-Project-State-Manager/`.
- Added Core-backed task creation and management through the PowerShell TUI. A project is refreshed and selected before task operations; existing working files stay in their original location.
- Added attachment inventory, pagination, and filename/relative-path search scoped only to **View Attached Task Files**.
- Preserved the architectural boundary: AIPM manages task context and evidence; AI agents edit the target project's original source files and run its tests under the host's existing permissions.

### Capability And Plugin Distribution

- Added a governed Skill/Prompt library and reproducible multi-host build/validation for ChatGPT/Codex, Claude Code, and Google Antigravity.
- Rebuilt the Legacy Project Agent Bridge and all three platform-specific archives from the refreshed, integrity-checked capability registry. Archive checks, content inventories, exclusion rules, and SHA-256 sidecars are validated locally.
- Expanded `powershell-tui-app-designer` with a complete reusable guide to resize-safe TUI frame/input lifecycle and Windows Terminal launcher argument diagnosis. The Skill now includes shared implementation templates, regression tests, detailed references, and a Windows `CommandLineToArgvW` parser probe.

### Documentation And User Experience

- Improved the PowerShell TUI task workflow, long-page pagination, attachment search, and registry guidance.
- Added English and Arabic beginner guides, project architecture and distribution documentation, release hygiene, and clearer status reporting.

## Verification

- PowerShell TUI App Designer Skill package: 63 checks passed on Windows PowerShell 5.1.26100.9444 and PowerShell 7.6.5, with zero failures and zero unverified checks in each run. This includes generation and tests of sample apps, validator checks, examples, and the Windows launcher argument probe.
- The full Core, TUI, Plugin distribution, and source-package checks are listed in the repository Support Matrix. These results do not imply that GitHub Actions ran.
- Full Python repository suite: 143 tests, 0 failures, 4 skipped for host-denied junction/hard-link creation. PowerShell TUI suite: 146 passed on both PowerShell 7 and Windows PowerShell 5.1; Skill package suite: 63 passed on each edition.
- `Releases/AI-Project-Manager-v1.4.0.zip` is the allowlisted source archive; `Releases/AI-Project-Manager-v1.4.0.zip.sha256` is its checksum sidecar. The embedded release manifest records hashes for the included files.

## Version And Release Assets

- Platform: `1.4.0`
- PowerShell TUI: `1.4.0`
- PowerShell TUI App Designer Skill: `1.1.0`
- Legacy Project Agent Bridge: `1.0.12`, independently versioned; generated and validated but not installed or separately published.
- Host archives: `AIPM-ChatGPT-Plugin-v1.4.0.zip`, `AIPM-Claude-Plugin-v1.4.0.zip`, and `AIPM-Antigavity-Plugin-v1.4.0.zip`. They are generated local packages, not claims of installation.

## Known Limitations

- The GitHub repository remains private; authenticated access is required.
- Plugin archive validation proves local structure and package integrity, not acceptance, installation, or runtime behavior inside ChatGPT, Claude Code, or Google Antigravity.
- Live cross-provider agent handoff, physically external-project execution gates, native Antigravity format/runtime acceptance, and durable native-terminal screenshot provenance remain `UNVERIFIED` unless separately exercised and recorded.
- GitHub Actions were not run as part of this release workflow; no paid CI minutes were consumed.

## Integrity

Use the attached `AI-Project-Manager-v1.4.0.zip` and `.sha256` sidecar from this GitHub Release. The local source-release verifier checks the sidecar and every manifest-listed file hash before upload.
