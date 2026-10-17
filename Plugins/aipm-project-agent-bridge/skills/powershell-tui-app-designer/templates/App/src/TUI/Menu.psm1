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
    param([Parameter(Mandatory)][string]$Label, [string]$Desc = '', [string]$Value = '', [string]$Icon = 'Item', [bool]$Enabled = $true, [string]$Reason = '')
    if (-not $Value) { $Value = $Label }
    return @{ Label = $Label; Desc = $Desc; Value = $Value; Icon = $Icon; Enabled = $Enabled; Reason = $Reason }
}
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
    $buffer = ''; $query = ''
    while ($true) {
        $visible = @()
        for ($i = 0; $i -lt $items.Count; $i++) {
            if ($Navigation -ne 'Search' -or -not $query -or
                $items[$i].Label.IndexOf($query,[System.StringComparison]::OrdinalIgnoreCase) -ge 0 -or
                $items[$i].Desc.IndexOf($query,[System.StringComparison]::OrdinalIgnoreCase) -ge 0) { $visible += $i }
        }
        if ($sel -ge $visible.Count) { $sel = [math]::Max(0,$visible.Count-1) }
        Clear-Ui
        switch ($profile.Layout) {
            'Classic' { Write-UiLine ((Get-Icon 'Run') + '  ' + $Title) 'Title' }
            'Assistant' { Write-UiLine ('  >  ' + $Title.ToUpperInvariant() + '    |    ready') 'Title' }
            'Minimal' { Write-UiLine ('  ' + $Title.ToUpperInvariant()) 'Title' }
            'Palette' { Write-UiLine ('  /  ' + $Title + '  /') 'Title' }
            'Retro' { Write-UiLine ('  [ ' + $Title.ToUpperInvariant() + ' ]') 'Title' }
            'Wizard' { Write-UiLine ('  STEP  /  ' + $Title) 'Title' }
            'Workbench' { Write-UiLine ('  WORKBENCH   /   ' + $Title) 'Title'; Write-UiLine '  ACTIONS                                  DETAILS' 'Dim' }
            'Dashboard' { Write-UiLine ('  DASHBOARD   /   ' + $Title) 'Title'; Write-UiLine ('  Available actions: ' + $items.Count) 'Heading' }
            'Split' { Write-UiLine ('  WORKSPACE   /   ' + $Title) 'Title'; Write-UiLine '  NAVIGATION                               CONTEXT' 'Dim' }
            'Monitor' { Write-UiLine ('  ACTIVITY   /   ' + $Title) 'Title'; Write-UiLine ('  ' + $items.Count + ' actions available') 'Info' }
            'Compact' { Write-UiLine ('  ' + $Title + '  /  actions') 'Title' }
            'Editorial' { Write-UiLine ('  ' + $Title.ToUpperInvariant()) 'Title'; Write-UiLine '  Clear, focused tasks' 'Dim' }
            'Neon' { Write-UiLine ('  [*]  ' + $Title.ToUpperInvariant() + '  [*]') 'Title' }
            'Slate' { Write-UiLine ('  ' + $Title + '  /  Workspace') 'Title' }
            'Paper' { Write-UiLine ('  ' + $Title) 'Title'; Write-UiLine '  Explore options' 'Dim' }
            'Operations' { Write-UiLine ('  OPERATIONS  ::  ' + $Title.ToUpperInvariant()) 'Title'; Write-UiLine ('  Commands: ' + $items.Count) 'Info' }
            'Explorer' { Write-UiLine ('  /  ' + $Title + '  /') 'Title'; Write-UiLine '  Browse available actions' 'Dim' }
            'Media' { Write-UiLine ('  WORKBENCH  ::  ' + $Title) 'Title' }
            'Diagnostic' { Write-UiLine ('  CHECK  /  ' + $Title) 'Title'; Write-UiLine '  Review and select an action' 'Dim' }
            'Onboarding' { Write-UiLine ('  GET STARTED  /  ' + $Title) 'Title'; Write-UiLine '  Select an option to continue' 'Dim' }
            default { Write-UiLine ('  ' + $profile.Name.ToUpperInvariant() + '  /  ' + $Title) 'Title' }
        }
        if ($profile.Density -ne 'Compact') { Write-UiLine ('  ' + ('-' * [math]::Min(48,(Get-TerminalSize).Width-5))) 'Dim' }
        if ($Description) { Write-UiLine ('  ' + $Description) 'Dim' }
        if ($Navigation -eq 'Search') { Write-UiLine ('  Search: ' + $query + '_') 'Key' }
        if ($profile.Density -eq 'Spacious') { Write-UiLine '' }
        if ($visible.Count -eq 0) { Write-UiLine '  No matching actions. Backspace to broaden the search.' 'Dim' }
        for ($pos = 0; $pos -lt $visible.Count; $pos++) {
            $it = $items[$visible[$pos]]
            $role = 'Normal'; $marker = ' '
            if ($pos -eq $sel) { $role = 'Selected'; $marker = '>' }
            if (-not $it.Enabled) { $role = 'Dim' }
            $d = $it.Desc; if (-not $it.Enabled -and $it.Reason) { $d = $it.Reason }
            $ico = Get-Icon $it.Icon
            $prefix = ' ' + $marker + ' '
            if ($Navigation -in @('Numbers','Hybrid')) { $prefix += (Format-MenuNumber ($visible[$pos] + 1)) + '  ' }
            if ($ico) { $prefix += $ico + '  ' }
            if ($profile.Layout -eq 'Explorer') { $prefix += '|-- ' }
            if ($profile.Layout -eq 'Diagnostic') { $prefix += '[ ] ' }
            $isSplit = (($profile.Layout -in @('Split','Workbench')) -and (Get-TerminalSize).Width -ge 90)
            if ($isSplit) {
                $left = ($prefix + $it.Label)
                if ($left.Length -gt 36) { $left = $left.Substring(0,33) + '...' }
                Write-Ui ($left.PadRight(39) + '| ') $role
                if ($DescriptionStyle -ne 'Off') { Write-UiLine $d 'Dim' } else { Write-UiLine '' }
            } else {
                Write-Ui $prefix $role
                Write-Ui $it.Label $role
                if ($DescriptionStyle -eq 'Inline' -and $d) { Write-Ui ('  -  ' + $d) 'Dim' }
                Write-UiLine ''
            }
            if (-not $isSplit -and $DescriptionStyle -in @('Muted','Shade') -and $d) {
                $descRole = $(if ($DescriptionStyle -eq 'Shade') { 'Description' } else { 'Dim' })
                Write-UiLine ('       ' + $d) $descRole
            }
            if ($profile.Density -eq 'Spacious') { Write-UiLine '' }
        }
        if ($DescriptionStyle -eq 'Panel' -and $visible.Count -gt 0) {
            $it = $items[$visible[$sel]]
            $d = $it.Desc; if (-not $it.Enabled -and $it.Reason) { $d = $it.Reason }
            if ($d) { Write-UiLine ('  Details: ' + $d) 'Dim' }
        }
        Write-UiLine ''
        if ($Navigation -ne 'Numbers') { Write-Ui 'Up/Down ' 'Key'; Write-Ui 'Navigate  ' 'Dim' }
        Write-Ui 'Enter ' 'Key'; Write-Ui 'Select  ' 'Dim'
        if ($Navigation -in @('Numbers','Hybrid')) { Write-Ui '00-99 ' 'Key'; Write-Ui 'Type a number  ' 'Dim' }
        if ($Navigation -eq 'Search') { Write-Ui 'Type ' 'Key'; Write-Ui 'Search  ' 'Dim' }
        Write-Ui 'Esc ' 'Key'; Write-UiLine 'Back' 'Dim'
        Complete-UiFrame
        $k = Read-AppKey
        switch ($k.Name) {
            'CtrlC' { throw (New-Object System.OperationCanceledException('Quit')) }
            'Esc' { return $null }
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
                if ($Navigation -eq 'Search') { $query += $k.Char; $sel = 0 }
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
Export-ModuleMember -Function Format-MenuNumber, Resolve-NumberInput, Set-TuiMenuStyle, Get-TuiMenuStyle, New-MenuItem, Show-Menu
