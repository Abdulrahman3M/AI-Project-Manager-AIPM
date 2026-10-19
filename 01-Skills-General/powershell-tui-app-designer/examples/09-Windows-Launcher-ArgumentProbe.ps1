<#
.SYNOPSIS
    Demonstrates how a quoted trailing-backslash directory can merge Windows command-line arguments.
.DESCRIPTION
    Parser-only diagnostic example. A project launcher still needs an end-to-end child-execution test.
.PARAMETER Demo
    Run a deterministic CommandLineToArgvW comparison using disposable sample paths.
#>
[CmdletBinding()]
param([switch]$Demo)
$ErrorActionPreference = 'Stop'
Set-StrictMode -Version 2.0

if ([Environment]::OSVersion.Platform -ne [PlatformID]::Win32NT) {
    Write-Output 'UNVERIFIED: CommandLineToArgvW is available only on Windows.'
    exit 0
}

if (-not ('TuiWindowsCommandLineProbe' -as [type])) {
    Add-Type -TypeDefinition @'
using System;
using System.Runtime.InteropServices;
public static class TuiWindowsCommandLineProbe {
    [DllImport("shell32.dll", SetLastError=true, CharSet=CharSet.Unicode)]
    public static extern IntPtr CommandLineToArgvW(string commandLine, out int argc);
    [DllImport("kernel32.dll")]
    public static extern IntPtr LocalFree(IntPtr memory);
}
'@
}

function ConvertFrom-WindowsCommandLine {
    param([Parameter(Mandatory)][string]$CommandLine)
    $count = 0
    $argv = [TuiWindowsCommandLineProbe]::CommandLineToArgvW($CommandLine, [ref]$count)
    if ($argv -eq [IntPtr]::Zero) { throw 'CommandLineToArgvW failed.' }
    try {
        $items = @()
        for ($i = 0; $i -lt $count; $i++) {
            $pointer = [Runtime.InteropServices.Marshal]::ReadIntPtr($argv, $i * [IntPtr]::Size)
            $items += [Runtime.InteropServices.Marshal]::PtrToStringUni($pointer)
        }
        return $items
    } finally { [void][TuiWindowsCommandLineProbe]::LocalFree($argv) }
}

if (-not $Demo) {
    Write-Output 'Run with -Demo to compare a risky command-line shape with a safer no-starting-directory shape.'
    exit 0
}

$pipe = [string][char]0x2502
$root = 'C:\Samples\02 ' + $pipe + ' Disk Helper\'
$entry = $root + 'Start-DiskHelper.ps1'
$powerShell = 'C:\Program Files\PowerShell\7\pwsh.exe'
$unsafe = 'wt.exe -w new -d "' + $root + '" "' + $powerShell + '" -NoProfile -File "' + $entry + '" --name "two words"'
$safer = 'wt.exe -w new "' + $powerShell + '" -NoProfile -File "' + $entry + '" --name "two words"'
$unsafeArgs = @(ConvertFrom-WindowsCommandLine -CommandLine $unsafe)
$saferArgs = @(ConvertFrom-WindowsCommandLine -CommandLine $safer)

Write-Output 'Unsafe Shape Parsed Arguments:'
for ($i = 0; $i -lt $unsafeArgs.Count; $i++) { Write-Output ('  [{0}] {1}' -f $i, $unsafeArgs[$i]) }
Write-Output 'Safer Shape Parsed Arguments:'
for ($i = 0; $i -lt $saferArgs.Count; $i++) { Write-Output ('  [{0}] {1}' -f $i, $saferArgs[$i]) }

if ($unsafeArgs -contains '-File') { throw 'The unsafe sample did not reproduce a merged argument vector.' }
if ($saferArgs -notcontains '-File' -or $saferArgs -notcontains $entry -or $saferArgs -notcontains 'two words') {
    throw 'The safer sample did not preserve the expected PowerShell arguments.'
}
Write-Output 'PASS: The parser separated the safer absolute-entry invocation and reproduced the unsafe trailing-separator shape.'
Write-Output 'NOTE: This parser probe does not prove that a child process ran or that native Windows Terminal displayed it.'
