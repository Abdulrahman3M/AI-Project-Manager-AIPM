#requires -Version 5.1
[CmdletBinding()]
param([ValidatePattern('^[A-Za-z][A-Za-z0-9-]{1,62}$')][string]$Name = 'AI-Agent-Browser',[switch]$NavigateTest)
& (Join-Path $PSScriptRoot 'Browser-Environment.ps1') -Action Connect -Name $Name -NavigateTest:$NavigateTest
