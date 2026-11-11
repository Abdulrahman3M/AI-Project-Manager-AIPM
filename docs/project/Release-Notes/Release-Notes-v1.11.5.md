# AIPM v1.11.5 Repository Update

This local, unpublished update introduces the Golden Triangle operating model for AIPM-managed task interactions. Project Manager coordinates task lifecycle and governance; Task Scope Contract handles scope and quality evidence; Resource Optimization handles resource efficiency and delegation policy.

The separate Shared Project State Manager is an opt-in local PowerShell tool. Existing AIPM Core project registry and task-state operations remain separately permission-gated. The supplied architecture diagram and [operating model](../Architecture/Golden-Triangle-Operating-Model.md) describe the intended policy.

Host instructions and package manifests do not by themselves enforce Skill invocation or grant local access. Actual host runtime and interception capabilities must be verified separately. This repository update is not a published release, and no Plugin is installed merely because a local archive exists.

The platform and TUI version declarations are synchronized. The preceding [v1.10.5 update](Release-Notes-v1.10.5.md) and its existing work remain preserved.
