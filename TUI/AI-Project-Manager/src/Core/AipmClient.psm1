# AipmClient.psm1 - the only boundary from PowerShell screens to AIPM Core.
Set-StrictMode -Version 2.0

function Get-AipmRepositoryRoot {
    param([Parameter(Mandatory)][string]$AppRoot)
    $candidate = [System.IO.Path]::GetFullPath($AppRoot)
    for ($i = 0; $i -lt 8; $i++) {
        $entry = Join-Path (Join-Path $candidate 'Core-Engine') 'aipm.py'
        if (Test-Path -LiteralPath $entry -PathType Leaf) { return $candidate }
        $parent = Split-Path -Parent $candidate
        if (-not $parent -or $parent -eq $candidate) { break }
        $candidate = $parent
    }
    throw 'AIPM Core was not found in the application root or its parents.'
}

function Find-AipmPython {
    param([string]$PythonPath = '')
    if ($PythonPath) {
        if (Test-Path -LiteralPath $PythonPath -PathType Leaf) { return [System.IO.Path]::GetFullPath($PythonPath) }
        return $null
    }
    $python = Find-Executable -Name 'python'
    if (-not $python) { $python = Find-Executable -Name 'python3' }
    return $python
}

function Invoke-AipmCore {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)][string]$AppRoot,
        [Parameter(Mandatory)][ValidateSet('health', 'list', 'dashboard', 'catalog', 'host-capabilities', 'registry-init', 'registry-register', 'registry-unregister', 'registry-backup', 'registry-restore', 'task-create', 'task-list', 'task-read', 'task-plan', 'task-checkpoint', 'task-blocker-add', 'task-blocker-clear', 'task-verify', 'task-report', 'task-artifact-list', 'task-artifact-write')][string]$Command,
        [string]$RegistryPath = '',
        [string]$ProjectRoot = '',
        [string]$ProjectId = '',
        [string]$Alias = '',
        [string]$TaskId = '',
        [string]$Title = '',
        [string]$Scope = '',
        [string]$Text = '',
        [string]$Result = '',
        [string]$Evidence = '',
        [string]$LastVerifiedAction = '',
        [string]$NextAction = '',
        [string]$RelativePath = '',
        [string]$FromFile = '',
        [string]$Destination = '',
        [string]$Source = '',
        [string]$PythonPath = '',
        [int]$TimeoutSec = 10
    )
    $root = Get-AipmRepositoryRoot -AppRoot $AppRoot
    $python = Find-AipmPython -PythonPath $PythonPath
    if (-not $python) { return [pscustomobject]@{ Status = 'BLOCKED'; Reason = 'PYTHON_NOT_FOUND'; Data = $null } }

    $entry = Join-Path (Join-Path $root 'Core-Engine') 'aipm.py'
    $arguments = @($entry, $Command)
    if ($RegistryPath -and ($Command -in @('list', 'dashboard', 'registry-init', 'registry-register', 'registry-unregister', 'registry-backup', 'registry-restore') -or $Command.StartsWith('task-'))) {
        $arguments += @('--registry', [System.IO.Path]::GetFullPath($RegistryPath))
    }
    if ($ProjectRoot) { $arguments += @('--project-root', [System.IO.Path]::GetFullPath($ProjectRoot)) }
    if ($ProjectId) { $arguments += @('--project-id', $ProjectId) }
    if ($Alias) { $arguments += @('--alias', $Alias) }
    if ($TaskId) { $arguments += @('--task-id', $TaskId) }
    if ($Title) { $arguments += @('--title', $Title) }
    if ($Scope) { $arguments += @('--scope', $Scope) }
    if ($Text) { $arguments += @('--text', $Text) }
    if ($Result) { $arguments += @('--result', $Result) }
    if ($Evidence) { $arguments += @('--evidence', $Evidence) }
    if ($LastVerifiedAction) { $arguments += @('--last-verified-action', $LastVerifiedAction) }
    if ($NextAction) { $arguments += @('--next-action', $NextAction) }
    if ($RelativePath) { $arguments += @('--relative-path', $RelativePath) }
    if ($FromFile) { $arguments += @('--from-file', [System.IO.Path]::GetFullPath($FromFile)) }
    if ($Destination) { $arguments += @('--destination', [System.IO.Path]::GetFullPath($Destination)) }
    if ($Source) { $arguments += @('--source', [System.IO.Path]::GetFullPath($Source)) }
    $process = Invoke-External -FilePath $python -Arguments $arguments -TimeoutSec $TimeoutSec
    if (-not $process.Started) { return [pscustomobject]@{ Status = 'BLOCKED'; Reason = 'CORE_NOT_STARTED'; Data = $null } }
    if ($process.TimedOut) { return [pscustomobject]@{ Status = 'BLOCKED'; Reason = 'CORE_TIMED_OUT'; Data = $null } }
    try { $data = $process.StdOut | ConvertFrom-Json -ErrorAction Stop }
    catch { return [pscustomobject]@{ Status = 'BLOCKED'; Reason = 'CORE_RESPONSE_INVALID'; Data = $null } }
    if ($null -eq $data -or -not $data.PSObject.Properties['status']) {
        return [pscustomobject]@{ Status = 'BLOCKED'; Reason = 'CORE_RESPONSE_INVALID'; Data = $null }
    }
    if ($process.ExitCode -ne 0 -or $data.status -ne 'PASS') {
        $reason = 'CORE_REQUEST_BLOCKED'
        if ($data.PSObject.Properties['reason'] -and $data.reason) { $reason = [string]$data.reason }
        return [pscustomobject]@{ Status = 'BLOCKED'; Reason = $reason; Data = $data }
    }
    return [pscustomobject]@{ Status = 'PASS'; Reason = ''; Data = $data }
}

function Get-AipmDependencyStatus {
    [CmdletBinding()]
    param([Parameter(Mandatory)][string]$AppRoot, [string]$PythonPath = '')
    $python = Find-AipmPython -PythonPath $PythonPath
    if (-not $python) { return [pscustomobject]@{ Status = 'BLOCKED'; Reason = 'PYTHON_NOT_FOUND'; Version = '' } }

    $versionResult = Invoke-External -FilePath $python -Arguments @('--version') -TimeoutSec 5
    if (-not $versionResult.Started -or $versionResult.TimedOut -or $versionResult.ExitCode -ne 0) {
        return [pscustomobject]@{ Status = 'BLOCKED'; Reason = 'PYTHON_VERSION_CHECK_FAILED'; Version = '' }
    }
    $versionText = $versionResult.StdOut.Trim()
    if (-not $versionText) { $versionText = $versionResult.StdErr.Trim() }
    if ($versionText -notmatch '^Python\s+(\d+)\.(\d+)\.(\d+)') {
        return [pscustomobject]@{ Status = 'BLOCKED'; Reason = 'PYTHON_VERSION_UNVERIFIED'; Version = $versionText }
    }
    $major = [int]$Matches[1]; $minor = [int]$Matches[2]
    if ($major -lt 3 -or ($major -eq 3 -and $minor -lt 10)) {
        return [pscustomobject]@{ Status = 'BLOCKED'; Reason = 'PYTHON_VERSION_UNSUPPORTED'; Version = $versionText }
    }
    $health = Invoke-AipmCore -AppRoot $AppRoot -Command 'health' -PythonPath $python -TimeoutSec 5
    if ($health.Status -ne 'PASS') { return [pscustomobject]@{ Status = 'BLOCKED'; Reason = $health.Reason; Version = $versionText } }
    return [pscustomobject]@{ Status = 'PASS'; Reason = ''; Version = $versionText }
}

Export-ModuleMember -Function Get-AipmRepositoryRoot, Find-AipmPython, Invoke-AipmCore, Get-AipmDependencyStatus
