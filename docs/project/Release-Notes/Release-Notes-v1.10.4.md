# AIPM v1.10.4 Release Notes

AIPM v1.10.4 raises the task artifact size limit from 16 MiB to 256 MiB in the Core Engine and host adapters, supporting large project packages, archives, and binaries within task workflows.

Artifact hash calculation in `list_artifacts` and `generate_metadata` is now streamed in 64 KiB chunks, eliminating excessive memory consumption when inspecting large task artifacts. Platform and TUI metadata are versioned together; this is a local repository update, not a published GitHub Release.
