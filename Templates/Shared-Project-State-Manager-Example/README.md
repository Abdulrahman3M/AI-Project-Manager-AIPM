# Shared Project State Manager Example

This folder is a maintained learning template for the current AIPM state layout. It demonstrates how to describe one project, record a task, hand work to another agent, and document safe file operations.

## Important: Example, Not A Live Project

All project names, IDs, task records, timestamps, Git details, and evidence here are fictional examples. Do not register this folder as a project, copy the whole folder into a real project, or treat its sample status as verified work.

To start safely, register your real project through AIPM's **Registry Management** screen. Core creates a fresh `<project-root>/Shared-Project-State-Manager/` with unique project identity and runtime metadata. Then use these example documents as references when writing task plans or handoffs in that real state folder. Never copy the sample `Project-Manifest.json` or `State-Manifest.json` into a live state folder.

## What The Files Demonstrate

- `Project-Overview.md`: what belongs in a concise project context note.
- `Current-State.md`: how to distinguish verified facts from unverified details.
- `Next-Agent-Handoff.md`: a restartable handoff with an exact next action.
- `File-Operations-Policy.md`: safe, reversible handling of project files.
- `Root-Exceptions.md`: how to record justified root-level files.
- `State-Manifest.example.json`: illustrative state metadata only; Core generates the real manifest.
- `Tasks/Task-Example/`: sample scope, plan, blockers, decisions, changed-file map, and verification report.

The real runtime layout is documented in [Plugin Distribution And Project Architecture](../../docs/project/Architecture/Plugin-Distribution-Architecture.md) and the beginner guides under `docs/guides/`.
