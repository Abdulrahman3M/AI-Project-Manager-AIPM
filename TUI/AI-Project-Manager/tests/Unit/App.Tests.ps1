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
        first_party_skills = @('tui-intelligence')
        skills = @(
            [pscustomobject]@{ slug='tui-intelligence'; version='0.1.0'; source_license='Apache-2.0'; aipm_apache_applies=$true }
            [pscustomobject]@{ slug='audio-timing-author'; version='1.0.0'; source_license='Universal AI ToolKit Personal Use License'; aipm_apache_applies=$false }
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
Assert-True 'catalog projection separates first-party and imported Skills' ($null -ne $capabilityRows -and @($capabilityRows.FirstParty).Count -eq 1 -and @($capabilityRows.Imported).Count -eq 1)
Assert-Equal 'first-party row retains its declared Apache-2.0 license' 'Apache-2.0' $(if ($capabilityRows -and $capabilityRows.FirstParty.Count) { $capabilityRows.FirstParty[0].License } else { '' })
Assert-Equal 'imported row retains its source license without AIPM relicensing' 'Universal AI ToolKit Personal Use License' $(if ($capabilityRows -and $capabilityRows.Imported.Count) { $capabilityRows.Imported[0].License } else { '' })
Assert-Equal 'Plugin package remains uninstalled and unpublished unless evidenced' 'Unverified,Unverified' $(if ($capabilityRows -and $capabilityRows.Plugins.Count) { $capabilityRows.Plugins[0].Installation + ',' + $capabilityRows.Plugins[0].Publication } else { '' })
Assert-Equal 'missing catalog is unverified and does not invent capability rows' 'Unverified,0,0' $(if ($missingCapabilityRows) { $missingCapabilityRows.CatalogStatus + ',' + $missingCapabilityRows.FirstParty.Count + ',' + $missingCapabilityRows.Imported.Count } else { '' })
