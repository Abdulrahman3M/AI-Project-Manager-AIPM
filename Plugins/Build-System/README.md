# AIPM Plugin Build System

This folder creates host-specific local Plugin archives from the protected AIPM capability registry. Read [Quick Start](Quick-Start.md) for the PowerShell command.

The builder validates the capability registry and provenance ledger, stages files below the repository, checks every capability hash, creates a ZIP with a SHA-256 sidecar, and validates the finished ZIP. It never installs or publishes a Plugin.

Host profiles are stored in `profiles/`. ChatGPT/Codex and Claude are format-verified package profiles. Antigavity remains `FORMAT_UNVERIFIED` until AIPM receives a provider specification and completes a live host test.
