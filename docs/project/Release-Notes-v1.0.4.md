# AI Project Manager v1.0.4

This patch updates the platform and TUI version together and consolidates the repository's documentation and plugin-related folder structure. No project runtime behavior or individual Skill version changed.

## Highlights

- Grouped user guides and project records under `docs/guides/` and `docs/project/`.
- Grouped host adapter specifications with the generated package under `Plugins/`.
- Updated Core Engine paths, migration tooling, release allowlists, documentation links, and repository maps.
- Preserved the published v1.0.3 release as the latest available GitHub release.

## Verification And Boundaries

- Capability Library validation passed with all 12 registered Skills and the standalone Prompt.
- Generated Agent Bridge validation passed with 12 Skills; it remains uninstalled and unpublished.
- Local Markdown links in the changed documentation areas passed validation.
- The automated test suites were not run for this organizational change.
- The v1.0.4 source archive and GitHub Release have not been prepared or published.
- P09 external-host and cross-agent gates remain `UNVERIFIED`.
