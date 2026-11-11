# Capability Library

## Purpose

This library records the approved General Skills and Prompt relationships in a deterministic, reviewable registry. Skill masters remain authoritative under `01-Skills-General`; this registry is generated metadata, not a replacement for those files.

## Registered Inventory

- 14 AIPM-owned General Skills, including `project-manager`, `task-scope-contract`, and `resource-optimization`.
- Skill-owned Prompts remain in their owning Skill folders and are listed in the registry.
- One owner-added standalone Prompt is registered from `02-Prompt-General`.
- Personal Skills, `import-memory`, and `morning` are excluded.

See [Registry](Registry.json), the [First-Party Skill Manifest](First-Party-Skills.json), and the [Provenance Ledger](../docs/project/Provenance/Capability-Library-Ledger.json) for file-level SHA-256 and source/licensing records.

## Validation And Generation

From the repository root, run:

```powershell
python Maintenance-Tools/Invoke-Capability-Library.py validate
python Maintenance-Tools/Invoke-Capability-Library.py build-plugin
python Maintenance-Tools/Invoke-Capability-Library.py validate-plugin
```

Plugin output is generated beneath `Plugins/aipm-project-agent-bridge`, staged and checked before replacement. The local **AIPM Project Agent Bridge** includes an agent handoff, AIPM Core guidance, and approved General Skills. It carries OpenAI portable/Codex compatibility, Claude Code, and Gemini CLI package manifests. The package does not publish, install, or grant automatic local-file access to an agent.

The protected initial registry is created once with `initialize-baseline --confirm-initial-baseline`. Refreshing existing records requires `refresh-baseline --confirm-integrity-baseline-update --reason "..."`, a valid reason, and the version/changelog changes required by the policy. Do not edit the registry or provenance ledger by hand.

An owner-authorized release-baseline reset also requires `--confirm-release-baseline-reset`; it is accepted only when every active Skill is exactly `1.0.0`.

## Version Policy

Skills use independent SemVer streams. Edits require PATCH, additions/removals require MINOR, and breaking capability changes require MAJOR. The product version is owned by `Versioning/VERSION` with its canonical history in `Versioning/CHANGELOG.md`; run `python Maintenance-Tools/Sync-Product-Version.py` to synchronize compatibility files. Platform, TUI, generated legacy bridge, and host Plugin distributions share this release version. Skills retain independent SemVer streams.

## License Boundaries

The Apache License 2.0 applies to every registered Skill and the generated local sample.
