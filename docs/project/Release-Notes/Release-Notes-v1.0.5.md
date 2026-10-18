# AI Project Manager v1.0.5 Release Notes

## Highlights

- The ChatGPT/Codex Plugin archive now generates documented portable and Codex compatibility manifests, complete listing metadata, a bundled SVG icon, and valid YAML Skill front matter.
- Canonical AIPM Skill source files are preserved; host-required metadata exists only in the generated ChatGPT/Codex distribution.
- `AGENTS.md` now requires automatic Plugin impact review, rebuild, validation, and reporting whenever Skills or Prompts change.

## Distribution

Build the current local archives with:

```powershell
.\Plugins\Build-System\Build-AIPM-Plugin.ps1 -Platform All -Validate
```

The command creates ChatGPT/Codex, Claude Code, and Google Antigravity ZIP archives plus SHA-256 sidecars under `Plugins/Dist/`.

## Limits

ChatGPT/Codex package validation is local and structural; final upload and host review remain controlled by the relevant ChatGPT account or workspace. Claude Code has not been live-installed. Google Antigravity remains `FORMAT_UNVERIFIED` until an official package specification and host test are available.
