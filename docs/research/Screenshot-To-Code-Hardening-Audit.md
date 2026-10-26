# Screenshot To Code Hardening Audit

**Audit date:** 2026-10-26
**Status:** Source, issue and instruction review completed; browser use and three junction-dependent checks remain unverified.
**Remote publication:** None. The local checkout was fast-forwarded to `origin/main` before editing; current changes remain local.

## Synchronization And Scope

- Remote: `origin` (AIPM GitHub repository).
- Before fetch: clean `main` at `2a32807bfa44bc2d2405d83006f04e10c0060571`; cached `origin/main` matched.
- After fetch: `origin/main` was one commit ahead. `git pull --ff-only origin main` fast-forwarded to `45c5d0746808a1d7a0250326cdf83e45ac1dc15d`; no merge commit or rebase.
- The post-sync source audit attempted 31 candidate repositories. Twenty-nine had readable primary evidence. The README and primary Skill for `Mrxyy/screenshot-to-page` were unavailable; `microsoft/AI-Lab` returned 404. Those two are not counted among the 29.
- Fifty-eight reviewed file paths were checked against their pinned blob identifiers: 56 matched and two were unavailable. The checked primary/additional evidence did not change from the previously recorded blobs. Pinned commit refs and each blob SHA are in [the machine-readable source audit](Screenshot-To-Code-Hardening-Audit.json); the pre-existing [research matrix](Screenshot-To-Code-Research.md) describes each project and its trade-offs.
- No third-party code was run, installed, copied or packaged. Public issue bodies and reported credentials are not reproduced in the issue index.

## GitHub Issue Inventory

Search used `is:issue` (excluding pull requests) against the 29 audited repositories. The connector exposes at most 100 results per query, so the 410 issues in `abi/screenshot-to-code` were split by state and date; the pre-2023 partition returned zero. The full title/status/URL index is [Screenshot-To-Code-Issue-Index.csv](Screenshot-To-Code-Issue-Index.csv).

| Scope | Repositories | Issues | Open | Closed |
| --- | ---: | ---: | ---: | ---: |
| Audited projects | 29 | 538 | 167 | 371 |
| Discovery-only `Mrxyy/screenshot-to-page` | 1 | 1 | 1 | 0 |
| Inaccessible `microsoft/AI-Lab` | 1 | unavailable | unavailable | unavailable |

### Per-Project Counts And Pinned Evidence

| Project | Default branch | Reviewed ref | Reviewed source files (blob prefixes) | Root license notice | Issues (open/closed) |
| --- | --- | --- | --- | --- | --- |
| [Ixe1/ui-from-image](https://github.com/Ixe1/ui-from-image) | `master` | `87ebe2e9b99a` | SKILL.md (ae2484d47417)<br>scripts/compare_screenshots.py (f178cea733f9) | UNVERIFIED | 0 (0/0) |
| [santowilem/skills](https://github.com/santowilem/skills) | `main` | `2caf2e1dd0e5` | skills/clone-ui/SKILL.md (f4b7fa0d07b8) | UNVERIFIED | 0 (0/0) |
| [sevzq/screenshot-to-html](https://github.com/sevzq/screenshot-to-html) | `main` | `7b5469b2c2c9` | SKILL.md (3d6a4094e550)<br>scripts/shot.mjs (b0767378c722) | MIT | 0 (0/0) |
| [Hoshino-wind/pixel-twin-lab](https://github.com/Hoshino-wind/pixel-twin-lab) | `main` | `138f40b9654d` | SKILL.md (595e37fd839f)<br>scripts/pixel_twin.py (e89b62be0d00) | Apache-2.0 | 0 (0/0) |
| [Core-Mate/Pixel-Perfect-Web-Replica](https://github.com/Core-Mate/Pixel-Perfect-Web-Replica) | `main` | `4673cf86f895` | SKILL.md (c53879d9eaf8)<br>scripts/mirror_public_page.py (e3f262a783fa) | MIT | 0 (0/0) |
| [fitoe/DesignToCode](https://github.com/fitoe/DesignToCode) | `main` | `80070c17f4e3` | skills/design-to-code/SKILL.md (25a708dd661d) | MIT | 0 (0/0) |
| [oil-oil/draw-ui](https://github.com/oil-oil/draw-ui) | `main` | `e4e03662144a` | SKILL.md (3b3792ad2df0) | UNVERIFIED | 0 (0/0) |
| [xiaopu-ai/web-clone-prompt](https://github.com/xiaopu-ai/web-clone-prompt) | `main` | `e943ee25da8d` | SKILL.md (7f99ba931471) | MIT | 0 (0/0) |
| [zwq-top/ui-image-to-code-studio](https://github.com/zwq-top/ui-image-to-code-studio) | `main` | `3376d299d0c5` | skill/SKILL.md (9c3ce1a52579) | MIT | 0 (0/0) |
| [zhu-guli326/image2_UI](https://github.com/zhu-guli326/image2_UI) | `main` | `462d6bd1ea8d` | SKILL.md (de53572287e7) | MIT | 0 (0/0) |
| [abi/screenshot-to-code](https://github.com/abi/screenshot-to-code) | `main` | `a8139779f7c5` | backend/prompts/__init__.py (57f5b7bcbcfd)<br>backend/prompts/system_prompt.py (65719c77b136) | MIT | 410 (126/284) |
| [uxkin/agent](https://github.com/uxkin/agent) | `main` | `6bb351e95de5` | .agents/skills/ui-from-screenshot/SKILL.md (b172ad21e68c) | MIT | 0 (0/0) |
| [ericshang98/Perfect-Web-Clone](https://github.com/ericshang98/Perfect-Web-Clone) | `main` | `c846c37937a7` | skill/SKILL.md (51e6e7bae311) | MIT | 6 (6/0) |
| [HarKro753/claude-copy](https://github.com/HarKro753/claude-copy) | `main` | `4cdf1d09ea1c` | README.md (2b69e034d66f) | MIT | 0 (0/0) |
| [rodrigonask/claude-code-clone-website-skill](https://github.com/rodrigonask/claude-code-clone-website-skill) | `main` | `0e7df323e8a2` | clone-website/SKILL.md (28534f0842b8) | MIT | 0 (0/0) |
| [WCF900905/screenshot-to-design-system](https://github.com/WCF900905/screenshot-to-design-system) | `main` | `030e3007a829` | SKILL.md (8c7eea92538f) | MIT | 0 (0/0) |
| [openwarehq/calque](https://github.com/openwarehq/calque) | `main` | `7749b86c0a7f` | README.md (efea95f2a7fd) | MIT | 0 (0/0) |
| [max0821/web-design-skill](https://github.com/max0821/web-design-skill) | `main` | `34a0470ea0ef` | web-design/SKILL.md (46f42eb1825d) | MIT | 0 (0/0) |
| [Huc91/pixel-perfect-skill](https://github.com/Huc91/pixel-perfect-skill) | `main` | `2c677882743e` | SKILL.md (1cb0ceedb8d2) | UNVERIFIED | 0 (0/0) |
| [niuniu122/pixel-perfect-website-clone-skill](https://github.com/niuniu122/pixel-perfect-website-clone-skill) | `main` | `80847e1ceee7` | SKILL.md (52988f844320) | UNVERIFIED | 0 (0/0) |
| [vibeeval/vibecosystem](https://github.com/vibeeval/vibecosystem) | `main` | `3b763b1fb288` | skills/visual-verdict/SKILL.md (926494ef2b5f) | MIT | 6 (5/1) |
| [ytvee-dev/webdev-agent-kit](https://github.com/ytvee-dev/webdev-agent-kit) | `main` | `ada52938b678` | skills/design-screenshot-spec/SKILL.md (d0ce35b9de3f) | Apache-2.0 | 20 (2/18) |
| [Surya17155/Replica](https://github.com/Surya17155/Replica) | `main` | `eede9904cd59` | SKILL.md (c1a007e84ae2) | MIT | 0 (0/0) |
| [vishnu-madhavan-git/9designer-skills](https://github.com/vishnu-madhavan-git/9designer-skills) | `main` | `b9b9289feec3` | skills/9designer/SKILL.md (150e4a54591a) | Apache-2.0 | 0 (0/0) |
| [gojodennis/OpenKombai](https://github.com/gojodennis/OpenKombai) | `main` | `515235e2a2c7` | README only | MIT | 1 (1/0) |
| [NoviScl/Design2Code](https://github.com/NoviScl/Design2Code) | `main` | `7a575e4c33f4` | README only | UNVERIFIED | 30 (7/23) |
| [tonybeltramelli/pix2code](https://github.com/tonybeltramelli/pix2code) | `master` | `eab4816e397e` | README only | Apache-2.0 | 0 (0/0) |
| [emilwallner/Screenshot-to-code](https://github.com/emilwallner/Screenshot-to-code) | `master` | `f7f8ceee3809` | README only | Apache-2.0 | 60 (18/42) |
| [mostafasadeghi97/design2code](https://github.com/mostafasadeghi97/design2code) | `main` | `5ffe29b31277` | README only | MIT | 5 (2/3) |

### Issue Findings And AIPM Decisions

Issue state is a report status, not proof of repair. Closed issues were treated as fixed only where a maintainer comment explicitly supported that conclusion. All issue titles/statuses are indexed; detailed issue-body/comment checks focused on reports that could affect this Skill.

| Evidence | What it indicates | AIPM treatment |
| --- | --- | --- |
| [abi#636](https://github.com/abi/screenshot-to-code/issues/636), [Perfect-Web-Clone#3](https://github.com/ericshang98/Perfect-Web-Clone/issues/3), [#4](https://github.com/ericshang98/Perfect-Web-Clone/issues/4) | Browser automation can fail on Windows/runtime combinations. | Keep browser use optional and capability-gated; continue in screenshot-only mode when preflight fails. No claim that AIPM browser rendering works on every host. |
| [abi#216](https://github.com/abi/screenshot-to-code/issues/216), [abi#262](https://github.com/abi/screenshot-to-code/issues/262) | Requests involve URL capture and password-protected pages. | Require specific user consent for a page and visible client-side inspection. Do not bypass sign-in or access hidden/private information. |
| [abi#435](https://github.com/abi/screenshot-to-code/issues/435), [abi#320](https://github.com/abi/screenshot-to-code/issues/320), [abi#6](https://github.com/abi/screenshot-to-code/issues/6), [NoviScl#31](https://github.com/NoviScl/Design2Code/issues/31) | Multiple sizes/viewports and screenshot capture conditions affect comparisons. | Keep each supplied reference tied to its viewport/state; record CSS size, DPR and capture conditions. Never imply responsive fidelity from one desktop frame. |
| [abi#456](https://github.com/abi/screenshot-to-code/issues/456), [abi#245](https://github.com/abi/screenshot-to-code/issues/245), [abi#463](https://github.com/abi/screenshot-to-code/issues/463), [NoviScl#30](https://github.com/NoviScl/Design2Code/issues/30) | Users report large visual mismatch, including when a metric appears favorable. | Preserve raw regional diagnostics and separate fidelity status. No subjective percentage or score threshold can produce PASS. |
| [abi#90](https://github.com/abi/screenshot-to-code/issues/90), [abi#404](https://github.com/abi/screenshot-to-code/issues/404), [abi#417](https://github.com/abi/screenshot-to-code/issues/417), [abi#123](https://github.com/abi/screenshot-to-code/issues/123), [abi#124](https://github.com/abi/screenshot-to-code/issues/124), [ytvee#10](https://github.com/ytvee-dev/webdev-agent-kit/issues/10) | Reports cover incomplete/blank output, wrong markup, component structure and undeclared CSS variables. | Keep the existing project stack, verify the rendered page, and confirm every referenced CSS token exists or define it in the owning scope. |
| [abi#445](https://github.com/abi/screenshot-to-code/issues/445), [abi#448](https://github.com/abi/screenshot-to-code/issues/448), [abi#436](https://github.com/abi/screenshot-to-code/issues/436), [abi#592](https://github.com/abi/screenshot-to-code/issues/592) | Reports raise non-English output, invented content, chart conversion and image fallback. | Preserve observed text/language/RTL; do not invent chart data or hidden content; do not add unapproved stock imagery. |
| [NoviScl#11](https://github.com/NoviScl/Design2Code/issues/11), [#14](https://github.com/NoviScl/Design2Code/issues/14), [#15](https://github.com/NoviScl/Design2Code/issues/15), [#30](https://github.com/NoviScl/Design2Code/issues/30), [#31](https://github.com/NoviScl/Design2Code/issues/31) | The research project itself tracks score interpretation and nondeterministic screenshot/metric problems. | Keep raw results and stable capture conditions; never present the upstream benchmark score or an uncalibrated score as pixel-fidelity evidence. |
| [abi#579](https://github.com/abi/screenshot-to-code/issues/579), [abi#618](https://github.com/abi/screenshot-to-code/issues/618), [Perfect-Web-Clone#2](https://github.com/ericshang98/Perfect-Web-Clone/issues/2) | Security reports concern wildcard CORS/evaluation and an alleged exposed key. | Static review confirmed wildcard CORS together with credentials in `abi/screenshot-to-code/backend/main.py`; the alleged eval path was not found at the pinned ref, and the key allegation was not independently verified. No credential value is reproduced. These are upstream findings, not AIPM vulnerabilities. Do not copy or run upstream server code. |
| [abi#311](https://github.com/abi/screenshot-to-code/issues/311), [abi#106](https://github.com/abi/screenshot-to-code/issues/106), [abi#108](https://github.com/abi/screenshot-to-code/issues/108), [mostafasadeghi#5](https://github.com/mostafasadeghi97/design2code/issues/5) | Upstream video, framework, UI library and deployment/runtime requests. | Out of this Skill's promise; work within the target project's actual stack and files. |

## Static Source Findings

These are bounded source reviews, not execution or a comprehensive security audit.

- `Core-Mate/Pixel-Perfect-Web-Replica`: [`mirror_public_page.py`](https://github.com/Core-Mate/Pixel-Perfect-Web-Replica/blob/4673cf86f895c4371c32eb9e0963aaed1dec4cac/scripts/mirror_public_page.py#L61-L66) URL-decodes a path after joining it to an output root; [later writes](https://github.com/Core-Mate/Pixel-Perfect-Web-Replica/blob/4673cf86f895c4371c32eb9e0963aaed1dec4cac/scripts/mirror_public_page.py#L196-L203) do not show a resolved-path containment check. Static path-traversal risk; no exploit was run. Do not reuse this mirroring helper.
- `xiaopu-ai/web-clone-prompt`: [single-screenshot workflow](https://github.com/xiaopu-ai/web-clone-prompt/blob/e943ee25da8d503354619098d4e8c66c8721913b/SKILL.md#L45) directs agents to infer and fill below-fold content when a screenshot is cropped. AIPM instead limits reconstruction to visible scope unless the user asks to extend it.
- `vibeeval/vibecosystem`: [visual verdict instructions](https://github.com/vibeeval/vibecosystem/blob/3b763b1fb288f57bfa3cce76ef18184b96461a78/skills/visual-verdict/SKILL.md#L25) define numeric thresholds and call 90+ production acceptable without calibrated evidence. AIPM retains `NOT_ASSESSED` and evidence-based gates.
- `gojodennis/OpenKombai`: [README install command](https://github.com/gojodennis/OpenKombai/blob/515235e2a2c7cf90070f5c5f50e24989c8765496/README.md#L36) still uses `yourusername`; do not treat that clone command as verified setup.
- `rodrigonask/claude-code-clone-website-skill`: [preflight](https://github.com/rodrigonask/claude-code-clone-website-skill/blob/0e7df323e8a241d840f0df475289db14d5439da2/clone-website/SKILL.md#L12) requires the user's real Chrome. AIPM's browser option requires an explicitly approved agent-connected browser and screenshot-only fallback.
- `fitoe/DesignToCode`: the pinned README and nested Skill are both readable; the earlier research review records their workflow drift. Current hashes still match the pinned evidence. Prefer concise current instructions, no mandatory tool/framework absent from the target project.

## Verification And Remaining Limits

- Historical 10-test failure set: current focused rerun was 7 PASS and 3 SKIP/UNVERIFIED. ACL and process/CLI identities no longer reproduced as failures. Three junction-dependent cases skipped because Windows denied `cmd /c mklink /J`. Exact names and prior/current outcome are in the verification record.
- Browser-environment status inspection found registered environment metadata but failed process inspection with `PROCESS_INSPECTION_UNAVAILABLE` (CIM access denied). No target URL was supplied, no page was opened, and no browser-driven target inspection was run. This does not prevent documenting the opt-in workflow; it means live browser availability is UNVERIFIED here.
- The full AIPM test suite, third-party projects' runtime, host-native package installation and the held-out autonomous reconstruction scenarios were not run. They remain explicitly unverified.
- The source project is not being published. Local packages and a local commit are review artifacts only; no push, release, tag, install or host acceptance is implied.
