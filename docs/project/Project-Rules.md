# AIPM Project Rules

## AIPM Self-Protection

When using AIPM on another project, the AIPM repository itself is protected from changes. Only a direct, explicit owner request to develop or repair AIPM permits edits to its source. The Core Engine rejects project roots, registry files, and registry backups whose paths overlap the detected AIPM installation. This is an application boundary, not an operating-system sandbox: external AI agents with direct filesystem permissions must also be constrained by their host workspace permissions or Windows ACLs.

## Project Registry And State

The project registry stores project IDs, display names, and root paths only. Its default location is `%LOCALAPPDATA%\AI-Project-Manager\registry.json` on Windows, selected only after the first-run TUI prompt is accepted. The user may choose a different `registry.json` path outside the AIPM installation. Registry selection is saved in per-user AIPM UI settings; the registry itself is not stored in the AIPM repository.

Each registered project's operational state remains in that project's `Shared-Project-State-Manager/` folder. Registering a project creates that AIPM-owned state folder after confirmation; it does not edit project source files. Unregistering removes only the pointer from the selected registry and never deletes the project's files or state. Registry backups are JSON plus SHA-256 sidecars; restore verifies the sidecar when present and saves a pre-restore copy before replacing the active registry. Changing the selected location does not copy or delete the previous registry.

## Authoritative Sources

- `01-Skills-General/` is the owner-managed General Skill library. The owner may add or remove Skills and establish a new SemVer release baseline. Active imported Skill content, excluding owner-managed `VERSION` and `CHANGELOG.md` release metadata, is checked against recorded source hashes; new AIPM-authored Skills must be declared in the first-party manifest. `project-orchestrator` is the documented derivative.
- `02-Prompt-General/` holds standalone Prompts only. A Prompt belonging to a Skill remains under that Skill and is versioned with it.
- `Capability-Library/Registry.json` and `docs/project/Provenance/Capability-Library-Ledger.json` record the inventory and file hashes. Validate before consuming or generating derived artifacts.
- `Capability-Library/First-Party-Skills.json` declares AIPM-authored Skills separately from imported migration provenance. `tui-intelligence` is the declared first-party Skill.

## Scope And Naming

Do not add `02-Skills-Personal`, `import-memory`, or `morning`. The owner may otherwise add or remove Skills, subject to accurate provenance, license review, and the capability-registry refresh gate. Use English Title Case for new human-facing names; retain technical filenames and Skill slugs.

## Versioning

Use SemVer. Skill edits require PATCH, capability additions/removals require MINOR, and breaking changes require MAJOR. AIPM's platform MINOR version carries the current patch component forward (for example, `0.9.5` to `0.10.5`); Plugin versions are independent standard SemVer. Each release needs matching `VERSION` and changelog metadata.

The capability registry is a protected integrity baseline. Its initial creation is one-time. A refresh requires explicit confirmation, a nonempty reason, valid metadata, and all required project/Skill version and changelog updates. Refresh through the maintenance CLI only.

## Licensing And Provenance

Apply the repository's AI Project Manager Personal Use License to project-owned material and generated distributions. Keep any applicable upstream notices and obligations for imported material accurate; a repository license file alone does not establish ownership or override third-party rights. The source repository is read-only unless the owner explicitly authorizes otherwise.

## Generated Plugin Boundary

Generate `Plugins/aipm-project-agent-bridge` from the owner-selected, validated General Skill set through the capability-library CLI. The bridge may contain no Personal Skill, excluded Skill, standalone Prompt, secret, or undeclared file. It includes a project-agent handoff and Core guidance, but does not grant a host automatic project-file access. Preserve applicable source notices. Validate byte parity before use. Host format manifests establish layout compatibility only; the sample remains local, unpublished, and uninstalled.

## Host And TUI Boundaries

Host adapters consult `Plugins/Adapters/Host-Capability-Matrix.json`, delegate only through Core Engine, require an explicit write grant, and fail closed for unsupported hosts/commands. Manual pasted handoffs are `UNVERIFIED` and cannot be imported as authoritative state. Never infer provider installation or local file access from a package manifest.

`UX-TUI/` and the `tui-intelligence` Skill define design and acceptance contracts. Supplied PNG/SVG files are documentation references, not screenshots or terminal icon resources. Do not claim zero flicker without interactive Windows Terminal evidence.
