# Capability Library

## Purpose

This library records the approved General Skills and Prompt relationships in a deterministic, reviewable registry. Skill masters remain authoritative under `01-Skills-General`; this registry is generated metadata, not a replacement for those files.

## Registered Inventory

- 18 General Skills: 16 byte-preserved imports, the documented `project-orchestrator` derivative, and the AIPM first-party `tui-intelligence` Skill.
- Skill-owned Prompts remain in their owning Skill folders and are listed in the registry.
- One owner-added standalone Prompt is registered from `02-Prompt-General`.
- Personal Skills, `import-memory`, and `morning` are excluded.

See [Registry](Registry.json), the [First-Party Skill Manifest](First-Party-Skills.json), and the [Provenance Ledger](../Project-Documentation/Provenance/Capability-Library-Ledger.json) for file-level SHA-256 and source/licensing records.

## Validation And Generation

From the repository root, run:

```powershell
python Maintenance-Tools/Invoke-Capability-Library.py validate
python Maintenance-Tools/Invoke-Capability-Library.py build-plugin
python Maintenance-Tools/Invoke-Capability-Library.py validate-plugin
```

Plugin output is generated beneath `Plugins/aipm-general-skills`, staged and checked before replacement, and limited to General Skill masters. The sample carries OpenAI portable/Codex compatibility, Claude Code, and Gemini CLI package manifests. The manifests establish layout only; this workflow does not publish or install any provider package.

The protected initial registry is created once with `initialize-baseline --confirm-initial-baseline`. Refreshing existing records requires `refresh-baseline --confirm-integrity-baseline-update --reason "..."`, a valid reason, and the version/changelog changes required by the policy. Do not edit the registry or provenance ledger by hand.

## Version Policy

Skills use independent SemVer streams. Edits require PATCH, additions/removals require MINOR, and breaking capability changes require MAJOR. The platform follows the owner's established MINOR carry-forward convention (`0.9.5` → `0.10.5`) for MINOR changes. The generated Plugin has an independent standard SemVer stream.

## License Boundaries

Apache-2.0 applies only to AIPM-authored files and the declared `tui-intelligence` Skill. Imported Skill terms and retained third-party notices remain in force. The exact Universal AI ToolKit Personal Use License is retained in the provenance directory and copied into the local sample; the sample carries both licenses with per-Skill scope and no blanket Plugin license.
