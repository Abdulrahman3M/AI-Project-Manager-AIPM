# Prompt.psm1 - typed input with help text, an example and validation. Free typing is only for values that are truly free-form.
Set-StrictMode -Version 2.0

function Write-PromptInput {
    # Render the editable value as physical UI rows. Rendering it as one logical row
    # lets the terminal wrap it independently, which displaces the rows that follow.
    param([AllowEmptyString()][string]$Text)
    $width = [Math]::Max(1, (Get-TerminalSize).Width - 2)
    $remaining = $Text
    $first = $true
    do {
        $prefix = if ($first) { '> ' } else { '  ' }
        $segmentLength = [Math]::Min($width, $remaining.Length)
        $segment = if ($segmentLength -gt 0) { $remaining.Substring(0, $segmentLength) } else { '' }
        Write-UiLine ($prefix + $segment) 'Normal'
        $remaining = if ($segmentLength -lt $remaining.Length) { $remaining.Substring($segmentLength) } else { '' }
        $first = $false
    } while ($remaining.Length -gt 0)
}

function Read-ValidatedInput {
    # -Validate is a scriptblock: param($text) -> $null when valid, otherwise the error message to show.
    # Returns the accepted text, or $null when the user presses Esc (cancel).
    param([Parameter(Mandatory)][string]$Prompt, [Parameter(Mandatory)][string]$Help, [Parameter(Mandatory)][string]$Example, [scriptblock]$Validate, [string]$Default = '')
    $text = $Default; $err = ''
    while ($true) {
        Clear-Ui
        Write-UiLine ((Get-Icon 'Form') + '  ' + $Prompt) 'Title'
        Write-UiLine ''
        Write-UiLine ('  ' + $Help) 'Dim'
        Write-UiLine ('  Example: ' + $Example) 'Dim'
        if ($err) { Write-UiLine ''; Write-UiLine ('  ' + (Get-Icon 'Error') + '  ' + $err) 'Error' }
        Write-UiLine ''
        Write-PromptInput -Text $text
        Write-Ui 'Enter ' 'Key'; Write-Ui 'Confirm   ' 'Dim'; Write-Ui 'Esc ' 'Key'; Write-UiLine 'Cancel' 'Dim'
        Complete-UiFrame
        $k = Read-AppKey
        switch ($k.Name) {
            'CtrlC' { throw (New-Object System.OperationCanceledException('Quit')) }
            'Esc' { return $null }
            'Backspace' { if ($text.Length -gt 0) { $text = $text.Substring(0, $text.Length - 1) } }
            'Char' { $text += $k.Char; $err = '' }
            'Enter' {
                $msg = $null
                if ($Validate) { $msg = & $Validate $text }
                if (-not $msg) { return $text }
                $err = [string]$msg
            }
        }
    }
}

Export-ModuleMember -Function Read-ValidatedInput
