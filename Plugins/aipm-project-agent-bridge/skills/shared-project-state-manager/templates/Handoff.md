# Next Agent Handoff

## Identity

- Task: `{{TASK_ID}}`
- Title: {{TASK_TITLE}}
- From Agent: {{AGENT}}
- To Agent: {{NEXT_AGENT}}
- Prepared At: {{UPDATED_AT}}

## Read First

1. Project governance / agent instruction files.
2. `State-Manifest.json`.
3. `Current-State.md`.
4. `Tasks/{{TASK_ID}}/Task-Plan.md`.
5. Latest checkpoint and verification evidence.

## Exact Resume Point

{{LAST_VERIFIED}}

## First Action

{{NEXT_ACTION}}

## Required Verification Before Editing

Compare the recorded state with the actual branch, HEAD, working tree, relevant files, processes, and test evidence. Repair any divergence before continuing.

## Repository Snapshot

- Branch: `{{BRANCH}}`
- HEAD: `{{HEAD_SHA}}`
- Working Tree: `{{WORKING_TREE}}`

## Do Not Repeat

Do not repeat already verified work unless repository reality invalidates the evidence.

## Known Modified Files

See `Tasks/{{TASK_ID}}/File-Change-Map.md`.

## Blocking Issues

See `Tasks/{{TASK_ID}}/Blockers.md`.

## Owner Decisions

See `Tasks/{{TASK_ID}}/Decision-Log.md`.

## Relevant Reports

See latest checkpoint, phase report, and test report paths.
