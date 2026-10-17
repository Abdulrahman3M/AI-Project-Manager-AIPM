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
- For every product release, increment the platform and TUI versions together using SemVer; update both changelogs and add versioned release notes.
- Keep the root README product title, adjacent version, release/status badges, and latest-release link synchronized with the current release. Update the Support Matrix and release index as needed, then build and verify the source ZIP and SHA-256 sidecar before publishing.
- Publish the same verified source ZIP and checksum sidecar attached to the matching `vX.Y.Z` GitHub Release; verify the remote tag, assets, and checksum against the local build. Do not claim CI, host, or cross-agent checks that were not run; avoid paid Actions when not authorized or available.
- Preserve independently versioned Skills and Plugins unless their own content or metadata changes require a version update.
