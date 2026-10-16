# TUI Product Shell And Capability Library Design

## Purpose

Make the AIPM PowerShell TUI feel like a disciplined developer product rather than a template menu. The work is limited to presentation, read-model caching, and release metadata. Project state remains read-only and Core Engine remains the sole authority.

## Approved Outcomes

- Every primary TUI screen has a compact product header that presents `AI Project Manager · v0.2.1` inside one thin terminal-safe frame.
- The header has a separate status line and a restrained divider. The product name and version are adjacent; neither is a page title substitute.
- Selection uses a cyan arrow and bright label without background fill. Numbers and explanations remain muted. This is true in ANSI, legacy Windows PowerShell, and no-color fallbacks.
- The former Skills & Plugins text dump becomes the Capability Library page: summary, first-party capability, imported capabilities, and local Plugin status arranged in terminal-safe framed sections and aligned columns.
- Ordinary navigation avoids Core CLI work and avoids recomputing stable menu geometry. Refresh is the explicit operation that requests fresh Core data.
- Root and TUI package versions both become `0.2.1`. Future compatible updates increase Patch and require synchronized version files and changelog entries.

## Visual System

### Tokens

| Role | Value | Use |
| --- | --- | --- |
| Canvas | `#101923` | Terminal background when true color is available. |
| Frame | `#587086` | Rules, outlines, and table separators. |
| Text | `#F0F5FA` | Product name, selected label, and primary values. |
| Muted | `#AAB9C9` | Explanations, numbers, labels, and metadata. |
| Accent | `#8ED3FF` | Arrow, focused route, and version frame. |
| Semantic Status | Existing success/warning/error roles | Evidence states only; never decorative. |

Only the selection arrow, the header outline, and explicit semantic state use color emphasis. There are no broad background fills, colored paragraphs, or decorative gradients.

### Header

The header is rendered by a shared owner, not copied into individual pages:

```text
 +--------------------------------------------------+
 | AI Project Manager · v0.2.1                      |
 +--------------------------------------------------+
 Core Ready · Registry Not Registered · Read-Only Workspace
 ----------------------------------------------------
```

At narrow widths, the status line wraps safely and the frame truncates only after retaining the product name and version. The header does not expose filesystem paths or claim unverified state.

### Capability Library

The page uses only catalog data returned by Core. It does not infer installation, publishing, or a license. It groups data as follows:

1. A small status frame with verified catalog totals and the local package state.
2. A `First-Party` table containing the declared AIPM Skill only.
3. An `Imported Skills` table containing preserved source records, version, and source-license label.
4. A local Plugin status line that must show `Uninstalled` and `Unpublished` unless Core says otherwise.

At normal width, tables use `Capability`, `Version`, and `License` columns. At narrow widths they become compact two-line rows in the same order. No row claims a third-party Skill is Apache-2.0.

## Behavior And Performance

- `dashboard`, `catalog`, and `host-capabilities` are loaded once at application start. Navigation consumes that session snapshot.
- Refresh is the only primary-menu operation that re-queries Core and replaces the snapshot. A page reached before Refresh continues to show the same evidence snapshot.
- The menu caches its measured row costs and viewport calculation keyed by terminal width, height, visible items, layout, density, and description style. A selection move must only update selection-dependent rows.
- A resize, search query change, or changed item set invalidates the menu cache safely.
- The legacy renderer recognizes `SelectionMarker` and never assigns a background color to `Selected` text.

## Version Policy

- Root `VERSION` and `TUI/AI-Project-Manager/VERSION` are release-coupled and must match.
- This release is `0.2.1`, a patch-level visual/performance release from platform `0.2.0`.
- Each future compatible update increases Patch and changes both version files plus the relevant changelog. Feature additions use Minor and breaking behavior uses Major, as specified in Project Rules.
- Tests fail on missing, invalid, or mismatched platform/TUI versions.

## Files And Boundaries

- `TUI/AI-Project-Manager/src/TUI/`: shared header, renderer legacy behavior, menu cache, and table/frame helpers.
- `TUI/AI-Project-Manager/src/Core/App.psm1`: session snapshot lifecycle and Capability Library composition only.
- `TUI/AI-Project-Manager/VERSION`, root `VERSION`, and changelogs: synchronized release metadata.
- `TUI/AI-Project-Manager/tests/`: test-first coverage for header, version synchronization, Capability Library layout, cache invalidation, refresh behavior, and legacy styling.

No imported Skill, protected capability baseline, generated Plugin contents, Core project-state schema, Universal AI ToolKit source, installation state, or remote repository is changed.

## Acceptance Criteria

1. Header renders the exact product name and synchronized version inside a frame on the main menu and pages.
2. Selected item and legacy console output contain no background color assignment.
3. Capability Library preserves source-license wording, groups the declared first-party Skill, and has a responsive compact representation.
4. Navigation tests prove that selection changes do not dispatch Core reads; Refresh does.
5. Cache tests prove reuse for stable geometry and invalidation for resize/search.
6. TUI test suite passes under PowerShell 7 and Windows PowerShell 5.1; project quality checks and `git diff --check` pass.
