# P08 Checkpoint

## Acceptance Status

IMPLEMENTED — automated and package gates pass; phase exit remains open because the required interactive Windows Terminal/console visual gate is `UNVERIFIED`. See [P08 Phase Report](../Phase-Reports/P08-Report.md). Do not start P09 until a real terminal review and screenshot evidence are recorded.

## Durable Invariants

- Core Engine remains the sole project-state source; the PowerShell client is read-only and invokes the Core CLI.
- Unknown evidence stays `Unknown`/`Unverified`; no unweighted progress, test count, agent identity, history, or AI connection is invented.
- Dashboard, Command Palette, and Assistant Console are available; Task Dashboard is the default. UI settings do not mutate project state.
- Renderer owns output diffs; unchanged frames emit no bytes. Automated tests do not establish a visually flicker-free experience on a host.
- Preserve imported Skill hashes and per-Skill licenses. Apache-2.0 applies only to AIPM-authored files and the declared first-party Skill.
- Do not install or publish the portable package; no Universal AI ToolKit source or remote was modified.

## Verified Gates

- Python P02–P08 focused suite: 105/105 passed.
- Full Python suite: 107/107 passed.
- TUI tests: 132/132 passed on PowerShell 7.6.5 and Windows PowerShell 5.1.
- TUI project checks: 22/22 passed on each edition.
- Capability `validate` and `validate-plugin`: PASS without refreshing the integrity baseline.
- Portable package extraction and launcher smoke tests: PASS; SHA-256 is recorded in the P08 report.

## Recovery And Resume

1. Read `Project-Documentation/Phase-Reports/P08-Report.md` and `TUI/AI-Project-Manager/docs/Screenshot-Status.md`.
2. From the actual repository, run `TUI/AI-Project-Manager/AIPM.bat` in Windows Terminal and the Windows PowerShell 5.1 console.
3. Inspect ordinary/narrow terminal sizes, semantic colors/icons and fallback, selected shading, descriptions, keyboard navigation, resize, and visible flicker. Capture actual screenshots only; keep `UNVERIFIED` until observed.
4. Update the screenshot status and P08 report/checkpoint with host/version, commands, captures, and any resolved defects. Rerun the affected tests and full relevant gates.
5. Only after P08's manual acceptance passes may P09 be considered. Do not use this checkpoint as authorization to publish or install.

## Exact Next Action

Perform the physical UI review in Windows Terminal and Windows PowerShell 5.1 console; no P09 work is authorized before that evidence closes the P08 visual gate.
