# Menu.psm1 - selectable navigation, layouts and descriptions, with a classic compatibility preset.
Set-StrictMode -Version 2.0
$script:MenuDesign = @{ Navigation = 'Hybrid'; Preset = 'classic-numbered'; Descriptions = 'Muted' }

function Format-MenuNumber { param([int]$Number) return ([string]$Number).PadLeft(2, '0') }
function Resolve-NumberInput {
    param([string]$Buffer, [int]$Count)
    if ([string]::IsNullOrEmpty($Buffer) -or $Buffer -notmatch '^\d+$') { return @{ State = 'Invalid'; Index = -1 } }
    $cands = @()
    for ($n = 1; $n -le $Count; $n++) { if ((Format-MenuNumber $n).StartsWith($Buffer)) { $cands += $n } }
    if ($cands.Count -eq 0) {
        if ($Buffer.Length -le 9) { $v = [int]$Buffer; if ($v -ge 1 -and $v -le $Count) { return @{ State = 'Select'; Index = $v - 1 } } }
        return @{ State = 'Invalid'; Index = -1 }
    }
    $exact = @($cands | Where-Object { (Format-MenuNumber $_) -eq $Buffer })
    if ($exact.Count -eq 1 -and $cands.Count -eq 1) { return @{ State = 'Select'; Index = $exact[0] - 1 } }
    return @{ State = 'Wait'; Index = -1 }
}
function Set-TuiMenuStyle {
    param([ValidateSet('Arrows','Numbers','Hybrid','Search')][string]$Navigation = 'Hybrid',
          [string]$Preset = 'classic-numbered',
          [ValidateSet('Muted','Shade','Inline','Panel','Off')][string]$Descriptions = 'Muted')
    [void](Get-TuiPreset -Id $Preset)
    $script:MenuDesign = @{ Navigation = $Navigation; Preset = $Preset; Descriptions = $Descriptions }
}
function Get-TuiMenuStyle { return $script:MenuDesign.Clone() }
function New-MenuItem {
    param([Parameter(Mandatory)][string]$Label, [string]$Desc = '', [string]$Value = '', [string]$Icon = 'Item', [string]$IconRole = 'Info', [bool]$Enabled = $true, [string]$Reason = '')
    if (-not $Value) { $Value = $Label }
    return @{ Label = $Label; Desc = $Desc; Value = $Value; Icon = $Icon; IconRole = $IconRole; Enabled = $Enabled; Reason = $Reason }
}
function Write-MenuWrapped {
    param([string]$Text, [int]$Width, [string]$Role = 'Dim', [string]$Indent = '       ')
    $limit = [Math]::Max(12, $Width - $Indent.Length - 3)
    $remaining = $Text
    while ($remaining.Length -gt $limit) {
        $cut = $remaining.LastIndexOf(' ', $limit)
        if ($cut -lt 1) { $cut = $limit }
        Write-UiLine ($Indent + $remaining.Substring(0, $cut).TrimEnd()) $Role
        $remaining = $remaining.Substring($cut).TrimStart()
    }
    if ($remaining) { Write-UiLine ($Indent + $remaining) $Role }
}
function Limit-MenuText { param([string]$Text, [int]$Width) if ($Text.Length -le $Width) { return $Text }; if ($Width -lt 4) { return $Text.Substring(0,[Math]::Max(0,$Width)) }; return ($Text.Substring(0,$Width-3) + '...') }
function Show-Menu {
    param([Parameter(Mandatory)][string]$Title, [string]$Description = '', [Parameter(Mandatory)][object[]]$Items, [int]$Default = 0,
          [ValidateSet('','Arrows','Numbers','Hybrid','Search')][string]$Navigation = '',
          [string]$Preset = '',
          [ValidateSet('','Muted','Shade','Inline','Panel','Off')][string]$DescriptionStyle = '')
    $items = @($Items)
    if ($items.Count -eq 0) { throw 'Show-Menu needs at least one item.' }
    if (-not $Navigation) { $Navigation = $script:MenuDesign.Navigation }
    if (-not $Preset) { $Preset = $script:MenuDesign.Preset }
    if (-not $DescriptionStyle) { $DescriptionStyle = $script:MenuDesign.Descriptions }
    $profile = Get-TuiPreset -Id $Preset
    $sel = [math]::Min([math]::Max($Default, 0), $items.Count - 1)
    $buffer = ''; $query = ''; $searchActive = ($Navigation -eq 'Search')
    while ($true) {
        $visible = @()
        for ($i = 0; $i -lt $items.Count; $i++) {
            if (-not $searchActive -or -not $query -or
                $items[$i].Label.IndexOf($query,[System.StringComparison]::OrdinalIgnoreCase) -ge 0 -or
                $items[$i].Desc.IndexOf($query,[System.StringComparison]::OrdinalIgnoreCase) -ge 0) { $visible += $i }
        }
        if ($sel -ge $visible.Count) { $sel = [math]::Max(0,$visible.Count-1) }
        Clear-Ui
        switch ($profile.Layout) {
            'Classic' { Write-UiLine ((Get-Icon 'Run') + '  ' + $Title) 'Title' }
            'Assistant' { Write-UiLine ('  >  ' + $Title + '  |  Ready') 'Title' }
            'Minimal' { Write-UiLine ('  ' + $Title) 'Title' }
            'Palette' { Write-UiLine ('  /  ' + $Title + '  /') 'Title' }
            'Retro' { Write-UiLine ('  [ ' + $Title + ' ]') 'Title' }
            'Wizard' { Write-UiLine ('  Step  /  ' + $Title) 'Title' }
            'Workbench' { Write-UiLine ('  Workbench  /  ' + $Title) 'Title'; Write-UiLine '  Actions                                  Details' 'Dim' }
            'Dashboard' { Write-UiLine ('  Dashboard  /  ' + $Title) 'Title'; Write-UiLine ('  Available Actions: ' + $items.Count) 'Heading' }
            'Split' { Write-UiLine ('  Workspace  /  ' + $Title) 'Title'; Write-UiLine '  Navigation                               Context' 'Dim' }
            'Monitor' { Write-UiLine ('  Activity  /  ' + $Title) 'Title'; Write-UiLine ('  ' + $items.Count + ' Actions Available') 'Info' }
            'Compact' { Write-UiLine ('  ' + $Title + '  /  Actions') 'Title' }
            'Editorial' { Write-UiLine ('  ' + $Title) 'Title'; Write-UiLine '  Clear, Focused Tasks' 'Dim' }
            'Neon' { Write-UiLine ('  [*]  ' + $Title + '  [*]') 'Title' }
            'Slate' { Write-UiLine ('  ' + $Title + '  /  Workspace') 'Title' }
            'Paper' { Write-UiLine ('  ' + $Title) 'Title'; Write-UiLine '  Explore Options' 'Dim' }
            'Operations' { Write-UiLine ('  Operations  ::  ' + $Title) 'Title'; Write-UiLine ('  Commands: ' + $items.Count) 'Info' }
            'Explorer' { Write-UiLine ('  /  ' + $Title + '  /') 'Title'; Write-UiLine '  Browse Available Actions' 'Dim' }
            'Media' { Write-UiLine ('  Workbench  ::  ' + $Title) 'Title' }
            'Diagnostic' { Write-UiLine ('  Check  /  ' + $Title) 'Title'; Write-UiLine '  Review And Select An Action' 'Dim' }
            'Onboarding' { Write-UiLine ('  Get Started  /  ' + $Title) 'Title'; Write-UiLine '  Select An Option To Continue' 'Dim' }
            default { Write-UiLine ('  ' + $profile.Name + '  /  ' + $Title) 'Title' }
        }
        if ($profile.Density -ne 'Compact') { Write-UiLine ('  ' + ('-' * [math]::Min(48,(Get-TerminalSize).Width-5))) 'Dim' }
        if ($Description) { Write-MenuWrapped -Text $Description -Width (Get-TerminalSize).Width -Role 'Dim' -Indent '  ' }
        if ($searchActive) { Write-UiLine ('  Search: ' + $query + '_') 'Key' }
        if ($profile.Density -eq 'Spacious') { Write-UiLine '' }
        if ($visible.Count -eq 0) { Write-UiLine '  No Matching Actions. Backspace To Broaden The Search.' 'Dim' }
        for ($pos = 0; $pos -lt $visible.Count; $pos++) {
            $it = $items[$visible[$pos]]
            $role = 'Normal'; $marker = ' '
            if ($pos -eq $sel) { $role = 'Selected'; $marker = '>' }
            if (-not $it.Enabled) { $role = 'Dim' }
            $d = $it.Desc; if (-not $it.Enabled -and $it.Reason) { $d = $it.Reason }
            $ico = Get-Icon $it.Icon
            $prefix = ' ' + $marker + ' '
            if ($Navigation -in @('Numbers','Hybrid') -and -not $searchActive) { $prefix += (Format-MenuNumber ($visible[$pos] + 1)) + '  ' }
            if ($profile.Layout -eq 'Explorer') { $prefix += '|-- ' }
            if ($profile.Layout -eq 'Diagnostic') { $prefix += '[ ] ' }
            $isSplit = (($profile.Layout -in @('Split','Workbench')) -and (Get-TerminalSize).Width -ge 90)
            if ($isSplit) {
                $left = ($prefix + $it.Label)
                $left = Limit-MenuText -Text $left -Width 36
                if ($ico) { Write-Ui $prefix $role; Write-Ui $ico $it.IconRole; Write-Ui '  ' $role }
                Write-Ui (Limit-MenuText -Text $it.Label -Width 32).PadRight(34) $role
                Write-Ui '| ' 'Dim'
                if ($DescriptionStyle -ne 'Off') { Write-UiLine $d 'Dim' } else { Write-UiLine '' }
            } else {
                Write-Ui $prefix $role
                if ($ico) { Write-Ui $ico $it.IconRole; Write-Ui '  ' $role }
                $label = Limit-MenuText -Text $it.Label -Width ([Math]::Max(8, (Get-TerminalSize).Width - $prefix.Length - [string]$ico.Length - 8))
                Write-Ui $label $role
                if ($DescriptionStyle -eq 'Inline' -and $d) { Write-Ui ('  -  ' + $d) 'Dim' }
                Write-UiLine ''
            }
            if (-not $isSplit -and $DescriptionStyle -in @('Muted','Shade','Panel') -and $d) {
                $descRole = $(if ($DescriptionStyle -eq 'Shade') { 'Description' } else { 'Dim' })
                Write-MenuWrapped -Text $d -Width (Get-TerminalSize).Width -Role $descRole
            }
            if ($profile.Density -eq 'Spacious') { Write-UiLine '' }
        }
        if ($DescriptionStyle -eq 'Panel' -and $visible.Count -gt 0) {
            $it = $items[$visible[$sel]]
            $d = $it.Desc; if (-not $it.Enabled -and $it.Reason) { $d = $it.Reason }
            if ($d) { Write-MenuWrapped -Text ('Details: ' + $d) -Width (Get-TerminalSize).Width -Role 'Dim' -Indent '  ' }
        }
        Write-UiLine ''
        if ($Navigation -ne 'Numbers') { Write-Ui 'Up/Down ' 'Key'; Write-Ui 'Navigate  ' 'Dim' }
        Write-Ui 'Enter ' 'Key'; Write-Ui 'Select  ' 'Dim'
        if ($Navigation -in @('Numbers','Hybrid') -and -not $searchActive) { Write-Ui '00-99 ' 'Key'; Write-Ui 'Type A Number  ' 'Dim' }
        if ($searchActive) { Write-Ui 'Type ' 'Key'; Write-Ui 'Search  ' 'Dim' }
        Write-Ui '/ ' 'Key'; Write-Ui 'Search  ' 'Dim'; Write-Ui '?/F1 ' 'Key'; Write-Ui 'Help  ' 'Dim'; Write-UiLine 'Esc Back' 'Dim'
        Complete-UiFrame
        $k = Read-AppKey
        switch ($k.Name) {
            'CtrlC' { throw (New-Object System.OperationCanceledException('Quit')) }
            'Esc' { if ($searchActive -and $query) { $query = ''; $searchActive = $false; $sel = 0 } else { return $null } }
            'Help' { return '__HELP__' }
            'F1' { return '__HELP__' }
            'Up' { if ($Navigation -ne 'Numbers' -and $visible.Count -gt 0) { $sel = ($sel - 1 + $visible.Count) % $visible.Count }; $buffer = '' }
            'Down' { if ($Navigation -ne 'Numbers' -and $visible.Count -gt 0) { $sel = ($sel + 1) % $visible.Count }; $buffer = '' }
            'Enter' {
                if ($Navigation -in @('Numbers','Hybrid') -and $buffer) {
                    $r = Resolve-NumberInput $buffer $items.Count
                    if ($r.State -eq 'Select') { $sel = $r.Index }
                    elseif ($buffer -match '^\d+$' -and [int]$buffer -ge 1 -and [int]$buffer -le $items.Count) { $sel = [int]$buffer - 1 }
                    $buffer = ''
                    if ($sel -ge 0 -and $sel -lt $items.Count -and $items[$sel].Enabled) { return $items[$sel].Value }
                }
                elseif ($visible.Count -gt 0 -and $items[$visible[$sel]].Enabled) { return $items[$visible[$sel]].Value }
            }
            'Char' {
                if ($k.Char -eq '?') { return '__HELP__' }
                elseif ($k.Char -eq '/' -and -not $searchActive) { $searchActive = $true; $query = ''; $sel = 0 }
                elseif ($k.Char -match '^[qQ]$' -and -not $searchActive -and $Navigation -ne 'Search') { return '__QUIT__' }
                elseif ($searchActive) { $query += $k.Char; $sel = 0 }
                elseif ($Navigation -in @('Numbers','Hybrid') -and $k.Char -match '^\d$') {
                    $buffer += $k.Char
                    $r = Resolve-NumberInput $buffer $items.Count
                    if ($r.State -eq 'Select') { $buffer = ''; if ($items[$r.Index].Enabled) { return $items[$r.Index].Value } }
                    elseif ($r.State -eq 'Invalid') { $buffer = '' }
                }
            }
            'Backspace' {
                if ($Navigation -eq 'Search' -and $query.Length -gt 0) { $query = $query.Substring(0,$query.Length-1); $sel = 0 }
                elseif ($buffer.Length -gt 0) { $buffer = $buffer.Substring(0,$buffer.Length-1) }
            }
        }
    }
}
Export-ModuleMember -Function Format-MenuNumber, Resolve-NumberInput, Set-TuiMenuStyle, Get-TuiMenuStyle, New-MenuItem, Show-Menu, Write-MenuWrapped, Limit-MenuText
