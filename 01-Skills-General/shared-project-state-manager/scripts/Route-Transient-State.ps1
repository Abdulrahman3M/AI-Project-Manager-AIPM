<#
.SYNOPSIS
    Automates and enforces routing of Cache, Temporary Files, and Test Workspaces under Shared-Project-State-Manager.
.DESCRIPTION
    Wraps route_transient_state.py to provide native PowerShell integration for Section 7 of Global Agent Directives:
    - Sets $env:PYTHONPYCACHEPREFIX, $env:TEMP, $env:TMP, $env:PYTEST_ADDOPTS, etc.
    - Sweeps stray __pycache__, temp files, and test caches into Shared-Project-State-Manager.
    - Displays transient storage status and size breakdown.
.EXAMPLE
    .\Route-Transient-State.ps1 -SetEnv
    .\Route-Transient-State.ps1 -Sweep
    .\Route-Transient-State.ps1 -Status
    .\Route-Transient-State.ps1 -Run pytest
#>
[CmdletBinding()]
param(
    [switch]$SetEnv,
    [switch]$Sweep,
    [switch]$Status,
    [switch]$Clean,
    [switch]$DryRun,
    [string]$ProjectRoot,
    [Parameter(ValueFromRemainingArguments = $true)]
    [string[]]$RunCommand
)

$python = Get-Command python -ErrorAction SilentlyContinue
if (-not $python) {
    throw "Python 3.10+ is required to execute Route-Transient-State."
}

$scriptPath = Join-Path $PSScriptRoot "route_transient_state.py"
if (-not (Test-Path $scriptPath)) {
    # If placed in root of Shared-Project-State-Manager, check local directory
    $scriptPath = Join-Path $PSScriptRoot "Route-Transient-State.py"
}

if ($SetEnv) {
    $argsList = @($scriptPath, "--env", "powershell")
    if ($ProjectRoot) { $argsList += @("--project-root", $ProjectRoot) }
    $lines = & $python.Source $argsList
    foreach ($line in $lines) {
        if ($line -match '^\$env:([^ =]+)\s*=\s*''(.+)''$') {
            $name = $Matches[1]
            $value = $Matches[2]
            [System.Environment]::SetEnvironmentVariable($name, $value, [System.EnvironmentVariableTarget]::Process)
            Write-Host " [ENV ROUTED] `$env:$name = $value" -ForegroundColor Cyan
        }
    }
    return
}

$arguments = @($scriptPath)
if ($ProjectRoot) { $arguments += @("--project-root", $ProjectRoot) }
if ($Sweep) { $arguments += "--sweep" }
if ($Status) { $arguments += "--status" }
if ($Clean) { $arguments += "--clean" }
if ($DryRun) { $arguments += "--dry-run" }
if ($RunCommand -and $RunCommand.Count -gt 0) {
    $arguments += @("--run") + $RunCommand
}

if ($arguments.Count -eq 1 -and -not $SetEnv) {
    $arguments += "--status"
}

& $python.Source $arguments
exit $LASTEXITCODE
