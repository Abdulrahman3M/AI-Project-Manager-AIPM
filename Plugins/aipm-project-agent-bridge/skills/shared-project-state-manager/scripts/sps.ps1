[CmdletBinding()]
param([Parameter(ValueFromRemainingArguments=$true)][string[]]$Arguments)
$node = Get-Command node -ErrorAction SilentlyContinue
if (-not $node) { throw 'Node.js is required. Install with: winget install --id OpenJS.NodeJS.LTS --exact' }
& $node.Source (Join-Path $PSScriptRoot 'sps.mjs') @Arguments
exit $LASTEXITCODE
