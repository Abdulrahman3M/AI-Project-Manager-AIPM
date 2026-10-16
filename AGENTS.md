# AI Project Manager Agent Rules

- Work only inside this repository unless the owner explicitly authorizes another path.
- Treat `01-Skills-General` as governed source material. Sixteen migrated Skills are byte-preserved; `project-orchestrator` is the documented derivative; `tui-intelligence` is the only declared AIPM first-party Skill in `Capability-Library/First-Party-Skills.json`.
- Do not add `02-Skills-Personal`, `import-memory`, or `morning`.
- Use English Title Case for new human-facing names. Preserve technical filenames and Skill slugs.
- Do not push, publish, or modify the Universal AI ToolKit source without explicit authorization.
- Preserve third-party notices and do not represent the root Apache-2.0 license as relicensing imported material.
- Apply Apache-2.0 to AIPM-authored files and the declared `tui-intelligence` Skill only; preserve per-Skill imported license metadata in generated distributions.
- Treat `Capability-Library/Registry.json` and its provenance ledger as protected integrity baselines. Refresh only with the explicit CLI confirmation flag, a reason, and required version/changelog updates.
- Generate Plugin output only with `Maintenance-Tools/Invoke-Capability-Library.py`; keep it inside this repository and unpublished/uninstalled unless separately authorized.
- Keep host adapters capability-declared, permission-gated, and fail-closed. A package-format manifest does not mean installed or runtime-tested; never infer local file access for ChatGPT text conversations.
- Treat `UX-TUI/Visual-References/` images as design references only. Do not claim a working or no-flicker terminal UI until real host/version tests are run.
