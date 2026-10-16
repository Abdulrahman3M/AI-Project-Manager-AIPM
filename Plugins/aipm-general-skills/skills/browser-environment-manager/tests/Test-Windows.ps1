#requires -Version 5.1
[CmdletBinding()]
param([string]$Name = 'AI-Agent-Browser')
$ErrorActionPreference = 'Stop'
if ([Environment]::OSVersion.Platform -ne [PlatformID]::Win32NT) { throw 'Windows-only integration test.' }
$entry = Join-Path (Split-Path -Parent $PSScriptRoot) 'scripts\Browser-Environment.ps1'
& $entry -Action Status -Name $Name
& $entry -Action Connect -Name $Name
Write-Host 'Connection diagnostics executed; browser screenshot requires compatible agent tooling.'
