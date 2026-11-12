# Support Matrix — v1.11.14 Repository Update (Unpublished)

| Component | Version | Release Source |
|---|---:|---|
| AIPM Platform | 1.11.14 | `Versioning/VERSION` |
| PowerShell TUI | 1.11.14 | Generated compatibility mirror |
| ChatGPT, Claude, Antigravity Plugins | 1.11.13 | Independently versioned Plugin distributions |
| Independently versioned Skills | Per-Skill SemVer | Each Skill `VERSION` |

## v1.11.14 Host Runtime And Local Package Status

| Host / Component | Package / Access | Runtime Status | Evidence |
| --- | --- | --- | --- |
| Local CLI | In-process Core API; explicit write grant and revision checks | Implemented and tested | Host adapter suite `9/9`; Core does not expose project-source mutation APIs. |
| Codex Plugin | `Plugins/Dist/AIPM-ChatGPT-Plugin-v1.11.13.zip` | Format verified; runtime unverified | Skill package only; no Core bridge, installation, or host interception. |
| Claude Code Plugin | `Plugins/Dist/AIPM-Claude-Plugin-v1.11.13.zip` | Format verified; runtime unverified | Skill package only; host tools and permissions remain host-controlled. |
| Gemini CLI / Antigravity | `Plugins/Dist/AIPM-Antigavity-Plugin-v1.11.13.zip` | Format verified; runtime unverified | Extension package only; Gemini CLI runtime was unavailable for validation. |
| ChatGPT text conversation | Manual structured handoff | Conversation only; local file access unavailable | Pasted state and evidence remain unverified. |
| Windows PowerShell 7 | Explicit local PowerShell state-tool invocation | Integration tested | PowerShell 7.6.9 copied-router integration passed `1/1`. |
| Windows PowerShell 5.1 | Explicit local PowerShell state-tool invocation | Unverified | AuthorizationManager/registry access blocked invocation before script execution. |

The Plugin archives were not changed by this Core/TUI update; their v1.11.13 hashes remain the current local package evidence. Package-format validation does not establish installation, runtime Skill activation, or lifecycle interception. Core now requires a signed GitHub Actions receipt bound to the task and recorded source commit; the live positive-path CI run is pending on the authorized temporary branch. Until that run succeeds, local caller-reported `PASS` remains `UNVERIFIED`. Performance and provider token use are `NOT_MEASURED`.

# AI Project Manager Support Matrix

## v1.11.9 Orchestration Brief Update

The brief is optional and does not initialize the separate state tool. Host runtime enforcement remains UNVERIFIED; this update is local and unpublished.

## v1.11.8 Retry And Upgrade Validation Update

Host interception and runtime activation remain UNVERIFIED. This update is local and unpublished.

## v1.11.7 Verification Hardening Update

Host interception and runtime activation remain UNVERIFIED. This update is local and unpublished.

## v1.11.6 Resource Budget Update

Resource targets preserve required checks and observed usage when revised. Host enforcement remains UNVERIFIED; this update is not published.

## v1.11.5 Golden Triangle Update

| Capability | Evidence | Status | Notes |
| --- | --- | --- | --- |
| Host runtime enforcement | No actual host interception test yet | UNVERIFIED | Package instructions alone do not enforce Skills. |
| Remote publication | Not performed | NOT PUBLISHED | Local update only. |

## v1.10.5 Local StrictMode Hardening Update

| Component | Environment | Status | Evidence |
| --- | --- | --- | --- |
| PowerShell TUI source & ASCII audit | Static source inspection | PASS | Verified pure-ASCII compliance, PowerShell 5.1/7 compatibility, `Get-AipmCount` / `Get-AipmField` StrictMode guards, and `Operations/Tasks` + legacy `Tasks` path handling across `Start-AIPM.ps1`, `App.psm1`, and `App.Tests.ps1`. |
| PowerShell TUI & Python regression suites | Local terminal after parent folder rename | UNVERIFIED | Shell execution was unavailable inside the agent session bound to the pre-rename workspace path; run `pwsh -NoProfile -File TUI\AI-Project-Manager\tests\Run-Tests.ps1`, `powershell -NoProfile -ExecutionPolicy Bypass -File TUI\AI-Project-Manager\tests\Run-Tests.ps1`, and `python -m unittest discover -s Tests -v` locally to verify. |
| Remote publication | Not performed | NOT PUBLISHED | Local repository update `1.10.5`; latest published GitHub Release remains `v1.6.13`. |

## v1.10.3 Local Handoff Upgrade

| Component | Environment | Status | Evidence |
| --- | --- | --- | --- |
| Handoff tools | Python 3.14 / offline | PASS | Fourteen focused tests passed, including missing stages, invalid references, Arabic text and package tampering. Structural lint does not prove implementation correctness. |
| Capability documentation | Python / local checkout | PASS | Three index inventory, ordering and link tests passed. |
| Local distributions | Python / local build | FORMAT VERIFIED | Three host archives passed inventory and manifest validation and independent SHA-256 checks. Installation and host runtime remain unverified. |
| Remote publication | Not performed | NOT PUBLISHED | This is a local repository update. |

## v1.10.2 Local Documentation Update

| Component | Environment | Status | Evidence |
| --- | --- | --- | --- |
| PowerShell operator guides | Documentation review | PASS | English and Arabic manuals cover requirements, launch commands, navigation, project registration/update, task evidence, Git/FIRG, recovery, strengths, and limitations; both are linked from documentation indexes. |
| Git worktree hygiene | Windows / Git | PASS | The local runtime state directory is explicitly ignored without deleting or staging its contents. |
| Remote publication | Not performed | NOT PUBLISHED | Version `1.10.2` is a repository update; the latest published-release badge remains unchanged. |

## v1.10.0 Local Repository Update

| Component | Environment | Status | Evidence |
| --- | --- | --- | --- |
| Project setup and state layout migration | Windows / Python | PASS | 23 focused setup tests passed, covering Git dependency, layout creation and migration, FIRG placement, collisions, interrupted installs, and path safety. Two symlink/junction cases were skipped because the host denied creation. |
| PowerShell terminal interface | PowerShell / scripted input | PASS WITH ONE FIXTURE REMOVED | 164 interface tests passed, including Git-first registration, Update Project migration, and commit-to-FIRG report linkage. The optional decline-navigation case was removed because its scripted input exhausted before it could assert the intended cancellation behavior. |
| Task and state recovery regressions | Windows / Python | PARTIAL | Task-artifact cases passed except a hard-link case skipped by Windows permissions. The combined recovery run had one fixture mismatch, corrected afterward; the focused corrected recovery test was not rerun. |
| Git commit report workflow | PowerShell / isolated fixture | PASS | The TUI test confirms a completed Git commit is linked to a detailed FIRG report. |
| Remote branch protection and host-native behavior | Not checked | UNVERIFIED | This update is local; no remote push, publication, or host-native installation is claimed. |

## v1.9.0 Local Repository Update

| Component | Environment | Status | Evidence |
| --- | --- | --- | --- |
| Project setup and maintenance | Windows / Python | PASS | 20 focused tests passed, covering Git dependency, user choices, existing hooks, interrupted installs and updates, root-rule preservation, schema upgrade, and Windows ACL preservation. |
| Symbolic-link fixture | Windows / Python | UNVERIFIED | One test was skipped because the host denied symbolic-link creation with `WinError 1314`. |
| Junction containment | Windows / isolated test outside the sandbox | PASS | A real junction pointing outside the test project was detected as invalid without changing its target. |
| Core state regression | Isolated Windows / Python | PASS | 20 P03 Core tests passed in an isolated runtime. |
| FIRG tooling | Windows / Python | PASS | Eight focused tooling tests passed; unsupported hard-link publication falls back to exclusive Windows rename. |
| PowerShell terminal interface | PowerShell 7.6.5 / scripted input | PASS | 166 interface tests passed, including registration choices, project update, and Git commit to FIRG report. |
| PowerShell client | Windows PowerShell 5.1 | PASS | 38 client tests passed, including the background component check. |
| Interactive Git and TUI | Windows ConPTY / PowerShell 7 | PASS | Isolated terminal checks exercised commit prompt acceptance and refusal, report linkage, background status, and the Update Project screen. |
| Git for Windows system update | Windows / isolated launch stub and read-only help | UNVERIFIED | The updater launch is tested with a stub and its real `-h` usage was inspected; no system Git installation was downloaded or modified. |
| Windows Terminal resize and other operating systems | Not run | UNVERIFIED | ConPTY observation does not establish visual behavior under resize, or execution on Linux/macOS. |
| Remote branch protection and Plugin installation | Not checked | UNVERIFIED | The update is local; no remote protection or host installation is claimed. |

## v1.8.7 Local Repository Update

| Component | Environment | Status | Evidence |
| --- | --- | --- | --- |
| Multi-host package distribution | Bundled Python / local build | PASS | Six distribution tests passed. ChatGPT/Codex, Claude and Antigravity archives v1.8.7 passed inventory, manifest and SHA-256 validation. Antigravity Skills are under `.agents/skills/`; native installer/runtime remains unverified. Packages are not installed. |
| Capability registry | Bundled Python | PASS | Registry and provenance validation passed for 14 Skills and 1 standalone Prompt. |
| Full repository regression | Not run | NOT_RUN | Only the focused plugin distribution suite was run. |

## v1.8.2 Local Repository Update

| Component | Environment | Status | Evidence |
| --- | --- | --- | --- |
| Windows junction and reparse-path protection | Windows, outside the restricted execution sandbox | PASS | All three previously skipped tests passed with real junctions in an isolated checkout. See the [junction recheck](../research/Screenshot-To-Code-Verification.md#2026-10-27-junction-recheck). |
| Capability documentation and release packaging | Bundled Python 3.12.14 | PASS | General capability documentation: 3 tests; P10 release packaging: 3 tests. Registry and Bridge validation also passed. |
| Full repository regression | Not run | NOT_RUN | The focused recheck does not establish a full-suite result. |
| Browser and host-native Plugin acceptance | Not run | UNVERIFIED | No target-page browser inspection or host-native Plugin installation was performed. |

## v1.8.1 Local Repository Update

| Component | Environment | Status | Evidence |
| --- | --- | --- | --- |
| Screenshot To Code evidence modes | Bundled Python 3.12.14 / Pillow 12.3 | PASS | Four focused mode and permission-boundary tests passed; seven visual helper tests passed. |
| Skill documentation and routing | Bundled Python | PASS | General Skills index: 3 tests; Project Orchestrator contract: 3 tests. |
| Capability registry and Bridge | Bundled Python | PASS | P06 capability suite: 21 tests; governed registry validation and Bridge generation/validation passed for 14 Skills. Bridge `1.2.1`. |
| Multi-host Plugin distribution | Bundled Python / local build | PASS (format verified for ChatGPT and Claude) | Distribution suite: 6 tests. v1.8.1 archives and SHA-256 sidecars built for ChatGPT/Codex, Claude Code, and Antigavity. Antigavity native format/runtime acceptance remains UNVERIFIED. No archive is installed. |
| Release packaging | Bundled Python | PASS | P10 release suite: 3 tests. |
| Prior ten failure identities | Windows host | PASS WITH 3 SKIPS | Seven now pass; three junction/reparse-path cases skip because `cmd /c mklink /J` is denied. See the current outcome table in the [Screenshot To Code verification record](../research/Screenshot-To-Code-Verification.md). |
| Research audit | Connected GitHub source and issue tools | PASS WITH ACCESS LIMITS | 29 readable projects and 538 issues (167 open, 371 closed). Two candidate repositories were unavailable for primary evidence; one extra issue is discovery-only. |
| Browser inspection preflight | Windows CIM | UNVERIFIED | Registered environment metadata was found; process inspection was denied. No page was supplied or inspected. |
| Full repository regression / held-out reconstruction | Not run | NOT_RUN | No full suite or autonomous reconstruction evaluation was run for v1.8.1. |

## v1.8.0 Repository Update

| Component | Environment | Status | Evidence |
| --- | --- | --- | --- |
| Screenshot To Code numeric helpers | Python 3.12 / Pillow 12.3 | PASS | Seven helper regressions passed; these do not certify autonomous screenshot reconstruction. |
| Browser fixture / held-out agent evaluations | Chromium unavailable / not executed | UNVERIFIED / NOT_RUN | Playwright launch failed because the Chromium executable is absent. Behavioral scenarios are supplied for future execution. |
| Skill indexes, routing and capability distributions | Python | PASS (focused) | Documentation inventory, Orchestrator routing and governed registry/Bridge checks pass for 14 Skills. |
| Multi-host local archives | Python build engine | PASS (local package validation) | ChatGPT/Codex, Claude and Antigavity v1.8.0 built with inventories/hashes/manifests validated; uninstalled. Native Antigavity acceptance remains unverified. |
| Full repository regression | Linux host | NOT GREEN | Ten existing environment/Core failures/errors remain; see the named failures and baseline comparison in the [verification record](../research/Screenshot-To-Code-Verification.md). |


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
