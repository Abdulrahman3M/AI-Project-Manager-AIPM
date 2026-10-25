# App.psm1 - the application: main menu loop and the actions. Business logic lives in Core modules, never in the TUI modules.
Set-StrictMode -Version 2.0
$script:SessionCoreReader = $null
$script:SessionDependencyReader = $null

function Get-AipmField {
    param($Object, [string]$Name, $Default = $null)
    if ($null -eq $Object) { return $Default }
    $property = $Object.PSObject.Properties[$Name]
    if ($property) { return $property.Value }
    return $Default
}

function Invoke-AipmSessionCore {
    param([string]$AppRoot, [string]$Command, [string]$RegistryPath = '')
    try {
        $result = if ($script:SessionCoreReader) {
            & $script:SessionCoreReader $AppRoot $Command $RegistryPath
        } else {
            Invoke-AipmCore -AppRoot $AppRoot -Command $Command -RegistryPath $RegistryPath -ErrorAction Stop
        }
        if ($null -eq $result -or -not $result.PSObject.Properties['Status']) {
            return [pscustomobject]@{ Status='BLOCKED'; Reason='CORE_RESPONSE_INVALID'; Data=$null }
        }
        return $result
    } catch {
        return [pscustomobject]@{ Status='BLOCKED'; Reason='CORE_REQUEST_FAILED'; Data=$null }
    }
}

function Get-AipmSessionDependency {
    param([string]$AppRoot)
    try {
        $result = if ($script:SessionDependencyReader) {
            & $script:SessionDependencyReader $AppRoot
        } else {
            Get-AipmDependencyStatus -AppRoot $AppRoot -ErrorAction Stop
        }
        if ($null -eq $result -or -not $result.PSObject.Properties['Status']) {
            return [pscustomobject]@{ Status='BLOCKED'; Reason='DEPENDENCY_STATUS_INVALID'; Version='' }
        }
        return $result
    } catch {
        return [pscustomobject]@{ Status='BLOCKED'; Reason='DEPENDENCY_CHECK_FAILED'; Version='' }
    }
}

function New-AipmBlockedSessionSnapshot {
    param($Dependency, $Dashboard, $Catalog, $Hosts, [string[]]$CoreCommands, [string]$Reason)
    return [pscustomobject]@{
        Status = 'BLOCKED'
        Reason = $(if ($Reason) { $Reason } else { 'CORE_REQUEST_BLOCKED' })
        Dependency = $Dependency
        Dashboard = $Dashboard
        Catalog = $Catalog
        Hosts = $Hosts
        CoreCommands = [string[]]$CoreCommands
        CapturedAt = [DateTime]::UtcNow.ToString('o')
    }
}

function Get-AipmSessionSnapshot {
    [CmdletBinding()]
    param([Parameter(Mandatory)][string]$Root, [string]$RegistryPath = '')
    $commands = New-Object System.Collections.Generic.List[string]
    $dependency = Get-AipmSessionDependency -AppRoot $Root
    if ($dependency.Status -ne 'PASS') {
        return (New-AipmBlockedSessionSnapshot -Dependency $dependency -CoreCommands @() -Reason ([string]$dependency.Reason))
    }
    $dashboard = Invoke-AipmSessionCore -AppRoot $Root -Command 'dashboard' -RegistryPath $RegistryPath
    $commands.Add('dashboard')
    if ($dashboard.Status -ne 'PASS') {
        return (New-AipmBlockedSessionSnapshot -Dependency $dependency -Dashboard $dashboard -CoreCommands $commands.ToArray() -Reason ([string]$dashboard.Reason))
    }
    $catalog = Invoke-AipmSessionCore -AppRoot $Root -Command 'catalog'
    $commands.Add('catalog')
    if ($catalog.Status -ne 'PASS') {
        return (New-AipmBlockedSessionSnapshot -Dependency $dependency -Dashboard $dashboard -Catalog $catalog -CoreCommands $commands.ToArray() -Reason ([string]$catalog.Reason))
    }
    $hosts = Invoke-AipmSessionCore -AppRoot $Root -Command 'host-capabilities'
    $commands.Add('host-capabilities')
    if ($hosts.Status -ne 'PASS') {
        return (New-AipmBlockedSessionSnapshot -Dependency $dependency -Dashboard $dashboard -Catalog $catalog -Hosts $hosts -CoreCommands $commands.ToArray() -Reason ([string]$hosts.Reason))
    }
    return [pscustomobject]@{
        Status = 'PASS'
        Reason = ''
        Dependency = $dependency
        Dashboard = $dashboard
        Catalog = $catalog
        Hosts = $hosts
        CoreCommands = $commands.ToArray()
        CapturedAt = [DateTime]::UtcNow.ToString('o')
    }
}

function Refresh-AipmSessionSnapshot {
    [CmdletBinding()]
    param([Parameter(Mandatory)][string]$Root, [string]$RegistryPath = '', $CurrentSnapshot)
    $candidate = Get-AipmSessionSnapshot -Root $Root -RegistryPath $RegistryPath
    if ($candidate.Status -eq 'PASS') {
        return [pscustomobject]@{ Status='PASS'; Snapshot=$candidate; Preserved=$false; Reason=''; FailedCandidate=$null }
    }
    $preserved = ($null -ne $CurrentSnapshot -and $CurrentSnapshot.Status -eq 'PASS')
    return [pscustomobject]@{
        Status = 'BLOCKED'
        Snapshot = $(if ($preserved) { $CurrentSnapshot } else { $candidate })
        Preserved = $preserved
        Reason = $candidate.Reason
        FailedCandidate = $candidate
    }
}

function ConvertTo-AipmDisplayStatus {
    param([string]$Status)
    switch ($Status) {
        'COMPLETE' { return 'Complete' }
        'IN-PROGRESS' { return 'In Progress' }
        'BLOCKED' { return 'Blocked' }
        'NOT-STARTED' { return 'Not Started' }
        'PASS' { return 'Passed' }
        'FAIL' { return 'Failed' }
        default { return 'Unverified' }
    }
}

function Format-AipmEvidenceCoverage {
    param([int]$Verified, [int]$Total)
    if ($Total -le 0) { return 'Evidence Coverage: Unknown (No Verifiable Tasks)' }
    $verifiedCount = [Math]::Min($Total, [Math]::Max(0, $Verified))
    $percent = [int][Math]::Floor(($verifiedCount * 100.0) / $Total)
    $filled = [int][Math]::Round($percent / 10.0, 0, [MidpointRounding]::AwayFromZero)
    return ('[{0}{1}] Evidence Coverage: {2}% ({3}/{4} Verified Tasks)' -f ('#' * $filled),('-' * (10 - $filled)),$percent,$verifiedCount,$Total)
}

function Get-AipmProjectSummary {
    [CmdletBinding()]
    param([Parameter(Mandatory)]$Project)
    $summary = @{
        Name = [string](Get-AipmField $Project 'alias' 'Unknown')
        ProjectId = [string](Get-AipmField $Project 'project_id' '')
        Status = 'Unverified'
        Phase = 'Unknown'
        TaskId = 'Unknown'
        TaskStatus = 'Unverified'
        TaskCount = 0
        VerifiedTaskCount = 0
        PassedEvidence = 0
        FailedEvidence = 0
        BlockedTaskCount = 0
        UnverifiedEvidence = 0
        TestsStatus = 'Unverified'
        AgentStatus = 'Unknown'
        Progress = 'Unknown'
        UpdatedAt = 'Unknown'
        UpdatedBy = 'Unknown'
        NextAction = 'Unknown'
        Branch = 'Unknown'
        Head = 'Unknown'
        Reason = [string](Get-AipmField $Project 'reason' '')
    }
    $state = Get-AipmField $Project 'state'
    if ((Get-AipmField $Project 'state_status') -ne 'PASS' -or $null -eq $state) {
        return [pscustomobject]$summary
    }

    $summary.Status = 'Ready'
    foreach ($pair in @(
        @{ Key = 'active_phase'; Target = 'Phase' },
        @{ Key = 'task_id'; Target = 'TaskId' },
        @{ Key = 'updated_at'; Target = 'UpdatedAt' },
        @{ Key = 'updated_by'; Target = 'UpdatedBy' },
        @{ Key = 'next_action'; Target = 'NextAction' },
        @{ Key = 'branch'; Target = 'Branch' },
        @{ Key = 'head_sha'; Target = 'Head' }
    )) {
        $value = Get-AipmField $state $pair.Key
        if ($null -ne $value -and [string]$value) { $summary[$pair.Target] = [string]$value }
    }
    $summary.TaskStatus = ConvertTo-AipmDisplayStatus ([string](Get-AipmField $state 'task_status' 'UNVERIFIED'))

    $tasks = Get-AipmField $state 'tasks'
    $taskItems = @()
    if ($tasks -is [System.Collections.IDictionary]) {
        $taskItems = @($tasks.Values)
    } elseif ($null -ne $tasks) {
        $taskItems = @($tasks.PSObject.Properties | ForEach-Object { $_.Value })
    }
    $summary.TaskCount = $taskItems.Count
    foreach ($task in $taskItems) {
        $verification = Get-AipmField $task 'verification'
        $result = [string](Get-AipmField $verification 'result' '')
        $evidence = [string](Get-AipmField $verification 'evidence' '')
        $report = [string](Get-AipmField $task 'report' '')
        $blockers = @(Get-AipmField $task 'blockers' @())
        if ($blockers.Count -gt 0) { $summary.BlockedTaskCount++ }
        if ($result -eq 'PASS' -and $evidence.Trim() -and $report.Trim()) {
            $summary.VerifiedTaskCount++; $summary.PassedEvidence++
        } elseif ($result -eq 'FAIL') {
            $summary.FailedEvidence++
        } else {
            $summary.UnverifiedEvidence++
        }
    }
    return [pscustomobject]$summary
}

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
    if ($d.descriptions -notin @('Muted','Shade','Inline','Panel')) { $d.descriptions = 'Muted' }
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
    foreach ($p in $catalog) { $items += (New-MenuItem -Label $p.Name -Desc ($p.Layout + ' Layout, ' + $p.Density + ' Spacing.') -Value $p.Id -Icon 'Form') }
    $preset = Show-Menu -Title 'Choose A Layout' -Description '20 Product-Neutral Styles, Including Classic Numbered.' -Items $items -Navigation Search -Preset 'command-palette'
    if (-not $preset -or $preset -in @('__HELP__','__QUIT__')) { return }
    $choices = @(
        (New-MenuItem -Label 'Arrow Keys + Enter' -Desc 'No Numeric Prefixes.' -Value 'Arrows'),
        (New-MenuItem -Label 'Numbered Choices' -Desc 'Type A Menu Item Number.' -Value 'Numbers'),
        (New-MenuItem -Label 'Numbers And Arrows' -Desc 'Both Keyboard Selection Modes.' -Value 'Hybrid'),
        (New-MenuItem -Label 'Search Actions' -Desc 'Type Words And Use Arrows Or Enter.' -Value 'Search')
    )
    $navigation = Show-Menu -Title 'Navigation Style' -Items $choices -Navigation Arrows
    if (-not $navigation -or $navigation -in @('__HELP__','__QUIT__')) { return }
    $choices = @(
        (New-MenuItem -Label 'Automatic Icon Detection' -Desc 'Choose The Safest Icons For The Terminal.' -Value 'Auto'),
        (New-MenuItem -Label 'Emoji' -Desc 'Colorful Icons In Modern Terminals.' -Value 'Emoji'),
        (New-MenuItem -Label 'Simple Symbols' -Desc 'Lightweight Unicode Symbols.' -Value 'Symbol'),
        (New-MenuItem -Label 'ASCII' -Desc 'Portable text icons.' -Value 'Ascii'),
        (New-MenuItem -Label 'No Icons' -Desc 'Clean Text-Only Choices.' -Value 'None')
    )
    $icons = Show-Menu -Title 'Icon Style' -Items $choices -Navigation Arrows
    if (-not $icons -or $icons -in @('__HELP__','__QUIT__')) { return }
    $choices = @(
        (New-MenuItem -Label 'Automatic' -Desc 'Adapt To Terminal Support.' -Value 'Auto'),
        (New-MenuItem -Label 'Rich Accents' -Desc 'Strong Accent Headings And Selections.' -Value 'Full'),
        (New-MenuItem -Label 'Subtle Accents' -Desc 'Restrained Color Hierarchy.' -Value 'Subtle'),
        (New-MenuItem -Label 'No Colors' -Desc 'Monochrome Interface.' -Value 'None')
    )
    $colors = Show-Menu -Title 'Color Style' -Items $choices -Navigation Arrows
    if (-not $colors -or $colors -in @('__HELP__','__QUIT__')) { return }
    $choices = @(
        (New-MenuItem -Label 'Muted And Indented' -Desc 'Subdued Explanation Under Each Option.' -Value 'Muted'),
        (New-MenuItem -Label 'Subtle Shading' -Desc 'Indented Explanation With Faint Shading When Supported.' -Value 'Shade'),
        (New-MenuItem -Label 'Inline' -Desc 'Description On The Same Line.' -Value 'Inline'),
        (New-MenuItem -Label 'Details Panel' -Desc 'Explain The Currently Highlighted Option.' -Value 'Panel')
    )
    $descriptions = Show-Menu -Title 'Option Descriptions' -Items $choices -Navigation Arrows
    if (-not $descriptions -or $descriptions -in @('__HELP__','__QUIT__')) { return }
    $summary = 'Preset: ' + $preset + '; Navigation: ' + $navigation + '; Icons: ' + $icons + '; Colors: ' + $colors + '; Descriptions: ' + $descriptions
    if (-not (Show-Confirm -Title 'Save This Design?' -Message $summary)) { return }
    foreach ($key in @('preset','navigation','icons','colors','descriptions')) {
        $value = switch ($key) {
            'preset' { $preset } 'navigation' { $navigation } 'icons' { $icons }
            'colors' { $colors } 'descriptions' { $descriptions }
        }
        if (-not (Set-UserSetting -Name ('design_' + $key) -Value $value)) {
            Show-Notice -Title 'Settings Not Saved' -Lines @('The Configuration Could Not Be Written.') -Kind Error
            return
        }
    }
    Apply-AppDesign -Root $Root
    Show-Notice -Title 'Design Updated' -Lines @('The New Appearance Is Active. ' + $summary) -Kind Success
}

function Get-AppVersion {
    param([string]$Root)
    $f = Join-Path $Root 'VERSION'
    if (Test-Path -LiteralPath $f) { return ((Get-Content -LiteralPath $f -TotalCount 1)).Trim() }
    return '0.0.0'
}

function Get-AipmViewMode {
    $mode = Get-UserSetting -Name 'view_mode' -Default 'Task Dashboard'
    if ($mode -notin @('Task Dashboard','Command Palette','Assistant Console')) { return 'Task Dashboard' }
    return $mode
}

function Test-PersonName {
    # Returns $null when valid, else the message. Pure function: unit tested without any UI.
    param([string]$Text)
    if ([string]::IsNullOrWhiteSpace($Text)) { return 'Please type a name.' }
    if ($Text.Length -gt 40) { return 'The name can have at most 40 characters.' }
    return $null
}

function Get-AipmStateTasks {
    param($State)
    $tasks = Get-AipmField $State 'tasks'
    if ($tasks -is [System.Collections.IDictionary]) { return @($tasks.GetEnumerator() | ForEach-Object { [pscustomobject]@{ Id=$_.Key; Data=$_.Value } }) }
    if ($null -ne $tasks) { return @($tasks.PSObject.Properties | ForEach-Object { [pscustomobject]@{ Id=$_.Name; Data=$_.Value } }) }
    return @()
}

function ConvertTo-AipmCapabilityName {
    param([string]$Slug)
    $knownNames = @{ 'tui-intelligence' = 'TUI Intelligence'; 'project-orchestrator' = 'Project Orchestrator' }
    if ($knownNames.ContainsKey($Slug)) { return $knownNames[$Slug] }
    $name = [System.Globalization.CultureInfo]::CurrentCulture.TextInfo.ToTitleCase(($Slug -replace '-', ' ').ToLowerInvariant())
    foreach ($acronym in @('AI','API','CLI','CUA','MCP','TUI','UI')) {
        $name = [regex]::Replace($name, ('(?i)\b' + $acronym + '\b'), $acronym)
    }
    return $name
}

function Get-AipmCapabilityLibraryRows {
    param($Catalog, [int]$Width = 100)
    $catalogData = Get-AipmField $Catalog 'catalog'
    $skillRows = New-Object System.Collections.Generic.List[object]
    $pluginRows = New-Object System.Collections.Generic.List[object]
    $summaryRows = New-Object System.Collections.Generic.List[object]
    $catalogStatus = 'Unverified'
    $catalogUsable = ([string](Get-AipmField $Catalog 'status' '')) -eq 'PASS' -and $null -ne $catalogData
    if ($catalogUsable) {
        $skills = @(Get-AipmField $catalogData 'skills' @())
        foreach ($skill in $skills) {
            $slug = [string](Get-AipmField $skill 'slug' '')
            if (-not $slug) { continue }
            $row = [pscustomobject]@{
                Type = 'AIPM-Owned'
                Capability = ConvertTo-AipmCapabilityName $slug
                Slug = $slug
                Version = [string](Get-AipmField $skill 'version' 'Unverified')
            }
            $skillRows.Add($row)
        }
        $skillRows = [System.Collections.Generic.List[object]]::new([object[]]@($skillRows | Sort-Object Slug))
        $integrity = ConvertTo-AipmDisplayStatus ([string](Get-AipmField $catalogData 'integrity_status' 'UNVERIFIED'))
        $declaredCount = Get-AipmField $catalogData 'skill_count'
        if ($null -ne $declaredCount -and [int]$declaredCount -eq $skillRows.Count) { $catalogStatus = $integrity }
        $summaryRows.Add([pscustomobject]@{ Metric='Catalog Integrity'; Value=$catalogStatus })
        $summaryRows.Add([pscustomobject]@{ Metric='Registered Skills'; Value=$(if ($null -ne $declaredCount) { [string]$declaredCount } else { 'Unverified' }) })
        $summaryRows.Add([pscustomobject]@{ Metric='AIPM-Owned Skills'; Value=[string]$skillRows.Count })
        $plugin = Get-AipmField $catalogData 'plugin_sample'
        if ($plugin) {
            $pluginStatus = [string](Get-AipmField $plugin 'status' 'UNVERIFIED')
            if ($pluginStatus -eq 'PACKAGE_SAMPLE_ONLY') { $pluginStatus = 'Package Sample Only' }
            $pluginRows.Add([pscustomobject]@{
                Package = 'AIPM Project Agent Bridge'
                Version = [string](Get-AipmField $plugin 'version' 'Unverified')
                Status = $pluginStatus
                Installation = ConvertTo-AipmDisplayStatus ([string](Get-AipmField $plugin 'installation' 'UNVERIFIED'))
                Publication = ConvertTo-AipmDisplayStatus ([string](Get-AipmField $plugin 'publication' 'UNVERIFIED'))
            })
        }
    }
    if ($summaryRows.Count -eq 0) {
        $summaryRows.Add([pscustomobject]@{ Metric='Catalog Integrity'; Value='Unverified' })
        $summaryRows.Add([pscustomobject]@{ Metric='Registered Skills'; Value='Unverified' })
    }
    if ($pluginRows.Count -eq 0) {
        $pluginRows.Add([pscustomobject]@{ Package='AIPM Project Agent Bridge'; Version='Unverified'; Status='Unverified'; Installation='Unverified'; Publication='Unverified' })
    }
    return [pscustomobject]@{
        CatalogStatus = $catalogStatus
        IsCompact = ($Width -lt 112)
        Summary = $summaryRows.ToArray()
        Skills = $skillRows.ToArray()
        Plugins = $pluginRows.ToArray()
    }
}

function Show-AipmCapabilityLibrary {
    param($Catalog, [string]$Version = '', [string]$Status = '')
    while ($true) {
        $size = Get-TerminalSize
        $projection = Get-AipmCapabilityLibraryRows -Catalog $Catalog -Width $size.Width
        Clear-Ui
        Write-AipmProductHeader -Version $Version -Status $Status -Width $size.Width
        Write-UiLine '  Skills & Plugins' 'Heading'
        Write-UiLine '  Capability Library  |  Read-Only Catalog View' 'Dim'
        if ($size.Width -ge 76) {
            Write-TuiTable -Headers @('Metric','Value') -Fields @('Metric','Value') -Rows $projection.Summary -ColumnWidths @(26,40) -Width $size.Width
        } else {
            foreach ($row in $projection.Summary) { Write-MenuWrapped -Text ($row.Metric + ': ' + $row.Value) -Width $size.Width -Role 'Normal' -Indent '  ' }
        }
        foreach ($group in @(
            @{ Title='AIPM-Owned Skills'; Rows=@($projection.Skills) }
        )) {
            Write-TuiRule -Width $size.Width -OpenRight
            Write-UiLine ('  ' + $group.Title) 'Heading'
            if ($group.Rows.Count -eq 0) {
                Write-UiLine '  Unverified - No Capability Rows Are Available.' 'Dim'
            } elseif ($size.Width -ge 88) {
                Write-TuiTable -Headers @('Type','Capability','Version') -Fields @('Type','Capability','Version') `
                    -Rows $group.Rows -ColumnWidths @(14,52,10) -Width $size.Width
            } else {
                foreach ($row in $group.Rows) {
                    Write-UiLine ('  ' + $row.Type + '  |  ' + $row.Capability + '  v' + $row.Version) 'Normal'
                }
            }
        }
        Write-MenuWrapped -Text 'All Listed Skills Are Covered By The Apache License 2.0.' -Width $size.Width -Role 'Dim' -Indent '  '
        Write-TuiRule -Width $size.Width -OpenRight
        Write-UiLine '  Plugin Packages' 'Heading'
        if ($size.Width -ge 106) {
            Write-TuiTable -Headers @('Package','Version','Status','Installation','Publication') `
                -Fields @('Package','Version','Status','Installation','Publication') -Rows $projection.Plugins `
                -ColumnWidths @(30,10,22,14,14) -Width $size.Width
        } else {
            foreach ($plugin in $projection.Plugins) {
                Write-UiLine ('  ' + $plugin.Package + '  v' + $plugin.Version) 'Normal'
                Write-MenuWrapped -Text ('Status: ' + $plugin.Status + ' | Installation: ' + $plugin.Installation + ' | Publication: ' + $plugin.Publication) -Width $size.Width -Role 'Dim' -Indent '      '
            }
        }
        Write-UiLine ''
        Write-Ui 'Enter / Esc ' 'Key'; Write-UiLine 'Back  |  ? / F1 Help  |  Q Request Exit' 'Dim'
        Complete-UiFrame
        $key = Read-AppKey
        if ($key.Name -in @('Enter','Esc')) { return $null }
        if ($key.Name -eq 'Help' -or ($key.Name -eq 'Char' -and $key.Char -eq '?')) { return '__HELP__' }
        if ($key.Name -eq 'Char' -and $key.Char -match '^[qQ]$') { return '__QUIT__' }
    }
}

function Get-AipmPageLines {
    param([string]$Section, $Dashboard, $Catalog, $HostMatrix, [string]$Version)
    $lines = New-Object System.Collections.Generic.List[string]
    $projects = @(Get-AipmField $Dashboard 'projects' @())
    $summaries = @($projects | ForEach-Object { Get-AipmProjectSummary -Project $_ })
    switch ($Section) {
        'Dashboard' {
            $lines.Add(('Core: ' + $(if ($Dashboard.status -eq 'PASS') { 'Ready' } else { 'Blocked' })))
            $lines.Add(('Registry: ' + (ConvertTo-AipmDisplayStatus ([string]$Dashboard.registry_status))))
            $lines.Add(('Registered Projects: ' + $summaries.Count))
            foreach ($s in $summaries) { $lines.Add(('{0} | {1} | Phase {2} | Task {3} | Progress {4}' -f $s.Name,$s.Status,$s.Phase,$s.TaskId,$s.Progress)) }
            if ($summaries.Count -eq 0) { $lines.Add('No Registered Projects Were Returned By Core.') }
        }
        'Projects' {
            if ($summaries.Count -eq 0) { $lines.Add('No Registered Projects Were Returned By Core.') }
            foreach ($s in $summaries) {
                $lines.Add(($s.Name + ' | ' + $s.Status + ' | Project Id: ' + $s.ProjectId))
                $lines.Add(('Phase: ' + $s.Phase + ' | Task: ' + $s.TaskId + ' | Status: ' + $s.TaskStatus + ' | Progress: ' + $s.Progress))
                $lines.Add(('Branch: ' + $s.Branch + ' | HEAD: ' + $s.Head))
                $lines.Add(('Updated: ' + $s.UpdatedAt + ' | By: ' + $s.UpdatedBy))
                $lines.Add(('Next Action: ' + $s.NextAction))
                if ($s.Reason) { $lines.Add(('State Note: ' + $s.Reason)) }
            }
        }
        'Tasks' {
            foreach ($project in $projects) {
                $s = Get-AipmProjectSummary -Project $project
                $lines.Add($s.Name + ' | ' + $s.TaskStatus + ' | Active Task: ' + $s.TaskId)
                foreach ($entry in @(Get-AipmStateTasks $project.state)) {
                    $task = $entry.Data; $verification = Get-AipmField $task 'verification'
                    $status = ConvertTo-AipmDisplayStatus ([string](Get-AipmField $verification 'result' 'UNVERIFIED'))
                    $lines.Add(('  ' + $entry.Id + ' | ' + [string](Get-AipmField $task 'title' 'Untitled Task') + ' | ' + $status))
                }
            }
            if ($summaries.Count -eq 0) { $lines.Add('Task Data Is Unavailable Until A Project Is Registered.') }
        }
        'Phases' {
            foreach ($s in $summaries) { $lines.Add($s.Name + ' | Active Phase: ' + $s.Phase) }
            $lines.Add('Phase History And Completion Weights: Unverified In Current Core State.')
        }
        'Tests & Evidence' {
            foreach ($s in $summaries) {
                $lines.Add($s.Name + ' | Evidence Status: ' + $s.TestsStatus)
                $lines.Add((Format-AipmEvidenceCoverage -Verified $s.VerifiedTaskCount -Total $s.TaskCount))
                $lines.Add(('Verified Tasks: {0} | Passed Evidence: {1} | Failed Evidence: {2} | Unverified Evidence: {3}' -f $s.VerifiedTaskCount,$s.PassedEvidence,$s.FailedEvidence,$s.UnverifiedEvidence))
            }
            $lines.Add('No Test Run Count Is Inferred From Task Evidence.')
            if ($summaries.Count -eq 0) { $lines.Add('No Project Evidence Is Available.') }
        }
        'Agents & Handoffs' {
            foreach ($s in $summaries) { $lines.Add($s.Name + ' | Live Session: ' + $s.AgentStatus) }
            $lines.Add('Live Process Identity And Handoff Evidence Are Not Supplied By Current Core State.')
            $matrix = Get-AipmField $HostMatrix 'matrix'
            if ($matrix) { $lines.Add(('Host Matrix: ' + [string](Get-AipmField $matrix 'policy' 'Unverified'))) }
        }
        'Timeline' {
            foreach ($s in $summaries) { $lines.Add(($s.Name + ' | Updated: ' + $s.UpdatedAt + ' | By: ' + $s.UpdatedBy)) }
            $lines.Add('Event-Level History Is Not Supplied By The Read-Only Dashboard Command.')
            if ($summaries.Count -eq 0) { $lines.Add('No Project Timeline Is Available.') }
        }
        'Skills & Plugins' {
            $c = Get-AipmField $Catalog 'catalog'
            if ($c) {
                $lines.Add(('Capability Integrity: ' + [string]$c.integrity_status))
                $lines.Add(('AIPM-Owned Skills: ' + [string]$c.skill_count))
                $lines.Add('All Listed Skills Are Covered By The Apache License 2.0.')
                foreach ($skill in @($c.skills)) { $lines.Add(('  ' + [string]$skill.slug + ' ' + [string]$skill.version + ' | ' + [string]$skill.source_license)) }
                if ($c.plugin_sample) { $lines.Add(('Plugin Package: ' + [string]$c.plugin_sample.status + ' | Install: ' + [string]$c.plugin_sample.installation + ' | Publish: ' + [string]$c.plugin_sample.publication)) }
            } else { $lines.Add('Capability Catalog Is Unverified.') }
        }
        'Assistant Console' {
            $lines.Add('No AI Session Is Connected Or Running.')
            $lines.Add('This Console Shows Only Evidence Returned By AIPM Core And Host Capability Metadata.')
            $lines.Add('Use Agents & Handoffs To Review Explicitly Available Session Evidence.')
        }
        'Settings' {
            $d = Get-AppDesign -Root $script:AppRoot
            $lines.Add(('View Mode: ' + (Get-AipmViewMode)))
            $theme = Get-ThemeRoles
            $lines.Add(('Theme: ' + $(if ($theme) { [string]$theme.theme_name } else { 'Semantic Fallback' })))
            $lines.Add(('Version: ' + $Version))
            $lines.Add(('Layout: ' + $d.preset + ' | Navigation: ' + $d.navigation))
            $lines.Add(('Icons: ' + $d.icons + ' | Colors: ' + $d.colors + ' | Descriptions: ' + $d.descriptions))
            $lines.Add(('Settings Scope: UI Preferences Only | Path: ' + (Get-SettingsPath)))
            $lines.Add('Project Tasks And Core State Are Not Stored In TUI Settings.')
        }
        'Help' {
            $lines.Add('Up/Down: Move Selection | Enter: Open Or Select | Esc: Back (At The Dashboard Esc Requests Exit Confirmation)')
            $lines.Add('Type A Number: Select Directly | /: Search Actions | ?: Help | F1: Help | Q: Request Exit')
            $lines.Add('Portfolio, Phase, Evidence, Skill And Plugin Views Are Read-Only; Task Actions Update AIPM-Owned State Only.')
            $lines.Add('Task Actions Never Edit Project Source Files Or Run Project Tests.')
            $lines.Add('Registry Management Can Connect Existing Registries, Register Projects, And Back Up Or Restore Registry Pointers.')
            $lines.Add('AIPM Core Blocks Managed Project Roots And Registry Files Inside The AIPM Installation.')
            $lines.Add('Unverified Means The Required Source Evidence Is Missing Or Could Not Be Checked.')
        }
        'About' {
            $runtime = Get-RuntimeInfo
            $lines.Add(('Version: ' + $Version))
            $lines.Add(('Platform: ' + $runtime.Platform + ' | PowerShell: ' + $runtime.PowerShell + ' (' + $runtime.Edition + ')'))
            $lines.Add(('Icon Fallback: ' + (Get-IconTierInUse)))
        }
        default { $lines.Add('No Data Is Available For This View.') }
    }
    return @($lines)
}

function Get-AipmDefaultRegistryPath {
    $base = $env:LOCALAPPDATA
    if (-not $base) {
        $profilePath = [Environment]::GetFolderPath([Environment+SpecialFolder]::UserProfile)
        if (Test-IsWindows) { $base = [Environment]::GetFolderPath([Environment+SpecialFolder]::LocalApplicationData) }
        elseif ($profilePath) { $base = Join-Path $profilePath '.local' }
    }
    if (-not $base) { throw 'A Per-User Registry Location Could Not Be Resolved.' }
    return [System.IO.Path]::GetFullPath((Join-Path (Join-Path $base 'AI-Project-Manager') 'registry.json'))
}

function Resolve-AipmRegistryPath {
    param([Parameter(Mandatory)][string]$Root, [string]$RequestedPath = '', [switch]$ForceChoose)
    if ($RequestedPath) { return [System.IO.Path]::GetFullPath($RequestedPath) }
    if (-not $ForceChoose) {
        $configured = Get-UserSetting -Name 'registry_path' -Default ''
        if ($configured) { return [System.IO.Path]::GetFullPath($configured) }
    }
    $defaultPath = Get-AipmDefaultRegistryPath
    while ($true) {
        $items = @(
            (New-MenuItem -Label 'Use Default Registry Location' -Desc $defaultPath -Value 'default' -Icon 'Yes'),
            (New-MenuItem -Label 'Use An Existing Registry File' -Desc 'Connect A Valid Registry From Another Device Without Replacing It.' -Value 'existing' -Icon 'Project'),
            (New-MenuItem -Label 'Choose A Different Location' -Desc 'Create Or Select A Full File Path With Any Name Ending In .json.' -Value 'custom' -Icon 'Settings'),
            (New-MenuItem -Label 'Exit Without Setup' -Desc 'Do Not Create Or Select A Registry.' -Value 'cancel' -Icon 'Exit')
        )
        $choice = Show-Menu -Title 'Project Registry Setup' -Description 'Choose A New Registry Location Or Connect A Registry File You Already Have. Project State Remains In Each Project.' -Items $items
        if ($choice -in @($null, 'cancel', 'Exit', '__QUIT__')) { return $null }
        if ($choice -eq '__HELP__') {
            [void](Show-AipmPage -Title 'Project Registry Setup Help' -Lines @(
                'Choose The Default Registry Location, Connect An Existing Registry File, Or Pick A Custom .json File Path.',
                'The Registry File Must Live Outside The AIPM Installation Folder.',
                'Project Task State Remains Inside Each Project Shared-Project-State-Manager.'
            ))
            continue
        }
        if ($choice -eq 'existing') {
            $existingPath = Connect-AipmExistingRegistry -Root $Root
            if ($existingPath) { return $existingPath }
            continue
        }
        $path = $defaultPath
        if ($choice -eq 'custom') {
            $entered = Read-ValidatedInput -Prompt 'Registry File Path' -Help 'Enter The Full File Path, Including Any File Name Ending In .json.' -Example $defaultPath -Default '' -Validate {
                param($text)
                if (-not $text.Trim()) { return 'Enter A Registry File Path.' }
                try { $candidate = [System.IO.Path]::GetFullPath($text.Trim()) } catch { return 'Enter A Valid Full Path.' }
                if (-not [System.IO.Path]::IsPathRooted($text.Trim())) { return 'Enter A Full File Path Ending In .json.' }
                if ([System.IO.Path]::GetExtension($candidate) -ine '.json') { return 'Enter A Full File Path Ending In .json; A Folder Path Alone Is Not A File.' }
                if ([System.IO.Directory]::Exists($candidate)) { return 'Enter A File Path, Not An Existing Folder.' }
                return $null
            }
            if (-not $entered) { continue }
            $path = [System.IO.Path]::GetFullPath($entered.Trim())
        }
        $initialized = Invoke-AipmCore -AppRoot $Root -Command 'registry-init' -RegistryPath $path
        if ($initialized.Status -eq 'PASS') {
            if (-not (Set-UserSetting -Name 'registry_path' -Value $path)) {
                Show-Notice -Title 'Registry Path Was Not Saved' -Lines @('This Session Can Continue, But AIPM Will Ask Again Next Time.') -Kind Warning
            }
            return $path
        }
        Show-Notice -Title 'Registry Setup Was Blocked' -Lines @([string]$initialized.Reason, 'Choose A Location Outside The AIPM Installation And Try Again.') -Kind Error
    }
}

function Get-AipmRegistryEntries {
    param([Parameter(Mandatory)][string]$Root, [Parameter(Mandatory)][string]$RegistryPath)
    $result = Invoke-AipmCore -AppRoot $Root -Command 'list' -RegistryPath $RegistryPath
    if ($result.Status -ne 'PASS') { return [pscustomobject]@{ Status='BLOCKED'; Reason=$result.Reason; Projects=@() } }
    return [pscustomobject]@{ Status='PASS'; Reason=''; Projects=@((Get-AipmField $result.Data 'projects' @())) }
}

function Connect-AipmExistingRegistry {
    param([Parameter(Mandatory)][string]$Root)
    $defaultPath = Get-AipmDefaultRegistryPath
    $entered = Read-ValidatedInput -Prompt 'Existing Registry File Path' -Help 'Enter The Full Path To An Existing .json Registry File. AIPM Validates It Without Replacing Its Contents.' -Example $defaultPath -Default '' -Validate {
        param($text)
        if (-not $text.Trim()) { return 'Enter The Full Path To An Existing Registry File.' }
        try { $candidate = [System.IO.Path]::GetFullPath($text.Trim()) } catch { return 'Enter A Valid Full File Path.' }
        if (-not [System.IO.Path]::IsPathRooted($text.Trim())) { return 'Enter A Full Path To An Existing .json File.' }
        if ([System.IO.Path]::GetExtension($candidate) -ine '.json') { return 'The Existing Registry File Must End In .json.' }
        if (-not (Test-Path -LiteralPath $candidate -PathType Leaf)) { return 'The Existing Registry File Was Not Found.' }
        return $null
    }
    if (-not $entered) { return $null }
    $path = [System.IO.Path]::GetFullPath($entered.Trim())
    $inventory = Get-AipmRegistryEntries -Root $Root -RegistryPath $path
    if ($inventory.Status -ne 'PASS') {
        Show-Notice -Title 'Existing Registry Could Not Be Connected' -Lines @([string]$inventory.Reason, 'The Selected Registry Was Not Changed. Choose A Valid AIPM Registry File.') -Kind Error
        return $null
    }
    $saved = Set-UserSetting -Name 'registry_path' -Value $path
    $lines = @(
        ('Loaded ' + $inventory.Projects.Count + ' Registered Project(s).'),
        'The Existing Registry File Was Validated And Kept Unchanged.',
        'Project Root Paths Must Exist On This Device; AIPM Does Not Copy Project Files.'
    )
    if (-not $saved) { $lines += 'This Session Can Continue, But The Registry Choice Could Not Be Saved For Next Time.' }
    Show-Notice -Title 'Existing Registry Connected' -Lines $lines -Kind $(if ($saved) { 'Success' } else { 'Warning' })
    return $path
}

function ConvertFrom-AipmCodePoints {
    param([Parameter(Mandatory)][string]$Sequence)
    $text = ''
    foreach ($code in ($Sequence -split '\s+')) {
        $text += [char]::ConvertFromUtf32([Convert]::ToInt32($code, 16))
    }
    return $text
}

function Invoke-AipmRegistryManagement {
    param([Parameter(Mandatory)][string]$Root, [Parameter(Mandatory)][string]$RegistryPath)
    $currentPath = [System.IO.Path]::GetFullPath($RegistryPath)
    while ($true) {
        $inventory = Get-AipmRegistryEntries -Root $Root -RegistryPath $currentPath
        $inventoryDescription = if ($inventory.Status -eq 'PASS') { ('{0} Project(s) | {1}' -f $inventory.Projects.Count, $currentPath) } else { ('Registry Read Blocked: ' + $inventory.Reason) }
        $actions = @(
            (New-MenuItem -Label 'View Registered Projects' -Desc 'Read Project IDs, Names, And Their Root Paths.' -Value 'view' -Icon 'Project'),
            (New-MenuItem -Label 'Register A Project' -Desc 'Create Its Shared State Folder, Then Add A Registry Pointer.' -Value 'register' -Icon 'Yes'),
            (New-MenuItem -Label 'Unregister A Project' -Desc 'Remove Only The Registry Pointer; Project Files And State Stay In Place.' -Value 'unregister' -Icon 'No'),
            (New-MenuItem -Label 'Back Up Registry' -Desc 'Create A JSON Copy And SHA-256 Sidecar; Existing Files Are Never Overwritten.' -Value 'backup' -Icon 'Handoff'),
            (New-MenuItem -Label 'Restore Registry Backup' -Desc 'Validate Its Checksum And Save A Pre-Restore Safety Copy.' -Value 'restore' -Icon 'Run'),
            (New-MenuItem -Label 'Change Registry Location' -Desc 'Select Or Create Another Registry; The Current Registry Is Kept Untouched.' -Value 'location' -Icon 'Settings'),
            (New-MenuItem -Label 'Connect Existing Registry File' -Desc 'Use A Valid Registry From Another Device Without Replacing Its Contents.' -Value 'connect' -Icon 'Project'),
            (New-MenuItem -Label 'Back' -Desc 'Return To The Main Dashboard.' -Value 'back' -Icon 'Exit')
        )
        $choice = Show-Menu -Title 'Registry Management' -Description $inventoryDescription -Items $actions
        if ($choice -in @($null, 'back', 'Back')) { return $currentPath }
        if ($choice -eq '__HELP__') {
            [void](Show-AipmPage -Title 'Registry Management Help' -Lines @(
                'The Registry Stores Project IDs, Aliases, And Root Paths Only.',
                'Project Task State Is Stored In Shared-Project-State-Manager Inside Each Managed Project.',
                'Unregister Removes A Pointer Only; It Never Deletes Project Files Or State.',
                'Registry Files And Backups Must Remain Outside The AIPM Installation.'
            ))
            continue
        }
        if ($choice -eq '__QUIT__') { return $currentPath }
        if ($inventory.Status -ne 'PASS' -and $choice -ne 'location') {
            Show-Notice -Title 'Registry Is Unavailable' -Lines @([string]$inventory.Reason) -Kind Error
            continue
        }
        if ($choice -eq 'view') {
            $lines = @('Registry Path: ' + $currentPath, 'Registered Projects: ' + $inventory.Projects.Count, '')
            foreach ($project in $inventory.Projects) {
                $lines += ([string]$project.alias + ' | ' + [string]$project.project_id)
                $lines += ('  Root: ' + [string]$project.root_path)
            }
            if ($inventory.Projects.Count -eq 0) { $lines += 'No Projects Are Registered Yet.' }
            [void](Show-AipmPage -Title 'Registered Projects' -Lines $lines)
            continue
        }
        if ($choice -eq 'register') {
            $projectPath = Read-ValidatedInput -Prompt 'Project Folder Path' -Help 'Enter The Existing Project Folder. AIPM Will Add Only Its Managed State Folder.' -Example 'D:\Work\My-Project' -Default '' -Validate {
                param($text)
                try { $candidate = [System.IO.Path]::GetFullPath($text.Trim()) } catch { return 'Enter A Valid Full Folder Path.' }
                if (-not (Test-Path -LiteralPath $candidate -PathType Container)) { return 'The Project Folder Must Already Exist.' }
                return $null
            }
            if (-not $projectPath) { continue }
            $defaultAlias = Split-Path -Leaf ([System.IO.Path]::GetFullPath($projectPath))
            $alias = Read-ValidatedInput -Prompt 'Project Display Name' -Help 'This Name Appears In The AIPM Dashboard.' -Example $defaultAlias -Default $defaultAlias -Validate { param($text) if (-not $text.Trim()) { return 'Enter A Project Name.' }; return $null }
            if (-not $alias) { continue }
            $confirm = Show-Confirm -Title 'Register This Project?' -Message ('AIPM Will Create Shared-Project-State-Manager Under ' + $projectPath + '. It Will Not Edit Project Source Files.') -YesLabel 'Create State And Register' -YesDesc 'Write AIPM-Owned State Metadata, Then Add The Registry Entry.' -NoLabel 'Cancel' -NoDesc 'Make No Project Or Registry Changes.' -Default $false
            if (-not $confirm) { continue }
            $projectId = 'Project-' + [Guid]::NewGuid().ToString('N').Substring(0, 12)
            $existingManifestPath = Join-Path (Join-Path $projectPath 'Shared-Project-State-Manager') 'Project-Manifest.json'
            if (Test-Path -LiteralPath $existingManifestPath -PathType Leaf) {
                try {
                    $existingManifest = Get-Content -LiteralPath $existingManifestPath -Raw -Encoding UTF8 | ConvertFrom-Json
                    if ($existingManifest -and $existingManifest.project_id -and ([string]$existingManifest.project_id).Trim()) {
                        $projectId = ([string]$existingManifest.project_id).Trim()
                    }
                } catch { }
            }
            $registered = Invoke-AipmCore -AppRoot $Root -Command 'registry-register' -RegistryPath $currentPath -ProjectRoot $projectPath -ProjectId $projectId -Alias $alias.Trim()
            if ($registered.Status -eq 'PASS') {
                $successLines = @(
                    'Project Folder Added Successfully.',
                    ('Please Select ' + (ConvertFrom-AipmCodePoints '27A1') + ' Refresh From The Home Page.')
                )
                Show-Notice -Title 'Project Registered' -Lines $successLines -Kind Success
            }
            else { Show-Notice -Title 'Project Registration Failed' -Lines @([string]$registered.Reason) -Kind Error }
            continue
        }
        if ($choice -eq 'unregister') {
            if ($inventory.Projects.Count -eq 0) { Show-Notice -Title 'No Projects To Unregister' -Lines @('The Registry Is Empty.') -Kind Info; continue }
            $projectItems = @($inventory.Projects | ForEach-Object { New-MenuItem -Label ([string]$_.alias) -Desc ([string]$_.root_path) -Value ([string]$_.project_id) -Icon 'Project' })
            $projectItems += New-MenuItem -Label 'Cancel' -Desc 'Return Without Removing A Registry Entry.' -Value 'cancel' -Icon 'Exit'
            $selected = Show-Menu -Title 'Select Project To Unregister' -Items $projectItems
            if (-not $selected -or $selected -in @('cancel','__HELP__','__QUIT__')) { continue }
            $entry = @($inventory.Projects | Where-Object { $_.project_id -eq $selected }) | Select-Object -First 1
            if (-not $entry) { continue }
            $confirm = Show-Confirm -Title 'Remove Registry Pointer?' -Message ('This removes ' + [string]$entry.alias + ' from this registry only. Its project files and Shared-Project-State-Manager remain untouched.') -YesLabel 'Remove Pointer' -YesDesc 'Keep All Project Files And State.' -NoLabel 'Cancel' -NoDesc 'Keep The Registry Entry.' -Default $false
            if ($confirm) {
                $removed = Invoke-AipmCore -AppRoot $Root -Command 'registry-unregister' -RegistryPath $currentPath -ProjectId ([string]$selected)
                if ($removed.Status -eq 'PASS') { Show-Notice -Title 'Project Unregistered' -Lines @('The Registry Pointer Was Removed. Project Files And State Were Kept.') -Kind Success }
                else { Show-Notice -Title 'Unregister Failed' -Lines @([string]$removed.Reason) -Kind Error }
            }
            continue
        }
        if ($choice -eq 'backup') {
            $suggested = Join-Path ([Environment]::GetFolderPath([Environment+SpecialFolder]::MyDocuments)) ('AIPM-Registry-Backup-' + [DateTime]::Now.ToString('yyyyMMdd-HHmmss') + '.json')
            $destination = Read-ValidatedInput -Prompt 'Backup File Path' -Help 'Use A New .json File Path Outside The AIPM Installation.' -Example $suggested -Default $suggested -Validate {
                param($text)
                try { $candidate = [System.IO.Path]::GetFullPath($text.Trim()) } catch { return 'Enter A Valid Full File Path.' }
                if ([System.IO.Path]::GetExtension($candidate) -ne '.json') { return 'The Backup File Must End In .json.' }
                if (Test-Path -LiteralPath $candidate) { return 'That File Already Exists; Choose A New File Name.' }
                return $null
            }
            if (-not $destination) { continue }
            $backup = Invoke-AipmCore -AppRoot $Root -Command 'registry-backup' -RegistryPath $currentPath -Destination $destination
            if ($backup.Status -eq 'PASS') { Show-Notice -Title 'Registry Backup Created' -Lines @(('Backup: ' + [string]$backup.Data.backup), ('SHA-256: ' + [string]$backup.Data.sha256)) -Kind Success }
            else { Show-Notice -Title 'Backup Failed' -Lines @([string]$backup.Reason) -Kind Error }
            continue
        }
        if ($choice -eq 'restore') {
            $source = Read-ValidatedInput -Prompt 'Backup File Path' -Help 'Enter The Registry Backup JSON. A SHA-256 Sidecar Is Checked When Present.' -Example 'C:\Users\YourName\Documents\AIPM-Registry-Backup.json' -Default '' -Validate {
                param($text)
                try { $candidate = [System.IO.Path]::GetFullPath($text.Trim()) } catch { return 'Enter A Valid Full File Path.' }
                if (-not (Test-Path -LiteralPath $candidate -PathType Leaf)) { return 'The Backup File Was Not Found.' }
                return $null
            }
            if (-not $source) { continue }
            $confirm = Show-Confirm -Title 'Restore Registry Backup?' -Message 'AIPM Validates The Backup And Saves A Pre-Restore Copy Of The Current Registry Before Replacing It.' -YesLabel 'Validate And Restore' -YesDesc 'Replace Registry Contents After All Checks Pass.' -NoLabel 'Cancel' -NoDesc 'Keep The Current Registry Unchanged.' -Default $false
            if ($confirm) {
                $restored = Invoke-AipmCore -AppRoot $Root -Command 'registry-restore' -RegistryPath $currentPath -Source $source
                if ($restored.Status -eq 'PASS') { Show-Notice -Title 'Registry Restored' -Lines @(('Safety Copy: ' + [string]$restored.Data.pre_restore_backup)) -Kind Success }
                else { Show-Notice -Title 'Restore Failed' -Lines @([string]$restored.Reason) -Kind Error }
            }
            continue
        }
        if ($choice -eq 'location') {
            $newPath = Resolve-AipmRegistryPath -Root $Root -ForceChoose
            if ($newPath -and $newPath -ne $currentPath) {
                $currentPath = $newPath
                Show-Notice -Title 'Registry Location Changed' -Lines @('The New Registry Is Selected. The Previous Registry Was Kept Untouched; Its Projects Were Not Copied.') -Kind Success
            }
            continue
        }
        if ($choice -eq 'connect') {
            $existingPath = Connect-AipmExistingRegistry -Root $Root
            if ($existingPath) { $currentPath = $existingPath }
            continue
        }
    }
}

function Show-AipmTaskRecord {
    param([Parameter(Mandatory)][string]$Root, [Parameter(Mandatory)][string]$RegistryPath, [Parameter(Mandatory)][string]$ProjectId, [string]$ProjectRoot = '', [Parameter(Mandatory)]$TaskRow)
    if (-not $ProjectRoot) {
        $regEntries = Get-AipmRegistryEntries -Root $Root -RegistryPath $RegistryPath
        if ($regEntries.Status -eq 'PASS') {
            $matchedProject = @($regEntries.Projects | Where-Object { [string]$_.project_id -eq $ProjectId }) | Select-Object -First 1
            if ($matchedProject) { $ProjectRoot = [string]$matchedProject.root_path }
        }
    }
    $recordResult = Invoke-AipmCore -AppRoot $Root -Command 'task-read' -RegistryPath $RegistryPath -ProjectId $ProjectId -TaskId ([string]$TaskRow.task_id)
    if ($recordResult.Status -ne 'PASS') {
        Show-Notice -Title 'Task Could Not Be Read' -Lines @([string]$recordResult.Reason) -Kind Error
        return
    }
    $task = $recordResult.Data.task
    while ($true) {
        $freshResult = Invoke-AipmCore -AppRoot $Root -Command 'task-read' -RegistryPath $RegistryPath -ProjectId $ProjectId -TaskId ([string]$TaskRow.task_id)
        if ($freshResult.Status -ne 'PASS') {
            Show-Notice -Title 'Task Could Not Be Refreshed' -Lines @([string]$freshResult.Reason, 'Return To The Task List And Try Again.') -Kind Error
            return
        }
        $task = $freshResult.Data.task
        $lines = @(
            ('Task ID: ' + [string]$TaskRow.task_id),
            ('Status: ' + [string]$task.task_status + ' (Derived From Task Evidence And Blockers)'),
            ('Scope: ' + [string]$task.scope),
            ('Last Verified Action: ' + [string](Get-AipmField $task 'last_verified_action' 'Not Recorded')),
            ('Next Action: ' + [string](Get-AipmField $task 'next_action' 'Not Recorded')),
            '',
            'Plan:',
            [string]$task.plan
        )
        foreach ($blocker in @($task.blockers)) { $lines += ('Blocker: ' + [string]$blocker) }
        if ($task.verification) { $lines += ('Verification: ' + [string]$task.verification.result + ' | ' + [string]$task.verification.evidence) }
        if ($task.report) { $lines += ('Report: ' + [string]$task.report) }
        $actions = @(
            (New-MenuItem -Label 'View Task Status And Details' -Desc ('Current Status: ' + [string]$task.task_status + ' | Review Scope, Progress, Plan And Evidence.') -Value 'view' -Icon 'Task'),
            (New-MenuItem -Label 'Update Task Plan' -Desc 'Replace The Current Plan In AIPM Task State.' -Value 'plan' -Icon 'Edit'),
            (New-MenuItem -Label 'Update Progress Checkpoint' -Desc 'Record The Last Verified Action And The Exact Next Action.' -Value 'checkpoint' -Icon 'Handoff'),
            (New-MenuItem -Label 'Add A Blocker' -Desc 'Record A Current Obstacle Without Editing Project Files.' -Value 'blocker' -Icon 'Warning'),
            (New-MenuItem -Label 'Clear Blockers' -Desc 'Remove All Recorded Blockers After They Are Resolved.' -Value 'clear' -Icon 'Success'),
            (New-MenuItem -Label 'Record Verification' -Desc 'Record A Result And Its Evidence; AIPM Does Not Run Tests.' -Value 'verify' -Icon 'Success'),
            (New-MenuItem -Label 'Update Task Report' -Desc 'Save A Progress Or Completion Note In Task State.' -Value 'report' -Icon 'Handoff'),
            (New-MenuItem -Label 'Mark Task Complete' -Desc 'Close This Task With A Completion Note.' -Value 'close' -Icon 'Success'),
            (New-MenuItem -Label 'Reopen Task' -Desc 'Return A Completed Task To In-Progress Work.' -Value 'reopen' -Icon 'Progress'),
            (New-MenuItem -Label 'Archive Completed Task' -Desc 'Create A Portable ZIP With Metadata.json And SHA-256 Checksum.' -Value 'archive' -Icon 'Project'),
            (New-MenuItem -Label 'Review Git Changes' -Desc 'View The Current Git Changes For This Managed Project.' -Value 'git-status' -Icon 'Project'),
            (New-MenuItem -Label 'Commit Git Changes' -Desc 'Stage Project Changes Excluding AIPM State, Then Create A Local Commit.' -Value 'git-commit' -Icon 'Success'),
            (New-MenuItem -Label 'Attach Plan, Report Or Supporting File' -Desc 'Copy One Selected File Into This Task; The Original File Stays In Place.' -Value 'attach' -Icon 'Item'),
            (New-MenuItem -Label 'View Attached Task Files' -Desc 'List Supporting Files Already Stored In This Task.' -Value 'artifacts' -Icon 'Project'),
            (New-MenuItem -Label 'Edit Task Name & Description' -Desc 'Update The Title Or Scope In AIPM Task State.' -Value 'edit' -Icon 'Edit'),
            (New-MenuItem -Label 'Rename Task Folder & Identity' -Desc 'Change The Task Folder Name And Its ID In AIPM State.' -Value 'rename' -Icon 'Item'),
            (New-MenuItem -Label 'Open Task Folder In Explorer' -Desc 'Open The Live Task Folder In File Explorer.' -Value 'open-folder' -Icon 'Project'),
            (New-MenuItem -Label 'Duplicate Task' -Desc 'Create A New Task Initialized With This Task Scope And Plan.' -Value 'clone' -Icon 'Task'),
            (New-MenuItem -Label 'Delete Task' -Desc 'Permanently Delete Live Folder And Unregister Task, Even If Incomplete.' -Value 'delete' -Icon 'Warning'),
            (New-MenuItem -Label 'Back' -Desc 'Return To The Project Task List.' -Value 'back' -Icon 'Exit')
        )
        $action = Show-Menu -Title ('Manage Task: ' + [string]$task.title) -Description ('Status: ' + [string]$task.task_status + ' | Task ID: ' + [string]$TaskRow.task_id) -Items $actions
        if ($action -in @($null, 'back', 'Back', '__QUIT__')) { return }
        if ($action -eq 'view') {
            [void](Show-AipmPage -Title ('Task Status And Details: ' + [string]$task.title) -Lines $lines)
            continue
        }
        if ($action -eq 'edit') {
            $currentTitle = [string]$task.title
            $currentScope = [string]$task.scope
            $editChoice = Show-Menu -Title 'Edit Task Title Or Description' -Description ('Task ID: ' + [string]$TaskRow.task_id) -Items @(
                (New-MenuItem -Label 'Edit Task Title' -Desc ('Current: ' + $currentTitle) -Value 'title' -Icon 'Edit'),
                (New-MenuItem -Label 'Edit Task Description / Scope' -Desc ('Current: ' + $currentScope) -Value 'scope' -Icon 'Edit'),
                (New-MenuItem -Label 'Edit Both Title And Description' -Desc 'Update Both Name And Description In Sequence.' -Value 'both' -Icon 'Edit'),
                (New-MenuItem -Label 'Cancel' -Desc 'Return Without Changing Task Details.' -Value 'cancel' -Icon 'Exit')
            )
            if (-not $editChoice -or $editChoice -eq 'cancel' -or $editChoice -in @('__QUIT__', '__HELP__')) { continue }
            $newTitle = $null
            $newScope = $null
            if ($editChoice -in @('title', 'both')) {
                $newTitle = Read-ValidatedInput -Prompt 'Edit Task Title' -Help 'Enter The New Display Name For This Task.' -Example $currentTitle -Default $currentTitle -Validate {
                    param($textVal)
                    if (-not $textVal.Trim()) { return 'Task Title Cannot Be Empty.' }
                    if ($textVal -match '[\\/:]') { return 'Task Title Must Be A Name, Not A File Path.' }
                    return $null
                }
                if ($null -eq $newTitle) { continue }
            }
            if ($editChoice -in @('scope', 'both')) {
                $newScope = Read-ValidatedInput -Prompt 'Edit Task Description / Scope' -Help 'Enter The Updated Description Or Scope For This Task.' -Example $currentScope -Default $currentScope -Validate {
                    param($textVal)
                    if (-not $textVal.Trim()) { return 'Task Description Cannot Be Empty.' }
                    return $null
                }
                if ($null -eq $newScope) { continue }
            }
            $editParams = @{ AppRoot = $Root; Command = 'task-edit'; RegistryPath = $RegistryPath; ProjectId = $ProjectId; TaskId = ([string]$TaskRow.task_id) }
            if ($newTitle) { $editParams['Title'] = $newTitle.Trim() }
            if ($newScope) { $editParams['Scope'] = $newScope.Trim() }
            $updated = Invoke-AipmCore @editParams
            if ($updated.Status -ne 'PASS') {
                Show-Notice -Title 'Failed To Update Task Details' -Lines @([string]$updated.Reason) -Kind Error
            } else {
                if ($updated.Data -and $updated.Data.task -and $updated.Data.task.title) {
                    $TaskRow.title = [string]$updated.Data.task.title
                }
                Show-Notice -Title 'Task Details Updated' -Lines @(
                    ('Title: ' + [string]$updated.Data.task.title),
                    ('Scope: ' + [string]$updated.Data.task.scope)
                ) -Kind Success
            }
            continue
        }
        if ($action -eq 'rename') {
            $currentId = [string]$TaskRow.task_id
            $newId = Read-ValidatedInput -Prompt 'New Task Folder & ID' -Help 'Must Start With Task- And Contain Only Letters, Digits, Hyphens, And Underscores.' -Example $currentId -Default $currentId -Validate {
                param($textVal)
                $val = $textVal.Trim()
                if (-not $val) { return 'Task Folder / ID Cannot Be Empty.' }
                if ($val -notmatch '^Task-[A-Za-z0-9][A-Za-z0-9_-]{0,159}$') { return 'Must Start With Task- And Contain Letters, Digits, Hyphens, Or Underscores.' }
                return $null
            }
            if (-not $newId -or $newId.Trim() -eq $currentId) { continue }
            $confirm = Show-Confirm -Title 'Rename Task Folder & Identity?' -Message ('Old: ' + $currentId + ' -> New: ' + $newId.Trim() + ' | This Renames The Task Folder And Updates Registry State.') -YesLabel 'Rename Folder' -YesDesc 'Apply The New Task Folder Name.' -NoLabel 'Cancel' -NoDesc 'Keep Current Name.' -Default $false
            if (-not $confirm) { continue }
            $renamed = Invoke-AipmCore -AppRoot $Root -Command 'task-rename' -RegistryPath $RegistryPath -ProjectId $ProjectId -TaskId $currentId -NewTaskId $newId.Trim()
            if ($renamed.Status -ne 'PASS') {
                Show-Notice -Title 'Failed To Rename Task' -Lines @([string]$renamed.Reason) -Kind Error
            } else {
                $TaskRow.task_id = $newId.Trim()
                Show-Notice -Title 'Task Renamed Successfully' -Lines @(('New Task ID: ' + $newId.Trim()), ('Path: ' + [string]$renamed.Data.task_path)) -Kind Success
            }
            continue
        }
        if ($action -eq 'open-folder') {
            $taskFolder = $null
            if ($ProjectRoot) {
                $candidate = Join-Path (Join-Path $ProjectRoot 'Shared-Project-State-Manager\Tasks') ([string]$TaskRow.task_id)
                if (Test-Path -LiteralPath $candidate) { $taskFolder = [System.IO.Path]::GetFullPath($candidate) }
            }
            if (-not $taskFolder) {
                $liveResult = Invoke-AipmCore -AppRoot $Root -Command 'task-read' -RegistryPath $RegistryPath -ProjectId $ProjectId -TaskId ([string]$TaskRow.task_id)
                if ($liveResult.Status -eq 'PASS' -and $liveResult.Data.task -and $liveResult.Data.task.task_path) {
                    $taskFolder = [string]$liveResult.Data.task.task_path
                }
            }
            if ($taskFolder -and (Test-Path -LiteralPath $taskFolder)) {
                try {
                    $opener = if (Test-IsWindows) { 'explorer.exe' } elseif ((Get-PlatformName) -eq 'macOS') { 'open' } else { 'xdg-open' }
                    [System.Diagnostics.Process]::Start($opener, ('"' + $taskFolder + '"')) | Out-Null
                    Show-Notice -Title 'Folder Opened' -Lines @(('Task Folder: ' + $taskFolder)) -Kind Success
                } catch {
                    Show-Notice -Title 'Could Not Open Folder' -Lines @(('Path: ' + $taskFolder), [string]$_.Exception.Message) -Kind Warning
                }
            } else {
                Show-Notice -Title 'Task Folder Not Found' -Lines @('The Live Task Folder Does Not Exist On Disk (It May Be Archived).') -Kind Warning
            }
            continue
        }
        if ($action -eq 'delete') {
            $deleteConfirm = Show-Confirm -Title 'Permanently Delete Task?' -Message ('Task ID: ' + [string]$TaskRow.task_id + ' (' + [string]$task.title + ') | Status: ' + [string]$task.task_status + ' | This Removes The Live Task Folder And Unregisters It From AIPM Registry. This Action Cannot Be Undone.') -YesLabel 'Delete Task' -YesDesc 'Permanently Delete Live Folder And Unregister Task.' -NoLabel 'Cancel' -NoDesc 'Keep Task Intact.' -Default $false
            if (-not $deleteConfirm) { continue }
            $deleted = Invoke-AipmCore -AppRoot $Root -Command 'task-delete' -RegistryPath $RegistryPath -ProjectId $ProjectId -TaskId ([string]$TaskRow.task_id) -DeleteArchive
            if ($deleted.Status -ne 'PASS') {
                Show-Notice -Title 'Task Deletion Failed' -Lines @([string]$deleted.Reason) -Kind Error
                continue
            }
            Show-Notice -Title 'Task Deleted Successfully' -Lines @(
                ('Task ID: ' + [string]$TaskRow.task_id),
                'Live Task Folder And Registry Record Have Been Removed.'
            ) -Kind Success
            return
        }
        if ($action -eq 'clone') {
            $defaultCloneTitle = 'Copy of ' + [string]$task.title
            $cloneTitle = Read-ValidatedInput -Prompt 'Duplicate Task Title' -Help 'Enter The Title For The New Duplicated Task.' -Example $defaultCloneTitle -Default $defaultCloneTitle -Validate {
                param($textVal)
                if (-not $textVal.Trim()) { return 'Title Cannot Be Empty.' }
                return $null
            }
            if (-not $cloneTitle) { continue }
            $cloned = Invoke-AipmCore -AppRoot $Root -Command 'task-clone' -RegistryPath $RegistryPath -ProjectId $ProjectId -TaskId ([string]$TaskRow.task_id) -Title $cloneTitle.Trim()
            if ($cloned.Status -ne 'PASS') {
                Show-Notice -Title 'Duplicate Task Failed' -Lines @([string]$cloned.Reason) -Kind Error
            } else {
                Show-Notice -Title 'Task Duplicated Successfully' -Lines @(
                    ('New Task ID: ' + [string]$cloned.Data.task_id),
                    ('Title: ' + [string]$cloned.Data.task.title),
                    'The New Task Was Created With The Same Scope And Plan.'
                ) -Kind Success
            }
            continue
        }
        if ($action -eq 'git-status') {
            if (-not $ProjectRoot) { Show-Notice -Title 'Project Root Is Unavailable' -Lines @('Verify The Registered Project Path And Try Again.') -Kind Error; continue }
            $projectRoot = [System.IO.Path]::GetFullPath($ProjectRoot)
            $git = Find-Executable -Name 'git'
            if (-not $git) { Show-Notice -Title 'Git Is Unavailable' -Lines @('Install Git Or Add It To PATH, Then Try Again.') -Kind Error; continue }
            $topResult = Invoke-External -FilePath $git -Arguments @('-C', $projectRoot, 'rev-parse', '--show-toplevel') -TimeoutSec 10
            $topRoot = if ($topResult.Started -and -not $topResult.TimedOut -and $topResult.ExitCode -eq 0 -and $topResult.StdOut.Trim()) { [System.IO.Path]::GetFullPath($topResult.StdOut.Trim()).TrimEnd([char[]]@('\','/')) } else { '' }
            if (-not $topRoot -or -not $topRoot.Equals($projectRoot.TrimEnd([char[]]@('\','/')), [System.StringComparison]::OrdinalIgnoreCase)) {
                Show-Notice -Title 'Git Repository Not Initialized' -Lines @('The Managed Project Root Is Not A Git Repository Root.') -Kind Error
                continue
            }
            $projectResult = Invoke-External -FilePath $git -Arguments @('-C', $projectRoot, 'status', '--short') -TimeoutSec 10
            if (-not $projectResult.Started -or $projectResult.TimedOut -or $projectResult.ExitCode -ne 0) { Show-Notice -Title 'Git Status Failed' -Lines @($projectResult.StdErr.Trim()) -Kind Error; continue }
            $gitLines = @($projectResult.StdOut.Trim() -split "`r?`n" | Where-Object { $_ })
            if ($gitLines.Count -eq 0) { $gitLines = @('Working Tree Is Clean.') }
            [void](Show-AipmPage -Title 'Git Changes' -Lines $gitLines)
            continue
        }
        if ($action -eq 'git-commit') {
            if (-not $ProjectRoot) { Show-Notice -Title 'Project Root Is Unavailable' -Lines @('Verify The Registered Project Path And Try Again.') -Kind Error; continue }
            $message = Read-ValidatedInput -Prompt 'Git Commit Message' -Help 'AIPM Stages Project Changes While Excluding Shared-Project-State-Manager, Then Creates A Local Commit.' -Example ('Complete task: ' + [string]$task.title) -Default '' -Validate { param($text) if (-not $text.Trim()) { return 'Enter A Commit Message.' }; return $null }
            if (-not $message) { continue }
            if (-not (Show-Confirm -Title 'Create Local Git Commit?' -Message 'This Stages The Current Project Changes, Excludes AIPM State, And Creates A Local Git Commit. It Does Not Push To Any Remote.' -YesLabel 'Commit Changes' -YesDesc 'Create The Local Commit.' -NoLabel 'Cancel' -NoDesc 'Return Without Changing Git.' -Default $false)) { continue }
            $git = Find-Executable -Name 'git'
            if (-not $git) { Show-Notice -Title 'Git Is Unavailable' -Lines @('Install Git Or Add It To PATH, Then Try Again.') -Kind Error; continue }
            $projectRoot = [System.IO.Path]::GetFullPath($ProjectRoot)
            $topResult = Invoke-External -FilePath $git -Arguments @('-C', $projectRoot, 'rev-parse', '--show-toplevel') -TimeoutSec 10
            $topRoot = if ($topResult.Started -and -not $topResult.TimedOut -and $topResult.ExitCode -eq 0 -and $topResult.StdOut.Trim()) { [System.IO.Path]::GetFullPath($topResult.StdOut.Trim()).TrimEnd([char[]]@('\','/')) } else { '' }
            if (-not $topRoot -or -not $topRoot.Equals($projectRoot.TrimEnd([char[]]@('\','/')), [System.StringComparison]::OrdinalIgnoreCase)) {
                Show-Notice -Title 'Git Repository Not Initialized' -Lines @('The Managed Project Root Is Not A Git Repository Root.') -Kind Error
                continue
            }
            $stage = Invoke-External -FilePath $git -Arguments @('-C', $projectRoot, 'add', '-A', '--', '.', ':!Shared-Project-State-Manager/**') -TimeoutSec 30
            if (-not $stage.Started -or $stage.TimedOut -or $stage.ExitCode -ne 0) { Show-Notice -Title 'Git Stage Failed' -Lines @($stage.StdErr.Trim()) -Kind Error; continue }
            $commit = Invoke-External -FilePath $git -Arguments @('-C', $projectRoot, 'commit', '--no-verify', '-m', $message.Trim()) -TimeoutSec 30
            if (-not $commit.Started -or $commit.TimedOut -or $commit.ExitCode -ne 0) {
                $errLines = @($commit.StdErr.Trim(), $commit.StdOut.Trim() | Where-Object { $_ })
                if ($errLines.Count -eq 0) { $errLines = @('Git Commit Failed.') }
                Show-Notice -Title 'Git Commit Failed' -Lines $errLines -Kind Error
                continue
            }
            Show-Notice -Title 'Git Commit Created' -Lines @($commit.StdOut.Trim()) -Kind Success
            continue
        }
        if ($action -eq '__HELP__') {
            [void](Show-AipmPage -Title 'Task Management Help' -Lines @(
                'Selecting A Task Opens This Action Menu Directly; Choose View Task Status And Details For The Full Status Page.',
                'Task Status Is Derived From Blockers, Verification, And Report Evidence; It Is Not Manually Toggled.',
                'Task Changes Update Only AIPM-Owned Shared Project State.',
                'Attach Plan, Report Or Supporting File Copies One Selected File Into A Task Category And Leaves The Original In Place.',
                'Project Source Files Stay In Their Original Locations And Are Never Edited By AIPM.',
                'Verification Records Evidence Supplied By You; AIPM Does Not Execute Project Tests.',
                'Task Records Can Be Renamed, Edited, Archived Or Permanently Deleted Directly From This Action Menu.'
            ))
            continue
        }
        if ($action -eq 'attach') {
            $categories = @(
                (New-MenuItem -Label 'Instructions And Plans' -Desc 'Store Task-Scoped Instructions Or A Plan Document.' -Value 'Instructions' -Icon 'Edit'),
                (New-MenuItem -Label 'Handoffs' -Desc 'Store A Handoff For Another Agent Or Session.' -Value 'Handoff' -Icon 'Handoff'),
                (New-MenuItem -Label 'Reports' -Desc 'Store A Progress, Verification Or Completion Report.' -Value 'Reports' -Icon 'Item'),
                (New-MenuItem -Label 'Scripts' -Desc 'Store A Task Helper Script.' -Value 'Scripts' -Icon 'Settings'),
                (New-MenuItem -Label 'Examples' -Desc 'Store A Supporting Example.' -Value 'Examples' -Icon 'Item'),
                (New-MenuItem -Label 'References' -Desc 'Store A Reference Needed To Resume This Task.' -Value 'References' -Icon 'Project'),
                (New-MenuItem -Label 'Cancel' -Desc 'Return Without Attaching A File.' -Value 'cancel' -Icon 'Exit')
            )
            $category = Show-Menu -Title 'Choose Task File Category' -Description 'The Selected File Is Copied Into AIPM Task State; Its Original Is Not Changed.' -Items $categories
            if (-not $category -or $category -eq 'cancel' -or $category -in @('__HELP__','__QUIT__')) { continue }
            $sourcePath = Read-ValidatedInput -Prompt 'Task Support File Path' -Help 'Enter The Full Path To One Existing File. Files Over 16 MiB Cannot Be Attached.' -Example 'D:\Work\Project\Progress-Report.md' -Default '' -Validate {
                param($text)
                try { $candidate = [System.IO.Path]::GetFullPath($text.Trim()) } catch { return 'Enter A Valid Full File Path.' }
                if (-not (Test-Path -LiteralPath $candidate -PathType Leaf)) { return 'The Selected File Was Not Found.' }
                try { if ((New-Object System.IO.FileInfo($candidate)).Length -gt 16777216) { return 'The Selected File Exceeds The 16 MiB Task Artifact Limit.' } } catch { return 'The Selected File Could Not Be Read.' }
                return $null
            }
            if (-not $sourcePath) { continue }
            $sourcePath = [System.IO.Path]::GetFullPath($sourcePath.Trim())
            $defaultName = [System.IO.Path]::GetFileName($sourcePath)
            $fileName = Read-ValidatedInput -Prompt 'Task Artifact File Name' -Help 'Choose A File Name Only; The Category Folder Is Added Automatically. Existing Files Are Never Overwritten.' -Example $defaultName -Default $defaultName -Validate {
                param($text)
                $name = $text.Trim()
                if (-not $name -or $name -in @('.', '..')) { return 'Enter A Valid File Name.' }
                if ($name -match '[\\/:]' -or $name -match '[<>"|?*]' -or $name.EndsWith('.') -or $name.EndsWith(' ')) { return 'Enter A File Name Without Folder Separators Or Invalid Characters.' }
                return $null
            }
            if (-not $fileName) { continue }
            $relativePath = [string]$category + '/' + $fileName.Trim()
            $confirm = Show-Confirm -Title 'Attach This Task File?' -Message ('Source: ' + $sourcePath + ' | Task File: ' + $relativePath) -YesLabel 'Attach File' -YesDesc 'Copy This File Into The Selected Task; Keep The Original.' -NoLabel 'Cancel' -NoDesc 'Do Not Copy The File.' -Default $false
            if (-not $confirm) { continue }
            $updated = Invoke-AipmCore -AppRoot $Root -Command 'task-artifact-write' -RegistryPath $RegistryPath -ProjectId $ProjectId -TaskId ([string]$TaskRow.task_id) -RelativePath $relativePath -FromFile $sourcePath
        } elseif ($action -eq 'artifacts') {
            $listed = Invoke-AipmCore -AppRoot $Root -Command 'task-artifact-list' -RegistryPath $RegistryPath -ProjectId $ProjectId -TaskId ([string]$TaskRow.task_id)
            if ($listed.Status -ne 'PASS') {
                Show-Notice -Title 'Task Files Could Not Be Listed' -Lines @([string]$listed.Reason, 'Return To The Task Menu And Try Again.') -Kind Error
            } else {
                $artifactRows = @($listed.Data.artifacts)
                $searchQuery = ''
                while ($true) {
                    $visibleArtifacts = @()
                    $exactArtifacts = @()
                    $normalizedQuery = $searchQuery.Trim().Replace('\', '/')
                    if (-not $normalizedQuery) {
                        $visibleArtifacts = $artifactRows
                    } else {
                        foreach ($artifact in $artifactRows) {
                            $artifactPath = [string]$artifact.path
                            $artifactName = [System.IO.Path]::GetFileName($artifactPath)
                            if ($artifactPath.IndexOf($normalizedQuery, [System.StringComparison]::OrdinalIgnoreCase) -ge 0 -or $artifactName.IndexOf($normalizedQuery, [System.StringComparison]::OrdinalIgnoreCase) -ge 0) {
                                $visibleArtifacts += $artifact
                            }
                            if ($artifactPath.Equals($normalizedQuery, [System.StringComparison]::OrdinalIgnoreCase) -or $artifactName.Equals($normalizedQuery, [System.StringComparison]::OrdinalIgnoreCase)) {
                                $exactArtifacts += $artifact
                            }
                        }
                    }
                    $queryLabel = if ($normalizedQuery) { $normalizedQuery } else { 'All Files' }
                    $artifactLines = @('Task: ' + [string]$task.title, 'Status: ' + [string]$task.task_status, ('Search Query: ' + $queryLabel))
                    if ($normalizedQuery) {
                        $exactLabel = if ($exactArtifacts.Count -gt 0) { 'Found' } else { 'Not Found' }
                        $artifactLines += ('Exact File Match: ' + $exactLabel)
                    }
                    $artifactLines += ('Matching Files: ' + $visibleArtifacts.Count)
                    $artifactLines += ''
                    if ($visibleArtifacts.Count -eq 0) {
                        if ($artifactRows.Count -eq 0 -and -not $normalizedQuery) { $artifactLines += 'No Supporting Files Are Attached To This Task Yet.' }
                        else { $artifactLines += 'No Matching Files Found.' }
                    }
                    foreach ($artifact in $visibleArtifacts) { $artifactLines += ([string]$artifact.path + ' | ' + [string]$artifact.sha256) }
                    $pageResult = Show-AipmPage -Title 'Attached Task Files' -Lines $artifactLines -Searchable
                    if ($pageResult -ne '__SEARCH__') { break }
                    $enteredQuery = Read-ValidatedInput -Prompt 'Search Attached Task Files' -Help 'Enter A Full Or Partial File Name Or Relative Path. Leave Empty To Show All Attached Files.' -Example 'Agent Progress Report.md' -Default $searchQuery
                    if ($null -ne $enteredQuery) { $searchQuery = $enteredQuery.Trim() }
                }
            }
            continue
        } elseif ($action -eq 'archive') {
            if (-not (Show-Confirm -Title 'Archive Completed Task?' -Message 'AIPM Creates A Portable ZIP Archive With Metadata.json And SHA-256 Checksum In Shared-Project-State-Manager/Archive.' -YesLabel 'Create Archive' -YesDesc 'Create A Portable Integrity-Checked Archive.' -NoLabel 'Cancel' -NoDesc 'Return Without Creating An Archive.' -Default $false)) { continue }
            $updated = Invoke-AipmCore -AppRoot $Root -Command 'task-archive' -RegistryPath $RegistryPath -ProjectId $ProjectId -TaskId ([string]$TaskRow.task_id)
            if ($updated.Status -ne 'PASS') {
                Show-Notice -Title 'Task Archive Failed' -Lines @([string]$updated.Reason, 'Task Folder Remains Intact.') -Kind Error
                continue
            }
            $deleteChoice = Show-Confirm -Title 'Archive Verified: Delete Live Task Folder?' -Message ('The Archive And SHA-256 Checksum Were Verified. All Files And Metadata.json Are Safely Preserved in: ' + [string]$updated.Data.archive_path) -YesLabel 'Delete Task Folder' -YesDesc 'Remove The Live Task Folder; The Portable Archive Preserves All Data And Files.' -NoLabel 'Keep Task Folder' -NoDesc 'Retain The Live Task Folder In Place Alongside The Archive.' -Default $false
            if ($deleteChoice) {
                $deletedResult = Invoke-AipmCore -AppRoot $Root -Command 'task-delete-folder' -RegistryPath $RegistryPath -ProjectId $ProjectId -TaskId ([string]$TaskRow.task_id)
                if ($deletedResult.Status -eq 'PASS') {
                    Show-Notice -Title 'Task Archived & Folder Removed' -Lines @(
                        ('Archive: ' + [string]$updated.Data.archive_path),
                        ('Checksum: ' + [string]$updated.Data.checksum_path),
                        'Metadata: Metadata.json Verified Inside Archive.',
                        'Live Folder: Removed (All Task Details Preserved In Archive).'
                    ) -Kind Success
                    $unregisterChoice = Show-Confirm -Title 'Remove Task From AIPM Registry?' -Message 'Metadata.json Inside The Archive Holds The Complete Task Record. You Can Restore This Task Later With Import Archived Task From ZIP, Even After Removing It From State-Manifest.json.' -YesLabel 'Remove From Registry' -YesDesc 'Remove The Task Record From AIPM State; The Verified Archive Is Kept.' -NoLabel 'Keep In Registry' -NoDesc 'Keep The Task Listed In AIPM; It Can Still Be Reopened From The Archive.' -Default $false
                    if ($unregisterChoice) {
                        $unregisterResult = Invoke-AipmCore -AppRoot $Root -Command 'task-unregister' -RegistryPath $RegistryPath -ProjectId $ProjectId -TaskId ([string]$TaskRow.task_id)
                        if ($unregisterResult.Status -eq 'PASS') {
                            Show-Notice -Title 'Task Removed From Registry' -Lines @(
                                ('Archive Kept: ' + [string]$updated.Data.archive_path),
                                'Restore Anytime: Task Management > Import Archived Task From ZIP.'
                            ) -Kind Success
                            return
                        }
                        Show-Notice -Title 'Registry Removal Failed' -Lines @([string]$unregisterResult.Reason, 'The Task Remains Registered.') -Kind Warning
                    }
                } else {
                    Show-Notice -Title 'Task Archived But Folder Deletion Failed' -Lines @([string]$deletedResult.Reason) -Kind Warning
                }
            } else {
                Show-Notice -Title 'Task Archived & Folder Kept' -Lines @(
                    ('Archive: ' + [string]$updated.Data.archive_path),
                    ('Checksum: ' + [string]$updated.Data.checksum_path),
                    'Metadata: Metadata.json Created And Verified.',
                    'Live Folder: Retained In Place Alongside The Archive.'
                ) -Kind Success
            }
            continue
        } elseif ($action -eq 'close' -or $action -eq 'reopen') {
            $promptTitle = if ($action -eq 'close') { 'Completion Note' } else { 'Reopen Note' }
            $entered = Read-ValidatedInput -Prompt $promptTitle -Help 'Record The Reason And Current Evidence In The Authoritative Task State.' -Example 'Work Is Complete And Ready For Handoff.' -Default '' -Validate { param($text) if (-not $text.Trim()) { return 'Enter A Note.' }; return $null }
            if (-not $entered) { continue }
            $command = if ($action -eq 'close') { 'task-close' } else { 'task-reopen' }
            $updated = Invoke-AipmCore -AppRoot $Root -Command $command -RegistryPath $RegistryPath -ProjectId $ProjectId -TaskId ([string]$TaskRow.task_id) -Text $entered.Trim()
        } elseif ($action -eq 'checkpoint') {
            $lastAction = Read-ValidatedInput -Prompt 'Last Verified Action' -Help 'State The Most Recent Action Confirmed By Direct Evidence.' -Example 'Reviewed Existing Task Files; No Source Files Changed.' -Default '' -Validate { param($text) if (-not $text.Trim()) { return 'Enter The Last Verified Action.' }; return $null }
            if (-not $lastAction) { continue }
            $nextAction = Read-ValidatedInput -Prompt 'Exact Next Action' -Help 'Describe The Next Concrete Step For The Agent.' -Example 'Inspect The Main Workflow And Record A Short Plan.' -Default '' -Validate { param($text) if (-not $text.Trim()) { return 'Enter The Next Action.' }; return $null }
            if (-not $nextAction) { continue }
            $updated = Invoke-AipmCore -AppRoot $Root -Command 'task-checkpoint' -RegistryPath $RegistryPath -ProjectId $ProjectId -TaskId ([string]$TaskRow.task_id) -LastVerifiedAction $lastAction.Trim() -NextAction $nextAction.Trim()
        } elseif ($action -eq 'plan' -or $action -eq 'report' -or $action -eq 'blocker') {
            $promptTitle = @{ plan='Task Plan'; report='Task Report'; blocker='Blocker Description' }[$action]
            $helpText = @{ plan='Describe The Work Steps For This Task.'; report='Summarize Progress, Outcome, Or Handoff Context.'; blocker='Describe The Obstacle That Needs Attention.' }[$action]
            $entered = Read-ValidatedInput -Prompt $promptTitle -Help $helpText -Example 'Describe The Current Task Context' -Default '' -Validate { param($text) if (-not $text.Trim()) { return 'Enter A Description.' }; return $null }
            if (-not $entered) { continue }
            $command = @{ plan='task-plan'; report='task-report'; blocker='task-blocker-add' }[$action]
            $updated = Invoke-AipmCore -AppRoot $Root -Command $command -RegistryPath $RegistryPath -ProjectId $ProjectId -TaskId ([string]$TaskRow.task_id) -Text $entered.Trim()
        } elseif ($action -eq 'clear') {
            if (-not (Show-Confirm -Title 'Clear Task Blockers?' -Message 'This Updates AIPM Task State Only. Confirm The Recorded Blockers Have Been Resolved.' -YesLabel 'Clear Blockers' -YesDesc 'Remove The Existing Blocker List.' -NoLabel 'Cancel' -NoDesc 'Keep The Blockers.' -Default $false)) { continue }
            $updated = Invoke-AipmCore -AppRoot $Root -Command 'task-blocker-clear' -RegistryPath $RegistryPath -ProjectId $ProjectId -TaskId ([string]$TaskRow.task_id)
        } elseif ($action -eq 'verify') {
            $resultItems = @(
                (New-MenuItem -Label 'Passed' -Desc 'Evidence Supports Successful Completion.' -Value 'PASS' -Icon 'Success'),
                (New-MenuItem -Label 'Failed' -Desc 'Evidence Shows The Check Did Not Pass.' -Value 'FAIL' -Icon 'Warning'),
                (New-MenuItem -Label 'Unverified' -Desc 'No Conclusive Verification Is Available Yet.' -Value 'UNVERIFIED' -Icon 'Progress')
            )
            $verificationResult = Show-Menu -Title 'Verification Result' -Items $resultItems
            if (-not $verificationResult -or $verificationResult -in @('__HELP__','__QUIT__')) { continue }
            $evidence = Read-ValidatedInput -Prompt 'Verification Evidence' -Help 'Record What Was Checked And The Actual Result. AIPM Does Not Run The Check.' -Example 'PowerShell unit suite passed; 12 tests.' -Default '' -Validate { param($text) if (-not $text.Trim()) { return 'Enter The Evidence Or Observation.' }; return $null }
            if (-not $evidence) { continue }
            $updated = Invoke-AipmCore -AppRoot $Root -Command 'task-verify' -RegistryPath $RegistryPath -ProjectId $ProjectId -TaskId ([string]$TaskRow.task_id) -Result ([string]$verificationResult) -Evidence $evidence.Trim()
        } else { continue }
        if ($updated.Status -eq 'PASS') {
            Show-Notice -Title 'Task Updated' -Lines @('AIPM Task State Was Updated Successfully.', 'Project Source Files Were Not Changed.') -Kind Success
            $recordResult = Invoke-AipmCore -AppRoot $Root -Command 'task-read' -RegistryPath $RegistryPath -ProjectId $ProjectId -TaskId ([string]$TaskRow.task_id)
            if ($recordResult.Status -eq 'PASS') { $task = $recordResult.Data.task }
        } else {
            Show-Notice -Title 'Task Update Failed' -Lines @([string]$updated.Reason) -Kind Error
        }
    }
}

function Invoke-AipmStateRecovery {
    param([Parameter(Mandatory)][string]$Root, [Parameter(Mandatory)][string]$RegistryPath, [Parameter(Mandatory)][string]$ProjectId, [string]$FailureReason = 'INVALID_STATE')
    $diagnosis = Invoke-AipmCore -AppRoot $Root -Command 'state-diagnose' -RegistryPath $RegistryPath -ProjectId $ProjectId
    if ($diagnosis.Status -eq 'PASS' -and $diagnosis.Data.repairable) {
        $reconciledItems = if ($diagnosis.Data.reconciled_tasks -and @($diagnosis.Data.reconciled_tasks).Count -gt 0) {
            @($diagnosis.Data.reconciled_tasks)
        } else {
            @($diagnosis.Data.untracked_tasks)
        }
        $taskList = if ($reconciledItems.Count -gt 0) { $reconciledItems -join ', ' } else { [string]$diagnosis.Data.pending_task_id }
        Show-Notice -Title 'Task State Problem Diagnosed' -Lines @(
            ('Cause: ' + [string]$diagnosis.Data.cause),
            ('Pending Task: ' + [string]$diagnosis.Data.pending_task_id + ' at revision ' + [string]$diagnosis.Data.pending_revision),
            ('Task Records To Preserve And Reconcile: ' + $taskList),
            ('Repair: ' + [string]$diagnosis.Data.remedy),
            'AIPM Has Not Changed The Project State Yet.'
        ) -Kind Warning
        $confirmed = Show-Confirm -Title 'Repair The Pending Task State?' -Message 'AIPM Will Save A Hash-Verified Backup First, Preserve The Listed Task Records In An Explicit Core History Event, Then Resume The Pending Task Creation.' -YesLabel 'Back Up And Repair' -YesDesc 'Apply The Validated Repair And Resume The Pending Task.' -NoLabel 'Cancel' -NoDesc 'Leave All State Files Unchanged.' -Default $false
        if (-not $confirmed) { return $false }
        $repaired = Invoke-AipmCore -AppRoot $Root -Command 'state-repair' -RegistryPath $RegistryPath -ProjectId $ProjectId -ConfirmRepair
        if ($repaired.Status -eq 'PASS') {
            Show-Notice -Title 'Task State Repaired' -Lines @(
                ('Verified Backup: ' + [string]$repaired.Data.backup),
                ('Recovered Task Records: ' + (@($repaired.Data.recovered_tasks) -join ', ')),
                ('Pending Task Created: ' + [string]$repaired.Data.created_task_id),
                ('Committed Revision: ' + [string]$repaired.Data.revision),
                'AIPM Verified The Event History And State Manifest After Repair.'
            ) -Kind Success
            return $true
        }
        $repairLines = @('Reason: ' + [string]$repaired.Reason, 'No repair success was reported.')
        if ($repaired.Data -and $repaired.Data.backup) { $repairLines += 'Safety Backup: ' + [string]$repaired.Data.backup }
        Show-Notice -Title 'Task State Repair Did Not Complete' -Lines $repairLines -Kind Error
        return $false
    }
    $cause = if ($diagnosis.Data -and $diagnosis.Data.cause) { [string]$diagnosis.Data.cause } else { 'AIPM could not confirm the internal state failure.' }
    $remedy = if ($diagnosis.Data -and $diagnosis.Data.remedy) { [string]$diagnosis.Data.remedy } else { 'Keep the state unchanged and restore a verified Shared Project State backup or request an integrity review.' }
    Show-Notice -Title 'Task State Needs Manual Review' -Lines @(
        ('Error Code: ' + $FailureReason),
        ('Diagnosis: ' + $cause),
        ('Recommended Action: ' + $remedy)
    ) -Kind Error
    return $false
}

function Invoke-AipmTaskManagement {
    param([Parameter(Mandatory)][string]$Root, [Parameter(Mandatory)][string]$RegistryPath)
    $currentPath = [System.IO.Path]::GetFullPath($RegistryPath)
    while ($true) {
        # Always re-read the selected registry before task operations; never rely on a stale dashboard snapshot.
        $inventory = Get-AipmRegistryEntries -Root $Root -RegistryPath $currentPath
        if ($inventory.Status -ne 'PASS') {
            Show-Notice -Title 'Project Registry Is Unavailable' -Lines @([string]$inventory.Reason, 'Resolve The Registry Before Managing Tasks.') -Kind Error
            return $currentPath
        }
        if ($inventory.Projects.Count -eq 0) {
            $emptyItems = @(
                (New-MenuItem -Label 'Register A Project First' -Desc 'Task Records Must Belong To A Registered Project.' -Value 'register' -Icon 'Project'),
                (New-MenuItem -Label 'Back' -Desc 'Return To The Main Dashboard.' -Value 'back' -Icon 'Exit')
            )
            $emptyChoice = Show-Menu -Title 'No Projects Are Registered' -Description 'Register A Project Before Creating Or Managing Tasks.' -Items $emptyItems
            if ($emptyChoice -eq '__HELP__') {
                [void](Show-AipmPage -Title 'Task Management Help' -Lines @(
                    'Register A Project First Before Creating Or Managing Tasks.',
                    'New Tasks Are Stored Under The Project Shared-Project-State-Manager.'
                ))
                continue
            }
            if ($emptyChoice -ne 'register') { return $currentPath }
            $currentPath = Invoke-AipmRegistryManagement -Root $Root -RegistryPath $currentPath
            continue
        }
        $projectItems = @($inventory.Projects | ForEach-Object {
            New-MenuItem -Label ([string]$_.alias) -Desc ([string]$_.root_path) -Value ([string]$_.project_id) -Icon 'Project'
        })
        $projectItems += New-MenuItem -Label 'Back' -Desc 'Return To The Main Dashboard.' -Value 'back' -Icon 'Exit'
        $selectedProjectId = Show-Menu -Title 'Select Registered Project' -Description 'Choose The Project Whose Task State You Want To Manage.' -Items $projectItems
        if (-not $selectedProjectId -or $selectedProjectId -in @('back','__QUIT__')) { return $currentPath }
        if ($selectedProjectId -eq '__HELP__') {
            [void](Show-AipmPage -Title 'Task Management Help' -Lines @(
                'Select A Registered Project Before Managing Its Tasks.',
                'New Tasks Are Stored Under The Project Shared-Project-State-Manager.',
                'Add Existing Work Folder Creates Task Context Only; It Does Not Move Or Copy Files.',
                'Task Names Are Descriptive And Do Not Need Numbered Labels.'
            ))
            continue
        }
        $project = @($inventory.Projects | Where-Object { [string]$_.project_id -eq [string]$selectedProjectId }) | Select-Object -First 1
        if (-not $project) { continue }
        while ($true) {
            $taskResult = Invoke-AipmCore -AppRoot $Root -Command 'task-list' -RegistryPath $currentPath -ProjectId ([string]$selectedProjectId)
            if ($taskResult.Status -ne 'PASS') {
                if (Invoke-AipmStateRecovery -Root $Root -RegistryPath $currentPath -ProjectId ([string]$selectedProjectId) -FailureReason ([string]$taskResult.Reason)) { continue }
                break
            }
            $taskItems = @(
                (New-MenuItem -Label 'Create New Task' -Desc 'Create A Task Record In AIPM State For This Project.' -Value 'create' -Icon 'Yes'),
                (New-MenuItem -Label 'Add Existing Work Folder' -Desc 'Create A Task Record Referencing A Folder; Keep Its Files In Place.' -Value 'folder' -Icon 'Project'),
                (New-MenuItem -Label 'Open Existing Task' -Desc 'Review Or Update An Existing Core-Managed Task.' -Value 'open' -Icon 'Task'),
                (New-MenuItem -Label 'Import Archived Task From ZIP' -Desc 'Restore And Re-Register A Task From Its Archive ZIP Using Metadata.json.' -Value 'import' -Icon 'Project'),
                (New-MenuItem -Label 'Back To Project Selection' -Desc 'Choose Another Registered Project.' -Value 'back' -Icon 'Exit')
            )
            $taskChoice = Show-Menu -Title ('Tasks: ' + [string]$project.alias) -Description ('Managed State: ' + [string]$project.root_path) -Items $taskItems
            if (-not $taskChoice -or $taskChoice -in @('back','__QUIT__')) { break }
            if ($taskChoice -eq '__HELP__') {
                [void](Show-AipmPage -Title 'Task Management Help' -Lines @(
                    'Select A Registered Project Before Managing Its Tasks.',
                    'New Tasks Are Stored Under The Project Shared-Project-State-Manager.',
                    'Add Existing Work Folder Creates Task Context Only; It Does Not Move Or Copy Files.',
                    'Task Names Are Descriptive And Do Not Need Numbered Labels.'
                ))
                continue
            }
            if ($taskChoice -eq 'create' -or $taskChoice -eq 'folder') {
                $scopePrefix = ''
                $folderPath = ''
                $isExistingTaskFolder = $false
                $defaultTitle = ''
                if ($taskChoice -eq 'folder') {
                    $folderPath = Read-ValidatedInput -Prompt 'Existing Work Folder Path' -Help 'Enter A Full Path To An Existing Folder Inside The Selected Project. Its Files Will Stay In Place.' -Example ([string]$project.root_path) -Default '' -Validate {
                        param($text)
                        $candidateText = $text.Trim().Trim('"')
                        try { $candidate = [System.IO.Path]::GetFullPath($candidateText) } catch { return 'Enter A Valid Full Folder Path.' }
                        if (-not (Test-Path -LiteralPath $candidate -PathType Container)) { return 'The Existing Work Folder Must Already Exist.' }
                        $base = [System.IO.Path]::GetFullPath([string]$project.root_path).TrimEnd([char[]]@('\','/')) + [System.IO.Path]::DirectorySeparatorChar
                        if (-not $candidate.StartsWith($base, [System.StringComparison]::OrdinalIgnoreCase)) { return 'Choose A Folder Inside The Selected Registered Project.' }
                        $stateBase = (Join-Path ([System.IO.Path]::GetFullPath([string]$project.root_path)) 'Shared-Project-State-Manager').TrimEnd([char[]]@('\','/'))
                        # Agent-created task folders inside Shared-Project-State-Manager are valid; only the state root and its Tasks container are rejected.
                        $trimmedCandidate = $candidate.TrimEnd([char[]]@('\','/'))
                        if ($trimmedCandidate.Equals($stateBase, [System.StringComparison]::OrdinalIgnoreCase) -or $trimmedCandidate.Equals((Join-Path $stateBase 'Tasks'), [System.StringComparison]::OrdinalIgnoreCase)) {
                            return 'Choose A Specific Work Folder, Not The Shared-Project-State-Manager Or Its Tasks Root.'
                        }
                        return $null
                    }
                    if (-not $folderPath) { continue }
                    $folderPath = [System.IO.Path]::GetFullPath($folderPath.Trim().Trim('"')).TrimEnd([char[]]@('\','/'))
                    $tasksContainer = (Join-Path (Join-Path ([System.IO.Path]::GetFullPath([string]$project.root_path)) 'Shared-Project-State-Manager') 'Tasks').TrimEnd([char[]]@('\','/'))
                    $parentCandidate = (Split-Path -Parent $folderPath).TrimEnd([char[]]@('\','/'))
                    if ($parentCandidate.Equals($tasksContainer, [System.StringComparison]::OrdinalIgnoreCase)) {
                        $isExistingTaskFolder = $true
                        $leafName = [System.IO.Path]::GetFileName($folderPath)
                        $defaultTitle = ($leafName -replace '^Task-(?:\d{4}-\d{2}-\d{2}-)?', '' -replace '-[0-9a-fA-F]{12}$', '' -replace '[-_]', ' ').Trim()
                        if (-not $defaultTitle) { $defaultTitle = $leafName }
                    } else {
                        $defaultTitle = ''
                        $scopePrefix = 'Existing Work Folder: ' + $folderPath + "`nFiles Remain In Their Original Location."
                    }
                }
                if ($isExistingTaskFolder) {
                    $created = Invoke-AipmCore -AppRoot $Root -Command 'task-import-work-folder' -RegistryPath $currentPath -ProjectId ([string]$selectedProjectId) -Source $folderPath
                    if ($created.Status -eq 'PASS') {
                        $createdId = [System.IO.Path]::GetFileName([string]$created.Data.task_path)
                        $createdTitle = [string]$created.Data.task.title
                        Show-Notice -Title 'Existing Task Folder Registered' -Lines @(
                            ('Task: ' + $createdTitle),
                            ('Task ID: ' + $createdId),
                            'The Existing Task Folder Was Registered In Place Without Creating A New Folder.'
                        ) -Kind Success
                    } else {
                        Show-Notice -Title 'Task Registration Failed' -Lines @([string]$created.Reason) -Kind Error
                    }
                    continue
                }
                $title = Read-ValidatedInput -Prompt 'Task Name' -Help 'Use Any Clear, Descriptive Name; Numbered Task Names Are Optional.' -Example 'Organize Existing Work Files' -Default $defaultTitle -Validate {
                    param($text)
                    $trimmed = $text.Trim().Trim('"')
                    if (-not $trimmed) { return 'Enter A Task Name.' }
                    if ($trimmed -match '^[A-Za-z]:[\\/]' -or $trimmed -match '[\\/]') { return 'Enter A Descriptive Task Name, Not A Folder Path.' }
                    return $null
                }
                if (-not $title) { continue }
                $scopeHelp = if ($scopePrefix) { 'Describe The Goal Or Next Work For This Existing Folder.' } else { 'Describe The Goal, Boundaries, And Expected Outcome For This Task.' }
                $scope = Read-ValidatedInput -Prompt 'Task Scope And Goal' -Help $scopeHelp -Example 'Describe The Expected Outcome And Boundaries' -Default '' -Validate { param($text) if (-not $text.Trim()) { return 'Enter The Task Scope And Goal.' }; return $null }
                if (-not $scope) { continue }
                $finalScope = if ($scopePrefix) { $scopePrefix + "`nTask Goal: " + $scope.Trim() } else { $scope.Trim() }
                $created = if ($taskChoice -eq 'folder') {
                    Invoke-AipmCore -AppRoot $Root -Command 'task-import-work-folder' -RegistryPath $currentPath -ProjectId ([string]$selectedProjectId) -Title $title.Trim() -Scope $finalScope -Source $folderPath
                } else {
                    Invoke-AipmCore -AppRoot $Root -Command 'task-create' -RegistryPath $currentPath -ProjectId ([string]$selectedProjectId) -Title $title.Trim() -Scope $finalScope
                }
                if ($created.Status -eq 'PASS') {
                    $createdId = [System.IO.Path]::GetFileName([string]$created.Data.task_path)
                    Show-Notice -Title 'Task Created' -Lines @(('Task: ' + $title.Trim()), ('Task ID: ' + $createdId), 'The Task Record Was Saved In AIPM Project State. No Project Files Were Moved Or Edited.') -Kind Success
                } elseif (-not (Invoke-AipmStateRecovery -Root $Root -RegistryPath $currentPath -ProjectId ([string]$selectedProjectId) -FailureReason ([string]$created.Reason))) {
                    Show-Notice -Title 'Task Creation Failed' -Lines @('The requested task was not confirmed as committed.', 'Review the state diagnosis above before retrying.') -Kind Error
                }
                continue
            }
            if ($taskChoice -eq 'import') {
                $zipPath = Read-ValidatedInput -Prompt 'Archive ZIP File Path' -Help 'Enter The Full Path To A Task Archive ZIP Created By AIPM, From Any Folder Or Drive.' -Example 'D:\Archives\Task-2026-10-23-Example-0123456789ab.zip' -Default '' -Validate {
                    param($text)
                    $candidateText = $text.Trim().Trim('"')
                    try { $candidate = [System.IO.Path]::GetFullPath($candidateText) } catch { return 'Enter A Valid Full File Path.' }
                    if (-not (Test-Path -LiteralPath $candidate -PathType Leaf)) { return 'The ZIP File Must Already Exist.' }
                    if ([System.IO.Path]::GetExtension($candidate).ToLowerInvariant() -ne '.zip') { return 'Choose A .zip Task Archive.' }
                    return $null
                }
                if (-not $zipPath) { continue }
                $imported = Invoke-AipmCore -AppRoot $Root -Command 'task-import-archive' -RegistryPath $currentPath -ProjectId ([string]$selectedProjectId) -Source ($zipPath.Trim().Trim('"'))
                if ($imported.Status -eq 'PASS') {
                    Show-Notice -Title 'Archived Task Imported' -Lines @(
                        ('Task: ' + [string]$imported.Data.title),
                        ('Task ID: ' + [string]$imported.Data.task_id),
                        ('Status: ' + [string]$imported.Data.task_status),
                        ('Archive Copy: ' + [string]$imported.Data.archive_path),
                        'The Task Was Re-Registered And Its Live Folder Was Restored From Metadata.json And The Archive.'
                    ) -Kind Success
                } else { Show-Notice -Title 'Archive Import Failed' -Lines @([string]$imported.Reason, 'Nothing Was Registered Or Changed.') -Kind Error }
                continue
            }
            if ($taskChoice -eq 'open') {
                $rows = @($taskResult.Data.tasks)
                if ($rows.Count -eq 0) { Show-Notice -Title 'No Tasks Yet' -Lines @('Create A New Task Or Add An Existing Work Folder First.') -Kind Info; continue }
                $existingItems = @($rows | ForEach-Object {
                    New-MenuItem -Label ([string]$_.title) -Desc (([string]$_.status) + ' | ' + [string]$_.task_id) -Value ([string]$_.task_id) -Icon 'Task'
                })
                $existingItems += New-MenuItem -Label 'Back' -Desc 'Return To Task Management.' -Value 'back' -Icon 'Exit'
                $selectedTaskId = Show-Menu -Title 'Open Existing Task' -Items $existingItems
                if (-not $selectedTaskId -or $selectedTaskId -in @('back','__QUIT__')) { continue }
                if ($selectedTaskId -eq '__HELP__') {
                    [void](Show-AipmPage -Title 'Open Existing Task Help' -Lines @(
                        'Choose A Task To Review Its Status, Plan, Reports, Next-Agent Handoff, Or Supporting Files.',
                        'Task Records Are Stored Under The Project Shared-Project-State-Manager/Tasks/.'
                    ))
                    continue
                }
                $selectedTask = @($rows | Where-Object { [string]$_.task_id -eq [string]$selectedTaskId }) | Select-Object -First 1
                if ($selectedTask) { Show-AipmTaskRecord -Root $Root -RegistryPath $currentPath -ProjectId ([string]$selectedProjectId) -ProjectRoot ([string]$project.root_path) -TaskRow $selectedTask }
            }
        }
    }
}

function ConvertTo-AipmPageRows {
    param([string[]]$Lines, [int]$Width)
    $indent = '  '
    $limit = [Math]::Max(12, $Width - $indent.Length - 3)
    $rows = New-Object System.Collections.Generic.List[string]
    foreach ($line in $Lines) {
        $remaining = [string]$line
        if (-not $remaining) { $rows.Add(''); continue }
        while ($remaining.Length -gt $limit) {
            $cut = $remaining.LastIndexOf(' ', $limit)
            if ($cut -lt 1) { $cut = $limit }
            $rows.Add($indent + $remaining.Substring(0, $cut).TrimEnd())
            $remaining = $remaining.Substring($cut).TrimStart()
        }
        if ($remaining) { $rows.Add($indent + $remaining) }
    }
    return $rows.ToArray()
}

function Show-AipmPage {
    param([string]$Title, [string[]]$Lines, [switch]$Searchable)
    $pageNumber = 0
    while ($true) {
        $size = Get-TerminalSize
        $displayRows = @(ConvertTo-AipmPageRows -Lines $Lines -Width $size.Width)
        $footerTemplate = if ($Searchable) { 'Page 1 of 1 | Up/Down Or PageUp/PageDown Navigate | Enter/Esc Back | / Search | ? Help | Q Exit' } else { 'Page 1 of 1 | Up/Down Or PageUp/PageDown Navigate | Enter/Esc Back | ? Help | Q Exit' }
        $footerRows = @(ConvertTo-AipmPageRows -Lines @($footerTemplate) -Width $size.Width).Count
        # Reserve the product shell, title/rule, blank separator, footer, and last terminal row.
        $pageCapacity = [Math]::Max(1, $size.Height - 1 - 4 - 2 - 1 - $footerRows)
        $pageCount = [Math]::Max(1, [int][Math]::Ceiling($displayRows.Count / [double]$pageCapacity))
        if ($pageNumber -ge $pageCount) { $pageNumber = $pageCount - 1 }
        $start = $pageNumber * $pageCapacity
        $end = [Math]::Min($displayRows.Count, $start + $pageCapacity)

        Clear-Ui
        $productShell = Get-TuiProductShell
        if ($productShell.Version) { Write-AipmProductHeader -Version $productShell.Version -Status $productShell.Status -Width $size.Width }
        Write-UiLine ('  ' + $Title) 'Title'
        Write-TuiRule -Width $size.Width
        for ($i = $start; $i -lt $end; $i++) {
            $line = [string]$displayRows[$i]
            $role = 'Normal'
            if ($line -match '(?i)\b(Ready|Passed|Complete)\b') { $role = 'Success' }
            elseif ($line -match '(?i)\b(Failed|Error)\b') { $role = 'Error' }
            elseif ($line -match '(?i)\b(Blocked|Warning)\b') { $role = 'Warning' }
            elseif ($line -match '(?i)\b(Unverified|Unknown|Not Registered)\b') { $role = 'Dim' }
            Write-UiLine $line $role
        }
        Write-UiLine ''
        if ($pageCount -gt 1) {
            $footer = 'Page ' + ($pageNumber + 1) + ' of ' + $pageCount + ' | Up/Down Or PageUp/PageDown Navigate | Enter/Esc Back'
            if ($Searchable) { $footer += ' | / Search' }
            $footer += ' | ? Help | Q Exit'
            foreach ($row in (ConvertTo-AipmPageRows -Lines @($footer) -Width $size.Width)) { Write-UiLine $row 'Dim' }
        } else {
            Write-Ui 'Enter / Esc ' 'Key'; Write-Ui 'Back  |  ' 'Dim'
            if ($Searchable) { Write-Ui '/ Search  |  ' 'Key' }
            Write-UiLine '? / F1 Help  |  Q Request Exit' 'Dim'
        }
        Complete-UiFrame
        $key = Read-AppKey
        if ($key.Name -in @('Enter','Esc')) { return $null }
        if ($key.Name -in @('Down','PageDown') -and $pageNumber -lt ($pageCount - 1)) { $pageNumber++; continue }
        if ($key.Name -in @('Up','PageUp') -and $pageNumber -gt 0) { $pageNumber--; continue }
        if ($key.Name -eq 'Help' -or ($key.Name -eq 'Char' -and $key.Char -eq '?')) { return '__HELP__' }
        if ($Searchable -and $key.Name -eq 'Char' -and $key.Char -eq '/') { return '__SEARCH__' }
        if ($key.Name -eq 'Char' -and $key.Char -match '^[qQ]$') { return '__QUIT__' }
    }
}

function Start-TuiApp {
    [CmdletBinding()]
    param([Parameter(Mandatory)][string]$Root, [string]$RegistryPath = '')
    $RegistryPath = Resolve-AipmRegistryPath -Root $Root -RequestedPath $RegistryPath
    if (-not $RegistryPath) { return }
    $script:AppRoot = $Root
    Apply-AppDesign -Root $Root
    $version = Get-AppVersion $Root
    $session = Get-AipmSessionSnapshot -Root $Root -RegistryPath $RegistryPath
    $refreshNotice = ''
    $quit = $false
    while (-not $quit) {
        $lines = $null
        if ($session.Status -eq 'PASS') {
            $core = $session.Dashboard
            $catalog = $session.Catalog
            $hosts = $session.Hosts
            $data = $core.Data
        } else {
            $core = [pscustomobject]@{ Status='BLOCKED'; Reason=$session.Reason; Data=[pscustomobject]@{ status='BLOCKED'; registry_status='UNVERIFIED'; projects=@() } }
            $catalog = [pscustomobject]@{ Data=$null }; $hosts = [pscustomobject]@{ Data=$null }
            $data = $core.Data
        }
        $items = @(
            (New-MenuItem -Label 'Projects' -Desc 'Review Registered Projects And Their Verified State.' -Value 'Projects' -Icon 'Project'),
            (New-MenuItem -Label 'Tasks' -Desc 'Select A Registered Project, Then Create Or Manage Its Tasks.' -Value 'Tasks' -Icon 'Task'),
            (New-MenuItem -Label 'Phases' -Desc 'Review Active Phase; Missing History Stays Unverified.' -Value 'Phases' -Icon 'Progress'),
            (New-MenuItem -Label 'Tests & Evidence' -Desc 'Separate Task Evidence From Test Runs.' -Value 'Tests & Evidence' -Icon 'Success' -IconRole 'Success'),
            (New-MenuItem -Label 'Agents & Handoffs' -Desc 'Show Only Session Evidence Exposed By A Host.' -Value 'Agents & Handoffs' -Icon 'Agent'),
            (New-MenuItem -Label 'Timeline' -Desc 'Review Verified Update Metadata, Not Invented Events.' -Value 'Timeline' -Icon 'Handoff'),
            (New-MenuItem -Label 'Skills & Plugins' -Desc 'Review Approved Skills And The Unverified Project-Agent Bridge Package.' -Value 'Skills & Plugins' -Icon 'Item'),
            (New-MenuItem -Label 'Assistant Console' -Desc 'Offline Evidence View; No AI Session Is Implied.' -Value 'Assistant Console' -Icon 'Agent'),
            (New-MenuItem -Label 'Registry Management' -Desc 'Connect Existing Registries, Register Projects, And Back Up Or Restore The Registry.' -Value 'Registry Management' -Icon 'Settings'),
            (New-MenuItem -Label 'Settings' -Desc 'Change UI Preferences Only.' -Value 'Settings' -Icon 'Settings'),
            (New-MenuItem -Label 'Help' -Desc 'Keyboard, Evidence And Read-Only Behavior.' -Value 'Help' -Icon 'About'),
            (New-MenuItem -Label 'Refresh' -Desc 'Read The Latest Core State Again.' -Value 'Refresh' -Icon 'Run'),
            (New-MenuItem -Label 'About' -Desc 'Version And Runtime Details.' -Value 'About' -Icon 'About'),
            (New-MenuItem -Label 'Exit' -Desc 'Close AIPM; No Background Session Is Started.' -Value 'Exit' -Icon 'Exit')
        )
        $coreText = if ($core.Status -eq 'PASS') { 'Core Ready' } else { 'Core Blocked: ' + $core.Reason }
        $mode = Get-AipmViewMode
        $design = Get-AppDesign -Root $Root
        $menuPreset = $design.preset; $menuNavigation = $design.navigation
        if ($mode -eq 'Command Palette') { $menuPreset = 'command-palette'; $menuNavigation = 'Search' }
        elseif ($mode -eq 'Assistant Console') { $menuPreset = 'assistant-console' }
        Set-TuiColorStyle -Mode $design.colors -Accent (Get-TuiPreset -Id $menuPreset).Accent
        $registryStatus = [string](Get-AipmField $data 'registry_status' 'UNVERIFIED')
        $statusText = $coreText + ' | Registry ' + $registryStatus + ' | ' + $items.Count + ' Options'
        $headerStatus = if ($refreshNotice) { $coreText + ' | ' + $refreshNotice } else { $statusText }
        Set-TuiProductShell -Version $version -Status $headerStatus
        $choice = Show-Menu -Title $mode -Items $items -Preset $menuPreset -Navigation $menuNavigation
        if ($choice -eq '__QUIT__') {
            if (Show-Confirm -Title 'Exit AI Project Manager?' -Message 'No project data will be changed.' -YesLabel 'Exit AIPM' -NoLabel 'Stay Here' -Default $false) { $quit = $true }
            continue
        }
        if ($choice -eq '__HELP__') { $section = 'Help' }
        elseif ($null -eq $choice) {
            $confirmExit = Show-Confirm -Title 'Exit AI Project Manager?' -Message 'You Pressed Esc At The Main Dashboard. Exiting Closes AIPM; No Project Data Will Be Changed.' -YesLabel 'Exit AIPM' -YesDesc 'Close AIPM And Return To The PowerShell Window.' -NoLabel 'Stay Here' -NoDesc 'Return To The Task Dashboard.' -Default $false
            if ($confirmExit) { $quit = $true }
            continue
        }
        elseif ($choice -eq 'Exit') { $quit = $true; continue }
        elseif ($choice -eq 'Refresh') {
            $refresh = Refresh-AipmSessionSnapshot -Root $Root -RegistryPath $RegistryPath -CurrentSnapshot $session
            $session = $refresh.Snapshot
            if ($refresh.Status -eq 'PASS') { $refreshNotice = '' }
            elseif ($refresh.Preserved) { $refreshNotice = 'Refresh Failed: ' + $refresh.Reason + ' | Last Snapshot Preserved' }
            else { $refreshNotice = 'Refresh Failed: ' + $refresh.Reason + ' | No Snapshot Available' }
            continue
        }
        elseif ($choice -eq 'Registry Management') {
            $previousRegistryPath = $RegistryPath
            $RegistryPath = Invoke-AipmRegistryManagement -Root $Root -RegistryPath $RegistryPath
            if ($RegistryPath -ne $previousRegistryPath) {
                $session = Get-AipmSessionSnapshot -Root $Root -RegistryPath $RegistryPath
                $refreshNotice = ''
            }
            continue
        }
        elseif ($choice -eq 'Tasks') {
            $RegistryPath = Invoke-AipmTaskManagement -Root $Root -RegistryPath $RegistryPath
            $session = Get-AipmSessionSnapshot -Root $Root -RegistryPath $RegistryPath
            $refreshNotice = ''
            continue
        }
        else { $section = [string]$choice }

        if ($section -eq 'Settings') {
            $settingsItems = @(
                (New-MenuItem -Label 'Change View Mode' -Desc 'Choose Task Dashboard, Command Palette Or Assistant Console.' -Value 'Mode' -Icon 'Settings'),
                (New-MenuItem -Label 'Customize Interface' -Desc 'Choose One Of Twenty Layouts And Interaction Preferences.' -Value 'Customize' -Icon 'Settings'),
                (New-MenuItem -Label 'View Current Settings' -Desc 'Show Per-User UI Settings And Runtime Information.' -Value 'View' -Icon 'About'),
                (New-MenuItem -Label 'Back' -Desc 'Return To The Task Dashboard.' -Value 'Back' -Icon 'Exit')
            )
            $settingsChoice = Show-Menu -Title 'Settings' -Items $settingsItems
            if ($settingsChoice -eq 'Mode') {
                $modeItems = @(
                    (New-MenuItem -Label 'Task Dashboard' -Desc 'Portfolio-First Overview; The Default View.' -Value 'Task Dashboard' -Icon 'Project'),
                    (New-MenuItem -Label 'Command Palette' -Desc 'Searchable Action List; Type To Filter.' -Value 'Command Palette' -Icon 'Run'),
                    (New-MenuItem -Label 'Assistant Console' -Desc 'Read-Only Evidence View; No AI Session Is Connected.' -Value 'Assistant Console' -Icon 'Agent')
                )
                $newMode = Show-Menu -Title 'Select View Mode' -Items $modeItems
                if (-not $newMode -or $newMode -in @('__HELP__','__QUIT__')) { continue }
                if (Set-UserSetting -Name 'view_mode' -Value $newMode) { continue }
                Show-Notice -Title 'View Mode Was Not Saved' -Lines @('UI Preferences Could Not Be Written. No Project State Was Changed.') -Kind Error
                continue
            }
            if ($settingsChoice -eq 'Customize') { Invoke-DesignWizard -Root $Root; continue }
            if ($settingsChoice -eq '__HELP__') { $section = 'Help' }
            elseif ($settingsChoice -eq '__QUIT__') {
                if (Show-Confirm -Title 'Exit AI Project Manager?' -Message 'No project data will be changed.' -YesLabel 'Exit AIPM' -NoLabel 'Stay Here' -Default $false) { $quit = $true }
                continue
            }
            elseif ($settingsChoice -ne 'View') { continue }
            else { $section = 'Settings' }
        }
        if ($section -eq 'Skills & Plugins') {
            $pageResult = Show-AipmCapabilityLibrary -Catalog $catalog.Data -Version $version -Status $headerStatus
        } else {
            if (-not $lines) { $lines = @(Get-AipmPageLines -Section $section -Dashboard $data -Catalog $catalog.Data -HostMatrix $hosts.Data -Version $version) }
            $pageResult = Show-AipmPage -Title $section -Lines $lines
        }
        if ($pageResult -eq '__QUIT__') {
            if (Show-Confirm -Title 'Exit AI Project Manager?' -Message 'No project data will be changed.' -YesLabel 'Exit AIPM' -NoLabel 'Stay Here' -Default $false) { $quit = $true }
        } elseif ($pageResult -eq '__HELP__' -and $section -ne 'Help') {
            $helpLines = @(Get-AipmPageLines -Section 'Help' -Dashboard $data -Catalog $catalog.Data -HostMatrix $hosts.Data -Version $version)
            $helpResult = Show-AipmPage -Title 'Help' -Lines $helpLines
            if ($helpResult -eq '__QUIT__' -and (Show-Confirm -Title 'Exit AI Project Manager?' -Message 'No project data will be changed.' -YesLabel 'Exit AIPM' -NoLabel 'Stay Here' -Default $false)) { $quit = $true }
        }
    }
}

Export-ModuleMember -Function Get-AppVersion, Get-AipmViewMode, Test-PersonName, Get-AppDesign, Apply-AppDesign, Invoke-DesignWizard, Start-TuiApp, Get-AipmProjectSummary, ConvertTo-AipmDisplayStatus, Format-AipmEvidenceCoverage, Get-AipmSessionSnapshot, Refresh-AipmSessionSnapshot, Get-AipmCapabilityLibraryRows, Show-AipmCapabilityLibrary, Get-AipmPageLines, Show-AipmPage
