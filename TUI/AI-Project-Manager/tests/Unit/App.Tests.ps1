Set-TestGroup 'Evidence-Based App View Models'

$updaterCapture = @{ Path = ''; Argument = '' }
$fakeUpdater = { param($path, $arguments) $updaterCapture.Path = $path; $updaterCapture.Argument = [string]$arguments[0]; return [pscustomobject]@{ Id = 123 } }.GetNewClosure()
$updaterStarted = Start-AipmGitUpdater -GitPath 'C:\Git With Spaces\git.exe' -Launcher $fakeUpdater
Assert-Equal 'Git updater reports only that the process started' 'STARTED' $updaterStarted.Status
Assert-Equal 'Git updater receives the selected executable without shell interpolation' 'C:\Git With Spaces\git.exe' $updaterCapture.Path
Assert-Equal 'Git updater uses the official Git for Windows command' 'update-git-for-windows' $updaterCapture.Argument
$updaterBlocked = Start-AipmGitUpdater -GitPath 'missing' -Launcher { param($path, $arguments) throw 'test failure' }
Assert-Equal 'Git updater launch errors are reported without claiming success' 'BLOCKED' $updaterBlocked.Status

$verifiedTask = [pscustomobject]@{
    title = 'Verify The Dashboard'
    scope = 'Core State Projection'
    blockers = @()
    verification = [pscustomobject]@{ result = 'PASS'; evidence = 'Focused Core suite passed.' }
    report = 'The dashboard was verified.'
}
$verifiedState = [pscustomobject]@{
    active_phase = 'P08'
    task_id = 'Task-P08'
    task_status = 'COMPLETE'
    tasks = [pscustomobject]@{ 'Task-P08' = $verifiedTask }
    updated_at = '2026-10-16T10:00:00Z'
    updated_by = 'aipm-core'
    branch = 'main'
    head_sha = 'abc123'
    next_action = 'Continue UI verification.'
}
$project = [pscustomobject]@{ project_id = 'P08-Fixture'; alias = 'AIPM Fixture'; state_status = 'PASS'; state = $verifiedState; reason = $null }
$summary = Get-AipmProjectSummary -Project $project
Assert-Equal 'project title comes from Core registry metadata' 'AIPM Fixture' $summary.Name
Assert-Equal 'active phase comes from verified Core state' 'P08' $summary.Phase
Assert-Equal 'active task comes from verified Core state' 'Task-P08' $summary.TaskId
Assert-Equal 'task verification evidence is counted without inventing test runs' 1 $summary.VerifiedTaskCount
Assert-Equal 'test run count remains unverified when Core has no test artifact' 'Unverified' $summary.TestsStatus
Assert-Equal 'agent session remains unknown without host evidence' 'Unknown' $summary.AgentStatus
Assert-Equal 'progress remains unknown when no verified weights exist' 'Unknown' $summary.Progress

$unreadable = [pscustomobject]@{ project_id = 'P08-Broken'; alias = 'Broken Fixture'; state_status = 'UNVERIFIED'; state = $null; reason = 'INVALID_STATE' }
$safeSummary = Get-AipmProjectSummary -Project $unreadable
Assert-Equal 'unreadable project state is never shown as complete' 'Unverified' $safeSummary.Status
Assert-Equal 'unreadable project phase is unknown' 'Unknown' $safeSummary.Phase
Assert-Equal 'unreadable project progress is unknown rather than zero' 'Unknown' $safeSummary.Progress
Assert-Equal 'zero task records do not become zero percent progress' 'Evidence Coverage: Unknown (No Verifiable Tasks)' (Format-AipmEvidenceCoverage -Verified 0 -Total 0)
Assert-Equal 'verified evidence coverage uses a separate, explicit denominator' '[##########] Evidence Coverage: 100% (4/4 Verified Tasks)' (Format-AipmEvidenceCoverage -Verified 4 -Total 4)

Set-TestGroup 'Capability Library projection'
$capabilityCatalog = [pscustomobject]@{
    status = 'PASS'
    catalog = [pscustomobject]@{
        integrity_status = 'UNVERIFIED'
        skill_count = 2
        skills = @(
            [pscustomobject]@{ slug='tui-intelligence'; version='1.0.0'; source_license='Apache License 2.0'; aipm_personal_license_applies=$true }
            [pscustomobject]@{ slug='audio-timing-author'; version='1.0.0'; source_license='Apache License 2.0'; aipm_personal_license_applies=$true }
        )
        plugin_sample = [pscustomobject]@{ version='0.1.0'; status='PACKAGE_SAMPLE_ONLY'; installation='UNVERIFIED'; publication='UNVERIFIED'; manifests=@('plugin.json') }
    }
}
$capabilityRows = $null
$missingCapabilityRows = $null
if (Get-Command Get-AipmCapabilityLibraryRows -ErrorAction SilentlyContinue) {
    $capabilityRows = Get-AipmCapabilityLibraryRows -Catalog $capabilityCatalog -Width 120
    $missingCapabilityRows = Get-AipmCapabilityLibraryRows -Catalog $null -Width 120
}
Assert-True 'catalog projection lists all AIPM-owned Skills together' ($null -ne $capabilityRows -and @($capabilityRows.Skills).Count -eq 2)
Assert-Equal 'AIPM-owned rows retain their full capability name without repeated license text' 'Audio Timing Author' $(if ($capabilityRows -and $capabilityRows.Skills.Count) { $capabilityRows.Skills[0].Capability } else { '' })
Assert-Equal 'Plugin package remains uninstalled and unpublished unless evidenced' 'Unverified,Unverified' $(if ($capabilityRows -and $capabilityRows.Plugins.Count) { $capabilityRows.Plugins[0].Installation + ',' + $capabilityRows.Plugins[0].Publication } else { '' })
Assert-Equal 'missing catalog is unverified and does not invent capability rows' 'Unverified,0' $(if ($missingCapabilityRows) { $missingCapabilityRows.CatalogStatus + ',' + $missingCapabilityRows.Skills.Count } else { '' })

Set-TestGroup 'Session Snapshot lifecycle'
$appModulePath = Join-Path (Join-Path (Get-TestRoot) 'src/Core') 'App.psm1'
$appModule = @(Get-Module | Where-Object { $_.Path -eq $appModulePath }) | Select-Object -First 1
$snapshotApiAvailable = [bool](Get-Command Get-AipmSessionSnapshot -ErrorAction SilentlyContinue) -and [bool](Get-Command Refresh-AipmSessionSnapshot -ErrorAction SilentlyContinue)
$sessionCoreLog = New-Object System.Collections.ArrayList
$sessionCoreFailure = @{ Enabled = $false; FailAt = 0 }
$sessionCoreResponses = @{
    dashboard = [pscustomobject]@{ Status='PASS'; Reason=''; Data=[pscustomobject]@{ status='PASS'; registry_status='REGISTERED'; projects=@() } }
    catalog = [pscustomobject]@{ Status='PASS'; Reason=''; Data=$capabilityCatalog }
    'host-capabilities' = [pscustomobject]@{ Status='PASS'; Reason=''; Data=[pscustomobject]@{ matrix=[pscustomobject]@{ policy='READ_ONLY' } } }
}
$sessionCoreReader = {
    param($AppRoot, $Command, $RegistryPath)
    [void]$sessionCoreLog.Add($Command)
    if ($Command -eq 'dashboard' -and ($sessionCoreFailure.Enabled -or ($sessionCoreFailure.FailAt -gt 0 -and $sessionCoreLog.Count -ge $sessionCoreFailure.FailAt))) { return [pscustomobject]@{ Status='BLOCKED'; Reason='TEST_REFRESH_BLOCKED'; Data=$null } }
    return $sessionCoreResponses[$Command]
}.GetNewClosure()
$sessionDependencyReader = { param($AppRoot) [pscustomobject]@{ Status='PASS'; Reason=''; Version='3.12.0' } }
$snapshotLifecycleResults = @{
    NavigationUi = [pscustomobject]@{ Error='Snapshot API unavailable.' }
    NavigationReadCount = -1
    InitialSnapshot = [pscustomobject]@{ Status='UNAVAILABLE'; Dashboard=$null; Catalog=$null; Hosts=$null }
    SuccessfulRefresh = [pscustomobject]@{ Status='UNAVAILABLE'; Snapshot=$null }
    SuccessfulRefreshReadCount = 0
    FailedRefresh = [pscustomobject]@{ Status='UNAVAILABLE'; Preserved=$false; Reason='Snapshot API unavailable.'; Snapshot=$null }
}
if ($snapshotApiAvailable -and $appModule) {
    & $appModule {
        param($CoreReader, $DependencyReader)
        $script:SessionCoreReader = $CoreReader
        $script:SessionDependencyReader = $DependencyReader
    } $sessionCoreReader $sessionDependencyReader
    $navigationUi = Invoke-Ui { Start-TuiApp -Root (Get-TestRoot) -RegistryPath (Join-Path (Get-TestWork) 'snapshot-test-registry.json') } '13{Enter}14'
    $snapshotLifecycleResults.NavigationUi = $navigationUi
    $snapshotLifecycleResults.NavigationReadCount = $sessionCoreLog.Count
    $sessionCoreLog.Clear()
    $initialSnapshot = Get-AipmSessionSnapshot -Root (Get-TestRoot) -RegistryPath (Join-Path (Get-TestWork) 'snapshot-test-registry.json')
    $snapshotLifecycleResults.InitialSnapshot = $initialSnapshot
    $snapshotLifecycleResults.InitialReadCount = $sessionCoreLog.Count
    $sessionCoreLog.Clear()
    $successfulRefresh = Refresh-AipmSessionSnapshot -Root (Get-TestRoot) -RegistryPath (Join-Path (Get-TestWork) 'snapshot-test-registry.json') -CurrentSnapshot $initialSnapshot
    $snapshotLifecycleResults.SuccessfulRefresh = $successfulRefresh
    $snapshotLifecycleResults.SuccessfulRefreshReadCount = $sessionCoreLog.Count
    $sessionCoreFailure.Enabled = $true
    $sessionCoreLog.Clear()
    $failedRefresh = Refresh-AipmSessionSnapshot -Root (Get-TestRoot) -RegistryPath (Join-Path (Get-TestWork) 'snapshot-test-registry.json') -CurrentSnapshot $successfulRefresh.Snapshot
    $snapshotLifecycleResults.FailedRefresh = $failedRefresh
    $snapshotLifecycleResults.FailedRefreshReadCount = $sessionCoreLog.Count
    $sessionCoreFailure.Enabled = $false
    $sessionCoreFailure.FailAt = 4
    $sessionCoreLog.Clear()
    $failedRefreshUi = Invoke-Ui { Start-TuiApp -Root (Get-TestRoot) -RegistryPath (Join-Path (Get-TestWork) 'snapshot-test-registry.json') } '1214'
    $snapshotLifecycleResults.FailedRefreshUi = $failedRefreshUi
    $snapshotLifecycleResults.FailedRefreshUiReadCount = $sessionCoreLog.Count
    $sessionCoreFailure.FailAt = 0
    & $appModule { $script:SessionCoreReader = $null; $script:SessionDependencyReader = $null }
}
Assert-True 'ordinary menu and page navigation use one complete initial Core snapshot' ($snapshotApiAvailable -and $snapshotLifecycleResults.NavigationUi.Error -eq '' -and $snapshotLifecycleResults.NavigationReadCount -eq 3) $(if ($snapshotLifecycleResults.NavigationUi) { $snapshotLifecycleResults.NavigationUi.Error } else { 'Snapshot API unavailable.' })
Assert-True 'session snapshot contains dashboard, catalog, and host capability facts' ($snapshotLifecycleResults.InitialSnapshot.Status -eq 'PASS' -and $null -ne $snapshotLifecycleResults.InitialSnapshot.Dashboard -and $null -ne $snapshotLifecycleResults.InitialSnapshot.Catalog -and $null -ne $snapshotLifecycleResults.InitialSnapshot.Hosts)
Assert-Equal 'each explicit successful refresh requests one complete new snapshot' 3 $snapshotLifecycleResults.SuccessfulRefreshReadCount
Assert-True 'successful refresh replaces the previous immutable snapshot' ($snapshotLifecycleResults.SuccessfulRefresh.Status -eq 'PASS' -and -not [object]::ReferenceEquals($snapshotLifecycleResults.InitialSnapshot, $snapshotLifecycleResults.SuccessfulRefresh.Snapshot))
Assert-Equal 'a failed refresh reports blocked status and preserves the last known-good snapshot' 'BLOCKED,True,TEST_REFRESH_BLOCKED' $(if ($snapshotLifecycleResults.FailedRefresh) { $snapshotLifecycleResults.FailedRefresh.Status + ',' + $snapshotLifecycleResults.FailedRefresh.Preserved + ',' + $snapshotLifecycleResults.FailedRefresh.Reason } else { '' })
Assert-True 'failed refresh exposes the exact last known-good snapshot instance' ($snapshotLifecycleResults.FailedRefresh -and $snapshotLifecycleResults.SuccessfulRefresh.Snapshot -and $snapshotLifecycleResults.FailedRefresh.Snapshot -and [object]::ReferenceEquals($snapshotLifecycleResults.SuccessfulRefresh.Snapshot, $snapshotLifecycleResults.FailedRefresh.Snapshot))
Assert-True 'the dashboard surfaces a failed Refresh while retaining the known-good session' ($snapshotLifecycleResults.FailedRefreshUi -and $snapshotLifecycleResults.FailedRefreshUi.Error -eq '' -and $snapshotLifecycleResults.FailedRefreshUi.Output.Contains('Refresh Failed: TEST_REFRESH_BLOCKED') -and $snapshotLifecycleResults.FailedRefreshUi.Output.Contains('Last Snapshot Preserved') -and $snapshotLifecycleResults.FailedRefreshUi.Output.Contains('Core Ready'))
Assert-Equal 'failed Refresh makes only one new Core call before preserving the snapshot' 4 $snapshotLifecycleResults.FailedRefreshUiReadCount

Set-TestGroup 'Task Management Regression'
$taskRegRoot = Join-Path (Get-TestWork) 'Task Creation Test Project'
[void](New-Item -ItemType Directory -Path $taskRegRoot -Force)
$taskRegRegistry = Join-Path (Get-TestWork) 'task-creation-regression-registry.json'
$taskRegProjectId = 'Task-Create-' + [guid]::NewGuid().ToString('N').Substring(0, 8)
$regResult = Invoke-AipmCore -AppRoot (Get-TestRoot) -Command 'registry-register' -RegistryPath $taskRegRegistry -ProjectRoot $taskRegRoot -ProjectId $taskRegProjectId -Alias 'Task Create Regression Fixture'
Assert-Equal 'project registers for task creation test' 'PASS' $regResult.Status

$createKeys = '02' + '01' + '01' + 'Regression Test Task{Enter}' + 'Verify task creation under strict mode{Enter}' + '{Enter}' + '05' + '02' + '14'
$createUi = Invoke-Ui { Start-TuiApp -Root (Get-TestRoot) -RegistryPath $taskRegRegistry } $createKeys
Assert-True 'Create New Task completes without uninitialized folderPath error' ($createUi.Error -eq '' -and -not $createUi.Output.Contains('folderPath')) ($createUi.Error + $createUi.Output)
$createdList = Invoke-AipmCore -AppRoot (Get-TestRoot) -Command 'task-list' -RegistryPath $taskRegRegistry -ProjectId $taskRegProjectId
Assert-True 'task record was created in Core by Create New Task' ($createdList.Status -eq 'PASS' -and @($createdList.Data.tasks | Where-Object { $_.title -eq 'Regression Test Task' }).Count -eq 1)

$workFolder = Join-Path $taskRegRoot 'Existing-Work'
[void](New-Item -ItemType Directory -Path $workFolder -Force)
[System.IO.File]::WriteAllText((Join-Path $workFolder 'file.txt'), 'Work file content', (New-Object System.Text.UTF8Encoding($false)))
$importKeys = '02' + '01' + '02' + $workFolder + '{Enter}' + 'Imported Work Folder Task{Enter}' + 'Verify folder import{Enter}' + '{Enter}' + '05' + '02' + '14'
$importUi = Invoke-Ui { Start-TuiApp -Root (Get-TestRoot) -RegistryPath $taskRegRegistry } $importKeys
Assert-True 'Add Existing Work Folder completes without error' ($importUi.Error -eq '') ($importUi.Error + $importUi.Output)
$afterImportList = Invoke-AipmCore -AppRoot (Get-TestRoot) -Command 'task-list' -RegistryPath $taskRegRegistry -ProjectId $taskRegProjectId
Assert-True 'task record was created in Core for imported work folder' ($afterImportList.Status -eq 'PASS' -and @($afterImportList.Data.tasks | Where-Object { $_.title -eq 'Imported Work Folder Task' }).Count -eq 1)

$tasksDir = Join-Path (Join-Path $taskRegRoot 'Shared-Project-State-Manager') 'Operations/Tasks'
$existingTaskFolder = Join-Path $tasksDir 'Task-2026-10-23-Manual-Task-Folder-abcdef123456'
[void](New-Item -ItemType Directory -Path $existingTaskFolder -Force)
[System.IO.File]::WriteAllText((Join-Path $existingTaskFolder 'Task-Plan.md'), "# Manual Task Folder`n`nRegistered directly in place.`n", (New-Object System.Text.UTF8Encoding($false)))
$registerExistingTaskKeys = '02' + '01' + '02' + $existingTaskFolder + '{Enter}' + '{Enter}' + '05' + '02' + '14'
$registerExistingTaskUi = Invoke-Ui { Start-TuiApp -Root (Get-TestRoot) -RegistryPath $taskRegRegistry } $registerExistingTaskKeys
Assert-True 'Add Existing Work Folder registers an existing task folder in place without prompting for a new name or creating a second folder' ($registerExistingTaskUi.Error -eq '' -and $registerExistingTaskUi.Output.Contains('Existing Task Folder Registered')) ($registerExistingTaskUi.Error + $registerExistingTaskUi.Output)
$afterTaskFolderList = Invoke-AipmCore -AppRoot (Get-TestRoot) -Command 'task-list' -RegistryPath $taskRegRegistry -ProjectId $taskRegProjectId
Assert-True 'existing task folder is officially registered under its own Task ID' ($afterTaskFolderList.Status -eq 'PASS' -and @($afterTaskFolderList.Data.tasks | Where-Object { $_.task_id -eq 'Task-2026-10-23-Manual-Task-Folder-abcdef123456' -and $_.title -eq 'Manual Task Folder' }).Count -eq 1)

# StrictMode and State Recovery Regression
$strictRecoveryBlock = {
    Set-StrictMode -Version 2.0
    $bareDiagnosis = [pscustomobject]@{
        Status = 'PASS'
        Data = [pscustomobject]@{
            repairable = $false
            reason = 'NO_PENDING_COMMIT'
        }
    }
    $cause = [string](Get-AipmField $bareDiagnosis.Data 'cause' 'Default Cause')
    $remedy = [string](Get-AipmField $bareDiagnosis.Data 'remedy' 'Default Remedy')
    return ($cause -eq 'Default Cause' -and $remedy -eq 'Default Remedy')
}
Assert-True 'Get-AipmField safely handles objects lacking cause and remedy under strict mode' (& $strictRecoveryBlock)

$recoveryUi = Invoke-Ui { Invoke-AipmStateRecovery -Root (Get-TestRoot) -RegistryPath $taskRegRegistry -ProjectId $taskRegProjectId } '{Enter}'
Assert-True 'Invoke-AipmStateRecovery completes under strict mode without PropertyNotFoundException' ($recoveryUi.Error -eq '') ($recoveryUi.Error + $recoveryUi.Output)
Assert-Equal 'Invoke-AipmStateRecovery returns false when state has no pending repair' $false $recoveryUi.Value

$strictNullFieldBlock = {
    Set-StrictMode -Version 2.0
    $nullFieldObj = [pscustomobject]@{ cause = $null }
    return ((Get-AipmField $nullFieldObj 'cause' 'Default Cause') -eq 'Default Cause')
}
Assert-True 'Get-AipmField falls back to Default when an existing property has a null value' (& $strictNullFieldBlock)

$strictCountBlock = {
    Set-StrictMode -Version 2.0
    $emptySubpipeline = if ($false) { 'never' }
    $cNull = Get-AipmCount $null
    $cAutoNull = Get-AipmCount $emptySubpipeline
    $cEmpty = Get-AipmCount @()
    $cScalarString = Get-AipmCount 'Task-2026-11-06-Single-Item-1ea6ea74c96a'
    $cScalarObj = Get-AipmCount ([pscustomobject]@{ task_id = 'Task-One' })
    $cArray = Get-AipmCount @('Task-One', 'Task-Two')
    $cHash = Get-AipmCount @{ first = 1; second = 2 }
    return (
        $cNull -eq 0 -and
        $cAutoNull -eq 0 -and
        $cEmpty -eq 0 -and
        $cScalarString -eq 1 -and
        $cScalarObj -eq 1 -and
        $cArray -eq 2 -and
        $cHash -eq 2
    )
}
Assert-True 'Get-AipmCount safely counts null, scalar string, scalar object, array, and dictionary under strict mode' (& $strictCountBlock)

$singleDriftRoot = Join-Path (Get-TestWork) 'Single Drift Project'
[void](New-Item -ItemType Directory -Path $singleDriftRoot -Force)
$singleDriftProjectId = 'Single-Drift-' + [guid]::NewGuid().ToString('N').Substring(0, 8)
$singleDriftReg = Invoke-AipmCore -AppRoot (Get-TestRoot) -Command 'registry-register' -RegistryPath $taskRegRegistry -ProjectRoot $singleDriftRoot -ProjectId $singleDriftProjectId -Alias 'Single Drift Fixture'
Assert-Equal 'single-task drift fixture registers cleanly' 'PASS' $singleDriftReg.Status
$singleDriftCreated = Invoke-AipmCore -AppRoot (Get-TestRoot) -Command 'task-create' -RegistryPath $taskRegRegistry -ProjectId $singleDriftProjectId -Title 'Single Reconciled Task' -Scope 'Reproduce single-element array unrolling under Set-StrictMode 2.0.'
Assert-Equal 'single-task drift fixture creates initial task' 'PASS' $singleDriftCreated.Status
$singleDriftManifestPath = Join-Path (Join-Path $singleDriftRoot 'Shared-Project-State-Manager') 'State-Manifest.json'
$singleDriftRaw = [System.IO.File]::ReadAllText($singleDriftManifestPath, [System.Text.Encoding]::UTF8)
$singleDriftParsed = $singleDriftRaw | ConvertFrom-Json
$singleDriftTaskId = [string](@($singleDriftParsed.tasks.PSObject.Properties)[0].Name)
$singleDriftMutated = [regex]::Replace($singleDriftRaw, '"revision"\s*:\s*(\d+)', { param($m) '"revision": ' + ([int]$m.Groups[1].Value + 1) }, 1)
$singleDriftMutated = [regex]::Replace($singleDriftMutated, '"report"\s*:\s*""', '"report": "Direct manifest edit without event file."', 1)
[System.IO.File]::WriteAllText($singleDriftManifestPath, $singleDriftMutated, (New-Object System.Text.UTF8Encoding($false)))

$singleDriftCancelUi = Invoke-Ui { Invoke-AipmStateRecovery -Root (Get-TestRoot) -RegistryPath $taskRegRegistry -ProjectId $singleDriftProjectId -FailureReason 'INVALID_HISTORY' } '{Enter}02'
Assert-True 'Invoke-AipmStateRecovery handles 1-element reconciled_tasks without Count PropertyNotFoundException' ($singleDriftCancelUi.Error -eq '' -and $singleDriftCancelUi.Output.Contains('Task State Problem Diagnosed') -and $singleDriftCancelUi.Output.Contains($singleDriftTaskId)) ($singleDriftCancelUi.Error + $singleDriftCancelUi.Output)
Assert-Equal 'cancelling 1-element drift recovery leaves state untouched and returns false' $false $singleDriftCancelUi.Value

$singleDriftRepairUi = Invoke-Ui { Invoke-AipmStateRecovery -Root (Get-TestRoot) -RegistryPath $taskRegRegistry -ProjectId $singleDriftProjectId -FailureReason 'INVALID_HISTORY' } '{Enter}01{Enter}'
Assert-True 'confirming 1-element drift recovery repairs state cleanly under strict mode' ($singleDriftRepairUi.Error -eq '' -and $singleDriftRepairUi.Output.Contains('Task State Repaired') -and $singleDriftRepairUi.Value -eq $true) ($singleDriftRepairUi.Error + $singleDriftRepairUi.Output)
$singleDriftAfter = Invoke-AipmCore -AppRoot (Get-TestRoot) -Command 'task-read' -RegistryPath $taskRegRegistry -ProjectId $singleDriftProjectId -TaskId $singleDriftTaskId
Assert-Equal 'repaired 1-element drift preserves direct manifest task edits' 'Direct manifest edit without event file.' $(if ($singleDriftAfter.Status -eq 'PASS') { [string]$singleDriftAfter.Data.task.report } else { $singleDriftAfter.Reason })

$zeroDriftRoot = Join-Path (Get-TestWork) 'Zero Task Drift Project'
[void](New-Item -ItemType Directory -Path $zeroDriftRoot -Force)
$zeroDriftProjectId = 'Zero-Drift-' + [guid]::NewGuid().ToString('N').Substring(0, 8)
[void](Invoke-AipmCore -AppRoot (Get-TestRoot) -Command 'registry-register' -RegistryPath $taskRegRegistry -ProjectRoot $zeroDriftRoot -ProjectId $zeroDriftProjectId -Alias 'Zero Drift Fixture')
$zeroDriftManifestPath = Join-Path (Join-Path $zeroDriftRoot 'Shared-Project-State-Manager') 'State-Manifest.json'
$zeroDriftRaw = [System.IO.File]::ReadAllText($zeroDriftManifestPath, [System.Text.Encoding]::UTF8)
$zeroDriftMutated = [regex]::Replace($zeroDriftRaw, '"revision"\s*:\s*(\d+)', { param($m) '"revision": ' + ([int]$m.Groups[1].Value + 1) }, 1)
[System.IO.File]::WriteAllText($zeroDriftManifestPath, $zeroDriftMutated, (New-Object System.Text.UTF8Encoding($false)))
$zeroDriftRepairUi = Invoke-Ui { Invoke-AipmStateRecovery -Root (Get-TestRoot) -RegistryPath $taskRegRegistry -ProjectId $zeroDriftProjectId -FailureReason 'INVALID_HISTORY' } '{Enter}01{Enter}'
Assert-True 'Invoke-AipmStateRecovery handles 0-element reconciled_tasks without Count PropertyNotFoundException' ($zeroDriftRepairUi.Error -eq '' -and $zeroDriftRepairUi.Output.Contains('Task State Repaired') -and $zeroDriftRepairUi.Value -eq $true) ($zeroDriftRepairUi.Error + $zeroDriftRepairUi.Output)
