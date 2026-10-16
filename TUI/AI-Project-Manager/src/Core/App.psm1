# App.psm1 - the application: main menu loop and the actions. Business logic lives in Core modules, never in the TUI modules.
Set-StrictMode -Version 2.0

function Get-AipmField {
    param($Object, [string]$Name, $Default = $null)
    if ($null -eq $Object) { return $Default }
    $property = $Object.PSObject.Properties[$Name]
    if ($property) { return $property.Value }
    return $Default
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
    if (-not $preset) { return }
    $choices = @(
        (New-MenuItem -Label 'Arrow Keys + Enter' -Desc 'No Numeric Prefixes.' -Value 'Arrows'),
        (New-MenuItem -Label 'Numbered Choices' -Desc 'Type A Menu Item Number.' -Value 'Numbers'),
        (New-MenuItem -Label 'Numbers And Arrows' -Desc 'Both Keyboard Selection Modes.' -Value 'Hybrid'),
        (New-MenuItem -Label 'Search Actions' -Desc 'Type Words And Use Arrows Or Enter.' -Value 'Search')
    )
    $navigation = Show-Menu -Title 'Navigation Style' -Items $choices -Navigation Arrows
    if (-not $navigation) { return }
    $choices = @(
        (New-MenuItem -Label 'Automatic Icon Detection' -Desc 'Choose The Safest Icons For The Terminal.' -Value 'Auto'),
        (New-MenuItem -Label 'Emoji' -Desc 'Colorful Icons In Modern Terminals.' -Value 'Emoji'),
        (New-MenuItem -Label 'Simple Symbols' -Desc 'Lightweight Unicode Symbols.' -Value 'Symbol'),
        (New-MenuItem -Label 'ASCII' -Desc 'Portable text icons.' -Value 'Ascii'),
        (New-MenuItem -Label 'No Icons' -Desc 'Clean Text-Only Choices.' -Value 'None')
    )
    $icons = Show-Menu -Title 'Icon Style' -Items $choices -Navigation Arrows
    if (-not $icons) { return }
    $choices = @(
        (New-MenuItem -Label 'Automatic' -Desc 'Adapt To Terminal Support.' -Value 'Auto'),
        (New-MenuItem -Label 'Rich Accents' -Desc 'Strong Accent Headings And Selections.' -Value 'Full'),
        (New-MenuItem -Label 'Subtle Accents' -Desc 'Restrained Color Hierarchy.' -Value 'Subtle'),
        (New-MenuItem -Label 'No Colors' -Desc 'Monochrome Interface.' -Value 'None')
    )
    $colors = Show-Menu -Title 'Color Style' -Items $choices -Navigation Arrows
    if (-not $colors) { return }
    $choices = @(
        (New-MenuItem -Label 'Muted And Indented' -Desc 'Subdued Explanation Under Each Option.' -Value 'Muted'),
        (New-MenuItem -Label 'Subtle Shading' -Desc 'Indented Explanation With Faint Shading When Supported.' -Value 'Shade'),
        (New-MenuItem -Label 'Inline' -Desc 'Description On The Same Line.' -Value 'Inline'),
        (New-MenuItem -Label 'Details Panel' -Desc 'Explain The Currently Highlighted Option.' -Value 'Panel')
    )
    $descriptions = Show-Menu -Title 'Option Descriptions' -Items $choices -Navigation Arrows
    if (-not $descriptions) { return }
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
                $lines.Add(('Skills: ' + [string]$c.skill_count + ' | First-Party: ' + (@($c.first_party_skills) -join ', ')))
                $lines.Add('Imported Skills Keep Their Source License; AIPM Apache-2.0 Does Not Relicense Them.')
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
            $lines.Add('Up/Down: Move Selection | Enter: Open Or Select | Esc: Back')
            $lines.Add('Type A Number: Select Directly | /: Search Actions | ?: Help | F1: Help | Q: Request Exit')
            $lines.Add('All Portfolio, Task, Phase, Evidence, Skill And Plugin Screens Are Read-Only.')
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

function Show-AipmPage {
    param([string]$Title, [string[]]$Lines)
    while ($true) {
        Clear-Ui
        Write-UiLine ('  ' + $Title) 'Title'
        Write-UiLine ('  ' + ('-' * [Math]::Min(48, (Get-TerminalSize).Width - 5))) 'Dim'
        foreach ($line in $Lines) {
            $role = 'Normal'
            if ($line -match '(?i)\b(Ready|Passed|Complete)\b') { $role = 'Success' }
            elseif ($line -match '(?i)\b(Failed|Error)\b') { $role = 'Error' }
            elseif ($line -match '(?i)\b(Blocked|Warning)\b') { $role = 'Warning' }
            elseif ($line -match '(?i)\b(Unverified|Unknown|Not Registered)\b') { $role = 'Dim' }
            Write-MenuWrapped -Text $line -Width (Get-TerminalSize).Width -Role $role -Indent '  '
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

function Start-TuiApp {
    [CmdletBinding()]
    param([Parameter(Mandatory)][string]$Root, [string]$RegistryPath = '')
    $script:AppRoot = $Root
    Apply-AppDesign -Root $Root
    $version = Get-AppVersion $Root
    $quit = $false
    while (-not $quit) {
        $lines = $null
        $dependency = Get-AipmDependencyStatus -AppRoot $Root
        if ($dependency.Status -eq 'PASS') {
            $core = Invoke-AipmCore -AppRoot $Root -Command dashboard -RegistryPath $RegistryPath
            $catalog = Invoke-AipmCore -AppRoot $Root -Command catalog
            $hosts = Invoke-AipmCore -AppRoot $Root -Command host-capabilities
        } else {
            $core = [pscustomobject]@{ Status='BLOCKED'; Reason=$dependency.Reason; Data=[pscustomobject]@{ status='BLOCKED'; registry_status='UNVERIFIED'; projects=@() } }
            $catalog = [pscustomobject]@{ Data=$null }; $hosts = [pscustomobject]@{ Data=$null }
        }
        $data = $core.Data
        $items = @()
        $projects = @(Get-AipmField $data 'projects' @())
        foreach ($project in $projects) {
            $summary = Get-AipmProjectSummary -Project $project
            $iconRole = if ($summary.Status -eq 'Ready') { 'Success' } else { 'Warning' }
            $items += New-MenuItem -Label $summary.Name -Desc ($summary.Status + ' | Phase ' + $summary.Phase + ' | Progress ' + $summary.Progress) -Value ('project:' + $summary.ProjectId) -Icon 'Project' -IconRole $iconRole
        }
        $items += @(
            (New-MenuItem -Label 'Projects' -Desc 'Review Registered Projects And Their Verified State.' -Value 'Projects' -Icon 'Project'),
            (New-MenuItem -Label 'Tasks' -Desc 'Read Current Task State And Evidence.' -Value 'Tasks' -Icon 'Task'),
            (New-MenuItem -Label 'Phases' -Desc 'Review Active Phase; Missing History Stays Unverified.' -Value 'Phases' -Icon 'Progress'),
            (New-MenuItem -Label 'Tests & Evidence' -Desc 'Separate Task Evidence From Test Runs.' -Value 'Tests & Evidence' -Icon 'Success' -IconRole 'Success'),
            (New-MenuItem -Label 'Agents & Handoffs' -Desc 'Show Only Session Evidence Exposed By A Host.' -Value 'Agents & Handoffs' -Icon 'Agent'),
            (New-MenuItem -Label 'Timeline' -Desc 'Review Verified Update Metadata, Not Invented Events.' -Value 'Timeline' -Icon 'Handoff'),
            (New-MenuItem -Label 'Skills & Plugins' -Desc 'Review Source Licenses And Unverified Package Status.' -Value 'Skills & Plugins' -Icon 'Item'),
            (New-MenuItem -Label 'Assistant Console' -Desc 'Offline Evidence View; No AI Session Is Implied.' -Value 'Assistant Console' -Icon 'Agent'),
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
        $choice = Show-Menu -Title $mode -Description $statusText -Items $items -Preset $menuPreset -Navigation $menuNavigation
        if ($choice -eq '__QUIT__') {
            if (Show-Confirm -Title 'Exit AI Project Manager?' -Message 'No project data will be changed.' -YesLabel 'Exit AIPM' -NoLabel 'Stay Here' -Default $false) { $quit = $true }
            continue
        }
        if ($choice -eq '__HELP__') { $section = 'Help' }
        elseif ($choice -eq 'Exit' -or $null -eq $choice) { $quit = $true; continue }
        elseif ($choice -eq 'Refresh') { continue }
        elseif ($choice -like 'project:*') {
            $id = $choice.Substring(8)
            $project = @($projects | Where-Object { $_.project_id -eq $id }) | Select-Object -First 1
            if ($project) { $lines = @(Get-AipmPageLines -Section 'Projects' -Dashboard ([pscustomobject]@{projects=@($project)}) -Catalog $catalog.Data -HostMatrix $hosts.Data -Version $version) }
            else { $lines = @('Project Data Changed Before It Could Be Read. Refresh The Dashboard.') }
            $section = 'Project Details'
        } else { $section = [string]$choice }

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
                if ($newMode -and (Set-UserSetting -Name 'view_mode' -Value $newMode)) { continue }
                if ($newMode) { Show-Notice -Title 'View Mode Was Not Saved' -Lines @('UI Preferences Could Not Be Written. No Project State Was Changed.') -Kind Error }
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
        if (-not $lines) { $lines = @(Get-AipmPageLines -Section $section -Dashboard $data -Catalog $catalog.Data -HostMatrix $hosts.Data -Version $version) }
        $pageResult = Show-AipmPage -Title $section -Lines $lines
        if ($pageResult -eq '__QUIT__') {
            if (Show-Confirm -Title 'Exit AI Project Manager?' -Message 'No project data will be changed.' -YesLabel 'Exit AIPM' -NoLabel 'Stay Here' -Default $false) { $quit = $true }
        } elseif ($pageResult -eq '__HELP__' -and $section -ne 'Help') {
            $helpLines = @(Get-AipmPageLines -Section 'Help' -Dashboard $data -Catalog $catalog.Data -HostMatrix $hosts.Data -Version $version)
            $helpResult = Show-AipmPage -Title 'Help' -Lines $helpLines
            if ($helpResult -eq '__QUIT__' -and (Show-Confirm -Title 'Exit AI Project Manager?' -Message 'No project data will be changed.' -YesLabel 'Exit AIPM' -NoLabel 'Stay Here' -Default $false)) { $quit = $true }
        }
    }
}

Export-ModuleMember -Function Get-AppVersion, Get-AipmViewMode, Test-PersonName, Get-AppDesign, Apply-AppDesign, Invoke-DesignWizard, Start-TuiApp, Get-AipmProjectSummary, ConvertTo-AipmDisplayStatus, Format-AipmEvidenceCoverage, Get-AipmPageLines, Show-AipmPage
