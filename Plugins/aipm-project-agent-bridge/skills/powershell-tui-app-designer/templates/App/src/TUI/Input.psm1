# Input.psm1 - the ONLY module that reads the keyboard. A scripted queue lets tests and CI drive the whole UI.
# Tokens: {Enter} {Esc} {Up} {Down} {Backspace} {CtrlC}; every other character is typed literally.
Set-StrictMode -Version 2.0
$script:Queue = New-Object System.Collections.Generic.Queue[object]
$script:Scripted = $false

function New-Key { param([string]$Name, [string]$Char = '') return [pscustomobject]@{ Name = $Name; Char = $Char; Width = $null; Height = $null } }

function Get-InputViewport {
    # Input observes viewport changes while waiting; the Renderer still owns all screen writes.
    $width = 80; $height = 30
    try { $width = [Console]::WindowWidth } catch { }
    try { $height = [Console]::WindowHeight } catch { }
    if ($width -lt 20) { $width = 80 }
    if ($height -lt 8) { $height = 30 }
    return [pscustomobject]@{ Width = [int]$width; Height = [int]$height }
}

function Test-ViewportChanged {
    param([object]$Before, [object]$After)
    if ($null -eq $Before -or $null -eq $After) { return $false }
    $beforeWidth = $Before.PSObject.Properties['Width']; $beforeHeight = $Before.PSObject.Properties['Height']
    $afterWidth = $After.PSObject.Properties['Width']; $afterHeight = $After.PSObject.Properties['Height']
    if ($null -eq $beforeWidth -or $null -eq $beforeHeight -or $null -eq $afterWidth -or $null -eq $afterHeight) { return $false }
    return ([int]$beforeWidth.Value -ne [int]$afterWidth.Value -or [int]$beforeHeight.Value -ne [int]$afterHeight.Value)
}

function ConvertFrom-ConsoleKey {
    param([Parameter(Mandatory)][System.ConsoleKeyInfo]$KeyInfo)
    if (($KeyInfo.Modifiers -band [ConsoleModifiers]::Control) -and $KeyInfo.Key -eq [ConsoleKey]::C) { return (New-Key 'CtrlC') }
    switch ($KeyInfo.Key) {
        'Enter' { return (New-Key 'Enter') }
        'Escape' { return (New-Key 'Esc') }
        'UpArrow' { return (New-Key 'Up') }
        'DownArrow' { return (New-Key 'Down') }
        'Backspace' { return (New-Key 'Backspace') }
        default { if ($KeyInfo.KeyChar -ne [char]0) { return (New-Key 'Char' ([string]$KeyInfo.KeyChar)) } return (New-Key 'Other') }
    }
}

function Set-ScriptedInput {
    param([Parameter(Mandatory)][AllowEmptyString()][string]$Keys)
    $script:Queue = New-Object System.Collections.Generic.Queue[object]
    $script:Scripted = $true
    $i = 0
    while ($i -lt $Keys.Length) {
        if ($Keys[$i] -eq '{') {
            $close = $Keys.IndexOf('}', $i)
            if ($close -gt $i) {
                $tok = $Keys.Substring($i + 1, $close - $i - 1)
                if ($tok -in @('Enter', 'Esc', 'Up', 'Down', 'Backspace', 'CtrlC', 'Resize')) { $script:Queue.Enqueue((New-Key $tok)); $i = $close + 1; continue }
            }
        }
        $script:Queue.Enqueue((New-Key 'Char' ([string]$Keys[$i]))); $i++
    }
}

function Clear-ScriptedInput { $script:Queue = New-Object System.Collections.Generic.Queue[object]; $script:Scripted = $false }
function Test-ScriptedInput { return $script:Scripted }

function Read-AppKey {
    param([object]$SinceViewport = $null,
          [ValidateRange(25, 500)][int]$PollIntervalMs = 100,
          [scriptblock]$ViewportProvider,
          [scriptblock]$KeyAvailableProvider,
          [scriptblock]$KeyReader,
          [scriptblock]$Waiter)
    if ($script:Scripted) {
        if ($script:Queue.Count -eq 0) { throw 'Scripted input exhausted.' }   # a test that runs out of keys must fail loudly
        return $script:Queue.Dequeue()
    }
    if (-not $ViewportProvider) { $ViewportProvider = { Get-InputViewport } }
    if (-not $KeyAvailableProvider) { $KeyAvailableProvider = { [Console]::KeyAvailable } }
    if (-not $KeyReader) { $KeyReader = { [Console]::ReadKey($true) } }
    if ($null -eq $SinceViewport) { $SinceViewport = & $ViewportProvider }
    while ($true) {
        try {
            if (& $KeyAvailableProvider) { return (ConvertFrom-ConsoleKey -KeyInfo (& $KeyReader)) }
        } catch { throw ('Interactive key polling failed: ' + $_.Exception.Message) }
        $current = & $ViewportProvider
        if (Test-ViewportChanged -Before $SinceViewport -After $current) {
            $event = New-Key 'Resize'; $event.Width = [int]$current.Width; $event.Height = [int]$current.Height
            return $event
        }
        if ($Waiter) { & $Waiter $PollIntervalMs } else { Start-Sleep -Milliseconds $PollIntervalMs }
    }
}

Export-ModuleMember -Function Get-InputViewport, Test-ViewportChanged, Set-ScriptedInput, Clear-ScriptedInput, Test-ScriptedInput, Read-AppKey
