# Keyboard And Test Matrix

| Scenario | Expected Result | Evidence |
|---|---|---|
| Up/Down Through Choices | Focus Moves; Marker And Shading Follow; Descriptions Stay Visible | Renderer Test + Live Terminal |
| Enter On Focused Choice | Opens Only The Selected Safe Action | Input Contract Test |
| Esc Back | Returns To Prior View Without Losing Valid Focus | Navigation Test |
| Stable Number Shortcut | Opens That Visible Choice In The Active Panel | Shortcut Test |
| Slash Search | Opens Command Palette; Text Input Disables Numeric Shortcuts | Input Test |
| F1 Or Question Mark | Shows Help And Returns Safely | Accessibility Test |
| Task Dashboard / Command Palette / Assistant Console | Mode Changes Preserve Selection And Truthful State | Mode Test |
| NO_COLOR / Redirected Output | Plain Text, Explicit Status, No ANSI, No Lost Descriptions | Process Capture Test |
| Narrow / Short / Resize | Wraps Or Pages; No Clipping; Back And Exit Stay Reachable | Dimension Test |
| Repeated Key / Unchanged Frame | No Races; Identical Styled Frame Performs Zero Writes | Diff Renderer Test |
| Row Shrink / Exit | Clears Stale Suffix; Cursor And Terminal State Are Restored | Renderer Test |
| Unicode / Wide Glyph | Correct Cell Width Or Safe Symbol/ASCII Fallback | Platform Test |
| Missing Or Stale Core State | Shows `Unknown` And Next Action; No Invented Progress | Data Contract Test |
| Windows Terminal With PowerShell 5.1 And 7.x | Visual, Focus, Color, Redirect, And Flicker Acceptance | Manual Capture Required |
