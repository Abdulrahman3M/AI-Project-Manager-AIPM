# P07 Checkpoint

## Acceptance Status

PASS — P07 complete at `24f53d5ae084b8e3f933fad9369c9bfaee3ed3dd` on `main`. Focused P07 tests: 16/16. Integrated P02–P07: 100/100 with the previously authorized scoped Windows junction capability. See [P07 Phase Report](../Phase-Reports/P07-Report.md) for commands, default-permission limitation, hashes, and unverified items.

## Durable Invariants

- The library contains 16 SHA-256-checked imported Skills, the documented `project-orchestrator` derivative, and the separately recorded AIPM first-party `tui-intelligence` Skill.
- Apache-2.0 applies to AIPM-authored files and the declared first-party Skill only. Imported Skills retain their Universal AI ToolKit terms and notices; no blanket Plugin license is asserted.
- Host requests use a fixed registered project ID and pass only through Core Engine. Mutations require explicit grant, revision, and idempotency key; unsupported/unverified host calls fail closed.
- Manual handoffs are path-free, read-only, and `UNVERIFIED`; they cannot be imported as authoritative state.
- Plugin sample includes OpenAI portable/Codex compatibility, Claude Code, and Gemini CLI manifests but is not installed or published.
- TUI material is a design contract and Skill, not a live renderer. No physical no-flicker or provider-runtime claim has been made.
- No Personal Skills, `import-memory`, or `morning`; no Universal AI ToolKit source writes; no remote push.

## Recovery And Resume

1. Run `python Maintenance-Tools/Invoke-Capability-Library.py validate` before consuming the registry.
2. Run `python Maintenance-Tools/Invoke-Capability-Library.py validate-plugin` before consuming the local package; rebuild only with the maintenance CLI and `--replace-generated` when the package is recognized and stale.
3. Run `python -m unittest discover -s Tests -p "test_p0[2-7]*.py" -q`. On Windows, the three junction fixtures require the previously authorized scoped capability and write only beneath `.test-workspace`.
4. For any TUI implementation, read the P08 phase specification first and follow the preserved `powershell-tui-app-designer` 13-gate methodology plus the P07 TUI contract. Capture genuine terminal evidence before changing any `UNVERIFIED` visual status.

## Next Exact Action

Wait for the owner to authorize P08. Then read `Phases/P08-PowerShell-TUI-Dashboard.md` in the implementation package, revalidate this checkpoint, and work on P08 only. Do not start P09/P10 or install/publish host packages in this checkpoint.
