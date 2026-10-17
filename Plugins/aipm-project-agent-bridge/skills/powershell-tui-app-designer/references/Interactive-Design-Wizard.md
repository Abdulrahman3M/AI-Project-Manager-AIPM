# Interactive Design Wizard

When a user requests a new PowerShell TUI, start with this conversational designer unless they already specified the choices, or explicitly ask for automatic decisions. Ask one compact question at a time or one small multiple-choice group; allow `preview`, `back`, `skip`, and `defaults`. Never block on optional preferences.

1. **Purpose**: What workflows does the app provide? Inspect existing project before suggesting changes.
2. **Layout**: Offer a gallery of the 20 named presets in `Modern-Presets.md`, grouped as Classic / Developer / Dashboard / Wizard / Utility / Experimental. Display a short text preview and allow `custom` / mixing presets. Keep Classic Numbered available, not compulsory.
3. **Navigation**: Arrows+Enter; numbers; hybrid (arrows and numbers); search/command palette; or context-sensitive auto. Arrow navigation must work independently of numbers.
4. **Icons**: Emoji / simple Unicode symbols / ASCII / none / automatic fallback. Support Emoji in Windows Terminal when its selected font renders them; test or detect rendering where feasible and retain simple Unicode-symbol and ASCII alternatives. Never make Emoji the only way to identify an action.
5. **Window host**: Ask whether to use a Windows Terminal window or a standalone Console window. On Windows, default to Windows Terminal when the user skips, does not answer, or the question is omitted. If Windows Terminal is unavailable, report the limitation and fall back to the native Console host. Record the choice in the run instructions and launch design.
6. **Colors**: Full-color / subtle accents / monochrome / system auto; offer theme palettes separately, light or dark where terminal supports them.
7. **Option explanation rows**: Muted and indented below each choice (recommended), inline descriptions, compact info panel, or no descriptions (only if discoverability remains adequate). Explain that actual terminal background shading depends on capability and must not reduce legibility.
8. **Density and composition**: Compact / balanced / spacious; borders / whitespace / separators; single column / split panes / responsive automatic.
9. **Feedback**: Success, warning, error, loading/progress display and whether to ask for confirmations on destructive actions (always confirm sensitive operations regardless of preference).
10. **Accessibility & compatibility**: Target PS 5.1/7 and Windows/Linux/macOS as appropriate; support no-color/no-emoji and reduced-motion (never rely on animation). Offer RTL and localization only when requested and feasible.
11. **Preview and summary**: Show a simulated text preview clearly labeled illustrative, plus the selected configuration. Ask once for confirmation or specific edits before generating; do not repeatedly seek approval for ordinary implementation steps.

Persist choices in a plain configuration contract as appropriate: `preset`, `navigation`, `icons`, `windowHost`, `colors`, `theme`, `descriptions`, `density`, `layout`, `borders`, `accessibility`. The Windows default for `windowHost` is `windows-terminal`; use `console-window` only when selected or when Windows Terminal cannot be launched and the fallback is reported. Defaults: `classic-numbered` when matching an existing classic app; `assistant-console` when creating an assistant-style console; otherwise propose the best fitting style. Default navigation `arrows`, default descriptions `muted-indented`. Never require numeric prefixes in arrow-only mode. Only inspect technology-specific features actually supported by the detected host.

Sample user-facing prompt:

> How should users select an action?
> A. Arrow keys + Enter (modern, no numbers)
> B. Type a number (classic)
> C. Both numbers and arrows
> D. Search actions by name
> E. Recommend automatically

Continue to layout, icon and color choices. Do not ask a question whose answer the user has already provided.


## User-Facing Text Style

Write every static string shown by the generated application in English Title Case, including screen titles, headings, menu options, prompts, help text, progress labels, status messages, validation feedback, confirmations, errors and next-step guidance. Preserve proper nouns, acronyms, command names and technical identifiers. Do not alter user-provided or dynamic content.
