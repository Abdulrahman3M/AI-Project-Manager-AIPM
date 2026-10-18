[CmdletBinding()]
param(
    [ValidateSet('ChatGPT', 'Claude', 'Antigavity', 'All')]
    [string]$Platform = 'All',
    [string]$OutputPath,
    [switch]$Validate
)

$ErrorActionPreference = 'Stop'
$repositoryRoot = (Resolve-Path (Join-Path $PSScriptRoot '..\..')).Path
$builder = Join-Path $PSScriptRoot 'build_plugins.py'
$python = Get-Command python -ErrorAction Stop
$platformArgument = $Platform.ToLowerInvariant()

$arguments = @($builder, '--root', $repositoryRoot, '--platform', $platformArgument)
if ($OutputPath) {
    $arguments += @('--output', (Resolve-Path -LiteralPath $OutputPath -ErrorAction Stop).Path)
}

& $python.Source @arguments
if ($LASTEXITCODE -ne 0) {
    throw "AIPM Plugin build failed with exit code $LASTEXITCODE."
}

if ($Validate) {
    Write-Verbose 'Each generated archive was already validated during the build. Use build_plugins.py --validate for an explicit single-archive recheck.'
}
