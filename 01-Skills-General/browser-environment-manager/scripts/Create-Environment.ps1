#requires -Version 5.1
[CmdletBinding()]
param([ValidatePattern('^[A-Za-z][A-Za-z0-9-]{1,62}$')][string]$Name = 'AI-Agent-Browser',[ValidateSet('Edge','Chrome')][string]$Browser = 'Edge',[ValidateRange(1024,65535)][int]$CdpPort = 9222,[string]$BrowserExecutable,[switch]$CreateShortcut)
& (Join-Path $PSScriptRoot 'Browser-Environment.ps1') -Action Create -Name $Name -Browser $Browser -CdpPort $CdpPort -BrowserExecutable $BrowserExecutable -CreateShortcut:$CreateShortcut
