# P07 Host Adapters And TUI Intelligence Skill

> **For Codex:** Execute this owner-authorized phase plan in order, test-first. Keep every write and fixture in the AIPM repository. Do not install, publish, push, or use subagents.

**Goal:** Add a policy-enforced host adapter contract, reproducible local sample bundles using documented host package formats, and a separately versioned AIPM-owned `tui-intelligence` Skill with complete Intelligent TUI design/QA artifacts.

**Architecture:** Extend the existing capability catalog without weakening the immutable 16-import + `project-orchestrator` migration boundary. Host adapters are thin, capability-declared routes into `CoreEngine`; unsupported, unverified, unauthorized, and out-of-project operations fail closed. The TUI Skill is design guidance and templates only, not a claim that a provider is installed or a live TUI has been implemented.

**Stack:** Python 3.11+, JSON, Markdown, unittest, PowerShell-compatible filesystem.

## File Change Map

- `Tests/test_p07_host_adapters.py`, `Tests/test_p07_tui_intelligence.py`: new failing contract tests.
- `Core-Engine/aipm_core/host_adapters.py`, `Plugin-Adapters/`: policy router, capability matrix, schemas, package-format profiles, handoff contract.
- `01-Skills-General/tui-intelligence/`: new Apache-2.0 first-party Skill, prompt, references, QA/evaluation artifacts.
- `Capability-Library/First-Party-Skills.json`, `capabilities.py`, CLI, registry, provenance ledger: add only declared first-party capabilities while retaining imported-byte checks.
- `Plugins/aipm-general-skills/`: regenerate local sample with explicit per-Skill licensing and documented host package manifests; bump its own version.
- Root/project docs and `Project-Documentation/{Phase-Reports,Checkpoints,Handoffs,Release-Notes}`: document P07; update index/rules/version.

## Tasks

1. **Baseline And Plan** — verify P06 gate, current `main` and clean tree; preserve `SOURCE_REPO_WRITES: 0`. *(Completed before plan authoring.)*
2. **Host Adapter Contract Tests** — add tests for matrix validity, Core Engine delegation, read-only/mutation authorization, project boundary, unsupported operations, structured handoff, and imported-vs-first-party license metadata. Run focused tests and confirm RED.
3. **Host Adapter Implementation** — add a minimal `CapabilityRouter` that delegates only policy-allowed commands to Core Engine and never does filesystem access itself; add profiles for local CLI, file-capable coding agents, ChatGPT text-only, and verified package formats. Test fail-closed outcomes.
4. **TUI Skill Contract Tests** — test Skill metadata/version, scope and provenance, links/templates, Title Case/palette/navigation/fallback/anti-flicker requirements, evaluation prompts, output contract and unverified live-visual status.
5. **TUI Skill And References** — author the first-party Skill and companion prompt; deliver a machine-readable screen contract, design handoff, QA report/template, keyboard matrix, screenshot provenance manifest, and realistic evaluation cases. Do not claim physical terminal validation.
6. **Capability Library And Bundle** — extend registry rules only for explicit first-party declarations; retain and recheck all 16 source hashes and derivative metadata; preserve per-skill license boundaries; regenerate and validate bundled host manifests from masters; version platform/Skill/bundle/changelogs. Confirm Personal Skills, `import-memory`, and `morning` remain absent.
7. **Verification And Phase Records** — run focused P07 then complete in-scope P02–P07 suite, core health, library validation, bundle generation/validation, secret/scope checks, `git diff --check`; self-review because subagents are prohibited. Write report/checkpoint/P08 handoff only after evidence; commit locally on `main` only after gates pass; never push.

## Verification Commands

- `python -m unittest Tests.test_p07_host_adapters Tests.test_p07_tui_intelligence Tests.test_p06_capability_library -v`
- `python -m unittest discover -s Tests -p "test_p0[2-7]*.py" -v`
- `python Core-Engine/aipm.py health`
- `python Maintenance-Tools/Invoke-Capability-Library.py validate`
- `python Maintenance-Tools/Invoke-Capability-Library.py validate-plugin`
- `git diff --check`

## Acceptance Boundaries

- PASS requires all blocking tests and repository validations to pass.
- UNVERIFIED: actual Codex/Claude/Gemini installation/runtime invocation, ChatGPT-to-local filesystem access, interactive PowerShell 5.1/7.0 no-flicker visual tests, and independent model-based Skill evaluations.
- No P08 work; next action is report P07 and wait for the owner to authorize P08.
