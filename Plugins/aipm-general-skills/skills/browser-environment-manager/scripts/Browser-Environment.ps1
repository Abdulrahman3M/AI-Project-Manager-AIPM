#requires -Version 5.1
<#
.SYNOPSIS
Safely creates, maintains, launches and checks isolated Chromium browser environments.
.DESCRIPTION
Windows-only. No administrator rights required. Never closes unrelated browser processes.
Connect checks listener/process identity and CDP HTTP; visual actions require external MCP.
.EXAMPLE
.\Browser-Environment.ps1 -Action Create -Name AI-Agent-Browser -CreateShortcut
.EXAMPLE
.\Browser-Environment.ps1 -Action Connect -Name AI-Agent-Browser -NavigateTest
#>
[CmdletBinding()]
param(
    [ValidateSet('Create','Start','Status','Repair','Connect','Reset')][string]$Action = 'Status',
    [ValidatePattern('^[A-Za-z][A-Za-z0-9-]{1,62}$')][string]$Name = 'AI-Agent-Browser',
    [ValidateSet('Edge','Chrome')][string]$Browser = 'Edge',
    [ValidateRange(1024,65535)][int]$CdpPort = 9222,
    [string]$BrowserExecutable,
    [switch]$CreateShortcut,
    [switch]$NavigateTest,
    [switch]$ConfirmReset
)
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
if ([Environment]::OSVersion.Platform -ne [PlatformID]::Win32NT) { throw 'Windows is required for this PowerShell implementation.' }
$managementRoot = Join-Path $env:LOCALAPPDATA 'AI-Browser-Environments'
$profilesRoot = Join-Path $env:LOCALAPPDATA 'AI-Browser-Profiles'
$environmentRoot = Join-Path $managementRoot $Name
$configPath = Join-Path $environmentRoot 'environment.json'

function Get-BrowserExecutable([string]$kind, [string]$override) {
    if ($override) {
        $candidate = [IO.Path]::GetFullPath([Environment]::ExpandEnvironmentVariables($override))
        if (-not (Test-Path -LiteralPath $candidate -PathType Leaf)) { throw "Executable not found: $candidate" }
        return $candidate
    }
    $roots = @(${env:ProgramFiles(x86)},$env:ProgramFiles,$env:LOCALAPPDATA) | Where-Object { $_ }
    $suffixes = if ($kind -eq 'Edge') { @('Microsoft\Edge\Application\msedge.exe') } else { @('Google\Chrome\Application\chrome.exe') }
    foreach ($root in $roots) { foreach ($suffix in $suffixes) {
        $file = Join-Path $root $suffix
        if (Test-Path -LiteralPath $file -PathType Leaf) { return [IO.Path]::GetFullPath($file) }
    }}
    throw "$kind was not found. Provide -BrowserExecutable explicitly."
}
function Get-Config {
    if (-not (Test-Path -LiteralPath $configPath -PathType Leaf)) { throw "Unknown environment: $Name. Use -Action Create first." }
    $config = Get-Content -LiteralPath $configPath -Raw -Encoding UTF8 | ConvertFrom-Json
    if ($config.schemaVersion -ne 1 -or $config.name -cne $Name -or $config.browser -notin @('Edge','Chrome')) { throw 'Environment configuration is invalid.' }
    $expected = [IO.Path]::GetFullPath((Join-Path $profilesRoot $Name)).TrimEnd('\')
    $actual = [IO.Path]::GetFullPath([string]$config.userDataDirectory).TrimEnd('\')
    if (-not [string]::Equals($expected,$actual,[StringComparison]::OrdinalIgnoreCase)) { throw 'User-data directory is outside the managed dedicated environment.' }
    if (-not (Test-Path -LiteralPath $config.executable -PathType Leaf)) { throw 'Configured browser executable no longer exists. Repair requires a deliberate executable update.' }
    if ([int]$config.cdpPort -lt 1024 -or [int]$config.cdpPort -gt 65535) { throw 'Invalid CDP port.' }
    return $config
}
function Get-BrowserProcesses([object]$config) {
    $name = if ($config.browser -eq 'Edge') { 'msedge.exe' } else { 'chrome.exe' }
    $expected = [IO.Path]::GetFullPath([string]$config.userDataDirectory).TrimEnd('\')
    # Require an exact quoted or unquoted --user-data-dir argument, not a substring.
    @(Get-CimInstance Win32_Process -Filter "Name = '$name'" | Where-Object {
        $cmd = [string]$_.CommandLine
        $found = [regex]::Match($cmd,'(?:^|\s)--user-data-dir=(?:"([^"]+)"|(\S+))')
        $folder = if ($found.Success) { if ($found.Groups[1].Success) { $found.Groups[1].Value } else { $found.Groups[2].Value } } else { '' }
        $folder -and [string]::Equals([IO.Path]::GetFullPath($folder).TrimEnd('\'),$expected,[StringComparison]::OrdinalIgnoreCase)
    })
}
function Get-Listener([int]$port) {
    @(Get-NetTCPConnection -LocalPort $port -State Listen -ErrorAction SilentlyContinue)
}
function Test-DedicatedCDP([object]$config, [switch]$ListPages) {
    $port = [int]$config.cdpPort
    $processes = @(Get-BrowserProcesses $config)
    if ($processes.Count -eq 0) { throw 'No running browser process matches the configured user-data directory.' }
    $listeners = @(Get-Listener $port)
    if ($listeners.Count -eq 0) { throw "No CDP listener found on port $port." }
    if (@($listeners | Where-Object { $_.LocalAddress -notin @('127.0.0.1','::1') }).Count -gt 0) { throw 'Remote debugging is exposed on a non-loopback address. Refusing connection.' }
    $owners = @($processes | ForEach-Object { [int]$_.ProcessId })
    if (@($listeners | Where-Object { [int]$_.OwningProcess -notin $owners }).Count -gt 0) { throw 'The CDP listener is owned by a process outside this environment.' }
    $main = @($processes | Where-Object { $_.CommandLine -notmatch '(?:^|\s)--type=' })
    if ($main.Count -ne 1) { throw 'Ambiguous browser parent process. Refusing connection.' }
    $command = [string]$main[0].CommandLine
    if ($command -notmatch ('(?:^|\s)--remote-debugging-port=' + [regex]::Escape([string]$port) + '(?:\s|$)')) { throw 'Browser did not start with the expected CDP port.' }
    if ($command -notmatch '(?:^|\s)--remote-debugging-address=127\.0\.0\.1(?:\s|$)') { throw 'Missing explicit loopback-only debugging address.' }
    $base = "http://127.0.0.1:$port"
    $version = Invoke-RestMethod -Uri "$base/json/version" -TimeoutSec 5
    $prefix = if ($config.browser -eq 'Edge') { 'Edg/' } else { 'Chrome/' }
    if (-not ([string]$version.Browser).StartsWith($prefix)) { throw "Browser identity mismatch: $($version.Browser)" }
    if ([string]$version.webSocketDebuggerUrl -notlike "ws://127.0.0.1:$port/*") { throw 'Unexpected CDP WebSocket endpoint.' }
    $tabs = @()
    if ($ListPages) { $tabs = @(Invoke-RestMethod -Uri "$base/json/list" -TimeoutSec 5) }
    [pscustomobject]@{ status='CDP_VERIFIED'; name=$config.name; browser=$version.Browser; dataDirectory=$config.userDataDirectory; cdpEndpoint=$base; parentPid=$main[0].ProcessId; tabs=$tabs.Count; activeProfile='NOT_VERIFIED_REQUIRES_EDGE_VERSION_OR_AGENT' }
}
function Set-DesktopShortcut([object]$config) {
    $desktop = [Environment]::GetFolderPath('Desktop')
    $path = Join-Path $desktop ("$($config.name) - $($config.browser).lnk")
    $shell = New-Object -ComObject WScript.Shell
    $shortcut = $shell.CreateShortcut($path)
    $shortcut.TargetPath = [string]$config.executable
    $shortcut.Arguments = ('--user-data-dir="{0}" --remote-debugging-address=127.0.0.1 --remote-debugging-port={1} --no-first-run --no-default-browser-check' -f $config.userDataDirectory,$config.cdpPort)
    $shortcut.WorkingDirectory = Split-Path -Path $config.executable -Parent
    $shortcut.IconLocation = "$($config.executable),0"
    $shortcut.Description = 'Isolated browser for AI agent automation'
    $shortcut.Save()
    Write-Host "Desktop shortcut: $path"
}
function Start-DedicatedBrowser([object]$config) {
    $existing = @(Get-BrowserProcesses $config)
    if ($existing.Count -gt 0) {
        Write-Host 'Existing dedicated browser processes detected. Not launching a duplicate.'
        return
    }
    if (@(Get-Listener ([int]$config.cdpPort)).Count -gt 0) { throw 'CDP port is already in use by another process.' }
    $arguments = @(
        ('--user-data-dir="{0}"' -f $config.userDataDirectory),
        '--remote-debugging-address=127.0.0.1',
        ('--remote-debugging-port={0}' -f $config.cdpPort),
        '--no-first-run',
        '--no-default-browser-check'
    ) -join ' '
    Start-Process -FilePath $config.executable -ArgumentList $arguments | Out-Null
    Write-Host 'Browser launch requested. Wait for CDP verification; this message is not proof of successful connection.'
}

switch ($Action) {
    'Create' {
        if (Test-Path -LiteralPath $environmentRoot) { throw 'Environment already exists; Create will never overwrite it.' }
        $profile = Join-Path $profilesRoot $Name
        if (Test-Path -LiteralPath $profile) { throw 'A browser profile directory with this name already exists; refusing to adopt or overwrite it.' }
        if (@(Get-Listener $CdpPort).Count -gt 0) { throw 'Requested CDP port is occupied.' }
        $exe = Get-BrowserExecutable $Browser $BrowserExecutable
        New-Item -ItemType Directory -Path $environmentRoot -Force | Out-Null
        New-Item -ItemType Directory -Path $profile -Force | Out-Null
        $config = [ordered]@{ schemaVersion=1; name=$Name; browser=$Browser; executable=$exe; userDataDirectory=$profile; cdpPort=$CdpPort; createdAt=[DateTimeOffset]::Now.ToString('o') }
        $config | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath $configPath -Encoding UTF8
        Write-Host "Created configuration: $configPath (browser not yet launched)"
        if ($CreateShortcut) { Set-DesktopShortcut $config }
        Start-DedicatedBrowser $config
        Start-Sleep -Seconds 2
        try { Test-DedicatedCDP $config | Format-List } catch { Write-Warning "Startup verification pending/failed: $($_.Exception.Message)" }
    }
    'Start' { Start-DedicatedBrowser (Get-Config) }
    'Status' {
        $config = Get-Config
        Write-Host "Environment: $($config.name) | Data directory: $($config.userDataDirectory)"
        Write-Host "Matching processes: $(@(Get-BrowserProcesses $config).Count)"
        try { Test-DedicatedCDP $config | Format-List } catch { Write-Warning $_.Exception.Message }
    }
    'Connect' {
        $config = Get-Config
        $result = Test-DedicatedCDP $config -ListPages
        $result | Format-List
        if ($NavigateTest) {
            $target = [uri]::EscapeDataString('https://example.com')
            $url = "http://127.0.0.1:$($config.cdpPort)/json/new?$target"
            $tab = Invoke-RestMethod -Uri $url -Method Put -TimeoutSec 10
            if ($tab.url -ne 'https://example.com/' -and $tab.url -ne 'https://example.com') { throw 'Browser did not report the expected test URL.' }
            Write-Host 'Test tab created via CDP. Screenshot and page-interaction tests still require an agent browser tool.'
        }
    }
    'Repair' {
        $config = Get-Config
        $processes = @(Get-BrowserProcesses $config)
        if ($processes.Count -gt 0) { Write-Host 'Browser is active. Existing profile and processes preserved.' }
        if ($CreateShortcut) { Set-DesktopShortcut $config }
        try { Test-DedicatedCDP $config | Format-List } catch { Write-Warning "Diagnostic only: $($_.Exception.Message)" }
        Write-Host 'Repair did not change profile contents or browser installation.'
    }
    'Reset' {
        if (-not $ConfirmReset) { throw 'Reset requires -ConfirmReset and explicit user approval.' }
        $config = Get-Config
        if (@(Get-BrowserProcesses $config).Count -gt 0) { throw 'Dedicated browser still running. Close only this environment first.' }
        $source = [string]$config.userDataDirectory
        $archive = "$source-Backup-$(Get-Date -Format yyyyMMdd-HHmmss)"
        if (Test-Path -LiteralPath $archive) { throw 'Backup destination already exists.' }
        if (Test-Path -LiteralPath $source) { Move-Item -LiteralPath $source -Destination $archive -ErrorAction Stop; Write-Host "Old profile archived at: $archive" }
        New-Item -ItemType Directory -Path $source | Out-Null
        Write-Host 'Fresh empty profile directory prepared. Existing configuration and shortcut preserved.'
    }
}
