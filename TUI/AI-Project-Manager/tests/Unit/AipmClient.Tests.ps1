Import-Module -Name (Join-Path (Join-Path (Join-Path (Get-TestRoot) 'src') 'Core') 'AipmClient.psm1') -Force -DisableNameChecking -Global
Set-TestGroup 'AIPM Core Client'

$appRoot = Get-TestRoot
$repoRoot = Get-AipmRepositoryRoot -AppRoot $appRoot
$expectedRoot = [System.IO.Path]::GetFullPath((Join-Path (Join-Path $appRoot '..') '..'))
Assert-Equal 'Core root resolves inside this AIPM checkout' $expectedRoot $repoRoot
Assert-True 'Core entry point exists below the resolved root' (Test-Path -LiteralPath (Join-Path (Join-Path $repoRoot 'Core-Engine') 'aipm.py') -PathType Leaf)

$ready = Get-AipmDependencyStatus -AppRoot $appRoot
Assert-Equal 'available Python and Core report ready' 'PASS' $ready.Status
Assert-True 'dependency status includes a parsed Python version' ([bool]$ready.Version)

$missing = Get-AipmDependencyStatus -AppRoot $appRoot -PythonPath (Join-Path (Get-TestWork) 'missing-python.exe')
Assert-Equal 'missing Python is reported as blocked' 'BLOCKED' $missing.Status

$broken = Get-AipmDependencyStatus -AppRoot $appRoot -PythonPath (Get-CurrentPowerShellPath)
Assert-Equal 'a non-Python executable is reported as blocked' 'BLOCKED' $broken.Status

$registryPath = Join-Path (Get-TestWork) 'P08 Registry With Spaces.json'
$read = Invoke-AipmCore -AppRoot $appRoot -Command 'dashboard' -RegistryPath $registryPath
Assert-Equal 'Core dashboard reads the explicit in-repository registry path' 'PASS' $read.Status
Assert-Equal 'missing fixture is distinguished from malformed state' 'NOT_REGISTERED' $read.Data.registry_status

$malformed = Join-Path (Get-TestWork) 'malformed registry.json'
[System.IO.File]::WriteAllText($malformed, '{"schema_version":"invalid"}', (New-Object System.Text.UTF8Encoding($false)))
$blocked = Invoke-AipmCore -AppRoot $appRoot -Command 'dashboard' -RegistryPath $malformed
Assert-Equal 'a malformed registry fails closed rather than looking empty' 'BLOCKED' $blocked.Status
Assert-Equal 'malformed registry reports a stable failure reason' 'INVALID_REGISTRY' $blocked.Reason

$inertPath = Join-Path (Get-TestWork) 'missing;python.exe'
$inert = Invoke-AipmCore -AppRoot $appRoot -Command 'dashboard' -RegistryPath $inertPath
Assert-Equal 'registry path punctuation remains one argument' 'NOT_REGISTERED' $inert.Data.registry_status

$taskProjectRoot = Join-Path (Get-TestWork) 'Task Client Project'
[void](New-Item -ItemType Directory -Path $taskProjectRoot -Force)
$taskRegistry = Join-Path (Get-TestWork) 'task-client-registry.json'
$taskProjectId = 'Task-Client-' + [guid]::NewGuid().ToString('N').Substring(0, 8)
$registeredTaskProject = Invoke-AipmCore -AppRoot $appRoot -Command 'registry-register' -RegistryPath $taskRegistry -ProjectRoot $taskProjectRoot -ProjectId $taskProjectId -Alias 'Task Client Fixture'
Assert-Equal 'task management fixture registers through Core' 'PASS' $registeredTaskProject.Status
$createdTask = Invoke-AipmCore -AppRoot $appRoot -Command 'task-create' -RegistryPath $taskRegistry -ProjectId $taskProjectId -Title 'Organize Existing Work' -Scope 'Keep work files at their original project paths.'
Assert-Equal 'task create crosses the Core client boundary' 'PASS' $createdTask.Status
Assert-Equal 'task create returns the requested title from Core state' 'Organize Existing Work' $createdTask.Data.task.title
$listedTasks = Invoke-AipmCore -AppRoot $appRoot -Command 'task-list' -RegistryPath $taskRegistry -ProjectId $taskProjectId
Assert-Equal 'task list returns the Core-authoritative new task' 'Organize Existing Work' $listedTasks.Data.tasks[0].title
$importWorkFolder = Join-Path $taskProjectRoot 'Incoming-Work-Folder'
[void](New-Item -ItemType Directory -Path $importWorkFolder -Force)
[System.IO.File]::WriteAllText((Join-Path $importWorkFolder 'notes.md'), 'Task notes remain in place.', (New-Object System.Text.UTF8Encoding($false)))
$importedTask = Invoke-AipmCore -AppRoot $appRoot -Command 'task-import-work-folder' -RegistryPath $taskRegistry -ProjectId $taskProjectId -Title 'Imported Existing Folder' -Scope 'Track work in place' -Source $importWorkFolder
Assert-Equal 'task import work folder passes validated path through the Core client boundary' 'PASS' $importedTask.Status
Assert-Equal 'task import work folder returns the requested title from Core state' 'Imported Existing Folder' $importedTask.Data.task.title
$taskId = [System.IO.Path]::GetFileName([string]$createdTask.Data.task_path)
$plannedTask = Invoke-AipmCore -AppRoot $appRoot -Command 'task-plan' -RegistryPath $taskRegistry -ProjectId $taskProjectId -TaskId $taskId -Text 'Review the existing folder without moving source files.'
Assert-Equal 'task plan updates through the whitelisted Core client' 'PASS' $plannedTask.Status
$checkpointTask = Invoke-AipmCore -AppRoot $appRoot -Command 'task-checkpoint' -RegistryPath $taskRegistry -ProjectId $taskProjectId -TaskId $taskId -LastVerifiedAction 'Reviewed the task files.' -NextAction 'Summarize the requested work.'
Assert-Equal 'task checkpoint updates through the whitelisted Core client' 'PASS' $checkpointTask.Status
$blockedTask = Invoke-AipmCore -AppRoot $appRoot -Command 'task-blocker-add' -RegistryPath $taskRegistry -ProjectId $taskProjectId -TaskId $taskId -Text 'Waiting for access confirmation.'
Assert-Equal 'task blocker updates through the whitelisted Core client' 'PASS' $blockedTask.Status
$verifiedTask = Invoke-AipmCore -AppRoot $appRoot -Command 'task-verify' -RegistryPath $taskRegistry -ProjectId $taskProjectId -TaskId $taskId -Result 'PASS' -Evidence 'Manual review confirmed the task output.'
Assert-Equal 'task verification evidence updates through the whitelisted Core client' 'PASS' $verifiedTask.Status
$reportedTask = Invoke-AipmCore -AppRoot $appRoot -Command 'task-report' -RegistryPath $taskRegistry -ProjectId $taskProjectId -TaskId $taskId -Text 'The task record was updated through the TUI client contract.'
Assert-Equal 'task report updates through the whitelisted Core client' 'PASS' $reportedTask.Status
$supportSource = Join-Path (Get-TestWork) 'Client Report.md'
[System.IO.File]::WriteAllText($supportSource, 'Report evidence from the client test.', (New-Object System.Text.UTF8Encoding($false)))
$artifactWrite = Invoke-AipmCore -AppRoot $appRoot -Command 'task-artifact-write' -RegistryPath $taskRegistry -ProjectId $taskProjectId -TaskId $taskId -RelativePath 'Reports/Client Report.md' -FromFile $supportSource
Assert-Equal 'task artifact files can be attached through the whitelisted Core client' 'PASS' $artifactWrite.Status
$artifactList = Invoke-AipmCore -AppRoot $appRoot -Command 'task-artifact-list' -RegistryPath $taskRegistry -ProjectId $taskProjectId -TaskId $taskId
Assert-True 'attached artifacts are listed with verified metadata' ($artifactList.Status -eq 'PASS' -and @($artifactList.Data.artifacts | Where-Object { $_.path -eq 'Reports/Client Report.md' }).Count -eq 1 -and $artifactList.Data.artifacts[0].sha256)
$clearBlockers = Invoke-AipmCore -AppRoot $appRoot -Command 'task-blocker-clear' -RegistryPath $taskRegistry -ProjectId $taskProjectId -TaskId $taskId
$closedTask = Invoke-AipmCore -AppRoot $appRoot -Command 'task-close' -RegistryPath $taskRegistry -ProjectId $taskProjectId -TaskId $taskId -Text 'Requirements satisfied.'
Assert-Equal 'task close completes through the Core client' 'PASS' $closedTask.Status
$archivedTask = Invoke-AipmCore -AppRoot $appRoot -Command 'task-archive' -RegistryPath $taskRegistry -ProjectId $taskProjectId -TaskId $taskId
Assert-Equal 'task archive completes through the Core client' 'PASS' $archivedTask.Status
Assert-True 'archived task data contains checksum and archive paths' ($archivedTask.Data.archive_path -and $archivedTask.Data.checksum_path -and $archivedTask.Data.verified)
$taskMeta = Invoke-AipmCore -AppRoot $appRoot -Command 'task-metadata' -RegistryPath $taskRegistry -ProjectId $taskProjectId -TaskId $taskId
Assert-True 'task metadata contains files summary and steps' ($taskMeta.Status -eq 'PASS' -and $taskMeta.Data.metadata.task_id -eq $taskId -and $taskMeta.Data.metadata.files.Count -gt 0)
$deletedFolder = Invoke-AipmCore -AppRoot $appRoot -Command 'task-delete-folder' -RegistryPath $taskRegistry -ProjectId $taskProjectId -TaskId $taskId
Assert-Equal 'task live folder can be deleted after verified archive' 'PASS' $deletedFolder.Status
$metaAfterDelete = Invoke-AipmCore -AppRoot $appRoot -Command 'task-metadata' -RegistryPath $taskRegistry -ProjectId $taskProjectId -TaskId $taskId
Assert-True 'task metadata remains readable from archive after folder deletion' ($metaAfterDelete.Status -eq 'PASS' -and $metaAfterDelete.Data.metadata.task_id -eq $taskId)

$importedTaskId = [string]$importedTask.Data.task.task_id
$editedTask = Invoke-AipmCore -AppRoot $appRoot -Command 'task-edit' -RegistryPath $taskRegistry -ProjectId $taskProjectId -TaskId $importedTaskId -Title 'Edited Imported Title' -Scope 'Edited Scope'
Assert-Equal 'task edit updates title and scope through Core client' 'PASS' $editedTask.Status
Assert-Equal 'edited task title is reflected' 'Edited Imported Title' $editedTask.Data.task.title

$clonedTask = Invoke-AipmCore -AppRoot $appRoot -Command 'task-clone' -RegistryPath $taskRegistry -ProjectId $taskProjectId -TaskId $importedTaskId -Title 'Cloned Client Task'
Assert-Equal 'task clone completes through Core client' 'PASS' $clonedTask.Status
Assert-Equal 'cloned task has requested title' 'Cloned Client Task' $clonedTask.Data.task.title

$newRenamedId = $importedTaskId.Replace('Task-', 'Task-Renamed-')
$renamedTask = Invoke-AipmCore -AppRoot $appRoot -Command 'task-rename' -RegistryPath $taskRegistry -ProjectId $taskProjectId -TaskId $importedTaskId -NewTaskId $newRenamedId
Assert-Equal 'task rename completes through Core client' 'PASS' $renamedTask.Status
Assert-Equal 'renamed task has new id' $newRenamedId $renamedTask.Data.task_id

$deletedTask = Invoke-AipmCore -AppRoot $appRoot -Command 'task-delete' -RegistryPath $taskRegistry -ProjectId $taskProjectId -TaskId $newRenamedId -DeleteArchive
Assert-Equal 'task delete completes through Core client' 'PASS' $deletedTask.Status
