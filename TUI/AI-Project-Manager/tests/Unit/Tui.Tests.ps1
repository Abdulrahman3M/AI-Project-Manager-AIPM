Set-TestGroup 'Differential frame rendering'
Assert-Equal 'Unchanged styled frame updates zero rows' 0 @(Get-UiChangedRows -Before @('A','B') -After @('A','B')).Count
Assert-Equal 'One changed selection role updates exactly one row' '1' (@(Get-UiChangedRows -Before @('row', 'ESC[NormalmChoice') -After @('row', 'ESC[SelectedmChoice')) -join ',')
Assert-Equal 'Moving selection updates two rows' '0,1' (@(Get-UiChangedRows -Before @('Selected','Normal') -After @('Normal','Selected')) -join ',')
Assert-Equal 'Shorter frame erases stale trailing row' '1' (@(Get-UiChangedRows -Before @('A','B') -After @('A')) -join ',')
Assert-Equal 'Larger frame draws newly added row' '1' (@(Get-UiChangedRows -Before @('A') -After @('A','B')) -join ',')

Set-TestGroup 'Product shell header and legacy roles'
$headerUi = Invoke-Ui { Write-AipmProductHeader -Version '0.2.1' -Status 'Core Ready' -Width 50 } ''
Assert-Contains 'product header shows the full product name' $headerUi.Output 'AI Project Manager'
Assert-Contains 'product header keeps the version next to the product name' $headerUi.Output 'AI Project Manager v0.2.1'
Assert-Contains 'product header is framed and reports current status' $headerUi.Output '+'
Assert-Contains 'product header reports the supplied status' $headerUi.Output 'Core Ready'
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
        Write-TuiTable -Headers @('Type','Capability','Version','Source License') -Fields @('Type','Capability','Version','License') `
            -Rows @([pscustomobject]@{Type='Imported';Capability='Audio Timing Author';Version='1.0.0';License='Universal AI ToolKit Personal Use License'}) `
            -ColumnWidths @(12,22,8,34) -Width 90
    } ''
}
Assert-True 'Capability Library table renders columns and imported source-license detail' ($null -ne $tableUi -and $tableUi.Error -eq '' -and $tableUi.Output.Contains('Capability') -and $tableUi.Output.Contains('Source License') -and $tableUi.Output.Contains('Audio Timing Author'))
Assert-Equal 'Capability Library table honors the requested terminal width' 0 $(if ($tableUi) { @($tableUi.Output -split "`n" | Where-Object { $_.Length -gt 90 }).Count } else { -1 })
$pageCatalog = [pscustomobject]@{
    status='PASS'
    catalog=[pscustomobject]@{
        integrity_status='UNVERIFIED'; skill_count=2; first_party_skills=@('tui-intelligence')
        skills=@(
            [pscustomobject]@{slug='tui-intelligence';version='0.1.0';source_license='Apache-2.0';aipm_apache_applies=$true}
            [pscustomobject]@{slug='audio-timing-author';version='1.0.0';source_license='Universal AI ToolKit Personal Use License';aipm_apache_applies=$false}
        )
        plugin_sample=[pscustomobject]@{version='0.1.0';status='PACKAGE_SAMPLE_ONLY';installation='UNVERIFIED';publication='UNVERIFIED';manifests=@('plugin.json')}
    }
}
$wideCapabilityText = ''; $mediumCapabilityText = ''; $compactCapabilityText = ''; $capabilityPageError = ''
if (Get-Command Show-AipmCapabilityLibrary -ErrorAction SilentlyContinue) {
    Initialize-Renderer -Ansi $true -Sink Capture -CaptureWidth 120 -CaptureHeight 32
    Set-ScriptedInput '{Enter}'
    try { [void](Show-AipmCapabilityLibrary -Catalog $pageCatalog -Version '0.2.1' -Status 'Core Ready') } catch { $capabilityPageError = $_.Exception.Message }
    $wideCapabilityText = [regex]::Replace((Get-CapturedOutput), '\x1B\[[0-?]*[ -/]*[@-~]', '')
    Clear-ScriptedInput
    Initialize-Renderer -Ansi $true -Sink Capture -CaptureWidth 100 -CaptureHeight 32
    Set-ScriptedInput '{Enter}'
    try { [void](Show-AipmCapabilityLibrary -Catalog $pageCatalog -Version '0.2.1' -Status 'Core Ready') } catch { $capabilityPageError = $_.Exception.Message }
    $mediumCapabilityText = [regex]::Replace((Get-CapturedOutput), '\x1B\[[0-?]*[ -/]*[@-~]', '')
    Clear-ScriptedInput
    Initialize-Renderer -Ansi $true -Sink Capture -CaptureWidth 76 -CaptureHeight 32
    Set-ScriptedInput '{Enter}'
    try { [void](Show-AipmCapabilityLibrary -Catalog $pageCatalog -Version '0.2.1' -Status 'Core Ready') } catch { $capabilityPageError = $_.Exception.Message }
    $compactCapabilityText = [regex]::Replace((Get-CapturedOutput), '\x1B\[[0-?]*[ -/]*[@-~]', '')
    Clear-ScriptedInput
    Initialize-Renderer -Ansi $false -Sink Buffer
}
Assert-True 'wide Capability Library uses framed tables and keeps Plugin installation unverified' ($capabilityPageError -eq '' -and $wideCapabilityText.Contains('Source License') -and $wideCapabilityText.Contains('Plugin Package') -and $wideCapabilityText.Contains('Unverified')) $capabilityPageError
Assert-True 'medium Capability Library avoids tables wider than the terminal' ($capabilityPageError -eq '' -and $mediumCapabilityText.Contains('AIPM General Skills Plugin') -and $mediumCapabilityText.Contains('Installation: Unverified')) $capabilityPageError
Assert-True 'narrow Capability Library switches to compact rows without losing license text' ($capabilityPageError -eq '' -and $compactCapabilityText.Contains('TUI Intelligence') -and $compactCapabilityText.Contains('Universal AI ToolKit Personal Use License')) $capabilityPageError
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
Initialize-Renderer -Ansi $false -Sink Capture -CaptureWidth 20 -CaptureHeight 10
Set-ScriptedInput '{Enter}'
$narrowChoice = Show-Menu -Title 'Narrow' -Items $narrowItems -Navigation Arrows
$narrowOutput = Get-CapturedOutput
Clear-ScriptedInput
Assert-Equal 'narrow terminal still selects the visible item' 'narrow' $narrowChoice
Assert-Contains 'narrow terminal keeps Esc Back visible' $narrowOutput 'Esc Back'
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

Set-TestGroup 'Whole application (scripted)'
$registry = Join-Path (Get-TestWork) 'registry.json'
$ui = Invoke-Ui { Start-TuiApp -Root (Get-TestRoot) -RegistryPath $registry } '12{Enter}13'
Assert-True 'the Core-backed dashboard, About page and safe Exit run without errors' ($ui.Error -eq '' -and $ui.Output.Contains('Task Dashboard') -and $ui.Output.Contains('About')) $ui.Error
$malformedRegistry = Join-Path (Get-TestWork) 'malformed-app-registry.json'
[System.IO.File]::WriteAllText($malformedRegistry, '{"schema_version":"invalid"}', (New-Object System.Text.UTF8Encoding($false)))
$ui = Invoke-Ui { Start-TuiApp -Root (Get-TestRoot) -RegistryPath $malformedRegistry } '13'
Assert-True 'a blocked Core registry stays visibly Unverified without crashing the dashboard' ($ui.Error -eq '' -and $ui.Output.Contains('Core Blocked') -and $ui.Output.Contains('UNVERIFIED')) $ui.Error
$ui = Invoke-Ui { Start-TuiApp -Root (Get-TestRoot) -RegistryPath $registry } '07{Enter}13'
Assert-True 'Skills and Plugins page reports source licenses and unverified package status in Title Case' ($ui.Error -eq '' -and $ui.Output.Contains('Skills & Plugins') -and $ui.Output.Contains('Universal AI ToolKit Personal Use License') -and $ui.Output.Contains('Unverified')) $ui.Error
$ui = Invoke-Ui { Start-TuiApp -Root (Get-TestRoot) -RegistryPath $registry } '?{Enter}13'
Assert-True 'question mark opens keyboard and evidence Help' ($ui.Error -eq '' -and $ui.Output.Contains('Up/Down: Move Selection')) $ui.Error
$ui = Invoke-Ui { Start-TuiApp -Root (Get-TestRoot) -RegistryPath $registry } '/help{Enter}{Enter}13'
Assert-True 'slash search opens matching Help action' ($ui.Error -eq '' -and $ui.Output.Contains('Search: help')) $ui.Error
$ui = Invoke-Ui { Start-TuiApp -Root (Get-TestRoot) -RegistryPath $registry } 'q0213'
Assert-True 'Q requires explicit confirmation before leaving the dashboard' ($ui.Error -eq '' -and $ui.Output.Contains('Exit AI Project Manager?')) $ui.Error
$ui = Invoke-Ui { Start-TuiApp -Root (Get-TestRoot) -RegistryPath $registry } '090102Exit{Enter}'
Assert-True 'Command Palette mode persists as a UI preference' ($ui.Error -eq '' -and $ui.Output.Contains('Command Palette') -and (Get-AipmViewMode) -eq 'Command Palette') $ui.Error
[void](Set-UserSetting -Name 'view_mode' -Value 'Assistant Console')
$ui = Invoke-Ui { Start-TuiApp -Root (Get-TestRoot) -RegistryPath $registry } '08{Enter}13'
Assert-True 'Assistant Console states that no live AI session is connected' ($ui.Error -eq '' -and $ui.Output.Contains('Assistant Console') -and $ui.Output.Contains('No AI Session Is Connected')) $ui.Error
[void](Set-UserSetting -Name 'view_mode' -Value 'Task Dashboard')

Set-TestGroup 'Core State Integration'
$fixtureRoot = Join-Path (Get-TestWork) 'Registered Project Fixture'
$stateRoot = Join-Path $fixtureRoot 'Shared-Project-State-Manager'
[void](New-Item -ItemType Directory -Path (Join-Path $stateRoot 'History/Events') -Force)
$task = @{ title='Verify AIPM TUI'; scope='Read-Only Core Integration'; plan='Read the verified Core state.'; report='TUI state integration passed.'; blockers=@(); verification=@{ result='PASS'; evidence='Core fixture was read successfully.' } }
$state = @{ schema_version='1.1'; revision=0; project_id='P08-Fixture'; task_id='Task-P08'; task_status='COMPLETE'; active_phase='P08'; state_health='CONSISTENT'; last_verified_action='P08 test fixture'; next_action='Continue read-only review.'; branch='main'; head_sha=('a' * 40); updated_at='2026-10-16T10:00:00Z'; updated_by='TUI Test'; tasks=@{ 'Task-P08'=$task }; diff_fingerprint=$null }
$statePath = Join-Path $stateRoot 'State-Manifest.json'
[System.IO.File]::WriteAllText($statePath, ($state | ConvertTo-Json -Depth 20), (New-Object System.Text.UTF8Encoding($false)))
$registeredPath = Join-Path (Get-TestWork) 'registered fixture registry.json'
$registered = @{ schema_version='1.0'; projects=@(@{ project_id='P08-Fixture'; root_path=$fixtureRoot; alias='Registered Fixture' }); preferences=@{} }
[System.IO.File]::WriteAllText($registeredPath, ($registered | ConvertTo-Json -Depth 10), (New-Object System.Text.UTF8Encoding($false)))
$ui = Invoke-Ui { Start-TuiApp -Root (Get-TestRoot) -RegistryPath $registeredPath } '01{Enter}14'
Assert-True 'project detail is derived from the registered Core state' ($ui.Error -eq '' -and $ui.Output.Contains('Registered Fixture') -and $ui.Output.Contains('Phase: P08')) $ui.Error
$ui = Invoke-Ui { Start-TuiApp -Root (Get-TestRoot) -RegistryPath $registeredPath } '03{Enter}14'
Assert-True 'task view lists verified tasks from Core without local state copies' ($ui.Error -eq '' -and $ui.Output.Contains('Verify AIPM TUI') -and $ui.Output.Contains('Passed')) $ui.Error
$ui = Invoke-Ui { Start-TuiApp -Root (Get-TestRoot) -RegistryPath $registeredPath } '05{Enter}14'
Assert-True 'evidence view shows bounded coverage and does not infer test execution' ($ui.Error -eq '' -and $ui.Output.Contains('Evidence Coverage: 100% (1/1 Verified Tasks)') -and $ui.Output.Contains('No Test Run Count Is Inferred')) $ui.Error
