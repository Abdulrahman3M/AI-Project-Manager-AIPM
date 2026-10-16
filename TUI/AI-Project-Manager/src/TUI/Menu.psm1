# Menu.psm1 - selectable navigation, layouts and descriptions, with a classic compatibility preset.
Set-StrictMode -Version 2.0
$script:MenuDesign = @{ Navigation = 'Hybrid'; Preset = 'classic-numbered'; Descriptions = 'Muted' }
$script:ProductShell = @{ Version = ''; Status = '' }
$script:MenuGeometryCache = @{ Key = ''; Metrics = $null; Hits = 0; Misses = 0 }

function Set-TuiProductShell {
    param([string]$Version = '', [string]$Status = '')
    $script:ProductShell = @{ Version = $Version; Status = $Status }
}
function Get-TuiProductShell { return $script:ProductShell.Clone() }
function Write-TuiRule {
    param([int]$Width)
    $width = [Math]::Min(240, [Math]::Max(20, $Width))
    Write-UiLine ('+' + ('-' * ($width - 2)) + '+') 'Frame'
}
function Write-TuiTable {
    param([string[]]$Headers, [string[]]$Fields, [object[]]$Rows, [int[]]$ColumnWidths, [int]$Width)
    if (-not $Headers -or $Headers.Count -eq 0 -or $Headers.Count -ne $Fields.Count -or $Headers.Count -ne $ColumnWidths.Count) {
        throw 'A TUI table requires matching headers, fields, and column widths.'
    }
    $tableWidth = 1
    foreach ($columnWidth in $ColumnWidths) {
        if ($columnWidth -lt 1) { throw 'TUI table columns must have a positive width.' }
        $tableWidth += $columnWidth + 3
    }
    if ($tableWidth -gt $Width) { throw ('TUI table width {0} exceeds the terminal width {1}.' -f $tableWidth,$Width) }
    $border = '+'
    foreach ($columnWidth in $ColumnWidths) { $border += ('-' * ($columnWidth + 2)) + '+' }
    Write-UiLine $border 'Frame'
    $allRows = @([pscustomobject]@{ Values = $Headers; Role = 'Heading' })
    foreach ($row in $Rows) {
        $cells = @()
        for ($index = 0; $index -lt $Fields.Count; $index++) {
            $value = ''
            if ($row -is [System.Collections.IDictionary]) { $value = [string]$row[$Fields[$index]] }
            elseif ($row -and $row.PSObject.Properties[$Fields[$index]]) { $value = [string]$row.PSObject.Properties[$Fields[$index]].Value }
            $cells += $value
        }
        $allRows += [pscustomobject]@{ Values = $cells; Role = 'Normal' }
    }
    foreach ($row in $allRows) {
        $line = '|'
        for ($index = 0; $index -lt $ColumnWidths.Count; $index++) {
            $cell = Limit-MenuText -Text ([string]$row.Values[$index]) -Width $ColumnWidths[$index]
            $line += ' ' + $cell.PadRight($ColumnWidths[$index]) + ' |'
        }
        Write-UiLine $line $row.Role
    }
    Write-UiLine $border 'Frame'
}
function Write-AipmProductHeader {
    param([string]$Version, [string]$Status, [int]$Width)
    $width = [Math]::Min(240, [Math]::Max(20, $Width))
    $innerWidth = $width - 4
    $product = 'AI Project Manager'
    $versionText = if ($Version) { 'v' + $Version } else { '' }
    $titleLength = $product.Length + [int]([bool]$versionText) + $versionText.Length
    if ($titleLength -gt $innerWidth) {
        $product = 'AIPM'
        $titleLength = $product.Length + [int]([bool]$versionText) + $versionText.Length
    }
    if ($titleLength -gt $innerWidth) {
        $versionText = Limit-MenuText -Text $versionText -Width ([Math]::Max(0, $innerWidth - $product.Length - 1))
        $titleLength = $product.Length + [int]([bool]$versionText) + $versionText.Length
    }
    $titlePadding = [Math]::Max(0, $innerWidth - $titleLength)
    $leftTitlePadding = [int][Math]::Floor($titlePadding / 2.0)
    Write-TuiRule -Width $width
    Write-Ui '| ' 'Frame'
    Write-Ui (' ' * $leftTitlePadding) 'Frame'
    Write-Ui $product 'Title'
    if ($versionText) { Write-Ui ' ' 'Frame'; Write-Ui $versionText 'Info' }
    Write-Ui (' ' * ($titlePadding - $leftTitlePadding)) 'Frame'
    Write-UiLine ' |' 'Frame'
    if ($width -lt 34) {
        Write-TuiRule -Width $width
        return
    }
    $statusText = [string]$Status
    if ($statusText.Length -gt $innerWidth) {
        $statusText = $statusText.Substring(0, [Math]::Max(0, $innerWidth - 3)) + '...'
    }
    $statusPadding = [Math]::Max(0, $innerWidth - $statusText.Length)
    $leftStatusPadding = [int][Math]::Floor($statusPadding / 2.0)
    Write-Ui '| ' 'Frame'
    Write-Ui (' ' * $leftStatusPadding) 'Frame'
    Write-Ui $statusText 'Dim'
    Write-Ui (' ' * ($statusPadding - $leftStatusPadding)) 'Frame'
    Write-UiLine ' |' 'Frame'
    Write-TuiRule -Width $width
}

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
function Measure-MenuWrappedLineCount {
    param([string]$Text, [int]$Width, [string]$Indent = '       ')
    if (-not $Text) { return 0 }
    $limit = [Math]::Max(12, $Width - $Indent.Length - 3)
    $remaining = $Text; $count = 0
    while ($remaining.Length -gt $limit) {
        $cut = $remaining.LastIndexOf(' ', $limit)
        if ($cut -lt 1) { $cut = $limit }
        $count++
        $remaining = $remaining.Substring($cut).TrimStart()
    }
    if ($remaining) { $count++ }
    return $count
}
function Get-MenuItemRowCount {
    param($Item, [string]$Layout, [string]$Density, [string]$DescriptionStyle, [int]$Width)
    $split = (($Layout -in @('Split','Workbench')) -and $Width -ge 90)
    $rows = 1
    if (-not $split -and $DescriptionStyle -in @('Muted','Shade','Panel')) {
        $rows += Measure-MenuWrappedLineCount -Text ([string]$Item.Desc) -Width $Width -Indent '       '
    }
    if ($Density -eq 'Spacious') { $rows++ }
    return [int]$rows
}
function Get-MenuLayoutMetrics {
    param([object[]]$Items, [string]$Layout, [string]$Density, [string]$DescriptionStyle, [int]$Width, [int]$Height)
    $metricItems = @()
    foreach ($item in $Items) {
        $metricItems += [ordered]@{
            Label = [string]$item.Label
            Desc = [string]$item.Desc
            Enabled = [bool]$item.Enabled
            Reason = [string]$item.Reason
        }
    }
    $key = ConvertTo-Json -InputObject ([ordered]@{
        Layout = $Layout
        Density = $Density
        DescriptionStyle = $DescriptionStyle
        Width = $Width
        Height = $Height
        Items = @($metricItems)
    }) -Depth 8 -Compress
    if ($script:MenuGeometryCache.Metrics -and $script:MenuGeometryCache.Key -ceq $key) {
        $script:MenuGeometryCache.Hits++
        return $script:MenuGeometryCache.Metrics
    }
    $lineCosts = @()
    foreach ($item in $Items) {
        $measureItem = $item
        if (-not $item.Enabled -and $item.Reason) { $measureItem = @{ Desc = $item.Reason } }
        $lineCosts += (Get-MenuItemRowCount -Item $measureItem -Layout $Layout -Density $Density -DescriptionStyle $DescriptionStyle -Width $Width)
    }
    $totalRows = 0
    foreach ($cost in $lineCosts) { $totalRows += $cost }
    $metrics = [pscustomobject]@{
        LineCosts = [int[]]$lineCosts
        TotalRows = [int]$totalRows
        Width = $Width
        Height = $Height
        Layout = $Layout
        Density = $Density
        DescriptionStyle = $DescriptionStyle
        ItemCount = $Items.Count
    }
    $script:MenuGeometryCache.Key = $key
    $script:MenuGeometryCache.Metrics = $metrics
    $script:MenuGeometryCache.Misses++
    return $metrics
}
function Get-MenuLayoutCacheStats {
    return [pscustomobject]@{ Hits = $script:MenuGeometryCache.Hits; Misses = $script:MenuGeometryCache.Misses }
}
function Get-MenuViewportRange {
    param([int[]]$LineCosts, [int]$Selected, [int]$AvailableLines)
    if (-not $LineCosts -or $LineCosts.Count -eq 0) {
        return [pscustomobject]@{ Start = 0; End = -1; Rows = 0; SelectedFits = $false }
    }
    $selected = [Math]::Min([Math]::Max(0, $Selected), $LineCosts.Count - 1)
    $budget = [Math]::Max(0, $AvailableLines)
    $selectedCost = [Math]::Max(1, $LineCosts[$selected])
    if ($selectedCost -gt $budget) {
        return [pscustomobject]@{ Start = $selected; End = $selected; Rows = $selectedCost; SelectedFits = $false }
    }
    $first = $selected; $last = $selected; $used = $selectedCost
    for ($i = $selected - 1; $i -ge 0; $i--) {
        $cost = [Math]::Max(1, $LineCosts[$i])
        if (($used + $cost) -gt $budget) { break }
        $used += $cost; $first = $i
    }
    for ($i = $selected + 1; $i -lt $LineCosts.Count; $i++) {
        $cost = [Math]::Max(1, $LineCosts[$i])
        if (($used + $cost) -gt $budget) { break }
        $used += $cost; $last = $i
    }
    return [pscustomobject]@{ Start = $first; End = $last; Rows = $used; SelectedFits = $true }
}
function Write-MenuFooter {
    param([string]$Navigation, [bool]$SearchActive, [bool]$SearchHasQuery, [int]$Width)
    $canQuit = (-not $SearchActive -and $Navigation -ne 'Search')
    if ($Width -lt 34) {
        $line1 = if ($SearchActive) { '  Type Search Enter' }
                 elseif ($Navigation -eq 'Numbers') { '  00-99 Enter' }
                 else { '  Up/Down Enter' }
        $line2 = if ($SearchActive -and $SearchHasQuery) { '  Esc Clear Search' }
                 else { '  ? Help Esc Back' }
        Write-UiLine ('  ' + (Limit-MenuText -Text $line1 -Width ([Math]::Max(8, $Width - 2)))) 'Key'
        Write-UiLine ('  ' + (Limit-MenuText -Text $line2 -Width ([Math]::Max(8, $Width - 2)))) 'Dim'
        return
    }
    if ($Width -lt 72) {
        $line1 = if ($SearchActive) { 'Up/Down  Type Search  Enter' }
                 elseif ($Navigation -eq 'Numbers') { 'Enter  00-99 Select' }
                 elseif ($Navigation -in @('Numbers','Hybrid')) { 'Up/Down  Enter  00-99' }
                 else { 'Up/Down  Enter' }
        $line2 = if ($SearchActive -and $SearchHasQuery) { '? Help  Esc Clear Search' }
                 elseif ($canQuit) { '? Help  Esc Back  Q Exit' }
                 else { '? Help  Esc Back' }
        Write-UiLine ('  ' + (Limit-MenuText -Text $line1 -Width ([Math]::Max(8, $Width - 2)))) 'Key'
        Write-UiLine ('  ' + (Limit-MenuText -Text $line2 -Width ([Math]::Max(8, $Width - 2)))) 'Dim'
        return
    }
    $line1 = if ($Navigation -eq 'Numbers') { '  Enter Select  00-99 Type Number' }
             elseif ($Navigation -eq 'Hybrid' -and -not $SearchActive) { '  Up/Down Navigate  Enter Select  00-99 Type Number  / Search' }
             elseif ($SearchActive) { '  Up/Down Navigate  Type Search  Enter Select' }
             else { '  Up/Down Navigate  Enter Select  / Search' }
    $line2 = if ($SearchActive -and $SearchHasQuery) { '  ?/F1 Help  Esc Clear Search' }
             elseif ($canQuit) { '  ?/F1 Help  Esc Back  Q Exit' }
             else { '  ?/F1 Help  Esc Back' }
    Write-UiLine $line1 'Dim'
    Write-UiLine $line2 'Dim'
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
        if ($script:ProductShell.Version) {
            Write-AipmProductHeader -Version $script:ProductShell.Version -Status $script:ProductShell.Status -Width (Get-TerminalSize).Width
            Write-UiLine ('  ' + $Title) 'Heading'
        } else { switch ($profile.Layout) {
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
        } }
        $terminalSize = Get-TerminalSize
        $compactVerticalShell = ($script:ProductShell.Version -and $terminalSize.Height -le 10)
        if ($profile.Density -ne 'Compact' -and -not $compactVerticalShell) { Write-UiLine ('  ' + ('-' * [math]::Min(48,$terminalSize.Width-5))) 'Dim' }
        if ($Description) { Write-MenuWrapped -Text $Description -Width (Get-TerminalSize).Width -Role 'Dim' -Indent '  ' }
        if ($searchActive) { Write-UiLine ('  Search: ' + $query + '_') 'Key' }
        if ($profile.Density -eq 'Spacious') { Write-UiLine '' }
        if ($visible.Count -eq 0) { Write-UiLine '  No Matching Actions. Backspace To Broaden The Search.' 'Dim' }
        $size = Get-TerminalSize
        $selectedItem = $null
        $selectedDetails = ''
        if ($visible.Count -gt 0) {
            $selectedItem = $items[$visible[$sel]]
            $selectedDetails = $selectedItem.Desc
            if (-not $selectedItem.Enabled -and $selectedItem.Reason) { $selectedDetails = $selectedItem.Reason }
        }
        $renderDescriptionStyle = $DescriptionStyle
        if ($compactVerticalShell) { $renderDescriptionStyle = 'Off' }
        $panelRows = 0
        if ($renderDescriptionStyle -eq 'Panel' -and $selectedDetails) {
            $panelRows = Measure-MenuWrappedLineCount -Text ('Details: ' + $selectedDetails) -Width $size.Width -Indent '  '
        }
        $prefixRows = Get-UiFrameLineCount
        $footerRows = 3
        $availableRows = [Math]::Max(0, $size.Height - 1 - $prefixRows - $footerRows - $panelRows)
        $metricItems = @()
        for ($pos = 0; $pos -lt $visible.Count; $pos++) { $metricItems += $items[$visible[$pos]] }
        $metrics = Get-MenuLayoutMetrics -Items $metricItems -Layout $profile.Layout -Density $profile.Density -DescriptionStyle $renderDescriptionStyle -Width $size.Width -Height $size.Height
        $lineCosts = @($metrics.LineCosts)
        $hasOverflow = ($metrics.TotalRows -gt $availableRows)
        if ($hasOverflow) { $availableRows = [Math]::Max(0, $availableRows - 1) }
        $viewport = Get-MenuViewportRange -LineCosts $lineCosts -Selected $sel -AvailableLines $availableRows
        if ($visible.Count -gt 0 -and -not $viewport.SelectedFits) {
            Write-UiLine '  Terminal Too Short - Resize To View An Option' 'Warning'
        } elseif ($visible.Count -gt 0 -and $hasOverflow) {
            Write-UiLine ('  Showing ' + (Format-MenuNumber ($visible[$viewport.Start] + 1)) + '-' + (Format-MenuNumber ($visible[$viewport.End] + 1)) + '/' + $visible.Count + ' Options') 'Info'
        }
        if ($visible.Count -eq 0) { Write-UiLine '  No Matching Actions. Backspace To Broaden The Search.' 'Dim' }
        for ($pos = $viewport.Start; $pos -le $viewport.End; $pos++) {
            if ($pos -lt 0 -or $pos -ge $visible.Count) { continue }
            $it = $items[$visible[$pos]]
            $role = 'Normal'; $marker = ' '; $markerRole = 'Dim'
            if ($pos -eq $sel) { $role = 'Selected'; $marker = '>'; $markerRole = 'SelectionMarker' }
            if (-not $it.Enabled) { $role = 'Dim' }
            $d = $it.Desc; if (-not $it.Enabled -and $it.Reason) { $d = $it.Reason }
            $ico = Get-Icon $it.Icon
            $markerPrefix = ' ' + $marker + ' '
            $prefix = ''
            if ($Navigation -in @('Numbers','Hybrid') -and -not $searchActive) { $prefix += (Format-MenuNumber ($visible[$pos] + 1)) + '  ' }
            if ($profile.Layout -eq 'Explorer') { $prefix += '|-- ' }
            if ($profile.Layout -eq 'Diagnostic') { $prefix += '[ ] ' }
            $isSplit = (($profile.Layout -in @('Split','Workbench')) -and (Get-TerminalSize).Width -ge 90)
            if ($isSplit) {
                $left = ($markerPrefix + $prefix + $it.Label)
                $left = Limit-MenuText -Text $left -Width 36
                Write-Ui $markerPrefix $markerRole; Write-Ui $prefix $role
                if ($ico) { Write-Ui $ico $it.IconRole; Write-Ui '  ' $role }
                Write-Ui (Limit-MenuText -Text $it.Label -Width 32).PadRight(34) $role
                Write-Ui '| ' 'Dim'
                if ($renderDescriptionStyle -ne 'Off') { Write-UiLine $d 'Dim' } else { Write-UiLine '' }
            } else {
                Write-Ui $markerPrefix $markerRole
                Write-Ui $prefix $role
                if ($ico) { Write-Ui $ico $it.IconRole; Write-Ui '  ' $role }
                $label = Limit-MenuText -Text $it.Label -Width ([Math]::Max(8, (Get-TerminalSize).Width - $markerPrefix.Length - $prefix.Length - [string]$ico.Length - 8))
                Write-Ui $label $role
            if ($renderDescriptionStyle -eq 'Inline' -and $d) { Write-Ui ('  -  ' + $d) 'Dim' }
                Write-UiLine ''
            }
            if (-not $isSplit -and $renderDescriptionStyle -in @('Muted','Shade','Panel') -and $d) {
                $descRole = $(if ($renderDescriptionStyle -eq 'Shade') { 'Description' } else { 'Dim' })
                Write-MenuWrapped -Text $d -Width (Get-TerminalSize).Width -Role $descRole
            }
            if ($profile.Density -eq 'Spacious') { Write-UiLine '' }
        }
        if ($renderDescriptionStyle -eq 'Panel' -and $visible.Count -gt 0 -and $selectedDetails) {
            Write-MenuWrapped -Text ('Details: ' + $selectedDetails) -Width $size.Width -Role 'Dim' -Indent '  '
        }
        Write-UiLine ''
        Write-MenuFooter -Navigation $Navigation -SearchActive $searchActive -SearchHasQuery ([bool]$query) -Width $size.Width
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
Export-ModuleMember -Function Format-MenuNumber, Resolve-NumberInput, Set-TuiMenuStyle, Get-TuiMenuStyle, Set-TuiProductShell, Get-TuiProductShell, Write-AipmProductHeader, Write-TuiRule, Write-TuiTable, New-MenuItem, Show-Menu, Write-MenuWrapped, Limit-MenuText, Get-MenuViewportRange, Get-MenuLayoutMetrics, Get-MenuLayoutCacheStats
