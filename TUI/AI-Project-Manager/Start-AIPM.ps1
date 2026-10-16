<#
.SYNOPSIS
    AI Project Manager - entry point. Works on Windows PowerShell 5.1 and PowerShell 7.x, on Windows and Linux.
.PARAMETER Version
    Print the version and exit.
.PARAMETER ScriptedInput
    Drive the UI with a key string such as '01{Enter}' (tests, CI, demos). Tokens: {Enter} {Esc} {Up} {Down} {Backspace} {CtrlC}.
.PARAMETER RegistryPath
    Read a project registry from an explicit path (tests and portable deployments).
#>
[CmdletBinding()]
param([switch]$Version, [string]$ScriptedInput, [string]$RegistryPath = '')
$ErrorActionPreference = 'Stop'
Set-StrictMode -Version 2.0
$root = $PSScriptRoot
. (Join-Path (Join-Path $root 'src') 'Import-Modules.ps1')
Import-AppModules -Root $root

if ($Version) { Write-Output ('AI Project Manager v' + (Get-AppVersion $root)); exit 0 }

$scripted = $PSBoundParameters.ContainsKey('ScriptedInput')
$interactive = $true
try { $interactive = (-not [Console]::IsInputRedirected) -and (-not [Console]::IsOutputRedirected) } catch { $interactive = $false }
if (-not $interactive -and -not $scripted) {
    Write-Output 'AI Project Manager Needs An Interactive Console (A Real Terminal Window). Start It From A Terminal, Not A Pipe Or Redirect.'
    exit 2
}

$sink = 'Console'
Initialize-Renderer -Ansi (Test-AnsiSupport) -Sink $sink
if ($scripted) { Set-ScriptedInput $ScriptedInput }
$code = 0
$oldCtrl = $false
$oldOutputEncoding = $null
try { $oldOutputEncoding = [Console]::OutputEncoding } catch { }
try { $oldCtrl = [Console]::TreatControlCAsInput; if (-not $scripted) { [Console]::TreatControlCAsInput = $true } } catch { }
try {
    Enter-Screen
    Start-TuiApp -Root $root -RegistryPath $RegistryPath
} catch [System.OperationCanceledException] {
    $code = 0   # Ctrl+C: leave quietly
} catch {
    $code = 1
    Write-AppLog ('unhandled: ' + $_.Exception.Message) 'ERROR'
    $failure = $_.Exception.Message
} finally {
    Exit-Screen
    try { [Console]::TreatControlCAsInput = $oldCtrl } catch { }
    if ($oldOutputEncoding) { try { [Console]::OutputEncoding = $oldOutputEncoding } catch { } }
}
if ($code -ne 0) { [Console]::Error.WriteLine('Unexpected Error: ' + $failure) }   # printed AFTER leaving the alternate screen so it stays visible
exit $code
