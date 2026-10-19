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
$authorizedLegacyEnvironment = [ordered]@{ name='AI-Agent-Browser'; browser='Edge'; executable='C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe'; userDataDirectory='C:\Users\Abdoo\AppData\Local\IB-Edge-Debug'; cdpPort=9222 }

function Get-NormalizedPath([string]$path) { [IO.Path]::GetFullPath([Environment]::ExpandEnvironmentVariables($path)).TrimEnd('\') }
function Test-PathEqual([string]$left, [string]$right) { [string]::Equals((Get-NormalizedPath $left),(Get-NormalizedPath $right),[StringComparison]::OrdinalIgnoreCase) }
function Get-CommandLineSwitchValue([string]$commandLine, [string]$switchName) {
    $match = [regex]::Match($commandLine,'(?:^|\s)' + [regex]::Escape($switchName) + '(?:=|\s+)(?:"([^"]+)"|(\S+))')
    if (-not $match.Success) { return $null }; if ($match.Groups[1].Success) { return $match.Groups[1].Value }; return $match.Groups[2].Value
}
function Test-AuthorizedLegacyConfig([object]$config) {
    ($Name -ceq 'AI-Agent-Browser') -and ($config.browser -ceq 'Edge') -and
    (Test-PathEqual ([string]$config.userDataDirectory) 'C:\Users\Abdoo\AppData\Local\IB-Edge-Debug') -and ([int]$config.cdpPort -eq 9222)
}
function Register-AuthorizedLegacyEnvironment {
    if ($Name -cne 'AI-Agent-Browser') { throw 'UNKNOWN_ENVIRONMENT: this name has no authorized legacy environment.' }
    $data = 'C:\Users\Abdoo\AppData\Local\IB-Edge-Debug'; $exe = 'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe'
    if (-not (Test-Path -LiteralPath $data -PathType Container)) { throw 'LEGACY_PROFILE_NOT_FOUND: authorized dedicated data directory is absent.' }
    if (-not (Test-Path -LiteralPath $exe -PathType Leaf)) { throw 'LEGACY_EXECUTABLE_NOT_FOUND: authorized Edge executable is absent.' }
    New-Item -ItemType Directory -Path $environmentRoot -Force | Out-Null
    $config = [ordered]@{ schemaVersion=1; name='AI-Agent-Browser'; browser='Edge'; executable=$exe; userDataDirectory=$data; cdpPort=9222; managedReference=$true; registeredAt=[DateTimeOffset]::Now.ToString('o') }
    $config | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath $configPath -Encoding UTF8
    Write-Host "CONFIGURED: registered authorized metadata reference at $configPath; profile data was not copied or changed."
    return [pscustomobject]$config
}

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
    if (-not (Test-Path -LiteralPath $configPath -PathType Leaf)) { return Register-AuthorizedLegacyEnvironment }
    $config = Get-Content -LiteralPath $configPath -Raw -Encoding UTF8 | ConvertFrom-Json
    if ($config.schemaVersion -ne 1 -or $config.name -cne $Name -or $config.browser -notin @('Edge','Chrome')) { throw 'Environment configuration is invalid.' }
    $expected = Get-NormalizedPath (Join-Path $profilesRoot $Name)
    $actual = Get-NormalizedPath ([string]$config.userDataDirectory)
    if (-not (Test-PathEqual $expected $actual) -and -not (Test-AuthorizedLegacyConfig $config)) { throw 'UNAUTHORIZED_USER_DATA_DIRECTORY: configuration is outside the managed dedicated environment.' }
    if (-not (Test-Path -LiteralPath $config.executable -PathType Leaf)) { throw 'Configured browser executable no longer exists. Repair requires a deliberate executable update.' }
    if ([int]$config.cdpPort -lt 1024 -or [int]$config.cdpPort -gt 65535) { throw 'Invalid CDP port.' }
    return $config
}
function Get-BrowserProcesses([object]$config) {
    $name = if ($config.browser -eq 'Edge') { 'msedge.exe' } else { 'chrome.exe' }
    $expected = Get-NormalizedPath ([string]$config.userDataDirectory)
    # Require an exact quoted or unquoted --user-data-dir argument, not a substring.
    try { @(Get-CimInstance Win32_Process -Filter "Name = '$name'" -ErrorAction Stop | Where-Object {
        $cmd = [string]$_.CommandLine
        $folder = Get-CommandLineSwitchValue $cmd '--user-data-dir'
        $folder -and (Test-PathEqual $folder $expected)
    }) } catch { throw "PROCESS_INSPECTION_UNAVAILABLE: $($_.Exception.Message)" }
}
function Get-Listener([int]$port) {
    try { @(Get-NetTCPConnection -LocalPort $port -State Listen -ErrorAction Stop) } catch { throw "LISTENER_INSPECTION_UNAVAILABLE: $($_.Exception.Message)" }
}
function Test-DedicatedCDP([object]$config, [switch]$ListPages) {
    $port = [int]$config.cdpPort
    $processes = @(Get-BrowserProcesses $config)
    if ($processes.Count -eq 0) { throw 'No running browser process matches the configured user-data directory.' }
    $listeners = @(Get-Listener $port)
    if ($listeners.Count -eq 0) { throw "No CDP listener found on port $port." }
    if (@($listeners | Where-Object { $_.LocalAddress -notin @('127.0.0.1','::1') }).Count -gt 0) { throw 'Remote debugging is exposed on a non-loopback address. Refusing connection.' }
    $main = @($processes | Where-Object { $_.CommandLine -notmatch '(?:^|\s)--type=' })
    if ($main.Count -ne 1) { throw 'PARENT_PROCESS_AMBIGUOUS: refusing connection.' }
    $command = [string]$main[0].CommandLine
    if ((Get-CommandLineSwitchValue $command '--remote-debugging-port') -ne [string]$port) { throw 'CDP_PORT_MISMATCH: browser did not start with the expected CDP port.' }
    if ((Get-CommandLineSwitchValue $command '--remote-debugging-address') -cne '127.0.0.1') { throw 'CDP_ADDRESS_NOT_LOOPBACK: missing explicit loopback-only debugging address.' }
    if (@($listeners | Where-Object { [int]$_.OwningProcess -ne [int]$main[0].ProcessId }).Count -gt 0) { throw 'LISTENER_OWNER_MISMATCH: refusing connection.' }
    $base = "http://127.0.0.1:$port"
    $version = Invoke-RestMethod -Uri "$base/json/version" -TimeoutSec 5
    $prefix = if ($config.browser -eq 'Edge') { 'Edg/' } else { 'Chrome/' }
    if (-not ([string]$version.Browser).StartsWith($prefix)) { throw "Browser identity mismatch: $($version.Browser)" }
    if ([string]$version.webSocketDebuggerUrl -notlike "ws://127.0.0.1:$port/*") { throw 'Unexpected CDP WebSocket endpoint.' }
    $tabs = @()
    if ($ListPages) { $tabs = @(Invoke-RestMethod -Uri "$base/json/list" -TimeoutSec 5) }
    [pscustomobject]@{ status='CDP_VERIFIED'; name=$config.name; browser=$version.Browser; dataDirectory=$config.userDataDirectory; cdpEndpoint=$base; parentPid=$main[0].ProcessId; tabs=$tabs.Count; activeProfile='PROFILE_VERIFICATION_REQUIRES_AGENT_TOOL'; screenshot='SCREENSHOT_NOT_RUN' }
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
    Write-Host 'BROWSER_START_REQUESTED: waiting for dedicated CDP verification.'
}
function Wait-DedicatedCDP([object]$config, [int]$TimeoutSeconds = 15) {
    $deadline = [DateTime]::UtcNow.AddSeconds($TimeoutSeconds); $lastError = $null
    do { try { return Test-DedicatedCDP $config -ListPages } catch { $lastError = $_.Exception.Message; Start-Sleep -Seconds 1 } } while ([DateTime]::UtcNow -lt $deadline)
    throw "STARTUP_TIMEOUT: $lastError"
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
        try { Wait-DedicatedCDP $config | Format-List } catch { Write-Warning "Startup verification failed: $($_.Exception.Message)" }
    }
    'Start' { $config = Get-Config; Start-DedicatedBrowser $config; Wait-DedicatedCDP $config | Format-List }
    'Status' {
        $config = Get-Config
        Write-Host "Environment: $($config.name) | Data directory: $($config.userDataDirectory)"
        Write-Host "Matching processes: $(@(Get-BrowserProcesses $config).Count)"
        try { Test-DedicatedCDP $config | Format-List } catch { Write-Warning $_.Exception.Message }
    }
    'Connect' {
        $config = Get-Config
        if (@(Get-BrowserProcesses $config).Count -eq 0) { Start-DedicatedBrowser $config }
        $result = Wait-DedicatedCDP $config
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
