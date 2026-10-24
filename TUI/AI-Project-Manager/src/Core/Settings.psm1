# Settings.psm1 - small per-user JSON settings file (UTF-8 without BOM, readable by 5.1 and 7).
Set-StrictMode -Version 2.0

$script:SettingsCache = $null
$script:SettingsPathCache = ''
$script:SettingsLastWrite = $null

function Get-SettingsPath { param([string]$AppName = 'AIPM') return (Join-Path (Get-AppDataDirectory -AppName $AppName -Override $env:AIPM_DATA_DIR) 'settings.json') }

function Get-UserSetting {
    param([Parameter(Mandatory)][string]$Name, [string]$Default = '')
    $p = Get-SettingsPath
    try {
        if ($script:SettingsCache -and $script:SettingsPathCache -eq $p -and $script:SettingsLastWrite) {
            if (Test-Path -LiteralPath $p -PathType Leaf) {
                $currentWrite = [System.IO.File]::GetLastWriteTimeUtc($p)
                if ($currentWrite -eq $script:SettingsLastWrite) {
                    if ($script:SettingsCache.ContainsKey($Name)) { return [string]$script:SettingsCache[$Name] }
                    return $Default
                }
            }
        }
        if (Test-Path -LiteralPath $p -PathType Leaf) {
            $raw = [System.IO.File]::ReadAllText($p)
            $j = $raw | ConvertFrom-Json
            $cache = @{}
            if ($j) {
                foreach ($pr in $j.PSObject.Properties) { $cache[$pr.Name] = [string]$pr.Value }
            }
            $script:SettingsCache = $cache
            $script:SettingsPathCache = $p
            $script:SettingsLastWrite = [System.IO.File]::GetLastWriteTimeUtc($p)
            if ($cache.ContainsKey($Name)) { return [string]$cache[$Name] }
        } else {
            $script:SettingsCache = @{}
            $script:SettingsPathCache = $p
            $script:SettingsLastWrite = $null
        }
    } catch { }
    return $Default
}

function Set-UserSetting {
    param([Parameter(Mandatory)][string]$Name, [Parameter(Mandatory)][AllowEmptyString()][string]$Value)
    $p = Get-SettingsPath
    $h = @{}
    try {
        if (Test-Path -LiteralPath $p -PathType Leaf) {
            foreach ($pr in ([System.IO.File]::ReadAllText($p) | ConvertFrom-Json).PSObject.Properties) { $h[$pr.Name] = $pr.Value }
        }
    } catch { }
    $h[$Name] = $Value
    try {
        $dir = Split-Path -Parent $p
        if (-not (Test-Path -LiteralPath $dir)) { [void](New-Item -ItemType Directory -Path $dir -Force) }
        [System.IO.File]::WriteAllText($p, ($h | ConvertTo-Json), (New-Object System.Text.UTF8Encoding($false)))
        $script:SettingsCache = $h.Clone()
        $script:SettingsPathCache = $p
        $script:SettingsLastWrite = [System.IO.File]::GetLastWriteTimeUtc($p)
        return $true
    } catch { return $false }   # a read-only profile must never crash the app
}

Export-ModuleMember -Function Get-SettingsPath, Get-UserSetting, Set-UserSetting
