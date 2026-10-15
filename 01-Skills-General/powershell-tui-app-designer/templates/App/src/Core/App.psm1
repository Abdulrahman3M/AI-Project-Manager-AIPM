# App.psm1 - the application: main menu loop and the actions. Business logic lives in Core modules, never in the TUI modules.
Set-StrictMode -Version 2.0

# Load design defaults supplied by New-TuiProject and prefer saved choices.
function Get-AppDesign {
    param([Parameter(Mandatory)][string]$Root)
    $d = @{ preset='classic-numbered'; navigation='Hybrid'; icons='Auto'; colors='Auto'; descriptions='Muted' }
    $file = Join-Path (Join-Path $Root 'config') 'design.json'
    if (Test-Path -LiteralPath $file) {
        try {
            $j = [System.IO.File]::ReadAllText($file) | ConvertFrom-Json
            foreach ($key in @('preset','navigation','icons','colors','descriptions')) {
                if ($j.PSObject.Properties[$key]) { $d[$key] = [string]$j.$key }
            }
        } catch { Write-AppLog ('Invalid design config: ' + $_.Exception.Message) 'WARNING' }
    }
    foreach ($key in @('preset','navigation','icons','colors','descriptions')) {
        $stored = Get-UserSetting -Name ('design_' + $key)
        if ($stored) { $d[$key] = $stored }
    }
    if ($d.navigation -notin @('Arrows','Numbers','Hybrid','Search')) { $d.navigation = 'Hybrid' }
    if ($d.icons -notin @('Auto','Emoji','Symbol','Ascii','None')) { $d.icons = 'Auto' }
    if ($d.colors -notin @('Auto','Full','Subtle','None')) { $d.colors = 'Auto' }
    if ($d.descriptions -notin @('Muted','Shade','Inline','Panel','Off')) { $d.descriptions = 'Muted' }
    try { [void](Get-TuiPreset -Id $d.preset) } catch { $d.preset = 'classic-numbered' }
    return $d
}
function Apply-AppDesign {
    param([Parameter(Mandatory)][string]$Root)
    $d = Get-AppDesign -Root $Root
    Set-TuiMenuStyle -Navigation $d.navigation -Preset $d.preset -Descriptions $d.descriptions
    Set-TuiColorStyle -Mode $d.colors -Accent (Get-TuiPreset -Id $d.preset).Accent
    Set-IconTier -Tier $d.icons
}
function Invoke-DesignWizard {
    param([Parameter(Mandatory)][string]$Root)
    $catalog = @(Get-TuiPresetCatalog)
    $items = @()
    foreach ($p in $catalog) { $items += (New-MenuItem -Label $p.Name -Desc ($p.Layout + ' layout, ' + $p.Density + ' spacing.') -Value $p.Id -Icon 'Form') }
    $preset = Show-Menu -Title 'Choose a layout' -Description '20 product-neutral styles, including Classic Numbered.' -Items $items -Navigation Search -Preset 'command-palette'
    if (-not $preset) { return }
    $choices = @(
        (New-MenuItem -Label 'Arrow keys + Enter' -Desc 'No numeric prefixes.' -Value 'Arrows'),
        (New-MenuItem -Label 'Numbered choices' -Desc 'Type a menu item number.' -Value 'Numbers'),
        (New-MenuItem -Label 'Numbers and arrows' -Desc 'Both keyboard selection modes.' -Value 'Hybrid'),
        (New-MenuItem -Label 'Search actions' -Desc 'Type words and use arrows/Enter.' -Value 'Search')
    )
    $navigation = Show-Menu -Title 'Navigation style' -Items $choices -Navigation Arrows
    if (-not $navigation) { return }
    $choices = @(
        (New-MenuItem -Label 'Automatic icon detection' -Desc 'Choose the safest icons for the terminal.' -Value 'Auto'),
        (New-MenuItem -Label 'Emoji' -Desc 'Colorful icons in modern terminals.' -Value 'Emoji'),
        (New-MenuItem -Label 'Simple symbols' -Desc 'Lightweight Unicode symbols.' -Value 'Symbol'),
        (New-MenuItem -Label 'ASCII' -Desc 'Portable text icons.' -Value 'Ascii'),
        (New-MenuItem -Label 'No icons' -Desc 'Clean text-only choices.' -Value 'None')
    )
    $icons = Show-Menu -Title 'Icon style' -Items $choices -Navigation Arrows
    if (-not $icons) { return }
    $choices = @(
        (New-MenuItem -Label 'Automatic' -Desc 'Adapt to terminal support.' -Value 'Auto'),
        (New-MenuItem -Label 'Rich accents' -Desc 'Strong accent headings and selections.' -Value 'Full'),
        (New-MenuItem -Label 'Subtle accents' -Desc 'Restrained color hierarchy.' -Value 'Subtle'),
        (New-MenuItem -Label 'No colors' -Desc 'Monochrome interface.' -Value 'None')
    )
    $colors = Show-Menu -Title 'Color style' -Items $choices -Navigation Arrows
    if (-not $colors) { return }
    $choices = @(
        (New-MenuItem -Label 'Muted and indented' -Desc 'Subdued explanation under each option.' -Value 'Muted'),
        (New-MenuItem -Label 'Subtle shading' -Desc 'Indented explanation with faint shading when supported.' -Value 'Shade'),
        (New-MenuItem -Label 'Inline' -Desc 'Description on the same line.' -Value 'Inline'),
        (New-MenuItem -Label 'Details panel' -Desc 'Explain the currently highlighted option.' -Value 'Panel'),
        (New-MenuItem -Label 'Compact, no descriptions' -Desc 'Hide optional explanation rows.' -Value 'Off')
    )
    $descriptions = Show-Menu -Title 'Option descriptions' -Items $choices -Navigation Arrows
    if (-not $descriptions) { return }
    $summary = 'Preset: ' + $preset + '; Navigation: ' + $navigation + '; Icons: ' + $icons + '; Colors: ' + $colors + '; Descriptions: ' + $descriptions
    if (-not (Show-Confirm -Title 'Save this design?' -Message $summary)) { return }
    foreach ($key in @('preset','navigation','icons','colors','descriptions')) {
        $value = switch ($key) {
            'preset' { $preset } 'navigation' { $navigation } 'icons' { $icons }
            'colors' { $colors } 'descriptions' { $descriptions }
        }
        if (-not (Set-UserSetting -Name ('design_' + $key) -Value $value)) {
            Show-Notice -Title 'Settings not saved' -Lines @('The configuration could not be written.') -Kind Error
            return
        }
    }
    Apply-AppDesign -Root $Root
    Show-Notice -Title 'Design updated' -Lines @('The new appearance is active. ' + $summary) -Kind Success
}

function Get-AppVersion {
    param([string]$Root)
    $f = Join-Path $Root 'VERSION'
    if (Test-Path -LiteralPath $f) { return ((Get-Content -LiteralPath $f -TotalCount 1)).Trim() }
    return '0.0.0'
}

function Test-PersonName {
    # Returns $null when valid, else the message. Pure function: unit tested without any UI.
    param([string]$Text)
    if ([string]::IsNullOrWhiteSpace($Text)) { return 'Please type a name.' }
    if ($Text.Length -gt 40) { return 'The name can have at most 40 characters.' }
    return $null
}

function Invoke-DemoForm {
    $name = Read-ValidatedInput -Prompt 'Your name' -Help 'Any name, up to 40 characters.' -Example 'Ada Lovelace' -Validate { param($t) Test-PersonName $t }
    if ($null -eq $name) { return }
    if (Show-Confirm -Title 'Save this name?' -Message ('The name is: ' + $name) -YesLabel 'Yes, save it' -YesDesc 'Store the name in your settings.' -NoLabel 'No, discard it' -NoDesc 'Keep the old value.') {
        if (Set-UserSetting -Name 'name' -Value $name) { Show-Notice -Title 'Saved' -Lines @('Hello, ' + $name + '.') -Kind Success }
        else { Show-Notice -Title 'Could not save' -Lines @('The settings file is not writable. Nothing was changed.') -Kind Error }
    }
}

function Invoke-DemoCommand {
    # External program from an argument array; here the host PowerShell itself, which exists on every platform.
    $ps = Get-CurrentPowerShellPath
    if (-not $ps) { Show-Notice -Title 'PowerShell not found' -Lines @('Cannot locate the PowerShell executable.') -Kind Error; return }
    $r = Invoke-External -FilePath $ps -Arguments @('-NoProfile', '-Command', '$PSVersionTable.PSVersion.ToString()') -TimeoutSec 30
    if ($r.Started -and $r.ExitCode -eq 0) { Show-Notice -Title 'Command finished' -Lines @('PowerShell version: ' + $r.StdOut.Trim()) -Kind Success }
    else { Write-AppLog ('demo command failed: exit ' + $r.ExitCode + ' ' + $r.Error) 'ERROR'; Show-Notice -Title 'Command failed' -Lines @('Exit code ' + $r.ExitCode + '. Details were written to the log file.') -Kind Error }
}

function Invoke-IconStyleChoice {
    $cur = Get-IconTierInUse
    $items = @(
        (New-MenuItem -Label 'Emoji icons' -Desc 'Colorful icons; needs a terminal that draws emoji (Windows Terminal, most Linux terminals).' -Value 'emoji' -Icon 'Run'),
        (New-MenuItem -Label 'Simple symbols' -Desc 'Single-column symbols that every console font can draw.' -Value 'symbol' -Icon 'Settings'),
        (New-MenuItem -Label 'Plain text' -Desc 'ASCII only: use this when icons show as empty boxes.' -Value 'ascii' -Icon 'Item')
    )
    $r = Show-Menu -Title ('Icon style (now: ' + $cur + ')') -Description 'The choice is remembered for next time.' -Items $items
    if ($r) {
        $tier = (Get-Culture).TextInfo.ToTitleCase($r)
        Set-IconTier $tier
        if ($r -ne 'ascii') { [void](Set-UserSetting -Name 'icons' -Value $r) }
    }
}

function Show-AppAbout {
    param([string]$Root)
    $ri = Get-RuntimeInfo
    Show-Notice -Title 'About {{AppName}}' -Lines @(('Version ' + (Get-AppVersion $Root) + '.'), ('Running on ' + $ri.Platform + ' with PowerShell ' + $ri.PowerShell + ' (' + $ri.Edition + ').'), ('Icons: ' + (Get-IconTierInUse) + '.')) -Kind Info
}

function Start-TuiApp {
    param([Parameter(Mandatory)][string]$Root)
    Apply-AppDesign -Root $Root
    $quit = $false
    while (-not $quit) {
        $items = @(
            (New-MenuItem -Label 'Demo form' -Desc 'Type a value with help, an example and validation.' -Value 'form' -Icon 'Form'),
            (New-MenuItem -Label 'Run a command' -Desc 'Start an external program safely and show its result.' -Value 'cmd' -Icon 'Run'),
            (New-MenuItem -Label 'Customize interface' -Desc 'Choose from twenty layouts, navigation, icons, colors and descriptions.' -Value 'icons' -Icon 'Settings'),
            (New-MenuItem -Label 'About' -Desc 'Version, platform and PowerShell edition.' -Value 'about' -Icon 'About'),
            (New-MenuItem -Label 'Exit' -Desc 'Close {{AppName}}. Nothing is left running.' -Value 'exit' -Icon 'Exit')
        )
        $choice = Show-Menu -Title '{{AppName}}' -Description 'Use the chosen keyboard navigation style.' -Items $items
        switch ($choice) {
            'form' { Invoke-DemoForm }
            'cmd' { Invoke-DemoCommand }
            'icons' { Invoke-DesignWizard -Root $Root }
            'about' { Show-AppAbout -Root $Root }
            'exit' { $quit = $true }
            $null { $quit = $true }   # Esc on the main menu leaves the app
        }
    }
}

Export-ModuleMember -Function Get-AppVersion, Test-PersonName, Get-AppDesign, Apply-AppDesign, Invoke-DesignWizard, Start-TuiApp
