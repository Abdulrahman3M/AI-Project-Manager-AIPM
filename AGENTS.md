# AI Project Manager Agent Rules

- Work only inside this repository unless the owner explicitly authorizes another path.
- The owner may add or remove Skills in `01-Skills-General`. Keep provenance and license metadata accurate; preserve source hashes for retained imported Skills. Declare new AIPM-authored Skills in `Capability-Library/First-Party-Skills.json`; update protected capability baselines only through the confirmed CLI workflow.
- `project-orchestrator` is the documented derivative; `tui-intelligence` is the declared AIPM first-party Skill in `Capability-Library/First-Party-Skills.json`.
- Do not add `02-Skills-Personal`, `import-memory`, or `morning`.
- Use English Title Case for new human-facing names. Preserve technical filenames and Skill slugs.
- Do not push, publish, or modify the Universal AI ToolKit source without explicit authorization.
- Apply the AI Project Manager Personal Use License to project material and generated distributions.
- Treat `Capability-Library/Registry.json` and its provenance ledger as protected integrity baselines. Refresh only with the explicit CLI confirmation flag, a reason, and required version/changelog updates.
- Generate Plugin output only with `Maintenance-Tools/Invoke-Capability-Library.py`; keep it inside this repository and unpublished/uninstalled unless separately authorized.
- Keep host adapters capability-declared, permission-gated, and fail-closed. A package-format manifest does not mean installed or runtime-tested; never infer local file access for ChatGPT text conversations.
- Treat `UX-TUI/Visual-References/` images as design references only. Do not claim a working or no-flicker terminal UI until real host/version tests are run.
