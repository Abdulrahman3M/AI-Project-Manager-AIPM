# AI Project Manager v1.4.7

## Task Report Prompt Rendering

The PowerShell TUI now renders a long typed value as explicit terminal rows. This prevents terminal line wrapping from visually overwriting the prompt's Enter and Escape guidance while writing a Task Report or any other free-text prompt.

The full PowerShell TUI unit suite includes a narrow-terminal regression test that verifies the report content is preserved and the confirmation controls remain below the wrapped input.

## Version Scope

- AIPM platform: `1.4.7`
- PowerShell TUI: `1.4.7`
- Skills and standalone Prompts: unchanged
- Plugin and Bridge distributions: unchanged; no package was rebuilt

This is an unpublished repository update. The latest published GitHub Release remains `v1.4.0`.
