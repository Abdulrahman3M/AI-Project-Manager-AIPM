# P08 Checkpoint

## Acceptance Status

IMPLEMENTED — automated and package gates pass; an interactive PTY test found and fixed short-terminal clipping, but the required actual Windows Terminal/native-console visual gate remains `UNVERIFIED`. See [P08 Phase Report](../Phase-Reports/P08-Report.md). Do not start P09 until a real terminal review and screenshot evidence are recorded.

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
- Full TUI test runner: 181/181 passed on PowerShell 7.6.5 and Windows PowerShell 5.1.26100.9444.
- TUI project checks: 22/22 passed on each edition.
- Product-shell follow-up: versions are synchronized at 0.2.1; the header keeps the name/version adjacent, selections use a colored arrow and foreground text without background fill, and descriptions are unshaded. Geometry reuse, Core session snapshots, explicit Refresh, and last-good preservation are covered by tests.
- Current portable package: `.test-workspace/P08-Package-20261017/AIPM-v0.2.1.zip`, SHA-256 `BDBCC255E951C08921823E5DD9C6B7CABAED6FFCCEB711FEC75C0AC3BD0D18A8`; source hashes, `-Version`, and scripted Exit pass on both PowerShell editions.
- Interactive follow-up: PowerShell 7.6.5 and Windows PowerShell 5.1.26100.9444 PTY sessions reached option 14 in the 14-action dashboard; the visible range, explanations, selected state, and footer remained in VT output. Arrow navigation used row updates without a full-screen clear. Full Python suite passed 107/107 when run with the required Windows junction capability.
- Screenshot status remains `UNVERIFIED`: no `WT_SESSION`, genuine Windows Terminal/native-console capture, or human visual review was available. Current Windows Computer-Use policy prohibits automating terminal applications, so this session cannot perform the native-host visual gate.
- Capability `validate` and `validate-plugin`: PASS without refreshing the integrity baseline.
- Portable package extraction and launcher smoke tests: PASS; SHA-256 is recorded in the P08 report.

## Recovery And Resume

1. Read `Project-Documentation/Phase-Reports/P08-Report.md` and `TUI/AI-Project-Manager/docs/Screenshot-Status.md`.
2. From the actual repository, run `TUI/AI-Project-Manager/AIPM.bat` in Windows Terminal and the Windows PowerShell 5.1 console.
3. Inspect ordinary/narrow terminal sizes, semantic colors/icons and fallback, the colored selection arrow, unshaded descriptions, keyboard navigation, resize, and visible flicker. Capture actual screenshots only; keep `UNVERIFIED` until observed.
4. Update the screenshot status and P08 report/checkpoint with host/version, commands, captures, and any resolved defects. Rerun the affected tests and full relevant gates.
5. Only after P08's manual acceptance passes may P09 be considered. Do not use this checkpoint as authorization to publish or install.

## Exact Next Action

Perform the physical UI review in Windows Terminal and Windows PowerShell 5.1 console; no P09 work is authorized before that evidence closes the P08 visual gate.
