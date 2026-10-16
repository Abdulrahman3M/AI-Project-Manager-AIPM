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
