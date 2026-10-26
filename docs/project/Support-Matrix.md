# AI Project Manager Support Matrix

## v1.6.13 Release Verification

| Component | Environment | Status | Evidence |
| --- | --- | --- | --- |
| Web Design Engineering Skill helpers | Python standard library | PASS | Focused helper suite: 3 checks passed. |
| General Skills documentation index | Python standard library | PASS | Inventory, ordering, source links, and navigation check passed with 13 General Skills. |
| Core dashboard regression | Python standard library | PASS (focused) | `test_p08_core_dashboard.py`: 5 tests passed after updating the expected first-party Skill count. The full Python suite was not rerun after this correction. |
| Capability registry and provenance | Python standard library | PASS | Protected capability registry validates 13 General Skills and their source hashes. |
| Legacy Project Agent Bridge | Local package validation | PASS | Bridge `1.1.1`, generated from the 13-Skill capability baseline; local validation passed. Not installed or published separately. |
| ChatGPT/Codex Plugin archive | Local package validation | PASS (format verified) | `AIPM-ChatGPT-Plugin-v1.6.13.zip` and SHA-256 sidecar validated; not installed in ChatGPT/Codex. |
| Claude Code Plugin archive | Local package validation | PASS (format verified) | `AIPM-Claude-Plugin-v1.6.13.zip` and SHA-256 sidecar validated; not installed in Claude Code. |
| Google Antigravity Plugin archive | Local package validation | PASS (host format unverified) | `AIPM-Antigavity-Plugin-v1.6.13.zip` content and SHA-256 validated; native host format/runtime acceptance remains unverified. |
| Source release archive | Python standard library | PASS | `AI-Project-Manager-v1.6.13.zip` and `.zip.sha256` rebuilt from the release source and verified against its embedded manifest and checksum. |

Historical verification below records the environment and project version at the time each check ran; it does not claim every older suite was rerun on v1.6.13.

## Verified In This Repository

| Component | Environment | Status | Evidence |
| --- | --- | --- | --- |
| Core, State, Task Context, Adapters, Plugins, And Release Tests | Python 3.12.14 | PASS | Most recent full `python -m unittest discover -s Tests` run on repository version `1.4.7`: 146 tests, 0 failures, 4 skipped because this host denies Windows junction/hard-link creation. Windows ACL-denial initialization tests complete promptly and pass. |
| P09 Integrated Security Regression | Python 3.12.14 | PASS | Closeout rerun on `1.4.8`: `test_p09_integrated_security.py`, 3 tests, 0 failures. This is local security/process-boundary evidence; the live real-project agent handoff is owner-verified separately below. |
| P10 Release Packaging Regression | Python 3.12.14 | PASS | Closeout rerun on `1.4.8`: `test_p10_release.py`, 3 tests, 0 failures; the current source archive also verifies successfully. |
| Project Documentation Navigation | Python 3.12.14 | PASS | Closeout rerun on `1.4.8`: `test_general_capability_docs.py`, 3 tests, 0 failures. |
| Terminal TUI Tests | PowerShell 7.6.7 | PASS | `TUI/AI-Project-Manager/tests/Run-Tests.ps1 -Filter Tui` on `1.4.9`: 151 pass, 0 fail, 0 unverified. Includes the main-dashboard Esc exit confirmation and confirmed-exit paths, plus wrap-tolerant verification that an added existing work folder is shown and kept in place. |
| Terminal TUI Tests | Windows PowerShell 5.1.26100.9711 | PASS | `TUI/AI-Project-Manager/tests/Run-Tests.ps1 -Filter Tui` on `1.4.9`: 151 pass, 0 fail, 0 unverified. The complete `Run-Tests.ps1` suite also reports 224 pass, 0 fail, 0 unverified. |
| Task Continuity Across Core Processes | Python CLI / separate Core Engine instances | PASS (local simulation) | Three independent tasks were created. A fresh Core Engine and later CLI processes read persisted checkpoint/handoff/artifact data; the project-source fixture stayed unchanged. This does not prove a live external AI-host session. |
| Project Orchestrator Skill Routing | Bundled Python 3.14.6 | PASS | `Test-SkillSelectionContract.py`: 3 tests, 0 failures; checks registry/catalog parity, handoff intent vs. generic Markdown, and online/offline capability-gap behavior. |
| Capability Library And Provenance | Python 3.12.14 | PASS | Confirmed refresh and `validate`: 12 Skills, 1 standalone Prompt; platform `1.4.6`, hashes, metadata, and provenance match authoritative sources. |
| General Skills And Prompts Documentation | Python 3.12.14 | PASS | The documentation check confirms 12 Skills and 1 standalone Prompt, alphabetical ordering, unique technical names, valid source links, and README/home navigation. |
| PowerShell TUI App Designer Skill | PowerShell 7.6.5 | PASS | `Test-SkillPackage.ps1 -SkipGenerate`: 49 checks, 0 failures; generated template app suite: 103 PASS, 0 FAIL, 0 UNVERIFIED. |
| Generated PowerShell TUI Template | Windows PowerShell 5.1.26100.9444 | PASS | Generated application unit/UI suite: 103 PASS, 0 FAIL, 0 UNVERIFIED, including managed input/frame transition cases. |
| Legacy AIPM Project Agent Bridge | Local package validation | PASS | Regenerated and validated at Bridge `1.0.16`, source project `1.4.9`, 12 Skills; Apache License 2.0 and NOTICE included; local sample only, not installed or published. |
| ChatGPT/Codex Plugin Archive | Local package validation | PASS (format verified) | `Plugins/Dist/AIPM-ChatGPT-Plugin-v1.4.5.zip` and `.sha256`; 12 Skills, validated, not installed in ChatGPT. |
| Claude Code Plugin Archive | Local package validation | PASS (format verified) | `Plugins/Dist/AIPM-Claude-Plugin-v1.4.5.zip` and `.sha256`; 12 Skills, validated, not installed in Claude Code. |
| Google Antigravity Plugin Archive | Local package validation | PASS (host format unverified) | `Plugins/Dist/AIPM-Antigavity-Plugin-v1.4.5.zip` and `.sha256`; contents/hashes validate, native host format/runtime remains UNVERIFIED. |
| Local Source Package | Python standard library | PASS | `Releases/AI-Project-Manager-v1.4.9.zip` (857 files) and `.zip.sha256`; build, allowlist, embedded file hashes, and checksum verified. |

## P09 Closure

| Acceptance Area | Status | Evidence Basis |
| --- | --- | --- |
| Integrated security behavior | COMPLETE | The repository's P09 automated integration suite and full repository test run are recorded as passing in this matrix. |
| Physically external project use | OWNER-VERIFIED | The owner confirmed successful use of AIPM on real projects outside the AIPM installation. This agent did not independently access those project files. |
| Live two-agent handoff | OWNER-VERIFIED | The owner confirmed successful handoff and continuation between two agents on active real-project work. The supplied AIPM terminal screenshots show the attached task-file view and task status/details. |
| Terminal evidence capture | OWNER-VERIFIED | Genuine terminal screenshots were submitted in this conversation on 2026-10-21. They are not copied into this repository/archive because they expose details from a separate private project. |
| Phase decision | COMPLETE | The owner explicitly accepted P09 and declared P00–P10 complete on 2026-10-21. This is owner acceptance, not a claim that this agent re-ran an external provider session. |

## Deliberately Not Claimed

| Capability | Status | Reason And Owner-Controlled Next Action |
| --- | --- | --- |
| Direct Windows hard-link write-through test | UNVERIFIED | `Path.hardlink_to` returned Windows `Access is denied`; a platform-independent atomic-replacement test passed instead. |
| Windows junction/reparse-point live creation tests | UNVERIFIED | Windows denied junction creation for three tests. Other path-boundary, reparse checks, and refusal cases passed. |
| Plugin installation in an AI host | UNVERIFIED; NOT A P09 BLOCKER | Local ZIP validation is not host installation or runtime evidence. This separate capability is not included in P09 closure. |
| ChatGPT Plugin uploader acceptance | UNVERIFIED; NOT A P09 BLOCKER | Archives were not uploaded to an authenticated ChatGPT host in this task. |
| Antigravity host format/runtime acceptance | UNVERIFIED; NOT A P09 BLOCKER | The official host-format/runtime path was not exercised. |
| Public repository visibility or marketplace listing | NOT PERFORMED | Repository visibility and marketplace publication remain separate owner-controlled actions. |
| Independently reproducible terminal capture provenance | UNVERIFIED | Owner-submitted screenshots establish a real terminal view, but this agent did not reproduce or hash the capture artifacts. P09 closure is owner-accepted. |

## Operating Boundaries

- Platform and PowerShell TUI repository versions are synchronized at `1.4.9`; the latest published GitHub Release remains `v1.4.0`. The local source package and SHA-256 sidecar are verified but are not attached to a release. Multi-host Plugin archives remain at `1.4.5`; Skill and Plugin versions are independently managed and were not changed by this update. Local package validation does not mean the Plugins are installed in their target hosts.
- TUI task management uses Core-validated operations for AIPM-owned task records. It does not edit project source files or run project tests; existing task folders are references and remain in place.
- AIPM does not edit target-project implementation files, execute target-project tests, or impose AIPM approval gates on agent source edits. Agents work directly in original files under target-project and AI-host permissions.
- Host adapters remain capability-declared, permission-gated for AIPM state mutations, and fail-closed. This state permission does not gate source edits performed through an AI host.
- A Plugin archive or manifest does not prove installation, account acceptance, agent connectivity, or local project access.
- Windows ACL, junction, and hard-link creation can be host-restricted independently of AIPM behavior; skipped tests are not reported as passing.
