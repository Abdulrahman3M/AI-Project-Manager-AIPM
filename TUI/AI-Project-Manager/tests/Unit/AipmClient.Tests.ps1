Import-Module -Name (Join-Path (Join-Path (Join-Path (Get-TestRoot) 'src') 'Core') 'AipmClient.psm1') -Force -DisableNameChecking -Global
Set-TestGroup 'AIPM Core Client'

$appRoot = Get-TestRoot
$repoRoot = Get-AipmRepositoryRoot -AppRoot $appRoot
$expectedRoot = [System.IO.Path]::GetFullPath((Join-Path (Join-Path $appRoot '..') '..'))
Assert-Equal 'Core root resolves inside this AIPM checkout' $expectedRoot $repoRoot
Assert-True 'Core entry point exists below the resolved root' (Test-Path -LiteralPath (Join-Path (Join-Path $repoRoot 'Core-Engine') 'aipm.py') -PathType Leaf)

$ready = Get-AipmDependencyStatus -AppRoot $appRoot
Assert-Equal 'available Python and Core report ready' 'PASS' $ready.Status
Assert-True 'dependency status includes a parsed Python version' ([bool]$ready.Version)

$missing = Get-AipmDependencyStatus -AppRoot $appRoot -PythonPath (Join-Path (Get-TestWork) 'missing-python.exe')
Assert-Equal 'missing Python is reported as blocked' 'BLOCKED' $missing.Status

$broken = Get-AipmDependencyStatus -AppRoot $appRoot -PythonPath (Get-CurrentPowerShellPath)
Assert-Equal 'a non-Python executable is reported as blocked' 'BLOCKED' $broken.Status

$registryPath = Join-Path (Get-TestWork) 'P08 Registry With Spaces.json'
$read = Invoke-AipmCore -AppRoot $appRoot -Command 'dashboard' -RegistryPath $registryPath
Assert-Equal 'Core dashboard reads the explicit in-repository registry path' 'PASS' $read.Status
Assert-Equal 'missing fixture is distinguished from malformed state' 'NOT_REGISTERED' $read.Data.registry_status

$malformed = Join-Path (Get-TestWork) 'malformed registry.json'
[System.IO.File]::WriteAllText($malformed, '{"schema_version":"invalid"}', (New-Object System.Text.UTF8Encoding($false)))
$blocked = Invoke-AipmCore -AppRoot $appRoot -Command 'dashboard' -RegistryPath $malformed
Assert-Equal 'a malformed registry fails closed rather than looking empty' 'BLOCKED' $blocked.Status
Assert-Equal 'malformed registry reports a stable failure reason' 'INVALID_REGISTRY' $blocked.Reason

$inertPath = Join-Path (Get-TestWork) 'missing;python.exe'
$inert = Invoke-AipmCore -AppRoot $appRoot -Command 'dashboard' -RegistryPath $inertPath
Assert-Equal 'registry path punctuation remains one argument' 'NOT_REGISTERED' $inert.Data.registry_status
