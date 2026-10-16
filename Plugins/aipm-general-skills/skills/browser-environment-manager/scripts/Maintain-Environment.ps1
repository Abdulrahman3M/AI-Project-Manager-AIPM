#requires -Version 5.1
[CmdletBinding()]
param([ValidateSet('Start','Status','Repair','Reset')][string]$Action = 'Status',[ValidatePattern('^[A-Za-z][A-Za-z0-9-]{1,62}$')][string]$Name = 'AI-Agent-Browser',[switch]$CreateShortcut,[switch]$ConfirmReset)
& (Join-Path $PSScriptRoot 'Browser-Environment.ps1') -Action $Action -Name $Name -CreateShortcut:$CreateShortcut -ConfirmReset:$ConfirmReset
