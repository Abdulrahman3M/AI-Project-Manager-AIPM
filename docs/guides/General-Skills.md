# General Skills

Browse the 14 Skills maintained in [`01-Skills-General`](../../01-Skills-General/). This educational index summarizes what each Skill does and when it can help; the linked `SKILL.md` file contains its complete instructions.

Use the Skill's technical name when asking an AI agent to apply it, or load it through the Skill mechanism supported by your AI host. This page is a reference and does not run Skills.

## Quick Navigation

- [Audio Timing Author](#audio-timing-author)
- [Browser Environment Manager](#browser-environment-manager)
- [Create A Strict Implementation Handoff](#create-a-strict-implementation-handoff)
- [Doc To MD](#doc-to-md)
- [PowerShell TUI App Designer](#powershell-tui-app-designer)
- [Professional Word Designer](#professional-word-designer)
- [Project Manager](#project-manager)
- [Resource Optimization](#resource-optimization)
- [Resume Task](#resume-task)
- [Screenshot To Code](#screenshot-to-code)
- [Shared Project State Manager](#shared-project-state-manager)
- [Task Scope Contract](#task-scope-contract)
- [TUI Intelligence](#tui-intelligence)
- [Web Design Engineering](#web-design-engineering)

---

### Audio Timing Author

`audio-timing-author`

**Description:** Creates publication-ready SRT sentence timings and structured sentence- or word-level timing data from audio and an authoritative transcript.

**When to Use:** Use it when subtitles or transcript segments need accurate timing and the words are already supplied as the source of truth.

**How to Use:** Example: “Use `audio-timing-author` to align this recording with the supplied transcript and prepare an SRT file.”

**Source:** [View Skill Instructions](../../01-Skills-General/audio-timing-author/SKILL.md)

---

### Browser Environment Manager

`browser-environment-manager`

**Description:** Discovers, creates with consent, diagnoses, and verifies isolated Windows browser environments for AI agents, including browser identity, agent extensions, and project-local server reachability.

**When to Use:** Use it before browser automation or screenshots that require a dedicated profile, to recover closed or unreachable browser sessions, verify the agent's browser integration, or connect to a local project server without assuming its port or restarting it.

**How to Use:** Example: “Use `browser-environment-manager` to verify my dedicated Edge profile and Codex extension, then check the project at `http://127.0.0.1:8000/` without restarting its server.”

**Source:** [View Skill Instructions](../../01-Skills-General/browser-environment-manager/SKILL.md)

---

### Create A Strict Implementation Handoff

`create-strict-implementation-handoff`

**Description:** Creates evidence-aware, six-stage implementation handoffs for another agent, with capability profiles, offline validation and portable packaging for complex tasks.

**When to Use:** Use it when the requested deliverable is an implementation handoff, strict task file, or coding brief for another agent to carry out.

**How to Use:** Example: “Use `create-strict-implementation-handoff` to create a guided handoff for the next coding agent.” Small tasks produce one Markdown file; complex tasks produce a self-contained ZIP. The Skill authors the handoff without implementing the target task.

**Source:** [View Skill Instructions](../../01-Skills-General/create-strict-implementation-handoff/SKILL.md)

---

### Doc To MD

`doc-to-md`

**Description:** Converts supplied documents and media into Markdown with an evidence audit that records coverage, source details, and possible conversion losses.

**When to Use:** Use it when an AI agent needs to read, extract, index, quote, or analyze user-provided Office files, PDFs, scans, tables, slides, EPUBs, images, or recordings.

**How to Use:** Example: “Use `doc-to-md` to convert these supplied files and report any content that needs checking against the originals.”

**Source:** [View Skill Instructions](../../01-Skills-General/doc-to-md/SKILL.md)

---

### PowerShell TUI App Designer

`powershell-tui-app-designer`

**Description:** Guides the design, implementation, troubleshooting, testing, and release of professional PowerShell terminal applications for Windows PowerShell 5.1 and PowerShell 7.

**When to Use:** Use it when creating or changing an interactive terminal application, including its navigation, rendering, input lifecycle, or packaging.

**How to Use:** Example: “Use `powershell-tui-app-designer` to plan an accessible PowerShell 7 and Windows PowerShell 5.1 terminal interface.”

**Source:** [View Skill Instructions](../../01-Skills-General/powershell-tui-app-designer/SKILL.md)

---

### Professional Word Designer

`professional-word-designer`

**Description:** Guides evidence-controlled research, editorial planning, enterprise-grade Word document production, a 36-pattern template atlas, citation handling, Arabic/English RTL hardening, visuals, and publication-quality review.

**When to Use:** Use it for substantial research papers, reports, books, theses, educational materials, executive documents, or other long-form publications that need structured evidence, polished visual design, correct multilingual layout, and document QA.

**How to Use:** Example: “Use `professional-word-designer` to plan and produce a cited research report from these approved sources.”

**Source:** [View Skill Instructions](../../01-Skills-General/professional-word-designer/SKILL.md)

---

### Project Manager

`project-manager`

**Description:** Coordinates governance, task lifecycle, specialist routing and verification as the mandatory AIPM entry.

**When to Use:** Use for every AIPM-managed task interaction, including revisions and reopened work.

**How to Use:** Example: “Start Project Manager for this task and apply the scope and resource policies.”

**Source:** [View Skill Instructions](../../01-Skills-General/project-manager/SKILL.md)

---

### Resource Optimization

`resource-optimization`

**Description:** Controls tokens, time, tool calls, limits and owner-approved delegation without reducing quality.

**When to Use:** Use continuously under Project Manager for every AIPM-managed task.

**How to Use:** Example: “Apply Resource Optimization while preserving every required check.”

**Source:** [View Skill Instructions](../../01-Skills-General/resource-optimization/SKILL.md)

---

### Resume Task

`resume-task`

**Description:** Reconstructs and finishes interrupted work by checking the original request, current files, project rules, and evidence before continuing.

**When to Use:** Use it after a session ends unexpectedly, context is lost, work is handed to another agent, or completion needs to be audited before resuming.

**How to Use:** Example: “Use `resume-task` to verify the current state of this interrupted task and complete the remaining requirements.”

**Source:** [View Skill Instructions](../../01-Skills-General/resume-task/SKILL.md)

---

### Screenshot To Code

`screenshot-to-code`

**Description:** Converts screenshots and design images into editable frontend code with measured geometry, font and asset provenance, Arabic RTL support, and regional rendered comparisons. Screenshot-only work is the default; visible browser inspection requires explicit opt-in.

**When to Use:** Use it to recreate a supplied website or app screenshot in the existing frontend stack, or repair visual differences while preserving business behavior.

**How to Use:** Example: “Use `screenshot-to-code` to implement this screenshot in the current project, compare local renders at the reference viewport, and ask before inspecting the reference page in an approved browser.”

**Source:** [View Skill Instructions](../../01-Skills-General/screenshot-to-code/SKILL.md)

---

### Shared Project State Manager

`shared-project-state-manager`

**Description:** Makes long-running project work resumable across sessions or AI agents using task state, verified checkpoints, handoffs, templates, and supporting tools.

**When to Use:** Use only when the owner explicitly requests the separate local PowerShell state tool; ordinary AIPM Core state operations remain separate.

**How to Use:** Example: “Explicitly invoke the local `shared-project-state-manager` through PowerShell to prepare a verified handoff.”

**Source:** [View Skill Instructions](../../01-Skills-General/shared-project-state-manager/SKILL.md)

---

### Task Scope Contract

`task-scope-contract`

**Description:** Defines task scope, read tracking, bounded retries and evidence-based quality gates.

**When to Use:** Use continuously under Project Manager for every AIPM-managed task.

**How to Use:** Example: “Establish a Task Scope Contract for the current task.”

**Source:** [View Skill Instructions](../../01-Skills-General/task-scope-contract/SKILL.md)

---

### TUI Intelligence

`tui-intelligence`

**Description:** Designs, specifies, reviews, and verifies accessible PowerShell terminal interfaces with evidence-based status, keyboard navigation, responsive layouts, and clear visual hierarchy.

**When to Use:** Use it to define or review TUI screens, accessibility, interaction contracts, QA plans, or evidence for terminal interface behavior.

**How to Use:** Example: “Use `tui-intelligence` to review this terminal screen design for accessibility and verifiable status.”

**Source:** [View Skill Instructions](../../01-Skills-General/tui-intelligence/SKILL.md)

---

### Web Design Engineering

`web-design-engineering`

**Description:** Designs, builds, reviews, and verifies distinctive responsive web interfaces with a product-specific visual direction, accessible behavior, purposeful motion, and current rendered evidence.

**When to Use:** Use it for websites, landing pages, web-app screens, components, design-system work, reference-fidelity implementation, or UI quality reviews. It is not for backend-only work.

**How to Use:** Example: “Use `web-design-engineering` to redesign this customer portal while preserving its component library and verifying keyboard, narrow-screen, and reduced-motion behavior.”

**Source:** [View Skill Instructions](../../01-Skills-General/web-design-engineering/SKILL.md)

---

[← Back To Project Home](../../README.md)
