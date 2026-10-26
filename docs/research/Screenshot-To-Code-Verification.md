# Screenshot To Code Verification Record

**Date:** 2026-10-26. **Baseline:** `2a32807bfa44bc2d2405d83006f04e10c0060571`. **Scope:** original Skill, diagnostic tools, routing/index/registry synchronization, generated distributions and source packaging.

## v1.8.1 Post-Sync Hardening Update

This section records the current task after a safe fast-forward from `2a32807bfa44bc2d2405d83006f04e10c0060571` to `origin/main` at `45c5d0746808a1d7a0250326cdf83e45ac1dc15d`. The earlier sections below preserve historical evidence from the prior repository update; their publication statements do not describe this task. This update remains local and unpublished.

| Check | Current result | Evidence / limits |
| --- | --- | --- |
| Evidence modes | PASS: 4 tests | Screenshot-only default, opt-in browser wording, authorization boundaries, and scenario guidance. |
| Visual helpers | PASS: 7 tests | Bundled Python 3.12.14 with Pillow 12.3. |
| General Skills documentation | PASS: 3 tests | Inventory, ordering, source links, and navigation. |
| Project Orchestrator contract | PASS: 3 tests | Catalog versions, handoff routing, and capability-gap behavior. |
| Plugin distribution regression | PASS: 6 tests | Inventories, hashes, host manifests, exclusions, tamper rejection, and documentation. |
| P06 Capability Library | PASS: 21 tests | Registry baseline, atomic update, source drift, Bridge/package boundaries, and capability inventory cases. |
| P10 Release packaging | PASS: 3 tests | Reproducible archive, sensitive-content exclusion, and tamper rejection. |
| Capability registry and Plugin | PASS | Governed refresh and validation succeeded for 14 Skills and 1 standalone Prompt; local Plugin validation reports not installed and not published. |
| Legacy Project Agent Bridge | PASS | Generated and validated at `1.2.1`; local only. |
| Multi-host archives | PASS: local build | v1.8.1 ChatGPT/Codex and Claude archives are format-verified; Antigavity archive inventory/checksum validates, while native host-format/runtime acceptance is UNVERIFIED. All have SHA-256 sidecars and remain uninstalled. |
| Historical ten failure identities | 7 PASS, 3 SKIP | Current outcomes are listed below. The seven ACL/CLI/process identities no longer reproduce as failures. Three junction-dependent cases could not create a junction because Windows denied `cmd /c mklink /J`. |
| Browser environment | UNVERIFIED | Status metadata was found; process inspection failed with `PROCESS_INSPECTION_UNAVAILABLE` because Windows denied CIM access. No target URL was provided, so no page or browser evidence was inspected. |
| Full repository suite and held-out reconstruction | NOT_RUN | No claim is made for either check in this update. |
| Remote publication | NOT PERFORMED | No push, tag, GitHub Release, Plugin installation, or publication occurred. |

### Current Outcomes For The Ten Prior Failure Identities

| Test identity | Current outcome |
| --- | --- |
| `test_acl_denial_leaves_no_partial_state_tree` | PASS |
| `test_inherited_directory_acl_denial_leaves_no_partial_state_tree` | PASS |
| `test_registry_acl_denial_preserves_existing_registry` | PASS |
| `test_rejects_junction_in_existing_state_path` | SKIP / UNVERIFIED: junction creation denied by Windows |
| `test_rejects_junction_in_project_root_path` | SKIP / UNVERIFIED: junction creation denied by Windows |
| `test_cli_lists_pointer_only_registry_as_json` | PASS |
| `test_lock_guard_rejects_reparse_path_before_opening_redirected_target` | SKIP / UNVERIFIED: junction/reparse fixture creation denied by Windows |
| `test_live_process_identity_blocks_expired_lease_recovery` | PASS |
| `test_resource_guard_serializes_a_real_child_process` | PASS |
| `test_terminated_process_allows_expired_lease_recovery` | PASS |

The audit reviewed 29 projects with readable primary evidence and indexed 538 issues (167 open, 371 closed). `Mrxyy/screenshot-to-page` remains discovery-only because its README and primary Skill were unavailable; `microsoft/AI-Lab` could not be read or searched. An additional issue from the discovery-only repository is separately marked in the CSV. No third-party code was executed or redistributed. See the [audit report](Screenshot-To-Code-Hardening-Audit.md), [machine-readable evidence](Screenshot-To-Code-Hardening-Audit.json), and [issue title/status index](Screenshot-To-Code-Issue-Index.csv).

Generated package files were copied from the isolated validation checkout after their paths were checked and key file hashes matched. The completed evidence and tests do not establish native Antigavity acceptance, browser access on this Windows host, an installation in any AI host, or autonomous screenshot reconstruction quality.

## Results

| Check | Result | Evidence / Limit |
| --- | --- | --- |
| Numeric helper regressions | PASS: 7 tests | Identical inputs, regional errors, mismatched sizes, overlapping/full/out-of-bounds masks, threshold behavior and pixel probe. Six positive-path assertions failed before the scripts existed, then all seven passed after implementation. |
| General capability docs | PASS: 3 tests | Inventory, ordering, source links and navigation, 14 Skills. |
| Orchestrator routing | PASS: 3 tests | Active registry slugs/versions, handoff routing and capability-gap behavior. |
| Plugin distribution suite | PASS: 6 tests | Host inventories, hashes, manifests, exclusions, tamper rejection and operator docs. |
| Source packaging regression | PASS: 3 tests | Reproducibility, integrity and sensitive-content exclusions; newly added assertions first failed when `.gitattributes` and research evidence were omitted, then passed after the allowlist change. |
| Registry and legacy Bridge | PASS | Governed CLI validation: 14 Skills, 1 standalone Prompt in registry; Bridge `1.2.0` valid, uninstalled/unpublished. |
| Multi-host archives | PASS: local package validation | `Plugins/Dist/AIPM-{ChatGPT,Claude,Antigavity}-Plugin-v1.8.0.zip` plus checksums. Antigavity native format/runtime acceptance remains UNVERIFIED. |
| Full repository suite | NOT GREEN | Final run: 158 tests, 148 successful, 3 failures and 7 errors. All ten failing test identities also fail on the baseline snapshot. Names are preserved in `Screenshot-To-Code-Test-Results.json`. |
| Optional browser fixture | UNVERIFIED | Playwright launch failed: Chromium executable absent. No browser render, screenshot inspection, real keyboard result or responsive browser PASS is claimed. |
| Autonomous agent reconstruction quality | NOT_RUN | Held-out behavioral evaluation scenarios are supplied, not executed. No claimed superiority over the researched tools. |

## Existing Full-Suite Failures

- `test_acl_denial_leaves_no_partial_state_tree`
- `test_inherited_directory_acl_denial_leaves_no_partial_state_tree`
- `test_registry_acl_denial_preserves_existing_registry`
- `test_rejects_junction_in_existing_state_path`
- `test_rejects_junction_in_project_root_path`
- `test_cli_lists_pointer_only_registry_as_json`
- `test_lock_guard_rejects_reparse_path_before_opening_redirected_target`
- `test_live_process_identity_blocks_expired_lease_recovery`
- `test_resource_guard_serializes_a_real_child_process`
- `test_terminated_process_allows_expired_lease_recovery`

Windows ACL/junction tests invoke unavailable Windows tooling (`whoami /user`, `cmd`); process-lock tests encounter `PROCESS_IDENTITY_UNAVAILABLE` on this host. The CLI listing test exits nonzero on both baseline and updated trees; its underlying Core behavior was not changed or repaired by this task. Baseline full suite: 158 tests, 6 failures and 7 errors, including the same ten identities plus stale first-party inventory assertions and one staging-cleanup failure.

An additional isolated capability-suite run reported `test_explicit_rebuild_upgrades_only_known_website_metadata_drift` returning `UNCHANGED` instead of expected `PASS`. The final full-suite run passed that test. An isolated baseline capability-suite run also failed in staging-preservation/idempotence assertions. These order/cleanup-sensitive existing checks are reported rather than being described as uniformly green. The task does not change capability-engine upgrade logic or process/ACL behavior.

## Checkout Integrity Repair

Git's committed LF VERSION bytes differed from the CRLF bytes previously recorded in the capability hashes for seven unchanged Skill masters and their generated Bridge copies. The governed refresh correctly rejected that mismatch. Restoring the exact already-recorded bytes resolved it; `.gitattributes` preserves those byte-sensitive VERSION files. Unrelated Skill content versions were not inflated and their protected source hashes were not replaced merely to accept line-ending drift.

Source packaging now includes `.gitattributes` and `docs/research/`, so the transport rule and linked research/verification evidence travel with the source distribution. Plugin archives contain original Skill resources, not third-party repository downloads.

## Reproduce The Focused Checks

From the repository root:

```bash
python -B 01-Skills-General/screenshot-to-code/tests/test_visual_tools.py
python -B -m unittest discover -s Tests -p 'test_general_capability_docs.py' -v
python -B 01-Skills-General/project-orchestrator/tests/Test-SkillSelectionContract.py
python -B -m unittest discover -s Tests -p 'test_plugin_distribution.py' -v
python -B -m unittest discover -s Tests -p 'test_p10_release.py' -v
python -B Maintenance-Tools/Invoke-Capability-Library.py validate
python -B Maintenance-Tools/Invoke-Capability-Library.py validate-plugin
```

Optional controlled browser fixture, in an environment with Playwright and its Chromium executable already available:

```bash
node 01-Skills-General/screenshot-to-code/tests/test_browser.cjs .test-workspace/screenshot-browser
```

That fixture detects an intentionally changed button with a regional diff, removes the change and checks the repaired diff, replays a keyboard action, tests RTL overflow at five widths and produces a DPR-2 capture. It tests tooling and rendering plumbing, not an agent's ability to reconstruct an unseen screenshot. Do not treat its unexecuted assertions as verification results.

## Publication Boundary

The user authorized updating the AIPM GitHub project. The task updates source on `main`; it does not create a Git tag, GitHub Release, install a plugin, or modify Universal AI ToolKit. Generated local archives are reviewable build outputs under `Plugins/Dist/` and the source package under `Releases/`. Public primary-source research code is not bundled.
