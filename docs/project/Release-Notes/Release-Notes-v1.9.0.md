# AIPM v1.9.0 Release Notes

## Project Setup And FIRG

- Registration offers optional Git and FIRG before the shared-state step required for registration. FIRG requires a Git repository at the project root.
- Git version reporting compares the installed executable with an offline `2.20.0` compatibility baseline; it does not claim that the executable is the latest release. On explicit request the interface can open the Git for Windows updater in a separate window; completion of a system update has not been verified.
- FIRG records verified Git references and user-supplied explanations in structured records and Markdown reports. An optional local post-commit prompt supports interactive Git terminals without replacing existing hooks; non-interactive and bypassed hooks require the manual workflow.
- Project management displays a background component check and offers explicit maintenance. Managed FIRG, root-rule and hook updates retain backups and refuse to overwrite locally modified material; interrupted FIRG updates can be resumed when their inputs remain unchanged.
- A supported legacy shared-state schema upgrade is previewed and backed up before recording an upgrade event. Conflicting or invalid state remains subject to the existing recovery workflow.

## Verification Limits

FIRG identifies possible impacts; a clean merge or AI-only analysis does not prove regression safety. Existing unmanaged FIRG installations, custom hooks, translated instructions, and instruction files with versioned metadata require review. Tests and terminal observations are reported in the support matrix; no remote branch protection, Plugin installation, push, tag, or publication is implied.

Platform and TUI versions are synchronized at `1.9.0`. Independently versioned Skills and Plugins remain unchanged. This is an unpublished local repository update.
