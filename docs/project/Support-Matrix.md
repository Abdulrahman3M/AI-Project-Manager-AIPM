# AI Project Manager Support Matrix

## Verified In This Repository

| Component | Environment | Status | Evidence |
| --- | --- | --- | --- |
| Core, State, Task Context, Adapters, Plugins, And Release Tests | Python 3.14.6 | PASS | Full `python -m unittest discover -s Tests -v`: 143 tests, 0 failures, 4 skipped because this host denies Windows junction/hard-link creation. Windows ACL-denial initialization tests now complete promptly and pass. |
| Terminal TUI Tests | PowerShell 7.6.5 | PASS | `TUI/AI-Project-Manager/tests/Run-Tests.ps1 -Filter Tui`: 146 pass, 0 fail, 0 unverified. Includes exact/partial attachment search, missing-file result, full-list reset, search scope, report attachment/listing, and source-file preservation. |
| Terminal TUI Tests | Windows PowerShell 5.1.26100.9444 | PASS | `TUI/AI-Project-Manager/tests/Run-Tests.ps1 -Filter Tui`: 146 pass, 0 fail, 0 unverified. |
| Task Continuity Across Core Processes | Python CLI / separate Core Engine instances | PASS (local simulation) | Three independent tasks were created. A fresh Core Engine and later CLI processes read persisted checkpoint/handoff/artifact data; the project-source fixture stayed unchanged. This does not prove a live external AI-host session. |
| Capability Library And Provenance | Python 3.14.6 | PASS | Protected registry metadata refreshed through the confirmed maintenance CLI for platform `1.4.0`; updated Skill files, metadata, hashes, registry, and provenance validate. |
| PowerShell TUI App Designer Skill | Windows PowerShell 5.1.26100.9444 | PASS | `scripts/Test-SkillPackage.ps1`: 63 checks, 0 failures, 0 unverified; includes generated application, runtime tests, examples, and Windows parser probe. |
| PowerShell TUI App Designer Skill | PowerShell 7.6.5 | PASS | `scripts/Test-SkillPackage.ps1`: 63 checks, 0 failures, 0 unverified; includes generated application, runtime tests, examples, and Windows parser probe. |
| Legacy AIPM Project Agent Bridge | Local package validation | PASS | Regenerated/validated at independent Bridge version `1.0.12`, with source project metadata `1.4.0`; not installed or published separately. |
| ChatGPT/Codex Plugin Archive | Local package validation | PASS (format verified) | `Plugins/Dist/AIPM-ChatGPT-Plugin-v1.4.0.zip` and `.sha256`; built from the updated registry and verified. Not installed in ChatGPT. |
| Claude Code Plugin Archive | Local package validation | PASS (format verified) | `Plugins/Dist/AIPM-Claude-Plugin-v1.4.0.zip` and `.sha256`; built from the updated registry and verified. Not installed in Claude Code. |
| Google Antigravity Plugin Archive | Local package validation | PASS (host format unverified) | `Plugins/Dist/AIPM-Antigavity-Plugin-v1.4.0.zip` and `.sha256`; local archive validation passed, but authoritative host format/runtime remains unverified. |
| Latest Published GitHub Source Release | Owner repository, private visibility | PASS | `v1.4.0` source ZIP and SHA-256 sidecar attached to the verified GitHub Release. |
| Local Source Package | Python standard library | PASS | `Releases/AI-Project-Manager-v1.4.0.zip` and `.zip.sha256`; allowlisted archive, manifest hashes, and sidecar verified. |

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

- Platform and PowerShell TUI are synchronized at `1.4.0`. The PowerShell TUI App Designer Skill is `1.1.0`; the Legacy Bridge is independently versioned at `1.0.12`. The three host archives are versioned `1.4.0` and remain local/uninstalled.
- TUI task management uses Core-validated operations for AIPM-owned task records. It does not edit project source files or run project tests; existing task folders are references and remain in place.
- AIPM does not edit target-project implementation files, execute target-project tests, or impose AIPM approval gates on agent source edits. Agents work directly in original files under target-project and AI-host permissions.
- Host adapters remain capability-declared, permission-gated for AIPM state mutations, and fail-closed. This state permission does not gate source edits performed through an AI host.
- A Plugin archive or manifest does not prove installation, account acceptance, agent connectivity, or local project access.
- Windows ACL, junction, and hard-link creation can be host-restricted independently of AIPM behavior; skipped tests are not reported as passing.
