# Theme.psm1 - the ONE place for colors and icons. Other modules ask for a ROLE or an icon NAME, never a color/glyph.
# Icons come in three tiers: Emoji (modern terminals), Symbol (single-column glyphs from the Windows Glyph List 4, drawn by
# every console font) and Ascii (redirected output / forced). A new icon needs all three forms.
Set-StrictMode -Version 2.0
$script:ColorMode = 'Full'
$script:Accent = 'Cyan'
$script:Tier = ''   # the tier in use; empty = detect on first use (tests and the settings screen can override it)
$script:IconTableCache = $null
$script:ThemeRoles = $null

function ConvertFrom-CodePoint { param([int]$Code) return [char]::ConvertFromUtf32($Code) }
function Get-AipmUxRoot {
    $path = $PSScriptRoot
    for ($i = 0; $i -lt 4; $i++) { $path = Split-Path -Parent $path }
    return [System.IO.Path]::GetFullPath($path)
}
function Get-SemanticGlyph {
    param([string]$Code, [string]$Ascii)
    if ($Code -match '^U\+([0-9A-Fa-f]{4,6})$') { return (ConvertFrom-CodePoint ([Convert]::ToInt32($Matches[1],16))) }
    return $Ascii
}
function Get-ThemeRoles {
    if ($script:ThemeRoles) { return $script:ThemeRoles }
    $path = Join-Path (Join-Path (Get-AipmUxRoot) 'UX-TUI') 'theme.json'
    try { $script:ThemeRoles = ([System.IO.File]::ReadAllText($path) | ConvertFrom-Json -ErrorAction Stop).roles }
    catch { $script:ThemeRoles = $null }
    return $script:ThemeRoles
}
function Get-ThemeAnsiIndex {
    param([string]$Hex, [int]$Default = 7)
    if ($Hex -notmatch '^#([0-9A-Fa-f]{6})$') { return $Default }
    $value = $Matches[1]
    $r = [int][Math]::Round(([Convert]::ToInt32($value.Substring(0,2),16)) / 51.0)
    $g = [int][Math]::Round(([Convert]::ToInt32($value.Substring(2,2),16)) / 51.0)
    $b = [int][Math]::Round(([Convert]::ToInt32($value.Substring(4,2),16)) / 51.0)
    return 16 + (36 * $r) + (6 * $g) + $b
}

function Get-IconTable {
    if ($script:IconTableCache) { return $script:IconTableCache }
    $fallback = @{
        project=@{emoji='U+1F4C1';symbol='U+25A3';ascii='[P]'}; task=@{emoji='U+1F4CB';symbol='U+25A6';ascii='[T]'}
        agent=@{emoji='U+1F916';symbol='U+25C9';ascii='[A]'}; 'test-pass'=@{emoji='U+2705';symbol='U+2713';ascii='[OK]'}
        'test-fail'=@{emoji='U+274C';symbol='U+2717';ascii='[X]'}; warning=@{emoji='U+26A0';symbol='U+25B3';ascii='[!]'}
        handoff=@{emoji='U+1F4E4';symbol='U+21C4';ascii='[H]'}; settings=@{emoji='U+2699';symbol='U+2699';ascii='[S]'}
        arrow=@{emoji='U+27A1';symbol='U+2192';ascii='->'}; progress=@{emoji='U+1F7E2';symbol='U+25CF';ascii='[#]'}
    }
    $path = Join-Path (Join-Path (Get-AipmUxRoot) 'UX-TUI') 'semantic-icons.json'
    try {
        $manifest = [System.IO.File]::ReadAllText($path) | ConvertFrom-Json -ErrorAction Stop
        foreach ($name in $fallback.Keys) {
            $item = $manifest.icons.PSObject.Properties[$name]
            if ($item) { $fallback[$name] = @{ emoji=[string]$item.Value.emoji; symbol=[string]$item.Value.symbol; ascii=[string]$item.Value.ascii } }
        }
    } catch { }
    $t = @{}
    foreach ($name in $fallback.Keys) { $item=$fallback[$name]; $t[$name]=@{ Emoji=(Get-SemanticGlyph $item.emoji $item.ascii); Symbol=(Get-SemanticGlyph $item.symbol $item.ascii); Ascii=$item.ascii } }
    $t.Run=$t.arrow; $t.Form=$t.task; $t.Settings=$t.settings; $t.About=$t.progress; $t.Exit=$t.arrow
    $t.Success=$t['test-pass']; $t.Warning=$t.warning; $t.Error=$t['test-fail']; $t.Info=$t.progress; $t.Yes=$t['test-pass']; $t.No=$t['test-fail']; $t.Item=$t.project
    $script:IconTableCache = $t
    return $script:IconTableCache
}

function Resolve-IconTier {
    # Pure decision logic (unit tested). $Env is a hashtable of the relevant variables.
    #   Emoji  : modern terminals (Windows Terminal, VS Code, ConEmu, UTF-8 Linux/macOS)
    #   Symbol : classic Windows console (conhost / Windows PowerShell window): single-column WGL4 glyphs
    #   Ascii  : redirected output, or forced
    # Overrides: AIPM_ICONS=emoji|symbol|ascii, AIPM_ASCII=1.
    param([hashtable]$Env, [bool]$IsWin, [bool]$Redirected, [bool]$Utf8Ok = $true)
    $force = ([string]$Env['AIPM_ICONS']).ToLowerInvariant()
    if ($force -eq 'emoji') { return 'Emoji' }
    if ($force -eq 'symbol') { return 'Symbol' }
    if ($force -eq 'ascii') { return 'Ascii' }
    if ($force -eq 'none') { return 'None' }
    if ($Env['AIPM_ASCII'] -eq '1') { return 'Ascii' }
    if ($Redirected) { return 'Ascii' }
    if (-not $IsWin) {
        if ([string]$Env['LANG'] -match 'UTF-?8' -or [string]$Env['LC_ALL'] -match 'UTF-?8') { return 'Emoji' }
        return 'Ascii'
    }
    if (-not $Utf8Ok) { return 'Ascii' }
    if ($Env['WT_SESSION'] -or $Env['TERM_PROGRAM'] -or $Env['ConEmuANSI'] -eq 'ON') { return 'Emoji' }
    return 'Symbol'
}

function Set-ConsoleUtf8Output {
    # Windows only: make the console write UTF-8 so the glyphs arrive unchanged. Also needed when output is redirected.
    if (-not (Test-IsWindows)) { return $true }
    try { [Console]::OutputEncoding = New-Object System.Text.UTF8Encoding($false); return $true } catch { return $false }
}

function Get-IconTier {
    $names = 'AIPM_ICONS', 'AIPM_ASCII', 'LANG', 'LC_ALL', 'WT_SESSION', 'TERM_PROGRAM', 'ConEmuANSI'
    $e = @{}; foreach ($n in $names) { $e[$n] = [Environment]::GetEnvironmentVariable($n) }
    if (-not $e['AIPM_ICONS'] -and $e['AIPM_ASCII'] -ne '1') {
        $saved = Get-UserSetting 'icons'
        if ($saved -in @('emoji', 'symbol', 'none')) { $e['AIPM_ICONS'] = $saved }   # the user's remembered choice
    }
    $redirected = $false
    try { $redirected = [Console]::IsOutputRedirected } catch { $redirected = $true }
    $win = Test-IsWindows
    $utf8 = $true
    if ($win) { $utf8 = Set-ConsoleUtf8Output }
    return (Resolve-IconTier -Env $e -IsWin $win -Redirected $redirected -Utf8Ok $utf8)
}

function Get-Icon {
    param([Parameter(Mandatory)][string]$Name, [string]$Tier = '')
    if (-not $Tier) { $Tier = $script:Tier; if (-not $Tier) { $Tier = Get-IconTier } }
    if ($Tier -eq 'None') { return '' }
    $t = Get-IconTable
    if (-not $t.ContainsKey($Name)) { $Name = 'Item' }
    return $t[$Name][$Tier]
}

function Set-IconTier { param([ValidateSet('Auto', 'Emoji', 'Symbol', 'Ascii', 'None')][string]$Tier) $script:Tier = $(if ($Tier -eq 'Auto') { '' } else { $Tier }) }
function Get-IconTierInUse { if ($script:Tier) { return $script:Tier } return (Get-IconTier) }

function Set-TuiColorStyle {
    param([ValidateSet('Full','Subtle','None','Auto')][string]$Mode = 'Full',
          [ValidateSet('Cyan','Teal','Blue','Green','Purple','Yellow','Gray','White','Magenta','Red')][string]$Accent = 'Cyan')
    $script:ColorMode = $Mode; $script:Accent = $Accent
}
# Roles -> ANSI SGR codes and the legacy console color. Add a role here, never a color elsewhere.
function Get-RoleStyle {
    param([Parameter(Mandatory)][string]$Role)
    $s = @{
        Title    = @{ Ansi = '1;36'; Legacy = 'Cyan' }
        Heading  = @{ Ansi = '1;37'; Legacy = 'White' }
        Normal   = @{ Ansi = '0';    Legacy = 'Gray' }
        Dim      = @{ Ansi = '90';   Legacy = 'DarkGray' }
        Selected = @{ Ansi = '1;96'; Legacy = 'Cyan' }
        Number   = @{ Ansi = '36';   Legacy = 'Cyan' }
        Key      = @{ Ansi = '96';   Legacy = 'Cyan' }
        Success  = @{ Ansi = '32';   Legacy = 'Green' }
        Warning  = @{ Ansi = '33';   Legacy = 'Yellow' }
        Error    = @{ Ansi = '31';   Legacy = 'Red' }
        Info     = @{ Ansi = '34';   Legacy = 'Blue' }
    }
    $acc = @{ Cyan = '36'; Teal = '36'; Blue = '34'; Green = '32'; Purple = '35'; Yellow = '33'; Gray = '37'; White = '37'; Magenta = '35'; Red = '31' }
    $legacy = @{ Cyan = 'Cyan'; Teal = 'Cyan'; Blue = 'Blue'; Green = 'Green'; Purple = 'Magenta'; Yellow = 'Yellow'; Gray = 'Gray'; White = 'White'; Magenta = 'Magenta'; Red = 'Red' }
    if ($Role -eq 'Description') {
        if ($script:ColorMode -eq 'None' -or $env:NO_COLOR) { return @{ Ansi = '2'; Legacy = 'DarkGray' } }
        $theme = Get-ThemeRoles
        if ($theme) { return @{ Ansi = ('2;38;5;' + (Get-ThemeAnsiIndex ([string]$theme.muted) 7) + ';48;5;236'); Legacy = 'DarkGray' } }
        return @{ Ansi = '2;37;48;5;236'; Legacy = 'DarkGray' }
    }
    if ($script:ColorMode -eq 'None' -or $env:NO_COLOR) {
        return @{ Ansi = $(if ($Role -eq 'Selected') { '1;7' } else { '0' }); Legacy = $(if ($Role -eq 'Selected') { 'White' } else { 'Gray' }) }
    }
    if ($Role -in @('Title','Selected','Number','Key')) {
        $shade = $(if ($script:ColorMode -eq 'Subtle') { '0;' } else { '1;' })
        if ($Role -eq 'Selected') {
            $theme = Get-ThemeRoles
            $selected = if ($theme) { Get-ThemeAnsiIndex ([string]$theme.selected) 24 } else { 24 }
            return @{ Ansi = ($shade + '97;48;5;' + $selected); Legacy = $legacy[$script:Accent] }
        }
        return @{ Ansi = ($shade + $acc[$script:Accent]); Legacy = $legacy[$script:Accent] }
    }
    if ($s.ContainsKey($Role)) {
        $theme = Get-ThemeRoles
        if ($theme) {
            $themeKey = switch ($Role) { 'Normal' { 'text' } 'Dim' { 'muted' } 'Success' { 'success' } 'Warning' { 'warning' } 'Error' { 'error' } 'Info' { 'accent' } default { '' } }
            if ($themeKey -and $theme.PSObject.Properties[$themeKey]) {
                $index = Get-ThemeAnsiIndex ([string]$theme.$themeKey) 7
                return @{ Ansi = ('38;5;' + $index); Legacy = $s[$Role].Legacy }
            }
        }
        return $s[$Role]
    }
    return $s['Normal']
}

Export-ModuleMember -Function Get-IconTable, Resolve-IconTier, Set-ConsoleUtf8Output, Get-IconTier, Get-Icon, Set-IconTier, Get-IconTierInUse, Set-TuiColorStyle, Get-RoleStyle, Get-ThemeRoles
