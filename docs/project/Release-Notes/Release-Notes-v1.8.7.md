# AIPM v1.8.7 Release Notes

## Antigravity Skills Bundle Layout

- Replaced the unrecognized `antigavity-plugin.json` with the documented `.agents/skills/<skill>/SKILL.md` discovery layout.
- Marked the Antigravity Skills folder layout `FORMAT_VERIFIED`; the ZIP is a transport bundle, not a native Plugin installer. Native installation and runtime discovery remain unverified until tested in Antigravity.
- Updated the builder and archive validator to use the host-specific Skills root and removed the fabricated manifest.
- Built ChatGPT/Codex, Claude and Antigravity archives at platform `1.8.7`; all three passed inventory, manifest and checksum validation. The six plugin distribution tests passed.
- The archives are local, uninstalled and unpublished. No GitHub push, tag or Release was created.
