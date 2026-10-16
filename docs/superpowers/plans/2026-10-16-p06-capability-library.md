# P06 Capability Library Implementation Plan

> **For agentic workers:** Use `superpowers:executing-plans` inline. Each task uses TDD and ends with verification.

**Goal:** Register the approved Skill/Prompt inventory, build a verifiable general-only Plugin, and close P06 with auditable evidence.

**Architecture:** A Core Engine capability module scans and validates authoritative masters against P01 provenance, then emits the capability registry and verifies a generated Plugin copy. A small maintenance CLI controls baseline initialization/refresh and Plugin generation; documentation reflects owner-approved scope.

**Tech Stack:** Python 3 standard library, JSON, SHA-256, `unittest`, Git.

**Spec:** `docs/superpowers/specs/2026-10-16-p06-capability-library-design.md`

## Global Constraints

- Work and write only inside the AIPM repository; the old Toolkit is read-only.
- Preserve all 17 current Skills; never edit imported masters; exclude `import-memory`, `morning`, and Personal Skills.
- Keep standalone Prompt root at `02-Prompt-General`; no Skill-owned Prompt duplication.
- Root Apache-2.0 applies only to AIPM-authored material; preserve source and third-party notices.
- No publish, push, or install; package output is a local sample.
- Use Title Case for new human-facing names; preserve technical names and Skill slugs.

## Review Focus

- Stale or tampered registry/source hashes must block validation and Plugin generation (Task 1/2).
- Hidden, sensitive, or linked files must never enter a Plugin bundle (Task 2).
- Unauthorized baseline refresh must fail without changing records (Task 1).
- A Skill-owned Prompt must not be duplicated as standalone or bundled into the Plugin (Task 1/2).
- Invalid SemVer/frontmatter/changelog must fail clearly rather than create a partial registry (Task 1).

---

### Task 1: Registry, Provenance, And Version Policy

**Files:** `Tests/test_p06_capability_library.py`; `Core-Engine/aipm_core/capabilities.py`; `Maintenance-Tools/Invoke-Capability-Library.py`; `Capability-Library/Registry.json`; `Project-Documentation/Provenance/Capability-Library-Ledger.json`; `Project-Documentation/Provenance/Source-Revision.json`; `Project-Documentation/Provenance/Source-Licenses/Universal-AI-ToolKit-LICENSE.txt`; root `VERSION` and `CHANGELOG.md`.

**Interfaces:** `scan_library(root) -> dict`; `validate_registry(root) -> dict`; `classify_version_change(before, after, breaking=False) -> str`; `bump_semver(version, increment, project=False) -> str`; `initialize_registry(root)`; `refresh_registry(root, *, confirmed, reason)`.

- [x] Add tests for the 17/1 inventory, exact owned Prompt map, imported hash integrity, malformed metadata, version edit/add/remove/major classification, project MINOR carry-forward, atomic-write rollback, and refusal/approval for baseline refresh.
- [x] Run focused P06 tests and observe expected failures before implementation.
- [x] Implement scanner, registry validation, SemVer policy, source provenance, safe JSON writes, and explicit baseline controls.
- [x] Run focused tests; revalidate the 16 P01 byte-preserved imports against the in-repository migration hashes. The P01 test module itself was not rerun because it reads the out-of-scope Archive tree.

### Task 2: General-Only Plugin Distribution

**Files:** `Core-Engine/aipm_core/capabilities.py`; `Tests/test_p06_capability_library.py`; `Plugins/aipm-general-skills/**`.

**Interfaces:** `build_plugin(root, target, replace_generated=False) -> dict`; `validate_plugin(root, target) -> dict`.

- [x] Add tests for complete copy parity, excluded Skills/Prompts, license retention, deterministic rebuild, tamper detection, sensitive-file rejection, path containment, and replacement rollback.
- [x] Run focused Plugin tests and observe expected failures before implementation.
- [x] Implement staged generation and fail-closed verification; create the local sample.
- [x] Run focused tests and verify generated bundle parity.

### Task 3: Phase Records And Final Gate

**Files:** `README.md`; `AGENTS.md`; `Index.md`; `02-Prompt-General/README.md`; `Capability-Library/README.md`; `Project-Documentation/Project-Rules.md`; `Project-Documentation/Phase-Reports/P06-Report.md`; `Project-Documentation/Checkpoints/P06-Checkpoint.md`; `Project-Documentation/Handoffs/P06-Next-Phase-Handoff.md`; `Project-Documentation/Release-Notes-v0.1.0.md`.

- [x] Synchronize inventory, versions, licensing scope, limitations, and exact next action.
- [x] Run `python -m unittest Tests.test_p06_capability_library -v` (13/13).
- [x] Run the in-scope integrated suite `python -m unittest discover -s Tests -p "test_p0[2-6]*.py" -v` (84/84 with the authorized scoped Windows junction capability).
- [x] Run CLI health/validate/build checks, `git diff --check`, verify P01 hashes through the P06 scanner, and inspect repository status.
- [x] Self-review the full P06 diff (no subagents per owner instruction); P06 is complete and P07 remains unstarted.
