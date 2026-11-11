[CmdletBinding()]
param([Parameter(ValueFromRemainingArguments=$true)][string[]]$Arguments)
$python = Get-Command python -ErrorAction SilentlyContinue
if (-not $python) { throw 'Python is required to validate the state. No installation was attempted.' }
& $python.Source (Join-Path $PSScriptRoot 'validate_state.py') @Arguments
exit $LASTEXITCODE
