Set-TestGroup 'Repository Scope'
$workPath = [System.IO.Path]::GetFullPath((Get-TestWork))
$repoRoot = [System.IO.Path]::GetFullPath((Join-Path (Join-Path (Get-TestRoot) '..') '..'))
$expectedParent = [System.IO.Path]::GetFullPath((Join-Path $repoRoot '.test-workspace'))
$actualParent = [System.IO.Path]::GetFullPath((Split-Path -Parent $workPath))
Assert-True 'TUI test data stays in the repository .test-workspace' ($actualParent.Equals($expectedParent, [System.StringComparison]::OrdinalIgnoreCase))
