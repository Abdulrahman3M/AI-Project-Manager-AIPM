# TUI Product Shell Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Deliver a framed AIPM product shell, responsive Capability Library, synchronized `0.2.1` release metadata, and measurably lighter terminal navigation without changing Core project-state authority.

**Architecture:** Introduce terminal-safe presentation helpers in the TUI layer for the product header, rules, frames, and compact tables. App owns a session read snapshot that only Refresh replaces; Menu owns geometry cache keyed by display inputs; Core remains responsible for all catalog and project facts.

**Tech Stack:** Windows PowerShell 5.1, PowerShell 7, existing PowerShell modules and test harness; no new dependencies.

**Spec:** `docs/superpowers/specs/2026-10-16-tui-product-shell-design.md`

## Global Constraints

- Platform and TUI package versions must both be exactly `0.2.1`.
- Preserve Core Engine as the sole project-state authority and all AIPM views as read-only.
- Preserve imported Skill bytes, source-license metadata, protected baselines, Plugin install/publish state, and Universal AI ToolKit boundaries.
- Use English Title Case for new human-facing labels; retain technical slugs and filenames.
- Support PowerShell 7 and Windows PowerShell 5.1 with ASCII-safe source files.
- Use no background color for selected labels, markers, or descriptions in ANSI, legacy, and no-color paths.

## Review Focus

- Narrow terminal width: retain product name/version and switch Capability rows to compact form without overflow — Task 3 tests.
- Missing or malformed catalog: show an unverified state without fake totals or an exception — Task 3 tests.
- Legacy Windows PowerShell rendering: `SelectionMarker` is recognized and does not set `BackgroundColor` — Task 1 tests.
- Repeated arrows: stable menu input must reuse geometry and make no Core read — Tasks 2 and 4 tests.
- Refresh failure: retain the last good session snapshot and present a safe blocked state rather than partial mixed data — Task 4 tests.

---

### Task 1: Product Header, Frames, And Legacy Selection Roles

**Files:**
- Modify: `TUI/AI-Project-Manager/src/TUI/Theme.psm1`
- Modify: `TUI/AI-Project-Manager/src/TUI/Renderer.psm1`
- Modify: `TUI/AI-Project-Manager/src/TUI/Menu.psm1`
- Modify: `TUI/AI-Project-Manager/tests/Unit/Tui.Tests.ps1`

**Interfaces:**
- Produces: `Write-AipmProductHeader([string]$Version, [string]$Status, [int]$Width)` and `Write-TuiRule([int]$Width)` in the TUI layer.
- Produces: semantic roles `Frame` and `SelectionMarker` consumable by ANSI and legacy renderers.
- Consumes: `Get-AppVersion` from App and existing `Write-Ui`/`Write-UiLine` framing API.

- [ ] **Step 1: Write failing header and legacy role tests**

Add assertions that captured header output contains `AI Project Manager`, `v0.2.1`, a frame/rule, and that legacy role parsing recognizes `SelectionMarker` without any selected background-color assignment.

- [ ] **Step 2: Run the TUI unit suite to verify the tests fail**

Run: `pwsh -NoLogo -NoProfile -File TUI/AI-Project-Manager/tests/Run-Tests.ps1`

Expected: FAIL because header helpers and legacy marker handling do not exist.

- [ ] **Step 3: Implement shared header and frame roles**

Implement the two helper signatures above, add `Frame` styling from the approved token system, and amend `Write-LegacyRow` so `SelectionMarker` is recognized and neither it nor `Selected` changes `Console.BackgroundColor`.

- [ ] **Step 4: Run the TUI unit suite to verify Task 1 passes**

Run: `pwsh -NoLogo -NoProfile -File TUI/AI-Project-Manager/tests/Run-Tests.ps1`

Expected: PASS including the new header/legacy tests.

- [ ] **Step 5: Commit Task 1**

```bash
git add TUI/AI-Project-Manager/src/TUI/Theme.psm1 TUI/AI-Project-Manager/src/TUI/Renderer.psm1 TUI/AI-Project-Manager/src/TUI/Menu.psm1 TUI/AI-Project-Manager/tests/Unit/Tui.Tests.ps1
git commit -m "feat(tui): add product shell header"
```

### Task 2: Stable Menu Geometry Cache

**Files:**
- Modify: `TUI/AI-Project-Manager/src/TUI/Menu.psm1`
- Modify: `TUI/AI-Project-Manager/tests/Unit/Tui.Tests.ps1`

**Interfaces:**
- Produces: `Get-MenuLayoutMetrics($Items, [string]$Layout, [string]$Density, [string]$DescriptionStyle, [int]$Width, [int]$Height)` with cache reuse only for equal inputs.
- Consumes: `Get-MenuViewportRange` and existing terminal size information.

- [ ] **Step 1: Write failing cache behavior tests**

Assert repeated equal metric requests return the cached measurement, while width, search-visible item set, and description-style changes cause a new measurement.

- [ ] **Step 2: Run the focused TUI test file to verify failure**

Run: `pwsh -NoLogo -NoProfile -File TUI/AI-Project-Manager/tests/Run-Tests.ps1`

Expected: FAIL because no metric-cache API exists.

- [ ] **Step 3: Implement `Get-MenuLayoutMetrics` and use it from `Show-Menu`**

Cache only deterministic row costs and total height; retain selection-sensitive viewport calculation per input event. Invalidate on any cache-key difference and do not cache terminal data across a resize.

- [ ] **Step 4: Run the TUI unit suite to verify Task 2 passes**

Run: `pwsh -NoLogo -NoProfile -File TUI/AI-Project-Manager/tests/Run-Tests.ps1`

Expected: PASS and existing short-terminal navigation tests remain green.

- [ ] **Step 5: Commit Task 2**

```bash
git add TUI/AI-Project-Manager/src/TUI/Menu.psm1 TUI/AI-Project-Manager/tests/Unit/Tui.Tests.ps1
git commit -m "perf(tui): cache stable menu geometry"
```

### Task 3: Capability Library Page And Responsive Tables

**Files:**
- Modify: `TUI/AI-Project-Manager/src/Core/App.psm1`
- Modify: `TUI/AI-Project-Manager/src/TUI/Menu.psm1`
- Modify: `TUI/AI-Project-Manager/tests/Unit/App.Tests.ps1`
- Modify: `TUI/AI-Project-Manager/tests/Unit/Tui.Tests.ps1`

**Interfaces:**
- Produces: `Get-AipmCapabilityLibraryRows($Catalog, [int]$Width)` returning summary, first-party, imported, and Plugin row groups.
- Produces: `Show-AipmCapabilityLibrary($Catalog, [string]$Version, [string]$Status)` as a read-only page.
- Consumes: Core `catalog` response only; never disk traversal or registry refresh.

- [ ] **Step 1: Write failing Capability Library projection and narrow-layout tests**

Assert a valid catalog produces a first-party group, source-license-preserving imported rows, and local Plugin status. Assert missing catalog yields unverified output and width below the column threshold produces compact rows.

- [ ] **Step 2: Run the focused test suite to verify failure**

Run: `pwsh -NoLogo -NoProfile -File TUI/AI-Project-Manager/tests/Run-Tests.ps1`

Expected: FAIL because the specialized projection/page does not exist.

- [ ] **Step 3: Implement read-only Capability Library composition and table rendering**

Use framed summary and section rules at normal width; use two-line compact rows at narrow width. Replace the `Skills & Plugins` route with this page while retaining the existing menu label and action value for compatibility.

- [ ] **Step 4: Run the TUI unit suite to verify Task 3 passes**

Run: `pwsh -NoLogo -NoProfile -File TUI/AI-Project-Manager/tests/Run-Tests.ps1`

Expected: PASS, including existing license and package-status assertions.

- [ ] **Step 5: Commit Task 3**

```bash
git add TUI/AI-Project-Manager/src/Core/App.psm1 TUI/AI-Project-Manager/src/TUI/Menu.psm1 TUI/AI-Project-Manager/tests/Unit/App.Tests.ps1 TUI/AI-Project-Manager/tests/Unit/Tui.Tests.ps1
git commit -m "feat(tui): add capability library page"
```

### Task 4: Session Snapshot, Refresh, And Release Metadata

**Files:**
- Modify: `TUI/AI-Project-Manager/src/Core/App.psm1`
- Modify: `TUI/AI-Project-Manager/VERSION`
- Modify: `VERSION`
- Modify: `TUI/AI-Project-Manager/CHANGELOG.md`
- Modify: `CHANGELOG.md`
- Modify: `TUI/AI-Project-Manager/tests/Unit/App.Tests.ps1`
- Modify: `TUI/AI-Project-Manager/tests/Unit/Static.Tests.ps1`

**Interfaces:**
- Produces: `Get-AipmSessionSnapshot([string]$Root, [string]$RegistryPath)` and `Refresh-AipmSessionSnapshot(...)` returning complete Core/dashboard/catalog/host facts or a safe blocked result.
- Consumes: `Invoke-AipmCore`, `Get-AipmDependencyStatus`, and existing `Start-TuiApp` action loop.

- [ ] **Step 1: Write failing snapshot and version-contract tests**

Assert a normal menu navigation sequence invokes no additional Core reads after its initial snapshot, Refresh requests a new snapshot, a failed Refresh preserves the last good one, and root/TUI versions are equal valid `0.2.1` SemVer values.

- [ ] **Step 2: Run the focused TUI test suite to verify failure**

Run: `pwsh -NoLogo -NoProfile -File TUI/AI-Project-Manager/tests/Run-Tests.ps1`

Expected: FAIL because each loop currently invokes all three Core commands and version files differ.

- [ ] **Step 3: Implement snapshot lifecycle and synchronize release metadata**

Load the snapshot before the menu loop, replace it only after explicit Refresh, retain a known-good snapshot after a refresh error, set both version files to `0.2.1`, and record the release in both changelogs.

- [ ] **Step 4: Run full PowerShell and project quality verification**

Run:

```bash
pwsh -NoLogo -NoProfile -File TUI/AI-Project-Manager/tests/Run-Tests.ps1
powershell.exe -NoLogo -NoProfile -ExecutionPolicy Bypass -File TUI/AI-Project-Manager/tests/Run-Tests.ps1
pwsh -NoLogo -NoProfile -Command "& '01-Skills-General/powershell-tui-app-designer/scripts/Test-TuiProject.ps1' -Path 'TUI/AI-Project-Manager'"
powershell.exe -NoLogo -NoProfile -ExecutionPolicy Bypass -Command "& '01-Skills-General/powershell-tui-app-designer/scripts/Test-TuiProject.ps1' -Path 'TUI/AI-Project-Manager'"
git diff --check
```

Expected: all tests and 22 project rules pass under both PowerShell editions; no whitespace errors.

- [ ] **Step 5: Commit Task 4**

```bash
git add TUI/AI-Project-Manager/src/Core/App.psm1 TUI/AI-Project-Manager/VERSION VERSION TUI/AI-Project-Manager/CHANGELOG.md CHANGELOG.md TUI/AI-Project-Manager/tests/Unit/App.Tests.ps1 TUI/AI-Project-Manager/tests/Unit/Static.Tests.ps1
git commit -m "feat(tui): cache session reads and release 0.2.1"
```

### Task 5: Final Acceptance Record

**Files:**
- Modify: `Project-Documentation/Phase-Reports/P08-Report.md`
- Modify: `Project-Documentation/Checkpoints/P08-Checkpoint.md`
- Modify: `Project-Documentation/Handoffs/P08-Next-Phase-Handoff.md`

**Interfaces:**
- Consumes: executed test results and the visual acceptance evidence already supplied by the owner.
- Produces: factual P08 record for this design/performance increment without claiming unobserved host behavior.

- [ ] **Step 1: Update acceptance records with executed evidence**

Record `0.2.1`, test outcomes, menu/cache behavior, and the Capability Library design. Retain any host-rendering condition that was not actually observed.

- [ ] **Step 2: Run documentation and integrity checks**

Run: `git diff --check; git status --short`

Expected: no whitespace errors and only intended repository changes.

- [ ] **Step 3: Commit Task 5**

```bash
git add Project-Documentation/Phase-Reports/P08-Report.md Project-Documentation/Checkpoints/P08-Checkpoint.md Project-Documentation/Handoffs/P08-Next-Phase-Handoff.md
git commit -m "docs(p08): record product shell verification"
```
