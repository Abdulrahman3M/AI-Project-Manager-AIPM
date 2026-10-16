# AIPM Project Rules

## Authoritative Sources

- `01-Skills-General/` is the authoritative General Skill master library. Do not edit migrated masters casually; the 16 preserved Skills must stay byte-identical to the P01 migration record. `project-orchestrator` is the one documented owner-approved derivative.
- `02-Prompt-General/` holds standalone Prompts only. A Prompt belonging to a Skill remains under that Skill and is versioned with it.
- `Capability-Library/Registry.json` and `Project-Documentation/Provenance/Capability-Library-Ledger.json` record the inventory and file hashes. Validate before consuming or generating derived artifacts.
- `Capability-Library/First-Party-Skills.json` declares AIPM-authored Skills separately from the imported migration baseline. The P07 `tui-intelligence` Skill is Apache-2.0 scoped; it does not alter imported Skill licensing.

## Scope And Naming

Do not add `02-Skills-Personal`, `import-memory`, or `morning`. Use English Title Case for new human-facing names; retain technical filenames and Skill slugs.

## Versioning

Use SemVer. Skill edits require PATCH, capability additions/removals require MINOR, and breaking changes require MAJOR. AIPM's platform MINOR version carries the current patch component forward (for example, `0.9.5` to `0.10.5`); Plugin versions are independent standard SemVer. Each release needs matching `VERSION` and changelog metadata.

The capability registry is a protected integrity baseline. Its initial creation is one-time. A refresh requires explicit confirmation, a nonempty reason, valid metadata, and all required project/Skill version and changelog updates. Refresh through the maintenance CLI only.

## Licensing And Provenance

The root Apache-2.0 license applies to AIPM-authored material and declared first-party Skills only. Imported Skills retain the Universal AI ToolKit Personal Use License and all per-Skill copyright, license, and notice files. Do not imply that the root license supersedes those terms. The source repository is read-only; do not write to it.

## Generated Plugin Boundary

Generate `Plugins/aipm-general-skills` from validated General Skill masters through the capability-library CLI. The bundle may contain no Personal Skill, excluded Skill, standalone Prompt, secret, or undeclared file. Preserve source licenses and per-Skill notices. Validate byte parity before use. Host format manifests establish layout compatibility only; the sample remains local, unpublished, and uninstalled.

## Host And TUI Boundaries

Host adapters consult `Plugin-Adapters/Host-Capability-Matrix.json`, delegate only through Core Engine, require an explicit write grant, and fail closed for unsupported hosts/commands. Manual pasted handoffs are `UNVERIFIED` and cannot be imported as authoritative state. Never infer provider installation or local file access from a package manifest.

`UX-TUI/` and the `tui-intelligence` Skill define design and acceptance contracts only until a later phase implements a renderer. Supplied PNG/SVG files are documentation references, not screenshots or terminal icon resources. Do not claim zero flicker without interactive Windows Terminal evidence.
