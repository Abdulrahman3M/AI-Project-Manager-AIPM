# Host Adapter Contract

## Purpose

Host adapters are thin entry points into the AIPM Core Engine. The checked-in [Host Capability Matrix](Host-Capability-Matrix.json) declares what is implemented, conditionally available, or unsupported. A package format being documented does not prove an installed or functioning runtime adapter.

## Runtime Rules

- Bind each adapter instance to one registered `project_id`; never accept a project filesystem path from the host request.
- Consult the matrix before dispatch. Unsupported host or command returns `BLOCKED` without calling Core.
- Delegate supported commands only through `CoreEngine.execute(CommandEnvelope(...))`.
- Read operations are permitted only where the host exposes the direct Core API. Mutations additionally require `allow_mutations=True`, a nonnegative expected revision, and a nonempty idempotency key; Core remains responsible for state validation and commit.
- Do not create files, invoke shell commands, access secrets, publish, install, or spawn agents from the adapter layer.
- A manual handoff is a path-free snapshot labeled `UNVERIFIED`; import is refused until the local Core rereads the registered project.
- Missing host tools, permissions, credentials, or executable are `UNVERIFIED` or `BLOCKED`, never inferred as success.

## Status Semantics

`PASS` means the local Core operation returned success. `BLOCKED` means policy or Core refused it. `UNVERIFIED` means data crossed a manual or unverified host boundary and cannot be treated as fresh authoritative state.

## Format References

- [OpenAI Portable Agent Plugins](https://developers.openai.com/plugins/build/plugins) use a root `plugin.json` and `skills/`; `.codex-plugin/plugin.json` remains a compatibility manifest.
- [Claude Code Plugins](https://code.claude.com/docs/en/plugins) use `.claude-plugin/plugin.json` and can bundle Skills under `skills/`.
- [Gemini CLI Extensions](https://github.com/google-gemini/gemini-cli/blob/main/docs/extensions/reference.md) use root `gemini-extension.json` and can bundle Agent Skills under `skills/`.

Package manifests establish layout compatibility only. This repository does not install or execute any provider package.
