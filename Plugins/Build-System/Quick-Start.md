# Multi-Host Plugin Quick Start

Build a complete local Plugin archive from the approved AIPM Skills and Prompts:

```powershell
.\Plugins\Build-System\Build-AIPM-Plugin.ps1 -Platform ChatGPT
```

Use one of these platform values:

```powershell
.\Plugins\Build-System\Build-AIPM-Plugin.ps1 -Platform Claude
.\Plugins\Build-System\Build-AIPM-Plugin.ps1 -Platform Antigavity
.\Plugins\Build-System\Build-AIPM-Plugin.ps1 -Platform All
```

The command writes a ZIP and its `.sha256` checksum sidecar to `Plugins/Dist/`, then validates the archive before reporting success. It includes every AIPM-approved General Skill, all Skill-owned Prompts, and each approved standalone Prompt.

The archives are local build products: this command does not install, publish, or grant any Plugin access to your local project files. For ChatGPT/Codex, use the import or marketplace workflow provided by your account or workspace. For Claude, use its available Plugin installation workflow. The Antigavity profile is a complete transport package but remains `FORMAT_UNVERIFIED` until an official specification and host test are available.

For a ChatGPT workspace upload, select the generated `AIPM-ChatGPT-Plugin-vX.Y.Z.zip` file. The package now includes the portable Agent Plugins manifest, Codex compatibility manifest, listing metadata, SVG icon, and YAML metadata required for a Skills-only package. If upload validation reports a server-side finding, copy its exact issue code before changing the package.

To recheck one archive without rebuilding it, use the Python validator from the repository root:

```powershell
$version = (Get-Content .\VERSION -Raw).Trim()
python .\Plugins\Build-System\build_plugins.py --platform chatgpt --validate ".\Plugins\Dist\AIPM-ChatGPT-Plugin-v$version.zip"
```
