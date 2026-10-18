# TestHelpers.ps1 - tiny test framework (no Pester needed; works on Windows PowerShell 5.1 and PowerShell 7).
Set-StrictMode -Version 2.0
$script:Results = New-Object System.Collections.Generic.List[object]
$script:Group = ''
$script:SourceRoot = [System.IO.Path]::GetFullPath((Join-Path (Join-Path (Join-Path $PSScriptRoot '..') '..') '..'))
$script:Root = $script:SourceRoot
$script:RuntimeRoot = ''
$script:OriginalDataDirectory = $null
$script:OriginalLocalAppData = $null

function Set-TestGroup { param([string]$Name) $script:Group = $Name; Write-Host ("`n== " + $Name) -ForegroundColor Cyan }
function Add-TestResult {
    param([string]$Name, [ValidateSet('PASS', 'FAIL', 'UNVERIFIED')][string]$Status, [string]$Detail = '')
    $script:Results.Add([pscustomobject]@{ Group = $script:Group; Name = $Name; Status = $Status; Detail = $Detail })
    $color = @{ PASS = 'Green'; FAIL = 'Red'; UNVERIFIED = 'Yellow' }[$Status]
    Write-Host ('  [{0}] {1}' -f $Status, $Name) -ForegroundColor $color
    if ($Status -ne 'PASS' -and $Detail) { Write-Host ('        ' + $Detail) -ForegroundColor DarkGray }
}
function Assert-True { param([string]$Name, $Condition, [string]$Detail = '') if ($Condition) { Add-TestResult $Name 'PASS' } else { Add-TestResult $Name 'FAIL' $Detail } }
function Assert-Equal { param([string]$Name, $Expected, $Actual) if ("$Expected" -eq "$Actual") { Add-TestResult $Name 'PASS' } else { Add-TestResult $Name 'FAIL' "expected [$Expected] actual [$Actual]" } }
function Assert-Contains { param([string]$Name, [string]$Text, [string]$Needle) if ($Text.Contains($Needle)) { Add-TestResult $Name 'PASS' } else { Add-TestResult $Name 'FAIL' "output does not contain [$Needle]" } }
function Skip-Test { param([string]$Name, [string]$Reason) Add-TestResult $Name 'UNVERIFIED' $Reason }   # never report PASS for something that did not run
function Get-TestResults { return $script:Results }

function Initialize-TestEnvironment {
    $testRoot = Join-Path $script:SourceRoot '.test-workspace'
    if (-not (Test-Path -LiteralPath $testRoot -PathType Container)) { [void](New-Item -ItemType Directory -Path $testRoot -Force) }
    $script:Work = Join-Path $testRoot ('aipm-tui-tests-' + [guid]::NewGuid().ToString('N').Substring(0, 8))
    [void](New-Item -ItemType Directory -Path $script:Work -Force)
    $script:RuntimeRoot = Join-Path $testRoot ('aipm-tui-runtime-' + [guid]::NewGuid().ToString('N').Substring(0, 8))
    [void](New-Item -ItemType Directory -Path $script:RuntimeRoot -Force)
    foreach ($name in @('Core-Engine', 'Capability-Library', 'TUI/AI-Project-Manager', 'Plugins/aipm-project-agent-bridge', 'Plugins/Adapters')) {
        $source = Join-Path $script:SourceRoot $name
        if (Test-Path -LiteralPath $source -PathType Container) {
            $destination = Join-Path $script:RuntimeRoot $name
            $parent = Split-Path -Parent $destination
            if (-not (Test-Path -LiteralPath $parent -PathType Container)) { [void](New-Item -ItemType Directory -Path $parent -Force) }
            Copy-Item -LiteralPath $source -Destination $destination -Recurse
        }
    }
    Copy-Item -LiteralPath (Join-Path $script:SourceRoot 'VERSION') -Destination (Join-Path $script:RuntimeRoot 'VERSION')
    $script:Root = Join-Path $script:RuntimeRoot 'TUI/AI-Project-Manager'
    . (Join-Path (Join-Path $script:Root 'src') 'Import-Modules.ps1')
    Import-AppModules -Root $script:Root
    $script:OriginalDataDirectory = $env:AIPM_DATA_DIR
    $script:OriginalLocalAppData = $env:LOCALAPPDATA
    $env:AIPM_DATA_DIR = Join-Path $script:Work 'data'    # tests never touch the real user profile
    Initialize-Renderer -Ansi $false -Sink Buffer
    Set-IconTier 'Ascii'
}
function Remove-TestEnvironment {
    $testRoot = [System.IO.Path]::GetFullPath((Join-Path $script:SourceRoot '.test-workspace'))
    foreach ($candidate in @($script:Work, $script:RuntimeRoot)) {
        if ($candidate -and (Test-Path -LiteralPath $candidate)) {
            $candidatePath = [System.IO.Path]::GetFullPath($candidate)
            $parentPath = [System.IO.Path]::GetFullPath((Split-Path -Parent $candidatePath))
            $name = [System.IO.Path]::GetFileName($candidatePath)
            $validName = $name.StartsWith('aipm-tui-tests-') -or $name.StartsWith('aipm-tui-runtime-')
            if ($parentPath.Equals($testRoot, [System.StringComparison]::OrdinalIgnoreCase) -and $validName) {
                Remove-Item -LiteralPath $candidatePath -Recurse -Force -ErrorAction SilentlyContinue
            }
        }
    }
    if ($null -eq $script:OriginalDataDirectory) { Remove-Item Env:AIPM_DATA_DIR -ErrorAction SilentlyContinue } else { $env:AIPM_DATA_DIR = $script:OriginalDataDirectory }
    if ($null -eq $script:OriginalLocalAppData) { Remove-Item Env:LOCALAPPDATA -ErrorAction SilentlyContinue } else { $env:LOCALAPPDATA = $script:OriginalLocalAppData }
}
function Get-TestWork { return $script:Work }
function Get-TestRoot { return $script:Root }
function Get-SourceRepositoryRoot { return $script:SourceRoot }

function Invoke-Ui {
    # Runs an action with a scripted key string; returns what the user would have seen.
    param([scriptblock]$Action, [string]$Keys)
    Initialize-Renderer -Ansi $false -Sink Buffer
    Set-ScriptedInput $Keys
    $err = ''; $val = $null
    try { $val = & $Action } catch { $err = $_.Exception.Message }
    $out = Get-CapturedOutput
    Clear-ScriptedInput
    return [pscustomobject]@{ Output = $out; Error = $err; Value = $val }
}
