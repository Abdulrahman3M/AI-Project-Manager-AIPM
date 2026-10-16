# P06 Capability Library Design

## Objective

Register the already-migrated General Skills and approved standalone Prompt, generate a reproducible general-only Plugin sample, and establish auditable provenance and version-classification rules without editing imported Skill masters.

## Accepted Inventory And Owner Decisions

- Register the 17 Skills present in AIPM: the 16 byte-preserved Skills plus the documented `project-orchestrator` derivative. `import-memory`, `morning`, and Personal Skills remain excluded.
- Keep the owner-added standalone Prompt under `02-Prompt-General`; do not move it to the package's superseded `03-Prompt-General` path.
- Keep Skill-owned Prompts in their owning Skill trees and list their exact paths; do not duplicate them in the standalone library or Plugin.
- Source `main` was read-only verified at commit `162dcdcac08d36967c00a6b4cadaf3ce8bddb4f2` on 2026-10-16. The ZIP migration record remains the authority for per-file import hashes.
- Root Apache-2.0 applies only to AIPM-authored files. Carry the source Toolkit Personal Use License and every per-Skill license/notice into generated copies; do not publish or install the sample.
- A new platform version baseline is `0.1.0`; Skill and Plugin version streams remain independent. Protected integrity baselines may only be refreshed through an explicit confirmation command.

## Architecture

`Core-Engine/aipm_core/capabilities.py` will validate the approved Skill inventory, frontmatter, SemVer/changelog metadata, prompt relationships, license evidence and SHA-256 baseline. `Maintenance-Tools/Invoke-Capability-Library.py` will expose validation, one-time baseline initialization, explicitly confirmed baseline refresh, and deterministic Plugin generation. `Capability-Library/Registry.json` and the provenance ledger are the machine-readable records; the generated Plugin is a verified copy of General Skill masters only.

Plugin output is staged inside the repository, rejects links and sensitive files, retains licenses, has no Apache license claim, and must match its source tree exactly. Publication and host installation are out of scope.

## Acceptance Criteria

1. The registry contains exactly 17 active Skills, their required metadata and exact Skill-owned Prompt relationships, plus the approved standalone Prompt.
2. All 16 byte-preserved Skills continue to match the recorded migration file hashes; `project-orchestrator` retains only its existing, documented migration exception.
3. The Plugin sample contains every active General Skill byte-for-byte, no Personal/excluded Skill and no standalone Prompt; its manifest validates source and generated SHA-256 values.
4. No sensitive file is copied; license and attribution files remain present, and the Plugin makes no blanket license assertion.
5. Version classification covers edit, add, remove and project-wide breaking changes, with the owner-specific AIPM MINOR numbering exception and standard independent Plugin SemVer.
6. Registry baseline initialization is one-time; refreshing it requires an explicit confirmation flag and reason.
7. P06 report, checkpoint, next-phase handoff, root index, README and change/release metadata agree. The full test suite and focused acceptance checks pass before P06 is marked complete.

## Scope Boundaries

No Skill master content changes, no Personal Skills, no old Toolkit writes, no external-project data, no dependency installation, no Plugin publication/installation, and no transition into P07 implementation.
