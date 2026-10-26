# AI Project Manager v1.8.2

**Date:** 2026-10-27. Repository update; not a GitHub Release.

- Re-ran the three previously skipped Windows junction and reparse-path security tests outside the restricted execution sandbox. All three passed using real junctions in an isolated checkout.
- Recorded the result in the [verification record](../../research/Screenshot-To-Code-Verification.md#2026-10-27-junction-recheck) and [support matrix](../Support-Matrix.md#v182-local-repository-update).
- Synchronized platform and TUI versions; Core and TUI runtime behavior did not change.
- Capability registry and Bridge validation passed; the unchanged Bridge `1.2.1` and host Plugin archives `1.8.1` retain their independent versions. No Skill or Plugin content changed.
- General capability documentation and P10 release packaging checks each passed all 3 tests in an isolated validation checkout.
- The full repository suite, browser inspection and host-native Plugin installation were not performed in this follow-up.
