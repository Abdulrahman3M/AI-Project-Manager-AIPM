Set-TestGroup 'Evidence-Based App View Models'

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
            [pscustomobject]@{ slug='tui-intelligence'; version='1.0.0'; source_license='AI Project Manager Personal Use License'; aipm_personal_license_applies=$true }
            [pscustomobject]@{ slug='audio-timing-author'; version='1.0.0'; source_license='AI Project Manager Personal Use License'; aipm_personal_license_applies=$true }
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
