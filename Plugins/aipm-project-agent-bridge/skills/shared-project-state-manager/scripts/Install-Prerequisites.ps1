[CmdletBinding()]
param([switch]$Install)
$missing = @()
if (-not (Get-Command node -ErrorAction SilentlyContinue)) { $missing += 'Node.js LTS' }
if (-not (Get-Command python -ErrorAction SilentlyContinue)) { $missing += 'Python 3' }
if ($missing.Count -eq 0) {
  Write-Host 'PASS: Node.js and Python are available.'
  node --version
  python --version
  exit 0
}
Write-Warning ('Missing: ' + ($missing -join ', '))
if (-not $Install) {
  Write-Host 'Install Node.js LTS: winget install --id OpenJS.NodeJS.LTS --exact'
  Write-Host 'Install Python 3:    winget install --id Python.Python.3.13 --exact'
  Write-Host 'Or rerun this script with -Install to invoke winget explicitly.'
  exit 2
}
if (-not (Get-Command winget -ErrorAction SilentlyContinue)) { throw 'winget is not available.' }
if ('Node.js LTS' -in $missing) { winget install --id OpenJS.NodeJS.LTS --exact --accept-source-agreements --accept-package-agreements }
if ('Python 3' -in $missing) { winget install --id Python.Python.3.13 --exact --accept-source-agreements --accept-package-agreements }
