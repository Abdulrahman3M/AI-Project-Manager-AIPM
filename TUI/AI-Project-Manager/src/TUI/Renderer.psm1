# Renderer.psm1 - the ONLY module that writes to the screen. Sinks: Console (real) and Buffer (tests capture the output).
Set-StrictMode -Version 2.0
$script:Sink = 'Console'
$script:Ansi = $false
$script:Buffer = New-Object System.Text.StringBuilder
$script:Capture = New-Object System.Text.StringBuilder
$script:CaptureWidth = 80
$script:CaptureHeight = 24
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

function Test-AnsiSupport {
    # NO_COLOR wins; AIPM_FORCE_ANSI=1 forces; redirected output never gets escape codes.
    if ($env:NO_COLOR) { return $false }
    if ($env:AIPM_FORCE_ANSI -eq '1') { return $true }
    try { if ([Console]::IsOutputRedirected) { return $false } } catch { return $false }
    if (-not (Test-IsWindows)) { return $true }
    if ($env:WT_SESSION -or $env:ConEmuANSI -eq 'ON' -or $env:TERM_PROGRAM) { return $true }
    try { if ($Host.UI.SupportsVirtualTerminal) { return $true } } catch { }
    return $false
}

function Initialize-Renderer {
    param([bool]$Ansi = $false, [ValidateSet('Console', 'Buffer', 'Capture')][string]$Sink = 'Console', [int]$CaptureWidth = 80, [int]$CaptureHeight = 24)
    $script:Ansi = $Ansi; $script:Sink = $Sink
    $script:Buffer = New-Object System.Text.StringBuilder
    $script:Capture = New-Object System.Text.StringBuilder
    $script:CaptureWidth = [Math]::Max(20, $CaptureWidth); $script:CaptureHeight = [Math]::Max(8, $CaptureHeight)
    $script:FrameStarted = $false
    $script:PendingFrame = New-Object System.Text.StringBuilder
    $script:PreviousRows = @()
    $script:PreviousViewport = ''
}

function Get-TerminalSize {
    if ($script:Sink -eq 'Capture') { return [pscustomobject]@{ Width = $script:CaptureWidth; Height = $script:CaptureHeight } }
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
    $Text = [regex]::Replace($Text, '\x1B\[[0-?]*[ -/]*[@-~]', '')
    $Text = [regex]::Replace($Text, '[\x00-\x1F\x7F]', '')
    if ($script:Sink -eq 'Buffer') { [void]$script:Buffer.Append($Text); return }
    $st = Get-RoleStyle $Role
    if ($script:Ansi) {
        $styled = $script:Esc + '[' + $st.Ansi + 'm' + $Text + $script:Esc + '[0m'
        if ($script:FrameStarted) { [void]$script:PendingFrame.Append($styled) }
        elseif ($script:Sink -eq 'Capture') { [void]$script:Capture.Append($styled) }
        else { [Console]::Out.Write($styled) }
    }
    elseif ($script:FrameStarted) {
        if ($script:Sink -eq 'Console') { [void]$script:PendingFrame.Append(([string][char]30) + $Role + ([string][char]31) + $Text) }
        else { [void]$script:PendingFrame.Append($Text) }
    }
    elseif ($script:Sink -eq 'Capture') { [void]$script:Capture.Append($Text) }
    else { Write-Host $Text -NoNewline -ForegroundColor $st.Legacy }
}

function Write-UiLine {
    param([AllowEmptyString()][string]$Text = '', [string]$Role = 'Normal')
    Write-Ui $Text $Role
    if ($script:Sink -eq 'Buffer') { [void]$script:Buffer.Append("`n") }
    elseif ($script:FrameStarted) { [void]$script:PendingFrame.Append("`n") }
    elseif ($script:Sink -eq 'Capture') { [void]$script:Capture.Append("`n") }
    elseif ($script:Ansi) { [Console]::Out.Write("`n") }
    else { Write-Host '' }
}

function Clear-Ui {
    # Starts an in-place frame. Do not clear a visible screen on every keypress.
    if ($script:Sink -eq 'Buffer') { [void]$script:Buffer.Append("`n=====CLEAR=====`n"); return }
    if ($script:Ansi) { $script:PendingFrame = New-Object System.Text.StringBuilder }
    else {
        try { [Console]::SetCursorPosition(0, 0) } catch { }
    }
    $script:FrameStarted = $true
}

function Complete-UiFrame {
    if ($script:Sink -eq 'Buffer' -or -not $script:FrameStarted) { return }
    try {
        if ($script:Ansi) {
            $frame = $script:PendingFrame.ToString()
            $rows = @($frame -split "`n")
            if ($frame.EndsWith("`n") -and $rows.Count -gt 0) {
                $rows = @($rows | Select-Object -SkipLast 1)
            }
            $size = Get-TerminalSize
            $viewport = [string]$size.Width + 'x' + [string]$size.Height
            if ($script:PreviousViewport -and $script:PreviousViewport -ne $viewport) {
                # Size changes invalidate the row cache; clear stale layout in place.
                Write-RendererOutput ($script:Esc + '[H' + $script:Esc + '[J')
                $script:PreviousRows = @()
            }
            foreach ($i in @(Get-UiChangedRows -Before $script:PreviousRows -After $rows)) {
                if ($i -ge $size.Height - 1) { continue }
                $command = $script:Esc + '[' + ($i + 1) + ';1H'
                if ($i -lt $rows.Count) {
                    Write-RendererOutput ($command + $rows[$i] + $script:Esc + '[K')
                } else {
                    Write-RendererOutput ($command + $script:Esc + '[2K')
                }
            }
            $script:PreviousRows = $rows
            $script:PreviousViewport = $viewport
        } elseif ($script:Sink -eq 'Capture') {
            $rows = @($script:PendingFrame.ToString() -split "`n")
            if ($script:PendingFrame.ToString().EndsWith("`n") -and $rows.Count -gt 0) { $rows = @($rows | Select-Object -SkipLast 1) }
            foreach ($i in @(Get-UiChangedRows -Before $script:PreviousRows -After $rows)) {
                if ($i -ge $script:CaptureHeight - 1) { continue }
                $command = $script:Esc + '[' + ($i + 1) + ';1H'
                if ($i -lt $rows.Count) { Write-RendererOutput ($command + $rows[$i] + $script:Esc + '[K') }
                else { Write-RendererOutput ($command + $script:Esc + '[2K') }
            }
            $script:PreviousRows = $rows
            $script:PreviousViewport = [string]$script:CaptureWidth + 'x' + [string]$script:CaptureHeight
        } else {
            # Windows PowerShell legacy consoles retain the same row-diff behavior without ANSI.
            $frame = $script:PendingFrame.ToString()
            $rows = @($frame -split "`n")
            if ($frame.EndsWith("`n") -and $rows.Count -gt 0) { $rows = @($rows | Select-Object -SkipLast 1) }
            $size = Get-TerminalSize
            $viewport = [string]$size.Width + 'x' + [string]$size.Height
            if ($script:PreviousViewport -and $script:PreviousViewport -ne $viewport) { $script:PreviousRows = @() }
            foreach ($i in @(Get-UiChangedRows -Before $script:PreviousRows -After $rows)) {
                if ($i -ge $size.Height - 1) { continue }
                try {
                    [Console]::SetCursorPosition(0, $i)
                    if ($i -lt $rows.Count) { Write-LegacyRow -Row $rows[$i] }
                    [Console]::ForegroundColor = [ConsoleColor]::Gray
                    [Console]::BackgroundColor = [ConsoleColor]::Black
                    if ($i -ge $rows.Count) { [Console]::Out.Write(' ' * [Math]::Max(1, $size.Width - 1)) }
                    else {
                        $visibleRow = [regex]::Replace($rows[$i], ([string][char]30) + '[^' + ([string][char]31) + ']*' + ([string][char]31), '')
                        [Console]::Out.Write(' ' * [Math]::Max(0, $size.Width - $visibleRow.Length - 1))
                    }
                } catch { }
            }
            $script:PreviousRows = $rows
            $script:PreviousViewport = $viewport
            try { [Console]::SetCursorPosition(0, [Math]::Min($rows.Count, $size.Height - 1)) } catch { }
        }
    } finally {
        $script:FrameStarted = $false
        [void]$script:PendingFrame.Clear()
    }
}

function Enter-Screen {
    $script:PreviousRows = @(); $script:PreviousViewport = ''
    # Alternate screen + hidden cursor (ANSI only); always pair with Exit-Screen in a finally block.
    if ($script:Sink -ne 'Buffer' -and $script:Ansi) { Write-RendererOutput ($script:Esc + '[?1049h' + $script:Esc + '[?25l') }
}
function Exit-Screen {
    $script:PreviousRows = @(); $script:PreviousViewport = ''; $script:FrameStarted = $false
    if ($script:Sink -ne 'Buffer') {
        if ($script:Ansi) { Write-RendererOutput ($script:Esc + '[?25h' + $script:Esc + '[?1049l' + $script:Esc + '[0m') }
        elseif ($script:Sink -eq 'Console') { try { [Console]::CursorVisible = $true } catch { } }
    }
}

function Write-RendererOutput { param([string]$Text) if ($script:Sink -eq 'Capture') { [void]$script:Capture.Append($Text) } else { [Console]::Out.Write($Text) } }
function Write-LegacyRow {
    param([string]$Row)
    $segments = [regex]::Split($Row, ([string][char]30) + '([^' + ([string][char]31) + ']*)' + ([string][char]31))
    $role = 'Normal'
    foreach ($segment in $segments) {
        if ($segment -in @('Title','Heading','Normal','Dim','Description','Selected','Number','Key','Success','Warning','Error','Info')) { $role = $segment; continue }
        if (-not $env:NO_COLOR) {
            $style = Get-RoleStyle $role
            try { [Console]::ForegroundColor = [ConsoleColor]$style.Legacy; if ($role -eq 'Selected') { [Console]::BackgroundColor = [ConsoleColor]::DarkCyan } } catch { }
        }
        [Console]::Out.Write($segment)
    }
    try { [Console]::ForegroundColor = [ConsoleColor]::Gray; [Console]::BackgroundColor = [ConsoleColor]::Black } catch { }
}
function Set-CaptureTerminalSize { param([int]$Width, [int]$Height) $script:CaptureWidth = [Math]::Max(20, $Width); $script:CaptureHeight = [Math]::Max(8, $Height) }
function Get-CapturedOutput { if ($script:Sink -eq 'Capture') { return $script:Capture.ToString() }; return $script:Buffer.ToString() }
function Clear-CapturedOutput { if ($script:Sink -eq 'Capture') { $script:Capture = New-Object System.Text.StringBuilder } else { $script:Buffer = New-Object System.Text.StringBuilder } }
function Get-LastFrame { return (((Get-CapturedOutput) -split '=====CLEAR=====')[-1]) }

Export-ModuleMember -Function Get-UiChangedRows, Test-AnsiSupport, Initialize-Renderer, Get-TerminalSize, Write-Ui, Write-UiLine, Clear-Ui, Complete-UiFrame, Enter-Screen, Exit-Screen, Get-CapturedOutput, Clear-CapturedOutput, Get-LastFrame, Set-CaptureTerminalSize
