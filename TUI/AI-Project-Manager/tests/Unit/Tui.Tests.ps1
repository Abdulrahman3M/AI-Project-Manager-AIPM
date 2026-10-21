Set-TestGroup 'Differential frame rendering'
Assert-Equal 'Unchanged styled frame updates zero rows' 0 @(Get-UiChangedRows -Before @('A','B') -After @('A','B')).Count
Assert-Equal 'One changed selection role updates exactly one row' '1' (@(Get-UiChangedRows -Before @('row', 'ESC[NormalmChoice') -After @('row', 'ESC[SelectedmChoice')) -join ',')
Assert-Equal 'Moving selection updates two rows' '0,1' (@(Get-UiChangedRows -Before @('Selected','Normal') -After @('Normal','Selected')) -join ',')
Assert-Equal 'Shorter frame erases stale trailing row' '1' (@(Get-UiChangedRows -Before @('A','B') -After @('A')) -join ',')
Assert-Equal 'Larger frame draws newly added row' '1' (@(Get-UiChangedRows -Before @('A') -After @('A','B')) -join ',')

Set-TestGroup 'Product shell header and legacy roles'
$headerUi = Invoke-Ui { Write-AipmProductHeader -Version '1.0.0' -Status 'Core Ready' -Width 50 } ''
Assert-Contains 'product header shows the full product name' $headerUi.Output 'AI Project Manager'
Assert-Contains 'product header keeps the version next to the product name' $headerUi.Output 'AI Project Manager v1.0.0'
Assert-Contains 'product header uses a connected top border' $headerUi.Output '┌'
Assert-Contains 'product header uses a connected bottom border' $headerUi.Output '└'
Assert-Contains 'product header reports the supplied status' $headerUi.Output 'Core Ready'
$refreshHeaderUi = Invoke-Ui { Write-AipmProductHeader -Version '1.0.0' -Status 'Core Ready | Refresh Failed: TEST_REFRESH_BLOCKED | Last Snapshot Preserved' -Width 80 } ''
Assert-Contains '80-column product header keeps the refresh failure and snapshot-preservation status visible' $refreshHeaderUi.Output 'Last Snapshot Preserved'
$compactHeaderUi = Invoke-Ui { Write-AipmProductHeader -Version '1.0.0' -Status 'Core Ready' -Width 20 } ''
Assert-Contains 'narrow product header keeps the compact product name and version adjacent' $compactHeaderUi.Output 'AIPM v1.0.0'
Assert-True 'narrow product header omits lower-priority status to preserve vertical space' (-not $compactHeaderUi.Output.Contains('Core Ready'))
$compactHeaderLines = @($compactHeaderUi.Output -split "`n" | Where-Object { $_ })
Assert-Equal 'narrow product header stays within the terminal width' 0 @($compactHeaderLines | Where-Object { $_.Length -gt 20 }).Count
$rendererPath = Join-Path (Join-Path (Get-TestRoot) 'src/TUI') 'Renderer.psm1'
$rendererText = [System.IO.File]::ReadAllText($rendererPath)
Assert-True 'legacy renderer never assigns a console background color' ($rendererText -notmatch '\[Console\]::BackgroundColor\s*=')
$rendererModule = @(Get-Module | Where-Object { $_.Path -eq $rendererPath }) | Select-Object -First 1
$legacySegments = @()
if ($rendererModule) {
    try {
        $legacySegments = @(& $rendererModule {
            param($row)
            Get-LegacyStyledSegments -Row $row
        } ([string][char]30 + 'Selected' + [string][char]31 + 'Choice' + [string][char]30 + 'SelectionMarker' + [string][char]31 + '> '))
    } catch { $legacySegments = @() }
}
Assert-Equal 'legacy renderer parses selected labels and colored selection markers' 'Selected,SelectionMarker' (@($legacySegments | Where-Object { $_.Text.Length -gt 0 } | ForEach-Object { $_.Role }) -join ',')
Assert-True 'legacy selection segments contain no background-color instruction' (@($legacySegments | Where-Object { $_.PSObject.Properties['Background'] -or $_.PSObject.Properties['BackgroundColor'] }).Count -eq 0)

Set-TestGroup 'Captured Renderer Writes'
$esc = [string][char]27
$savedNoColor = $env:NO_COLOR
Remove-Item Env:NO_COLOR -ErrorAction SilentlyContinue
Set-TuiColorStyle -Mode Full -Accent Cyan
$selectedStyle = Get-RoleStyle 'Selected'
$selectionMarkerStyle = Get-RoleStyle 'SelectionMarker'
Assert-True 'selected labels use foreground styling without a background fill' (-not $selectedStyle.Ansi.Contains('48;') -and -not $selectedStyle.Ansi.Contains('49;'))
Assert-True 'selection marker has a colored foreground without a background fill' ($selectionMarkerStyle.Ansi.Contains('38;') -and -not $selectionMarkerStyle.Ansi.Contains('48;') -and -not $selectionMarkerStyle.Ansi.Contains('49;'))
if ($null -ne $savedNoColor) { $env:NO_COLOR = $savedNoColor }
$env:NO_COLOR = '1'
Assert-Equal 'no-color selection stays bold without inverse background styling' '1' (Get-RoleStyle 'Selected').Ansi
if ($null -eq $savedNoColor) { Remove-Item Env:NO_COLOR -ErrorAction SilentlyContinue } else { $env:NO_COLOR = $savedNoColor }
function Write-TestFrame {
    param([string[]]$Rows, [string[]]$Roles)
    Clear-Ui
    for ($i = 0; $i -lt $Rows.Count; $i++) { Write-UiLine -Text $Rows[$i] -Role $Roles[$i] }
    Complete-UiFrame
}
Initialize-Renderer -Ansi $true -Sink Capture -CaptureWidth 80 -CaptureHeight 24
Enter-Screen
Write-TestFrame -Rows @('Alpha', 'Beta') -Roles @('Normal', 'Normal')
Clear-CapturedOutput
Write-TestFrame -Rows @('Alpha', 'Beta') -Roles @('Normal', 'Normal')
Assert-Equal 'an unchanged captured frame emits zero bytes' '' (Get-CapturedOutput)
Write-TestFrame -Rows @('Alpha', 'Beta') -Roles @('Normal', 'Selected')
Assert-Contains 'a style-only change repaints the affected row' (Get-CapturedOutput) ($esc + '[2;1H')
Clear-CapturedOutput
Write-TestFrame -Rows @('Alpha') -Roles @('Normal')
Assert-Contains 'a shorter frame clears the removed physical row' (Get-CapturedOutput) ($esc + '[2;1H' + $esc + '[2K')
Clear-CapturedOutput
Set-CaptureTerminalSize -Width 120 -Height 30
Write-TestFrame -Rows @('Alpha') -Roles @('Normal')
Assert-True 'resize invalidates the cache and redraws in place' ((Get-CapturedOutput).Contains($esc + '[H' + $esc + '[J') -and -not (Get-CapturedOutput).Contains($esc + '[2J'))
Exit-Screen
Assert-Contains 'the captured renderer restores the cursor' (Get-CapturedOutput) ($esc + '[?25h')
Assert-Contains 'the captured renderer restores the alternate screen' (Get-CapturedOutput) ($esc + '[?1049l')

Initialize-Renderer -Ansi $true -Sink Capture
$rapidItems = @((New-MenuItem -Label 'First Action' -Desc 'Explain The First Action.' -Value 'first'), (New-MenuItem -Label 'Second Action' -Desc 'Explain The Second Action.' -Value 'second'))
Set-ScriptedInput '{Down}{Up}{Enter}'
$rapidChoice = Show-Menu -Title 'Rapid Navigation' -Items $rapidItems -Navigation Arrows
Clear-ScriptedInput
Assert-Equal 'rapid arrow navigation still selects the intended item' 'first' $rapidChoice
Assert-True 'ordinary navigation never emits a full clear-screen command' (-not (Get-CapturedOutput).Contains($esc + '[2J'))
Initialize-Renderer -Ansi $true -Sink Capture
Clear-Ui
Write-UiLine -Text ('Safe' + $esc + '[2J' + 'Text')
Complete-UiFrame
Assert-True 'untrusted dynamic text cannot inject terminal control sequences' (-not (Get-CapturedOutput).Contains($esc + '[2J') -and (Get-CapturedOutput).Contains('SafeText'))
Initialize-Renderer -Ansi $false -Sink Buffer

Set-TestGroup 'Icon tiers'
$wt = @{ WT_SESSION = 'x' }
Assert-Equal 'Windows Terminal -> Emoji' 'Emoji' (Resolve-IconTier -Env $wt -IsWin $true -Redirected $false)
Assert-Equal 'classic Windows console -> Symbol' 'Symbol' (Resolve-IconTier -Env @{} -IsWin $true -Redirected $false)
Assert-Equal 'redirected output -> Ascii' 'Ascii' (Resolve-IconTier -Env $wt -IsWin $true -Redirected $true)
Assert-Equal 'UTF-8 Linux -> Emoji' 'Emoji' (Resolve-IconTier -Env @{ LANG = 'en_US.UTF-8' } -IsWin $false -Redirected $false)
Assert-Equal 'non-UTF-8 Linux -> Ascii' 'Ascii' (Resolve-IconTier -Env @{ LANG = 'C' } -IsWin $false -Redirected $false)
Assert-Equal 'override symbol wins' 'Symbol' (Resolve-IconTier -Env @{ AIPM_ICONS = 'symbol'; WT_SESSION = 'x' } -IsWin $true -Redirected $true)
foreach ($tier in 'Emoji', 'Symbol', 'Ascii') {
    $table = Get-IconTable; $missing = @($table.Keys | Where-Object { -not $table[$_][$tier] })
    Assert-Equal "every icon has a $tier form" 0 $missing.Count
}
Assert-True 'semantic icons match the AIPM map' ((Get-Icon -Name Project -Tier Ascii) -eq '[P]' -and (Get-Icon -Name Task -Tier Ascii) -eq '[T]')
Assert-True 'ASCII icon forms are printable ASCII' (@((Get-IconTable).Values | Where-Object { $_.Ascii -notmatch '^[\x20-\x7E]+$' }).Count -eq 0)

Set-TestGroup 'Numbered menu'
Assert-Equal 'number 1 is 01' '01' (Format-MenuNumber 1)
Assert-Equal 'number 100 is not truncated' '100' (Format-MenuNumber 100)
Assert-Equal 'two-digit number selects at once' 'Select' (Resolve-NumberInput '05' 12).State
Assert-Equal 'a prefix of a longer number waits' 'Wait' (Resolve-NumberInput '1' 12).State
Assert-Equal 'a number outside the list is invalid' 'Invalid' (Resolve-NumberInput '99' 12).State

Set-TestGroup 'Stable menu geometry cache'
$geometryItems = @(
    (New-MenuItem -Label 'Geometry Alpha' -Desc 'First cache row.' -Value 'geometry-alpha'),
    (New-MenuItem -Label 'Geometry Beta' -Desc 'Second cache row.' -Value 'geometry-beta'),
    (New-MenuItem -Label 'Geometry Gamma' -Desc 'Third cache row.' -Value 'geometry-gamma')
)
$geometryFirst = $null; $geometrySame = $null; $geometryBeforeHit = $null; $geometryAfterHit = $null
$geometryWide = $null; $geometrySearch = $null; $geometryDescriptionStyle = $null; $geometryResize = $null
if (Get-Command Get-MenuLayoutMetrics -ErrorAction SilentlyContinue) {
    $geometryFirst = Get-MenuLayoutMetrics -Items $geometryItems -Layout Classic -Density Standard -DescriptionStyle Muted -Width 80 -Height 24
    $geometryBeforeHit = Get-MenuLayoutCacheStats
    $geometrySame = Get-MenuLayoutMetrics -Items $geometryItems -Layout Classic -Density Standard -DescriptionStyle Muted -Width 80 -Height 24
    $geometryAfterHit = Get-MenuLayoutCacheStats
    $geometryWide = Get-MenuLayoutMetrics -Items $geometryItems -Layout Classic -Density Standard -DescriptionStyle Muted -Width 81 -Height 24
    $geometrySearch = Get-MenuLayoutMetrics -Items @($geometryItems[1]) -Layout Classic -Density Standard -DescriptionStyle Muted -Width 80 -Height 24
    $geometryDescriptionStyle = Get-MenuLayoutMetrics -Items $geometryItems -Layout Classic -Density Standard -DescriptionStyle Inline -Width 80 -Height 24
    $geometryResize = Get-MenuLayoutMetrics -Items $geometryItems -Layout Classic -Density Standard -DescriptionStyle Muted -Width 80 -Height 25
}
Assert-True 'equal menu measurements reuse the same cached metrics object' ($null -ne $geometryFirst -and [object]::ReferenceEquals($geometryFirst, $geometrySame))
Assert-True 'equal menu measurements record a cache hit' ($null -ne $geometryBeforeHit -and $null -ne $geometryAfterHit -and $geometryAfterHit.Hits -eq ($geometryBeforeHit.Hits + 1))
Assert-True 'width changes invalidate cached menu geometry' ($null -ne $geometryWide -and -not [object]::ReferenceEquals($geometryFirst, $geometryWide))
Assert-True 'a changed search-visible item set invalidates cached menu geometry' ($null -ne $geometrySearch -and -not [object]::ReferenceEquals($geometryFirst, $geometrySearch))
Assert-True 'description style changes invalidate cached menu geometry' ($null -ne $geometryDescriptionStyle -and -not [object]::ReferenceEquals($geometryFirst, $geometryDescriptionStyle))
Assert-True 'terminal height changes invalidate cached menu geometry' ($null -ne $geometryResize -and -not [object]::ReferenceEquals($geometryFirst, $geometryResize))
$cacheNavigationItems = @((New-MenuItem -Label 'Cache First' -Desc 'First navigation row.' -Value 'cache-first'), (New-MenuItem -Label 'Cache Second' -Desc 'Second navigation row.' -Value 'cache-second'))
$cacheBeforeNavigation = Get-MenuLayoutCacheStats
$cacheNavigation = Invoke-Ui { Show-Menu -Title 'Cache Navigation' -Items $cacheNavigationItems -Navigation Arrows } '{Down}{Down}{Enter}'
$cacheAfterNavigation = Get-MenuLayoutCacheStats
Assert-Equal 'geometry-backed menu navigation still selects the intended action' 'cache-first' $cacheNavigation.Value
Assert-True 'arrow navigation reuses geometry instead of recomputing row layout' ($cacheAfterNavigation.Hits -ge ($cacheBeforeNavigation.Hits + 2))

Set-TestGroup 'Capability Library tables'
$tableUi = $null
if (Get-Command Write-TuiTable -ErrorAction SilentlyContinue) {
    $tableUi = Invoke-Ui {
        Write-TuiTable -Headers @('Type','Capability','Version') -Fields @('Type','Capability','Version') `
            -Rows @([pscustomobject]@{Type='AIPM-Owned';Capability='Create Strict Implementation Handoff';Version='1.0.0'}) `
            -ColumnWidths @(12,52,8) -Width 90
    } ''
}
Assert-True 'Capability Library table renders compact columns and the full capability name' ($null -ne $tableUi -and $tableUi.Error -eq '' -and $tableUi.Output.Contains('Capability') -and -not $tableUi.Output.Contains('Source License') -and $tableUi.Output.Contains('Create Strict Implementation Handoff'))
Assert-Equal 'Capability Library table honors the requested terminal width' 0 $(if ($tableUi) { @($tableUi.Output -split "`n" | Where-Object { $_.Length -gt 90 }).Count } else { -1 })
Assert-True 'Capability Library table uses connected bounded borders' ($null -ne $tableUi -and $tableUi.Output.Contains('┌') -and $tableUi.Output.Contains('┬') -and $tableUi.Output.Contains('└') -and $tableUi.Output.Contains('┴') -and $tableUi.Output.Contains('│'))
$pageCatalog = [pscustomobject]@{
    status='PASS'
    catalog=[pscustomobject]@{
        integrity_status='UNVERIFIED'; skill_count=2
        skills=@(
            [pscustomobject]@{slug='tui-intelligence';version='1.0.0';source_license='Apache License 2.0';aipm_personal_license_applies=$true}
            [pscustomobject]@{slug='audio-timing-author';version='1.0.0';source_license='Apache License 2.0';aipm_personal_license_applies=$true}
        )
        plugin_sample=[pscustomobject]@{version='0.1.0';status='PACKAGE_SAMPLE_ONLY';installation='UNVERIFIED';publication='UNVERIFIED';manifests=@('plugin.json')}
    }
}
$wideCapabilityText = ''; $mediumCapabilityText = ''; $compactCapabilityText = ''; $capabilityPageError = ''
if (Get-Command Show-AipmCapabilityLibrary -ErrorAction SilentlyContinue) {
    Initialize-Renderer -Ansi $true -Sink Capture -CaptureWidth 120 -CaptureHeight 32
    Set-ScriptedInput '{Enter}'
    try { [void](Show-AipmCapabilityLibrary -Catalog $pageCatalog -Version '1.0.0' -Status 'Core Ready') } catch { $capabilityPageError = $_.Exception.Message }
    $wideCapabilityText = [regex]::Replace((Get-CapturedOutput), '\x1B\[[0-?]*[ -/]*[@-~]', '')
    Clear-ScriptedInput
    Initialize-Renderer -Ansi $true -Sink Capture -CaptureWidth 100 -CaptureHeight 32
    Set-ScriptedInput '{Enter}'
    try { [void](Show-AipmCapabilityLibrary -Catalog $pageCatalog -Version '1.0.0' -Status 'Core Ready') } catch { $capabilityPageError = $_.Exception.Message }
    $mediumCapabilityText = [regex]::Replace((Get-CapturedOutput), '\x1B\[[0-?]*[ -/]*[@-~]', '')
    Clear-ScriptedInput
    Initialize-Renderer -Ansi $true -Sink Capture -CaptureWidth 76 -CaptureHeight 32
    Set-ScriptedInput '{Enter}'
    try { [void](Show-AipmCapabilityLibrary -Catalog $pageCatalog -Version '1.0.0' -Status 'Core Ready') } catch { $capabilityPageError = $_.Exception.Message }
    $compactCapabilityText = [regex]::Replace((Get-CapturedOutput), '\x1B\[[0-?]*[ -/]*[@-~]', '')
    Clear-ScriptedInput
    Initialize-Renderer -Ansi $false -Sink Buffer
}
Assert-True 'wide Capability Library uses compact framed Skill tables and keeps Plugin installation unverified' ($capabilityPageError -eq '' -and -not $wideCapabilityText.Contains('Source License') -and $wideCapabilityText.Contains('AIPM Project Agent Bridge') -and $wideCapabilityText.Contains('Unverified')) $capabilityPageError
Assert-True 'medium Capability Library keeps the agent bridge visible without truncating the license into rows' ($capabilityPageError -eq '' -and $mediumCapabilityText.Contains('AIPM Project Agent Bridge') -and $mediumCapabilityText.Contains('Installation: Unverified')) $capabilityPageError
Assert-True 'narrow Capability Library keeps the AIPM license statement below the Skills table' ($capabilityPageError -eq '' -and $compactCapabilityText.Contains('TUI Intelligence') -and $compactCapabilityText.Contains('All Listed Skills Are Covered') -and -not $compactCapabilityText.Contains('License: Apache License 2.0.')) $capabilityPageError
$pluginHeadingIndex = $wideCapabilityText.IndexOf('Plugin Packages')
$pluginRuleIndex = if ($pluginHeadingIndex -ge 0) { $wideCapabilityText.LastIndexOf([string][char]0x251C, $pluginHeadingIndex) } else { -1 }
$pluginTableIndex = if ($pluginHeadingIndex -ge 0) { $wideCapabilityText.IndexOf([string][char]0x250C, $pluginHeadingIndex) } else { -1 }
Assert-True 'Capability Library places the Plugin rule before its heading and table' ($capabilityPageError -eq '' -and $pluginRuleIndex -ge 0 -and $pluginRuleIndex -lt $pluginHeadingIndex -and $pluginHeadingIndex -lt $pluginTableIndex) $capabilityPageError
$skillsHeadingIndex = $wideCapabilityText.IndexOf('AIPM-Owned Skills')
$skillsRuleIndex = if ($skillsHeadingIndex -ge 0) { $wideCapabilityText.LastIndexOf([string][char]0x251C, $skillsHeadingIndex) } else { -1 }
$skillsTableIndex = if ($skillsHeadingIndex -ge 0) { $wideCapabilityText.IndexOf([string][char]0x250C, $skillsHeadingIndex) } else { -1 }
Assert-True 'Capability Library places the Skills rule before its heading and table' ($capabilityPageError -eq '' -and $skillsRuleIndex -ge 0 -and $skillsRuleIndex -lt $skillsHeadingIndex -and $skillsHeadingIndex -lt $skillsTableIndex) $capabilityPageError
$scriptedIdleKey = $null
Set-ScriptedInput '{Idle}'
try { $scriptedIdleKey = Read-AppKey -TimeoutMilliseconds 1 } finally { Clear-ScriptedInput }
Assert-Equal 'scripted idle polling returns a non-key event instead of typed token characters' 'None' $scriptedIdleKey.Name
$items = @((New-MenuItem -Label 'First' -Desc 'd1' -Value 'a'), (New-MenuItem -Label 'Second' -Desc 'd2' -Value 'b'), (New-MenuItem -Label 'Third' -Desc 'd3' -Value 'c'))
$ui = Invoke-Ui { Show-Menu -Title 'T' -Items $items } '02'
Assert-Equal 'typing 02 chooses the second item' 'b' $ui.Value
Assert-True 'every option is shown as NN with its description' ($ui.Output.Contains('01') -and $ui.Output.Contains('02') -and $ui.Output.Contains('03') -and $ui.Output.Contains('d2'))
$ui = Invoke-Ui { Show-Menu -Title 'T' -Items $items } '{Down}{Down}{Enter}'
Assert-Equal 'arrows and Enter choose the third item' 'c' $ui.Value
$viewportItems = @()
for ($i = 1; $i -le 14; $i++) {
    $label = 'Option ' + (Format-MenuNumber $i)
    $viewportItems += New-MenuItem -Label $label -Desc ('Description For ' + $label) -Value ('option-' + $i)
}
Initialize-Renderer -Ansi $true -Sink Capture -CaptureWidth 80 -CaptureHeight 24
$viewportKeys = ((('{Down}' * 13) -join '') + '{Enter}')
Set-ScriptedInput $viewportKeys
$viewportChoice = Show-Menu -Title 'Short Terminal Menu' -Items $viewportItems -Navigation Hybrid
$viewportOutput = Get-CapturedOutput
Clear-ScriptedInput
Assert-Equal 'short terminal arrow navigation reaches an off-screen option' 'option-14' $viewportChoice
Assert-Contains 'short terminal scroll keeps the selected option visible' $viewportOutput 'Option 14'
Assert-Contains 'short terminal indicates the visible option range' $viewportOutput 'Showing'
Assert-Contains 'short terminal keeps the navigation footer reachable' $viewportOutput 'Esc Back'
Initialize-Renderer -Ansi $false -Sink Buffer
$narrowItems = @((New-MenuItem -Label 'A Narrow Option' -Desc 'A concise explanation.' -Value 'narrow'))
Set-TuiProductShell -Version '1.0.0' -Status 'Core Ready | Registry Registered | 13 Options'
Initialize-Renderer -Ansi $false -Sink Capture -CaptureWidth 20 -CaptureHeight 10
Set-ScriptedInput '{Enter}'
$narrowChoice = Show-Menu -Title 'Narrow' -Items $narrowItems -Navigation Arrows
$narrowOutput = Get-CapturedOutput
Clear-ScriptedInput
Assert-Equal 'narrow terminal still selects the visible item' 'narrow' $narrowChoice
Assert-Contains 'narrow terminal keeps Esc Back visible' $narrowOutput 'Esc Back'
Set-TuiProductShell
Initialize-Renderer -Ansi $false -Sink Buffer
$ui = Invoke-Ui { Show-Menu -Title 'T' -Items $items } '{Esc}'
Assert-True 'Esc returns $null (Back)' ($null -eq $ui.Value -and $ui.Error -eq '')
$dis = @((New-MenuItem -Label 'Off' -Desc 'x' -Value 'off' -Enabled $false -Reason 'Needs something that is missing.'), (New-MenuItem -Label 'On' -Desc 'y' -Value 'on'))
$ui = Invoke-Ui { Show-Menu -Title 'T' -Items $dis } '01{Enter}02'
Assert-Equal 'a disabled option cannot be chosen' 'on' $ui.Value
Assert-Contains 'a disabled option shows its reason' $ui.Output 'Needs something that is missing.'
$ui = Invoke-Ui { Show-Menu -Title 'T' -Items $items } ''
Assert-Contains 'running out of scripted keys fails loudly' $ui.Error 'Scripted input exhausted'

Set-TestGroup 'Modern interaction styles'
$ui = Invoke-Ui { Show-Menu -Title 'T' -Items $items -Navigation Arrows } '{Down}{Enter}'
Assert-Equal 'arrow-only selection works' 'b' $ui.Value
Assert-True 'arrow-only menu contains no numeric prefixes' (-not $ui.Output.Contains('01  '))
$ui = Invoke-Ui { Show-Menu -Title 'T' -Items $items -Navigation Numbers } '02'
Assert-Equal 'number selection remains supported' 'b' $ui.Value
$ui = Invoke-Ui { Show-Menu -Title 'T' -Items $items -Navigation Search } 'th{Enter}'
Assert-Equal 'search filters and selects action' 'c' $ui.Value
$ui = Invoke-Ui { Show-Menu -Title 'T' -Items $items -DescriptionStyle Off } '{Enter}'
Assert-True 'descriptions are optional' (-not $ui.Output.Contains('d1'))
$ui = Invoke-Ui { Show-Menu -Title 'T' -Items $items -DescriptionStyle Shade } '{Enter}'
Assert-Contains 'subtle shaded descriptions remain visible' $ui.Output 'd1'
Assert-Equal 'twenty presets are available' 20 @(Get-TuiPresetCatalog).Count
foreach ($p in @(Get-TuiPresetCatalog)) {
    $ui = Invoke-Ui { Show-Menu -Title 'Preview' -Items $items -Preset $p.Id -Navigation Arrows } '{Enter}'
    Assert-Equal ('preset works: ' + $p.Id) 'a' $ui.Value
}
Assert-Equal 'icon suppression returns empty' '' (Get-Icon -Name Item -Tier None)
Set-IconTier -Tier Auto
Assert-Equal 'default view mode is Task Dashboard' 'Task Dashboard' (Get-AipmViewMode)
$ui = Invoke-Ui { Show-Menu -Title 'Help Shortcut' -Items $items } '{F1}'
Assert-Equal 'F1 returns the Help action' '__HELP__' $ui.Value

Set-TestGroup 'Dialogs and prompts'
Assert-Equal 'Show-Confirm 01 is Yes' $true (Invoke-Ui { Show-Confirm -Title 'Q' } '01').Value
Assert-Equal 'Show-Confirm 02 is No' $false (Invoke-Ui { Show-Confirm -Title 'Q' } '02').Value
Assert-Equal 'Esc counts as No' $false (Invoke-Ui { Show-Confirm -Title 'Q' } '{Esc}').Value
$ui = Invoke-Ui { Read-ValidatedInput -Prompt 'P' -Help 'h' -Example 'e' -Validate { param($t) Test-PersonName $t } } '{Enter}Bob{Enter}'
Assert-Equal 'invalid input is rejected, then the valid value is accepted' 'Bob' $ui.Value
Assert-Contains 'the validation message is shown' $ui.Output 'Please type a name.'
Assert-True 'Esc cancels a prompt' ($null -eq (Invoke-Ui { Read-ValidatedInput -Prompt 'P' -Help 'h' -Example 'e' } '{Esc}').Value)
$longPromptText = 'This report summary is long enough to span several terminal rows without hiding the confirmation instructions.'
Initialize-Renderer -Ansi $false -Sink Capture -CaptureWidth 30 -CaptureHeight 24
$ui = Invoke-Ui { Read-ValidatedInput -Prompt 'Task Report' -Help 'h' -Example 'e' -Default $longPromptText } '{Enter}'
Assert-Equal 'long prompt input is accepted intact' $longPromptText $ui.Value
$promptFrame = Get-LastFrame
Assert-Contains 'wrapped prompt retains its input prefix' $promptFrame '> This report summary is long'
Assert-Contains 'wrapped prompt retains confirmation instructions below the input' $promptFrame 'Enter Confirm'

Set-TestGroup 'Whole application (scripted)'
$registry = Join-Path (Get-TestWork) 'registry.json'
$ui = Invoke-Ui { Start-TuiApp -Root (Get-TestRoot) -RegistryPath $registry } '13{Enter}14'
Assert-True 'the Core-backed dashboard, About page and safe Exit run without errors' ($ui.Error -eq '' -and $ui.Output.Contains('Task Dashboard') -and $ui.Output.Contains('About')) $ui.Error
$runtimeVersion = (Get-Content -LiteralPath (Join-Path (Get-TestRoot) 'VERSION') -Raw).Trim()
Assert-True 'the product name and version stay adjacent on the dashboard and primary pages' (([regex]::Matches($ui.Output, ('AI Project Manager v' + $runtimeVersion))).Count -ge 2)
$malformedRegistry = Join-Path (Get-TestWork) 'malformed-app-registry.json'
[System.IO.File]::WriteAllText($malformedRegistry, '{"schema_version":"invalid"}', (New-Object System.Text.UTF8Encoding($false)))
$ui = Invoke-Ui { Start-TuiApp -Root (Get-TestRoot) -RegistryPath $malformedRegistry } '14'
Assert-True 'a blocked Core registry stays visibly Unverified without crashing the dashboard' ($ui.Error -eq '' -and $ui.Output.Contains('Core Blocked') -and $ui.Output.Contains('UNVERIFIED')) $ui.Error
$ui = Invoke-Ui { Start-TuiApp -Root (Get-TestRoot) -RegistryPath $registry } '07{Enter}14'
Assert-True 'Skills and Plugins page reports the project license and unverified package status in Title Case' ($ui.Error -eq '' -and $ui.Output.Contains('Skills & Plugins') -and $ui.Output.Contains('Apache License 2.0') -and $ui.Output.Contains('Unverified')) $ui.Error
$ui = Invoke-Ui { Start-TuiApp -Root (Get-TestRoot) -RegistryPath $registry } '?{Enter}14'
Assert-True 'question mark opens keyboard and evidence Help' ($ui.Error -eq '' -and $ui.Output.Contains('Up/Down: Move Selection')) $ui.Error
$ui = Invoke-Ui { Start-TuiApp -Root (Get-TestRoot) -RegistryPath $registry } '/help{Enter}{Enter}14'
Assert-True 'slash search opens matching Help action' ($ui.Error -eq '' -and $ui.Output.Contains('Search: help')) $ui.Error
$ui = Invoke-Ui { Start-TuiApp -Root (Get-TestRoot) -RegistryPath $registry } 'q0214'
Assert-True 'Q requires explicit confirmation before leaving the dashboard' ($ui.Error -eq '' -and $ui.Output.Contains('Exit AI Project Manager?')) $ui.Error
$ui = Invoke-Ui { Start-TuiApp -Root (Get-TestRoot) -RegistryPath $registry } '{Esc}0214'
Assert-True 'Esc at the main dashboard asks for confirmation before closing AIPM' ($ui.Error -eq '' -and $ui.Output.Contains('Exit AI Project Manager?') -and $ui.Output.Contains('Task Dashboard')) $ui.Error
$ui = Invoke-Ui { Start-TuiApp -Root (Get-TestRoot) -RegistryPath $registry } '{Esc}01'
Assert-True 'confirming the Esc exit prompt closes AIPM without an error' ($ui.Error -eq '') $ui.Error
$ui = Invoke-Ui { Start-TuiApp -Root (Get-TestRoot) -RegistryPath $registry } '100102Exit{Enter}'
Assert-True 'Command Palette mode persists as a UI preference' ($ui.Error -eq '' -and $ui.Output.Contains('Command Palette') -and (Get-AipmViewMode) -eq 'Command Palette') $ui.Error
[void](Set-UserSetting -Name 'view_mode' -Value 'Assistant Console')
$ui = Invoke-Ui { Start-TuiApp -Root (Get-TestRoot) -RegistryPath $registry } '08{Enter}14'
Assert-True 'Assistant Console states that no live AI session is connected' ($ui.Error -eq '' -and $ui.Output.Contains('Assistant Console') -and $ui.Output.Contains('No AI Session Is Connected')) $ui.Error
[void](Set-UserSetting -Name 'view_mode' -Value 'Task Dashboard')
$previousLocalAppData = $env:LOCALAPPDATA
$env:LOCALAPPDATA = Join-Path (Get-TestWork) 'Local App Data'
[void](Set-UserSetting -Name 'registry_path' -Value '')
$defaultRegistry = Join-Path (Join-Path $env:LOCALAPPDATA 'AI-Project-Manager') 'registry.json'
$ui = Invoke-Ui { Start-TuiApp -Root (Get-TestRoot) } '0114'
Assert-True 'first launch asks before creating the default per-user registry' ($ui.Error -eq '' -and $ui.Output.Contains('Project Registry Setup') -and $ui.Output.Contains('Use Default Registry Location') -and (Test-Path -LiteralPath $defaultRegistry -PathType Leaf)) $ui.Error
Assert-Equal 'first-run registry choice is remembered in per-user settings' ([System.IO.Path]::GetFullPath($defaultRegistry)) (Get-UserSetting -Name 'registry_path')
[void](Set-UserSetting -Name 'registry_path' -Value '')
$existingRegistry = Join-Path (Get-TestWork) 'Existing Device Registry.json'
$existingProjectRoot = Join-Path (Get-TestWork) 'Existing Registered Project'
[void](New-Item -ItemType Directory -Path $existingProjectRoot -Force)
$existingData = @{ schema_version='1.0'; projects=@(@{ project_id='Project-Existing123'; root_path=$existingProjectRoot; alias='Existing Device Project' }); preferences=@{} }
[System.IO.File]::WriteAllText($existingRegistry, ($existingData | ConvertTo-Json -Depth 10), (New-Object System.Text.UTF8Encoding($false)))
$existingKeys = '02' + $existingRegistry + '{Enter}{Enter}01{Enter}14'
$ui = Invoke-Ui { Start-TuiApp -Root (Get-TestRoot) } $existingKeys
Assert-True 'first-run setup can connect to and display a valid registry already copied from another device' ($ui.Error -eq '' -and $ui.Output.Contains('Use An Existing Registry File') -and $ui.Output.Contains('Existing Registry Connected') -and $ui.Output.Contains('Project Root Paths Must Exist On This Device') -and $ui.Output.Contains('Existing Device Project') -and (Get-UserSetting -Name 'registry_path') -eq [System.IO.Path]::GetFullPath($existingRegistry)) ($ui.Error + $ui.Output)
[void](Set-UserSetting -Name 'registry_path' -Value '')
$invalidExistingRegistry = Join-Path (Get-TestWork) 'Invalid Existing Registry.json'
[System.IO.File]::WriteAllText($invalidExistingRegistry, '{ not valid registry json', (New-Object System.Text.UTF8Encoding($false)))
$invalidExistingKeys = '02' + $invalidExistingRegistry + '{Enter}{Enter}04'
$ui = Invoke-Ui { Start-TuiApp -Root (Get-TestRoot) } $invalidExistingKeys
Assert-True 'invalid existing registry files are refused without being overwritten or remembered' ($ui.Error -eq '' -and $ui.Output.Contains('Existing Registry Could Not Be Connected') -and (Get-Content -LiteralPath $invalidExistingRegistry -Raw) -eq '{ not valid registry json' -and -not (Get-UserSetting -Name 'registry_path')) ($ui.Error + $ui.Output)
$customRegistry = Join-Path (Join-Path (Get-TestWork) 'Custom Registry Location') 'project-data.json'
$customFolderEntry = (Split-Path -Parent $customRegistry) + [System.IO.Path]::DirectorySeparatorChar
$eraseFolderEntry = '{Backspace}' * $customFolderEntry.Length
$customKeys = '03' + $customFolderEntry + '{Enter}' + $eraseFolderEntry + $customRegistry + '{Enter}14'
$ui = Invoke-Ui { Start-TuiApp -Root (Get-TestRoot) } $customKeys
Assert-True 'first-run setup accepts a custom full path and any .json filename' ($ui.Error -eq '' -and $ui.Output.Contains('Project Registry Setup') -and (Test-Path -LiteralPath $customRegistry -PathType Leaf)) $ui.Error
Assert-Contains 'registry location help requires the full path and permits a chosen JSON filename' $ui.Output 'Enter The Full File Path, Including Any File Name Ending In .json.'
Assert-Contains 'folder-only registry input explains why the full JSON file path is required' $ui.Output 'Enter A Full File Path Ending In .json; A Folder Path Alone Is Not A File.'
Assert-Equal 'custom registry choice is saved without changing the selected path' ([System.IO.Path]::GetFullPath($customRegistry)) (Get-UserSetting -Name 'registry_path')
$env:LOCALAPPDATA = $previousLocalAppData
[void](Set-UserSetting -Name 'registry_path' -Value '')
$ui = Invoke-Ui { Start-TuiApp -Root (Get-TestRoot) -RegistryPath $registry } '090814'
Assert-True 'the main TUI exposes a dedicated Registry Management section with explicit existing-registry connection' ($ui.Error -eq '' -and $ui.Output.Contains('Registry Management') -and $ui.Output.Contains('View Registered Projects') -and $ui.Output.Contains('Back Up Registry') -and $ui.Output.Contains('Connect Existing Registry File')) $ui.Error
$managementRegistry = Join-Path (Get-TestWork) 'Current Management Registry.json'
$remoteRegistry = Join-Path (Get-TestWork) 'Copied Device Registry.json'
$remoteRoot = Join-Path (Get-TestWork) 'Copied Device Project'
[void](New-Item -ItemType Directory -Path $remoteRoot -Force)
$emptyRegistryData = @{ schema_version='1.0'; projects=@(); preferences=@{} }
$remoteRegistryData = @{ schema_version='1.0'; projects=@(@{ project_id='Project-Copied789'; root_path=$remoteRoot; alias='Copied Device Project' }); preferences=@{} }
[System.IO.File]::WriteAllText($managementRegistry, ($emptyRegistryData | ConvertTo-Json -Depth 10), (New-Object System.Text.UTF8Encoding($false)))
[System.IO.File]::WriteAllText($remoteRegistry, ($remoteRegistryData | ConvertTo-Json -Depth 10), (New-Object System.Text.UTF8Encoding($false)))
$connectKeys = '0907' + $remoteRegistry + '{Enter}{Enter}01{Enter}0814'
$ui = Invoke-Ui { Start-TuiApp -Root (Get-TestRoot) -RegistryPath $managementRegistry } $connectKeys
Assert-True 'Registry Management connects to a validated existing file and makes its registered projects active' ($ui.Error -eq '' -and $ui.Output.Contains('Existing Registry Connected') -and $ui.Output.Contains('Project Root Paths Must Exist On This Device') -and $ui.Output.Contains('Copied Device Project') -and (Get-UserSetting -Name 'registry_path') -eq [System.IO.Path]::GetFullPath($remoteRegistry)) ($ui.Error + $ui.Output)
$afterConnect = Get-Content -LiteralPath $remoteRegistry -Raw | ConvertFrom-Json
Assert-Equal 'connecting an existing registry does not rewrite its source file' 1 $afterConnect.projects.Count

Set-TestGroup 'Core State Integration'
$fixtureRoot = Join-Path (Get-TestWork) 'Registered Project Fixture'
$stateRoot = Join-Path $fixtureRoot 'Shared-Project-State-Manager'
[void](New-Item -ItemType Directory -Path (Join-Path $stateRoot 'History/Events') -Force)
$task = @{ title='Verify AIPM TUI'; scope='Read-Only Core Integration'; plan='Read the verified Core state.'; report='TUI state integration passed.'; blockers=@(); verification=@{ result='PASS'; evidence='Core fixture was read successfully.' } }
$state = @{ schema_version='1.1'; revision=0; project_id='P08-Fixture'; task_id='Task-P08'; task_status='COMPLETE'; active_phase='P08'; state_health='CONSISTENT'; last_verified_action='P08 test fixture'; next_action='Continue read-only review.'; branch='main'; head_sha=('a' * 40); updated_at='2026-10-16T10:00:00Z'; updated_by='TUI Test'; tasks=@{ 'Task-P08'=$task }; diff_fingerprint=$null }
$statePath = Join-Path $stateRoot 'State-Manifest.json'
[System.IO.File]::WriteAllText($statePath, ($state | ConvertTo-Json -Depth 20), (New-Object System.Text.UTF8Encoding($false)))
$registeredPath = Join-Path (Get-TestWork) 'registry.json'
$registered = @{ schema_version='1.0'; projects=@(@{ project_id='P08-Fixture'; root_path=$fixtureRoot; alias='Registered Fixture' }); preferences=@{} }
[System.IO.File]::WriteAllText($registeredPath, ($registered | ConvertTo-Json -Depth 10), (New-Object System.Text.UTF8Encoding($false)))
$taskEditRoot = Join-Path (Get-TestWork) 'Task Edit Fixture'
[void](New-Item -ItemType Directory -Path $taskEditRoot -Force)
$taskEditRegistry = Join-Path (Get-TestWork) 'task-edit-registry.json'
$taskEditProjectId = 'Task-Edit-' + [guid]::NewGuid().ToString('N').Substring(0, 8)
$taskEditRegistration = Invoke-AipmCore -AppRoot (Get-TestRoot) -Command 'registry-register' -RegistryPath $taskEditRegistry -ProjectRoot $taskEditRoot -ProjectId $taskEditProjectId -Alias 'Task Edit Fixture'
$taskEditCreated = Invoke-AipmCore -AppRoot (Get-TestRoot) -Command 'task-create' -RegistryPath $taskEditRegistry -ProjectId $taskEditProjectId -Title 'Verify TUI Task Editing' -Scope 'Exercise task plan editing from the user interface.'
$taskEditId = [System.IO.Path]::GetFileName([string]$taskEditCreated.Data.task_path)
$appModule = @(Get-Module | Where-Object { $_.Path -eq (Join-Path (Join-Path (Get-TestRoot) 'src/Core') 'App.psm1') }) | Select-Object -First 1
$taskRow = [pscustomobject]@{ task_id=$taskEditId; title='Verify TUI Task Editing'; status='NOT-STARTED' }
$taskRecordUi = Invoke-Ui { & $appModule { param($root,$registryPath,$projectId,$row) Show-AipmTaskRecord -Root $root -RegistryPath $registryPath -ProjectId $projectId -TaskRow $row } (Get-TestRoot) $taskEditRegistry $taskEditProjectId $taskRow } '02Update plan from TUI{Enter}{Enter}03Verified first test flow{Enter}Next inspect issue boundaries{Enter}{Enter}{Esc}'
$updatedFixtureTask = Invoke-AipmCore -AppRoot (Get-TestRoot) -Command 'task-read' -RegistryPath $taskEditRegistry -ProjectId $taskEditProjectId -TaskId $taskEditId
Assert-True 'task selection opens the management menu directly and task detail is an explicit action' ($taskEditRegistration.Status -eq 'PASS' -and $taskRecordUi.Error -eq '' -and $taskRecordUi.Output.Contains('Manage Task: Verify TUI Task Editing') -and $taskRecordUi.Output.Contains('View Task Status And Details') -and $taskRecordUi.Output.Contains('Current Status: IN-PROGRESS') -and $updatedFixtureTask.Status -eq 'PASS' -and $updatedFixtureTask.Data.task.plan.Contains('Update plan from TUI') -and $updatedFixtureTask.Data.task.last_verified_action -eq 'Verified first test flow' -and $updatedFixtureTask.Data.task.next_action -eq 'Next inspect issue boundaries') ($taskRecordUi.Error + $taskRecordUi.Output)
$reportSource = Join-Path (Get-TestWork) 'Agent Progress Report.md'
[System.IO.File]::WriteAllText($reportSource, '# Verified Agent Report`n- Tests: PASS', (New-Object System.Text.UTF8Encoding($false)))
$attachKeys = '08' + '03' + $reportSource + '{Enter}{Enter}01{Enter}{Esc}'
$attachUi = Invoke-Ui { & $appModule { param($root,$registryPath,$projectId,$row) Show-AipmTaskRecord -Root $root -RegistryPath $registryPath -ProjectId $projectId -TaskRow $row } (Get-TestRoot) $taskEditRegistry $taskEditProjectId $taskRow } $attachKeys
$attachedFiles = Invoke-AipmCore -AppRoot (Get-TestRoot) -Command 'task-artifact-list' -RegistryPath $taskEditRegistry -ProjectId $taskEditProjectId -TaskId $taskEditId
Assert-True 'TUI attaches a selected report through Core without changing its original file' ($attachUi.Error -eq '' -and $attachUi.Output.Contains('Attach Plan, Report Or Supporting File') -and $attachedFiles.Status -eq 'PASS' -and @($attachedFiles.Data.artifacts | Where-Object { $_.path -eq 'Reports/Agent Progress Report.md' }).Count -eq 1 -and [System.IO.File]::ReadAllText($reportSource).Contains('Verified Agent Report')) ($attachUi.Error + $attachUi.Output)
$artifactListingUi = Invoke-Ui { & $appModule { param($root,$registryPath,$projectId,$row) Show-AipmTaskRecord -Root $root -RegistryPath $registryPath -ProjectId $projectId -TaskRow $row } (Get-TestRoot) $taskEditRegistry $taskEditProjectId $taskRow } '09{Enter}{Esc}'
Assert-True 'attached task files can be reviewed from the task management menu' ($artifactListingUi.Error -eq '' -and $artifactListingUi.Output.Contains('Attached Task Files') -and $artifactListingUi.Output.Contains('Reports/Agent Progress Report.md')) ($artifactListingUi.Error + $artifactListingUi.Output)
$artifactSearchUi = Invoke-Ui { & $appModule { param($root,$registryPath,$projectId,$row) Show-AipmTaskRecord -Root $root -RegistryPath $registryPath -ProjectId $projectId -TaskRow $row } (Get-TestRoot) $taskEditRegistry $taskEditProjectId $taskRow } '09/Agent Progress Report.md{Enter}/Definitely Missing.md{Enter}/{Enter}{Esc}{Esc}'
Assert-True 'attached task file search reports exact matches, missing files, and restores the full list when cleared' ($artifactSearchUi.Error -eq '' -and $artifactSearchUi.Output.Contains('Exact File Match: Found') -and $artifactSearchUi.Output.Contains('Matching Files: 1') -and $artifactSearchUi.Output.Contains('Exact File Match: Not Found') -and $artifactSearchUi.Output.Contains('No Matching Files Found') -and $artifactSearchUi.Output.Contains('Search Query: All Files') -and $artifactSearchUi.Output.Contains('Reports/Agent Progress Report.md')) ($artifactSearchUi.Error + $artifactSearchUi.Output)
$longArtifactLines = @('Task: GitHub Learning Series', 'Status: IN-PROGRESS', '') + @(1..12 | ForEach-Object { 'Artifact Entry {0:D2}' -f $_ })
$pagedArtifactUi = Invoke-Ui {
    Initialize-Renderer -Ansi $false -Sink Capture -CaptureWidth 100 -CaptureHeight 14
    [void](Show-AipmPage -Title 'Attached Task Files' -Lines $longArtifactLines)
} '{PageDown}{PageDown}{Esc}'
Assert-True 'long attached task file lists are paginated and the last artifact is reachable on a short terminal' ($pagedArtifactUi.Error -eq '' -and $pagedArtifactUi.Output.Contains('Page 1 of 3') -and $pagedArtifactUi.Output.Contains('Page 3 of 3') -and $pagedArtifactUi.Output.Contains('Artifact Entry 12')) ($pagedArtifactUi.Error + $pagedArtifactUi.Output)
$ordinaryPageUi = Invoke-Ui {
    Initialize-Renderer -Ansi $false -Sink Capture -CaptureWidth 100 -CaptureHeight 20
    [void](Show-AipmPage -Title 'Ordinary Read-Only Page' -Lines @('Ordinary Content'))
} '/{Esc}'
Assert-True 'search affordance is absent from non-attachment information pages' ($ordinaryPageUi.Error -eq '' -and -not $ordinaryPageUi.Output.Contains('/ Search')) ($ordinaryPageUi.Error + $ordinaryPageUi.Output)
$ui = Invoke-Ui { Start-TuiApp -Root (Get-TestRoot) -RegistryPath $registeredPath } '14'
Assert-True 'registered projects are not separate actions on the main dashboard' ($ui.Error -eq '' -and -not $ui.Output.Contains('Registered Fixture')) ($ui.Error + $ui.Output)
$ui = Invoke-Ui { Start-TuiApp -Root (Get-TestRoot) -RegistryPath $registeredPath } '01{Enter}14'
Assert-True 'Projects section lists registered projects and their verified state' ($ui.Error -eq '' -and $ui.Output.Contains('Registered Fixture') -and $ui.Output.Contains('Phase: P08')) ($ui.Error + $ui.Output)
$ui = Invoke-Ui { Start-TuiApp -Root (Get-TestRoot) -RegistryPath $registeredPath } '0201040214'
Assert-True 'task management refreshes projects and offers opening existing tasks after project selection' ($ui.Error -eq '' -and $ui.Output.Contains('Select Registered Project') -and $ui.Output.Contains('Tasks: Registered Fixture') -and $ui.Output.Contains('Open Existing Task')) ($ui.Error + $ui.Output)
$emptyTaskRegistry = Join-Path (Get-TestWork) 'empty-task-registry.json'
$emptyRegistryData = @{ schema_version='1.0'; projects=@(); preferences=@{} }
[System.IO.File]::WriteAllText($emptyTaskRegistry, ($emptyRegistryData | ConvertTo-Json -Depth 10), (New-Object System.Text.UTF8Encoding($false)))
$ui = Invoke-Ui { Start-TuiApp -Root (Get-TestRoot) -RegistryPath $emptyTaskRegistry } '02214'
Assert-True 'task management requires a registered project and directs an empty registry to project registration' ($ui.Error -eq '' -and $ui.Output.Contains('No Projects Are Registered') -and $ui.Output.Contains('Register A Project First')) ($ui.Error + $ui.Output)
$managedTaskRoot = Join-Path (Get-TestWork) 'TUI Task Management Project'
$existingWorkFolder = Join-Path $managedTaskRoot 'Incoming Work'
[void](New-Item -ItemType Directory -Path $existingWorkFolder -Force)
[System.IO.File]::WriteAllText((Join-Path $existingWorkFolder 'notes.md'), 'User work stays here.', (New-Object System.Text.UTF8Encoding($false)))
$managedTaskRegistry = Join-Path (Get-TestWork) 'tui-task-management-registry.json'
$managedTaskProjectId = 'TUI-Task-' + [guid]::NewGuid().ToString('N').Substring(0, 8)
$taskProjectRegistration = Invoke-AipmCore -AppRoot (Get-TestRoot) -Command 'registry-register' -RegistryPath $managedTaskRegistry -ProjectRoot $managedTaskRoot -ProjectId $managedTaskProjectId -Alias 'TUI Task Fixture'
Assert-Equal 'TUI task fixture is registered in Core' 'PASS' $taskProjectRegistration.Status
$taskCreateKeys = '02' + '01' + '01' + 'Organize The Existing Work{Enter}' + 'Review files and agree on next steps{Enter}' + '{Enter}' + '04' + '02' + '14'
$ui = Invoke-Ui { Start-TuiApp -Root (Get-TestRoot) -RegistryPath $managedTaskRegistry } $taskCreateKeys
$createdTaskList = Invoke-AipmCore -AppRoot (Get-TestRoot) -Command 'task-list' -RegistryPath $managedTaskRegistry -ProjectId $managedTaskProjectId
Assert-True 'TUI creates a new task only after selecting a registered project and Core lists it' ($ui.Error -eq '' -and $createdTaskList.Status -eq 'PASS' -and $createdTaskList.Data.tasks.Count -eq 1 -and $createdTaskList.Data.tasks[0].title -eq 'Organize The Existing Work') ($ui.Error + $ui.Output)
$taskFolderKeys = '02' + '01' + '02' + $existingWorkFolder + '{Enter}' + 'Organize Imported Notes{Enter}' + 'Review existing task files in place{Enter}' + '{Enter}' + '04' + '02' + '14'
$ui = Invoke-Ui { Start-TuiApp -Root (Get-TestRoot) -RegistryPath $managedTaskRegistry } $taskFolderKeys
$afterFolderTaskList = Invoke-AipmCore -AppRoot (Get-TestRoot) -Command 'task-list' -RegistryPath $managedTaskRegistry -ProjectId $managedTaskProjectId
Assert-True 'existing work folder is added as task context without moving its files' ($ui.Error -eq '' -and $afterFolderTaskList.Status -eq 'PASS' -and $afterFolderTaskList.Data.tasks.Count -eq 2 -and (Test-Path -LiteralPath (Join-Path $existingWorkFolder 'notes.md') -PathType Leaf) -and (($ui.Output -replace '\s','').Contains(($existingWorkFolder -replace '\s','')))) ($ui.Error + $ui.Output)
$ui = Invoke-Ui { Start-TuiApp -Root (Get-TestRoot) -RegistryPath $registeredPath } '04{Enter}14'
Assert-True 'evidence view shows bounded coverage and does not infer test execution' ($ui.Error -eq '' -and $ui.Output.Contains('Evidence Coverage: 100% (1/1 Verified Tasks)') -and $ui.Output.Contains('No Test Run Count Is Inferred')) ($ui.Error + $ui.Output)
$registrationRegistry = Join-Path (Get-TestWork) 'registration-message-registry.json'
$newProjectRoot = Join-Path (Get-TestWork) 'New Project Fixture'
[void](New-Item -ItemType Directory -Path $newProjectRoot -Force)
$registrationKeys = '0902' + $newProjectRoot + '{Enter}New Project{Enter}01{Enter}081201{Enter}14'
$ui = Invoke-Ui { Start-TuiApp -Root (Get-TestRoot) -RegistryPath $registrationRegistry } $registrationKeys
Assert-True 'successful project registration shows English refresh instructions and the refreshed Projects section lists it' ($ui.Error -eq '' -and $ui.Output.Contains('Project Folder Added Successfully.') -and $ui.Output.Contains('Please Select') -and $ui.Output.Contains('Refresh From The Home Page.') -and $ui.Output.Contains('New Project')) ($ui.Error + $ui.Output)
