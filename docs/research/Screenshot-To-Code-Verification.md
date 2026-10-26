# Screenshot To Code Verification Record

**Date:** 2026-10-26. **Baseline:** `2a32807bfa44bc2d2405d83006f04e10c0060571`. **Scope:** original Skill, diagnostic tools, routing/index/registry synchronization, generated distributions and source packaging.

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
