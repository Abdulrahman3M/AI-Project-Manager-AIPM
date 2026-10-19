# Renderer.psm1 - the ONLY module that writes to the screen. Sinks: Console (real) and Buffer (tests capture the output).
Set-StrictMode -Version 2.0
$script:Sink = 'Console'
$script:Ansi = $false
$script:Buffer = New-Object System.Text.StringBuilder
$script:Esc = [string][char]27
$script:FrameStarted = $false
$script:PendingFrame = New-Object System.Text.StringBuilder
$script:PreviousRows = @()
$script:PreviousViewport = ''

function Get-UiChangedRows {
    # Pure row-diff: ANSI text includes all semantic style segments.
    param([string[]]$Before = @(), [string[]]$After = @())
    $limit = [Math]::Max($Before.Count, $After.Count)
    for ($i = 0; $i -lt $limit; $i++) {
        $a = if ($i -lt $Before.Count) { $Before[$i] } else { $null }
        $b = if ($i -lt $After.Count) { $After[$i] } else { $null }
        if ($null -eq $a -or $null -eq $b -or $a -cne $b) { Write-Output $i }
    }
}

function Get-UiFramePlan {
    # Pure frame planner. A viewport change repaints the complete logical frame in place once.
    param([string[]]$BeforeRows = @(), [string[]]$AfterRows = @(), [string]$BeforeViewport = '', [string]$AfterViewport = '')
    $viewportChanged = ($BeforeViewport -and $AfterViewport -and $BeforeViewport -cne $AfterViewport)
    if ($viewportChanged) {
        $limit = [Math]::Max($BeforeRows.Count, $AfterRows.Count)
        $rows = @(); for ($i = 0; $i -lt $limit; $i++) { $rows += $i }
    } else { $rows = @(Get-UiChangedRows -Before $BeforeRows -After $AfterRows) }
    return [pscustomobject]@{ Rows = [int[]]@($rows); ViewportChanged = [bool]$viewportChanged }
}

function Test-AnsiSupport {
    # NO_COLOR wins; {{ENVPREFIX}}_FORCE_ANSI=1 forces; redirected output never gets escape codes.
    if ($env:NO_COLOR) { return $false }
    if ($env:{{ENVPREFIX}}_FORCE_ANSI -eq '1') { return $true }
    try { if ([Console]::IsOutputRedirected) { return $false } } catch { return $false }
    if (-not (Test-IsWindows)) { return $true }
    if ($env:WT_SESSION -or $env:ConEmuANSI -eq 'ON' -or $env:TERM_PROGRAM) { return $true }
    try { if ($Host.UI.SupportsVirtualTerminal) { return $true } } catch { }
    return $false
}

function Initialize-Renderer {
    param([bool]$Ansi = $false, [ValidateSet('Console', 'Buffer')][string]$Sink = 'Console')
    $script:Ansi = $Ansi; $script:Sink = $Sink
    $script:Buffer = New-Object System.Text.StringBuilder
    $script:FrameStarted = $false
    $script:PendingFrame = New-Object System.Text.StringBuilder
    $script:PreviousRows = @()
    $script:PreviousViewport = ''
}

function Get-TerminalSize {
    $w = 100; $h = 30
    try { $w = [Console]::WindowWidth } catch { }
    try { $h = [Console]::WindowHeight } catch { }
    if ($w -lt 20) { $w = 80 }
    if ($h -lt 8) { $h = 30 }
    return [pscustomobject]@{ Width = $w; Height = $h }
}

function Write-Ui {
    # Writes text in a ROLE (see Theme). No newline.
    param([AllowEmptyString()][string]$Text, [string]$Role = 'Normal')
    if ($script:Sink -eq 'Buffer') { [void]$script:Buffer.Append($Text); return }
    $st = Get-RoleStyle $Role
    if ($script:Ansi) {
        $styled = $script:Esc + '[' + $st.Ansi + 'm' + $Text + $script:Esc + '[0m'
        if ($script:FrameStarted) { [void]$script:PendingFrame.Append($styled) }
        else { [Console]::Out.Write($styled) }
    }
    else { Write-Host $Text -NoNewline -ForegroundColor $st.Legacy }
}

function Write-UiLine { param([AllowEmptyString()][string]$Text = '', [string]$Role = 'Normal') Write-Ui $Text $Role; Write-Ui "`n" 'Normal' }

function Clear-Ui {
    # Starts an in-place frame. Do not clear a visible screen on every keypress.
    if ($script:Sink -eq 'Buffer') { [void]$script:Buffer.Append("`n=====CLEAR=====`n"); return }
    if ($script:Ansi) { $script:PendingFrame = New-Object System.Text.StringBuilder }
    else {
        try { [Console]::SetCursorPosition(0, 0) }
        catch { try { Clear-Host } catch { } }
    }
    $script:FrameStarted = $true
}

function Complete-UiFrame {
    $size = Get-TerminalSize
    if ($script:Sink -eq 'Buffer' -or -not $script:FrameStarted) { return $size }
    try {
        if ($script:Ansi) {
            $frame = $script:PendingFrame.ToString()
            $rows = @($frame -split "`n")
            if ($frame.EndsWith("`n") -and $rows.Count -gt 0) {
                $rows = @($rows | Select-Object -SkipLast 1)
            }
            $viewport = [string]$size.Width + 'x' + [string]$size.Height
            $plan = Get-UiFramePlan -BeforeRows $script:PreviousRows -AfterRows $rows -BeforeViewport $script:PreviousViewport -AfterViewport $viewport
            foreach ($i in @($plan.Rows)) {
                if ($i -ge $size.Height - 1) { continue }
                $command = $script:Esc + '[' + ($i + 1) + ';1H'
                if ($i -lt $rows.Count) {
                    [Console]::Out.Write($command + $rows[$i] + $script:Esc + '[K')
                } else {
                    [Console]::Out.Write($command + $script:Esc + '[2K')
                }
            }
            $script:PreviousRows = $rows
            $script:PreviousViewport = $viewport
        } else {
            # Legacy console: remove characters from the old, longer frame.
            try {
                $left = [Console]::CursorLeft; $top = [Console]::CursorTop
                $width = [Console]::WindowWidth; $height = [Console]::WindowHeight
                if ($top -lt $height) {
                    [Console]::Out.Write(' ' * [Math]::Max(0,$width - $left - 1))
                    for ($row = $top + 1; $row -lt $height; $row++) {
                        [Console]::SetCursorPosition(0,$row)
                        [Console]::Out.Write(' ' * [Math]::Max(0,$width - 1))
                    }
                }
            } catch { }
        }
    } finally {
        $script:FrameStarted = $false
        [void]$script:PendingFrame.Clear()
    }
    return $size
}

function Enter-Screen {
    $script:PreviousRows = @(); $script:PreviousViewport = ''
    # Alternate screen + hidden cursor (ANSI only); always pair with Exit-Screen in a finally block.
    if ($script:Sink -eq 'Console' -and $script:Ansi) { [Console]::Out.Write($script:Esc + '[?1049h' + $script:Esc + '[?25l') }
}
function Exit-Screen {
    $script:PreviousRows = @(); $script:PreviousViewport = ''; $script:FrameStarted = $false
    if ($script:Sink -eq 'Console') {
        if ($script:Ansi) { [Console]::Out.Write($script:Esc + '[?25h' + $script:Esc + '[?1049l' + $script:Esc + '[0m') }
        else { try { [Console]::CursorVisible = $true } catch { } }
    }
}

function Get-CapturedOutput { return $script:Buffer.ToString() }
function Clear-CapturedOutput { $script:Buffer = New-Object System.Text.StringBuilder }
function Get-LastFrame { return (((Get-CapturedOutput) -split '=====CLEAR=====')[-1]) }

Export-ModuleMember -Function Get-UiChangedRows, Get-UiFramePlan, Test-AnsiSupport, Initialize-Renderer, Get-TerminalSize, Write-Ui, Write-UiLine, Clear-Ui, Complete-UiFrame, Enter-Screen, Exit-Screen, Get-CapturedOutput, Clear-CapturedOutput, Get-LastFrame
