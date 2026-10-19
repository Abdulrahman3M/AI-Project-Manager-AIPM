# AI Project Manager Support Matrix

## Verified In This Repository

| Component | Environment | Status | Evidence |
| --- | --- | --- | --- |
| Core, State, Task Context, Adapters, Plugins, And Release Tests | Python 3.13 | PASS | Full `python -m unittest discover -s Tests -v`: 142 tests, 0 failures, 4 skipped because this host denies Windows junction/hard-link creation. |
| Terminal TUI Tests | PowerShell 7.6.5 | PASS | `TUI/AI-Project-Manager/tests/Run-Tests.ps1`: 132 pass, 0 fail, 0 unverified. |
| Terminal TUI Tests | Windows PowerShell 5.1.26100.9444 | NOT RUN FOR 1.1.9 | Last recorded run was for the prior 1.1.7 development baseline: 190 pass, 0 fail, 0 unverified. |
| Task Continuity Across Core Processes | Python CLI / separate Core Engine instances | PASS (local simulation) | Three independent tasks were created. A fresh Core Engine and later CLI processes read persisted checkpoint/handoff/artifact data; the project-source fixture stayed unchanged. This does not prove a live external AI-host session. |
| Capability Library And Provenance | Python 3.13 | PASS | Protected registry metadata refreshed via the confirmed maintenance CLI for development version `1.1.9`; current registry and provenance validate. |
| Legacy AIPM Project Agent Bridge | Local package validation | PASS | Rebuilt/validated at independent Bridge version `1.0.9`, with source project metadata `1.1.9`; not installed or published. |
| ChatGPT/Codex Plugin Archive | Local package validation | PASS (format verified) | `Plugins/Dist/AIPM-ChatGPT-Plugin-v1.1.9.zip` and `.sha256`; archive manifest and inventory validated locally. Not uploaded or installed. |
| Claude Code Plugin Archive | Local package validation | PASS (format verified) | `Plugins/Dist/AIPM-Claude-Plugin-v1.1.9.zip` and `.sha256`; archive manifest and inventory validated locally. Not installed. |
| Google Antigravity Plugin Archive | Local package validation | PASS (host format unverified) | `Plugins/Dist/AIPM-Antigavity-Plugin-v1.1.9.zip` and `.sha256`; local inventory/manifest checks pass, but authoritative host format/runtime remains unverified. |
| Latest Published GitHub Source Release | Owner repository, private visibility | PASS | `v1.0.2` remains the latest published release. Repository version `1.1.9` is development-only and not published as a GitHub Release. |
| Local Source Package | Python standard library | NOT BUILT | No `1.1.9` source ZIP or checksum was produced because this is an unpublished development update. |

## Deliberately Not Claimed

| Capability | Status | Reason And Owner-Controlled Next Action |
| --- | --- | --- |
| Live cross-agent handoff through separate AI providers | UNVERIFIED | The automated test uses separate local Core/CLI processes. Confirm only with a real supported host session and explicit access grant. |
| Physically external project fixture | UNVERIFIED | All test writes were kept inside the AIPM repository as required by the task boundary. |
| Direct Windows hard-link write-through test | UNVERIFIED | `Path.hardlink_to` returned Windows `Access is denied`; a platform-independent atomic-replacement test passed instead. |
| Windows junction/reparse-point live creation tests | UNVERIFIED | Windows denied junction creation for three tests. Other path-boundary, reparse checks, and refusal cases passed. |
| Plugin installation in an AI host | UNVERIFIED | Local ZIP validation is not host installation or runtime evidence. |
| ChatGPT Plugin uploader acceptance | UNVERIFIED | Archives were not uploaded to an authenticated ChatGPT host in this task. |
| Antigravity host format/runtime acceptance | UNVERIFIED | The official host-format/runtime path was not exercised. |
| Public repository visibility or marketplace listing | NOT PERFORMED | Repository visibility and marketplace publication remain separate owner-controlled actions. |
| Reproducible native-terminal capture provenance | UNVERIFIED | Automated TUI tests passed, but this task did not capture new durable screenshots from the actual terminal hosts. |

## Operating Boundaries

- Platform and PowerShell TUI development versions are synchronized at `1.1.9`; latest published GitHub release remains `v1.0.2`.
- TUI task views are read-only. Core CLI/API task operations update only AIPM-owned task state and supporting artifacts.
- AIPM does not edit target-project implementation files, execute target-project tests, or impose AIPM approval gates on agent source edits. Agents work directly in original files under target-project and AI-host permissions.
- Host adapters remain capability-declared, permission-gated for AIPM state mutations, and fail-closed. This state permission does not gate source edits performed through an AI host.
- A Plugin archive or manifest does not prove installation, account acceptance, agent connectivity, or local project access.
- Windows ACL, junction, and hard-link creation can be host-restricted independently of AIPM behavior; skipped tests are not reported as passing.
