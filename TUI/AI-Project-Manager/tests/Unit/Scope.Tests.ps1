Set-TestGroup 'Repository Scope'
$workPath = [System.IO.Path]::GetFullPath((Get-TestWork))
$repoRoot = [System.IO.Path]::GetFullPath((Get-SourceRepositoryRoot))
$expectedParent = [System.IO.Path]::GetFullPath((Join-Path $repoRoot 'Shared-Project-State-Manager/Test-Workspace'))
$actualParent = [System.IO.Path]::GetFullPath((Split-Path -Parent $workPath))
Assert-True 'TUI test data stays in the shared test workspace' ($actualParent.Equals($expectedParent, [System.StringComparison]::OrdinalIgnoreCase))
