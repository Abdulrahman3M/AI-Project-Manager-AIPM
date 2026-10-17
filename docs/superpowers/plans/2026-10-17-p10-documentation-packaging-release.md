# P10 Documentation Packaging And Release Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Produce beginner-friendly documentation and a verified AIPM source package, then publish the owner-authorized v1.0.2 GitHub release without installing or triggering paid CI workflows.

**Architecture:** A small standard-library Python release module owns allowlisted source selection, deterministic ZIP creation, sensitivity checks, checksum generation, and archive verification. Public documentation describes supported environments and the distinction between a prepared local artifact and a published release. Phase evidence records the P09 waiver and the remaining unverified gates without changing their status.

**Tech Stack:** Python 3 standard library, PowerShell 5.1/7 test runners, Git metadata, Markdown, SHA-256.

**Spec:** `Archive/AI-Project-Manager-AIPM-V2/Phases/P10-Documentation-Packaging-And-Release.md`

## Global Constraints

- Work only inside the AIPM repository; do not modify the Universal AI ToolKit source.
- Publish only to `Abdulrahman3M/AI-Project-Manager-AIPM`; preserve its current visibility and do not install the Agent Bridge or publish it to a marketplace.
- Do not trigger GitHub Actions or other paid CI workflows; use the local verified package and owner-authorized repository release path.
- Keep generated release artifacts in-repository and scan them for credentials, local repository paths, test traces, and non-public development folders.
- Preserve the owner-approved P09 exceptions as `UNVERIFIED`; do not reclassify them as PASS.
- Apply the AI Project Manager Personal Use License to project material and generated distributions.

## Review Focus

- A ZIP must be byte-reproducible for identical inputs and must not include itself or generated test directories.
- A secret-looking filename, private key, cloud credential, or actual checkout path must stop packaging before an archive is written.
- The archive manifest must hash every payload file and verification must reject any modified payload.
- Version and changelog metadata must agree across platform, TUI, and local bridge package.
- Documentation must not imply host installation, publication, or closure of P09's unverified external gates.

---

### Task 1: Deterministic Release Builder

**Files:**
- Create: `Core-Engine/aipm_core/release.py`
- Create: `Maintenance-Tools/New-Release-Package.py`
- Create: `Tests/test_p10_release.py`

- [ ] Write failing tests for deterministic build, checksum/manifest verification, and sensitive/local-path rejection.
- [ ] Implement an allowlisted, deterministic source ZIP builder with SHA-256 sidecar and archive verifier.
- [ ] Run the focused P10 tests and the existing capability validation.

### Task 2: Release Documentation And Metadata

**Files:**
- Create: `Project-Documentation/Release-Notes-v1.0.2.md`
- Create: `Project-Documentation/Support-Matrix.md`
- Modify: `VERSION`, `CHANGELOG.md`, `TUI/AI-Project-Manager/VERSION`, `TUI/AI-Project-Manager/CHANGELOG.md`, `README.md`, `TUI/AI-Project-Manager/README.md`, `.gitignore`

- [ ] Advance the platform and TUI patch version to `1.0.2` with matching release notes.
- [ ] State the verified Windows PowerShell/Python support matrix, local-only package status, and owner-controlled host activation.
- [ ] Run version-sync and documentation/package tests.

### Task 3: Local Build, Audit, And Phase Evidence

**Files:**
- Create: `Project-Documentation/P10-Implementation-Plan.md`
- Create: `Project-Documentation/Phase-Reports/P10-Report.md`
- Create: `Project-Documentation/Checkpoints/P10-Checkpoint.md`
- Create: `Project-Documentation/Handoffs/P10-Release-Handoff.md`
- Modify: `Project-Documentation/Handoffs/P09-Next-Phase-Handoff.md`

- [ ] Build and verify `Releases/AI-Project-Manager-v1.0.2.zip` and its SHA-256 sidecar.
- [ ] Run the focused Python, capability, and both PowerShell compatibility suites; record exact outcomes.
- [ ] Review the scoped diff and record release decision as local-prepared only, with P09 exceptions inherited.

### Task 4: Beginner Guides And Owner-Authorized GitHub Release

**Files:**
- Create: `docs/User-Guides/README.md`
- Create: `docs/User-Guides/Beginner-Guide.en.md`
- Create: `docs/User-Guides/دليل-المبتدئين.ar.md`
- Modify: `Core-Engine/aipm_core/release.py`, `README.md`, `Index.md`, release notes, support matrix, and P10 phase evidence

- [ ] Write matching step-by-step English and Arabic guides using verified commands and clearly state read-only, package-only, and unverified host boundaries.
- [ ] Include only the guide directory in the allowlisted release package; keep internal plans, checkpoints, and temporary workspaces out.
- [ ] Build and verify the v1.0.2 archive, then publish the repository commit, tag, and release asset to the specified GitHub repository without invoking Actions.
- [ ] Reconcile README, release notes, support matrix, and phase evidence with the actual remote result; keep P09 external gates `UNVERIFIED` and the current repository visibility unchanged.
