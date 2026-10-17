# Modern TUI Preset Library

These are original, product-neutral terminal design archetypes. They are not reproductions of proprietary application UIs. Every preset must support keyboard navigation and a high-contrast monochrome fallback. Pick one, combine elements, or define a custom layout.

| ID | Preset | Layout and use |
|---|---|---|
| classic-numbered | Classic Numbered | Original numbered list with indented muted explanatory descriptions; preserved for compatibility |
| assistant-console | Assistant Console | Minimal conversation transcript, prompt dock, command suggestions, compact status line |
| command-palette | Command Palette | Search-first ranked action list, keyboard shortcuts and contextual descriptions |
| developer-workbench | Developer Workbench | Project summary, task list, output log and contextual command bar |
| task-dashboard | Task Dashboard | KPI strip, status sections, actionable lists |
| split-pane | Split Pane | Navigation sidebar and details/output pane |
| wizard-stepper | Wizard Stepper | Progressive questions, step indicators, previews and validation |
| task-monitor | Task Monitor | Activity feed, determinate/indeterminate progress and cancellation |
| compact-utilities | Compact Utilities | Space-efficient single-column responsive list |
| spacious-editorial | Spacious Editorial | Deliberate whitespace, crisp typographic hierarchy, understated accents |
| minimal-monochrome | Minimal Monochrome | Accessible no-color layout with explicit selection markers |
| neon-night | Neon Night | Dark high-contrast palette with limited saturated accents |
| soft-slate | Soft Slate | Restrained slate-and-blue surfaces and subtle secondary text |
| warm-paper | Warm Paper | Light warm palette and soft separators |
| terminal-retro | Terminal Retro | Optional nostalgic text-console aesthetic with modern input behavior |
| operations-center | Operations Center | Multi-section monitoring, status labels and safe actions |
| file-explorer | File Explorer | Hierarchical navigation, breadcrumbs and details |
| media-workbench | Media Workbench | File metadata, batch status and clear task actions; domain neutral |
| troubleshooting | Troubleshooting | Diagnostic checks, repair choices and explanation rows |
| setup-onboarding | Setup Onboarding | First-run option picker with live preview and summary |

## Design contract

- Navigation mode is chosen independently from visuals: `arrows`, `numbers`, `hybrid` or `search` where relevant. None is mandatory.
- Description style independently chosen as `muted-indented`, `inline`, `panel`, or `off`; muted-indented is the default for lists. Use semantic `Dim` with appropriate contrast, subtle shade only if supported, and a visible indent; no explanation must rely solely on color.
- Icon mode is `emoji`, `symbol`, `ascii` or `none`. Colors may be `auto`, `full`, `subtle` or `none`. Respect `NO_COLOR` and narrow terminals.
- Themes and layouts are orthogonal. User may mix palettes, spacing, density, borders, accent, icon tier and menu input.
- A preset MUST NOT dictate a product domain or copy the visual identity of a branded tool.
- Use the wizard in `Interactive-Design-Wizard.md` to collect preferences. Display examples before asking the user to commit. Preserve explicitly chosen settings.
