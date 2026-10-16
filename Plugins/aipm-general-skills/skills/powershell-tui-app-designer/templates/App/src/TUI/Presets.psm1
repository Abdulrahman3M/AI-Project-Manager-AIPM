# Presets.psm1 - generic theme and layout catalog; no third-party branding.
Set-StrictMode -Version 2.0
function Get-TuiPresetCatalog {
    $rows = @(
        'classic-numbered|Classic Numbered|Classic|Cyan|Balanced'
        'assistant-console|Assistant Console|Assistant|Teal|Spacious'
        'command-palette|Command Palette|Palette|Blue|Compact'
        'developer-workbench|Developer Workbench|Workbench|Cyan|Balanced'
        'task-dashboard|Task Dashboard|Dashboard|Green|Balanced'
        'split-pane|Split Pane|Split|Blue|Balanced'
        'wizard-stepper|Wizard Stepper|Wizard|Purple|Spacious'
        'task-monitor|Task Monitor|Monitor|Yellow|Compact'
        'compact-utilities|Compact Utilities|Compact|Gray|Compact'
        'spacious-editorial|Spacious Editorial|Editorial|White|Spacious'
        'minimal-monochrome|Minimal Monochrome|Minimal|Gray|Compact'
        'neon-night|Neon Night|Neon|Magenta|Balanced'
        'soft-slate|Soft Slate|Slate|Blue|Balanced'
        'warm-paper|Warm Paper|Paper|Yellow|Spacious'
        'terminal-retro|Terminal Retro|Retro|Green|Compact'
        'operations-center|Operations Center|Operations|Yellow|Balanced'
        'file-explorer|File Explorer|Explorer|Cyan|Compact'
        'media-workbench|Media Workbench|Media|Magenta|Balanced'
        'troubleshooting|Troubleshooting|Diagnostic|Red|Balanced'
        'setup-onboarding|Setup Onboarding|Onboarding|Purple|Spacious'
    )
    $all = @()
    foreach ($row in $rows) {
        $s = $row.Split('|')
        $all += [pscustomobject]@{ Id = $s[0]; Name = $s[1]; Layout = $s[2]; Accent = $s[3]; Density = $s[4] }
    }
    return $all
}
function Get-TuiPreset {
    param([string]$Id = 'classic-numbered')
    $found = @(Get-TuiPresetCatalog | Where-Object { $_.Id -eq $Id })
    if ($found.Count -eq 0) { throw "Unknown TUI preset: $Id" }
    return $found[0]
}
Export-ModuleMember -Function Get-TuiPresetCatalog, Get-TuiPreset
