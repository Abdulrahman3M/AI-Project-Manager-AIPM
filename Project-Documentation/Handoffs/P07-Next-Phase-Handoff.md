# P08 Next-Phase Handoff

## Current State

P07 is complete on `main`; implementation checkpoint commit is `24f53d5ae084b8e3f933fad9369c9bfaee3ed3dd`. The current registry has 18 Skills: 16 byte-preserved imports, the documented `project-orchestrator` derivative, and first-party `tui-intelligence`. The generated 18-Skill package includes OpenAI portable/Codex, Claude Code, and Gemini CLI manifests, but is neither installed nor published.

## Verified Gate

- Focused P07 suite: 16/16 passed.
- Integrated P02–P07 suite: 100/100 passed with the authorized in-repository Windows junction capability.
- Core health, capability registry, package parity, reproducible build, Python compilation, SHA-256 image parity, and Git whitespace checks passed.
- The default-permission suite still cannot create three junction test fixtures (`Access is denied`); see the P07 report. The permission-scoped rerun passed all tests.

## Boundaries To Preserve

- Work only inside AIPM. Keep the Universal AI ToolKit source read-only and the 16 preserved Skills byte-identical.
- Preserve per-Skill license terms; Apache-2.0 does not relicense imported material.
- Keep adapter calls Core-only, permission-gated, and fail-closed. Manual handoffs remain unverified until local Core rereads state.
- Treat plugin manifests as package layout only. No provider is installed or runtime-verified.
- Use P07's approved reference mockups and contracts, but do not call them live screenshots. P07 contains no running terminal renderer.
- Do not push, publish, install, or advance beyond P08 without the owner's authorization.

## Resume Procedure

After owner authorization, read the authoritative `Phases/P08-PowerShell-TUI-Dashboard.md` from the package, inspect all applicable repository rules, rerun the P07 checkpoint validation, and execute P08 only. Use the preserved `powershell-tui-app-designer` 13 phase gates and the P07 `tui-intelligence` screen/QA contracts. Record `UNVERIFIED` until real PowerShell/Windows Terminal evidence is captured.
