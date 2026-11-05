# Large Handoff Layout

Create the following relative paths in a staging directory; substitute task-specific documents, not fictional source facts:

- `IMPLEMENTATION-HANDOFF_<Task>.md`: canonical objective, scope, all six stages, decision tree, requirement/evidence/unit/test/acceptance matrix and final status.
- `01-Phases/PHASE-01.md`, etc.: ordered units, prerequisites, master reference, task-specific context, allowed scope, actions, focused tests, acceptance and stop rules; independently understandable without chat history.
- `scripts/`: copies of both skill-owned utilities; `tests/`: the test suite and its fixture; `templates/`: the sample used by that suite. Preserve those relative paths so the tests run offline.
- `HOW-TO-VALIDATE-AND-EXECUTE.md`: adapt the skill-owned guide to actual relative paths and commands.
- `HANDOFF-PACKAGE.json`: generated SHA-256 manifest; never create by hand.

Run document lint and semantic review, then use the skill's bundler with an output outside the staging tree. It automatically adds missing support files at the paths above. Inspect and verify the ZIP; revalidate after transfer. Do not include secrets, profiles or absolute private paths.
