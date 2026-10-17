# Textual Design Preview Gallery

These are illustrative mockups only, not screenshots or verified app output. All are original and use generic placeholder labels.

## Classic Numbered

```text
  APP  |  Home

 > 01  *  Start new task
           Create a task with guided questions.
   02  +  Review results
           Inspect the latest completed work.
   03  #  Settings
           Adjust display and behavior.

  Up/Down  Enter  01-03  Esc
```

## Assistant Console

```text
  assistant                                      ready
  --------------------------------------------------
  You  >  Summarize recent jobs
  Tool |  Scanned 8 tasks; 2 need attention
  AI   |  Select a task or describe your next goal.
  --------------------------------------------------
  > Type a command or question ...
  /help     /tasks     /settings
```

## Command Palette

```text
  Actions                               Ctrl+P  Search
  > deploy_
    > Deploy current project
      Run checks, then stage a release.
      View change summary
      Inspect pending modifications.
```

## Developer Workbench

```text
  PROJECT / Workbench                   clean
  TASKS                      OUTPUT
  > Run tests                 [PASS] 18 checks
    Inspect changes            no warnings
    Package release
  Esc Back       Enter Select
```

## Task Monitor

```text
  Task / Building
  [#############-------]  65%
  Stage: Verify package
  Elapsed: 00:12   3 / 5 stages
  Esc Cancel    ? Details
```

## Minimal Monochrome

```text
  TASKS
  > Start
    Inspect
    Settings
  Enter select | Esc back
```

## Subtle description rows

```text
  > Check environment
      Examine runtime and missing dependencies.
    Build package
      Produce a portable release archive.
```

Render the explanatory row in a lower-emphasis but still readable semantic role, with an indent. A slightly shaded band is optional on terminals that support it; do not require background styling to convey meaning.
