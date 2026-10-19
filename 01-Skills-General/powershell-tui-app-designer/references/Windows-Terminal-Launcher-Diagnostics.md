# Windows Terminal Launcher Diagnostics

Use this reference only when a Windows PowerShell TUI launcher fails to start Windows Terminal (`wt.exe`) or the intended child PowerShell entry script. It applies to **new launcher design and existing launcher repair/review**. Do not apply its diagnosis to unrelated errors without evidence.

## 1. Specific Quoting Failure Pattern

Batch `%~dp0` expands to the launcher's directory **with a trailing backslash**. Passing that value unmodified as a quoted argument can create a trailing-backslash-before-closing-quote shape:

```bat
set "APP_ROOT=%~dp0"
start "" /wait "%WT_EXE%" -w new -d "%APP_ROOT%" "%POWERSHELL_EXE%" -NoProfile -File "%APP_ROOT%Start-App.ps1"
```

When the resulting command-line string contains `... -d "C:\Folder\\?`, the final backslash can escape the closing quote under Windows argument-parsing rules. The directory token may absorb following command text, shifting the PowerShell executable and script arguments. The visible error may be `0x80070002` / “file not found,” but that code alone does not prove this cause.

The supplied FFmpeg User Manager handoff reports that `CommandLineToArgvW` reproduced a merged argument vector for the quoted `%~dp0` directory, and that the final repair removed the unnecessary `-d` route and directly invoked the absolute PowerShell executable and `.ps1` path through Windows Terminal. Treat this as a known failure class to verify in a future project, not as proof about that project's launcher.

Unicode (including `│`) can be present in the path without being the cause. Do not blame Unicode unless the parsed argument vector or a focused encoding test proves that boundary is failing.

## 2. Evidence-First Decision Tree

```text
Launcher or wt.exe reports target missing
  -> inspect actual launcher, runtime values, and exact wt.exe boundary
  -> reconstruct parsed argv with CommandLineToArgvW or an equivalent real parser
  -> quoted directory ends with \ immediately before its closing quote?
       yes -> make a minimal reproduction; prove whether that closing quote is lost
       no  -> this root cause is not established; trace the actual missing path/tool
  -> invoke the parsed PowerShell child and prove the intended entry script ran
  -> verify native Windows Terminal behavior if required; keep stub and host results separate
```

Inspect the project instructions, launcher, runtime selection, terminal detection/recursion rules, path construction, quoting, argument forwarding, and existing launcher tests. Capture the command **as delivered at the process boundary**, not only how it looks in the `.bat` source. Check actual variable values: another directory variable can have the same trailing separator.

## 3. Reconstruct The Argument Vector

Use `CommandLineToArgvW` or an equivalent native Windows parser/test executable to reconstruct how the exact command line is split. Do not conclude that quoting is correct from a `Write-Output`, echo, or text log. A passing parser probe proves only parsing; it does not prove the child was started.

For a one-off parser probe, a Windows PowerShell script can declare the native API and return each parsed argument as a separate indexed row:

```powershell
Add-Type -TypeDefinition @'
using System;
using System.Runtime.InteropServices;
public static class NativeCommandLine {
    [DllImport("shell32.dll", SetLastError=true, CharSet=CharSet.Unicode)]
    public static extern IntPtr CommandLineToArgvW(string commandLine, out int argc);
    [DllImport("kernel32.dll")]
    public static extern IntPtr LocalFree(IntPtr memory);
}
'@

function ConvertFrom-WindowsCommandLine {
    param([Parameter(Mandatory)][string]$CommandLine)
    $count = 0
    $argv = [NativeCommandLine]::CommandLineToArgvW($CommandLine, [ref]$count)
    if ($argv -eq [IntPtr]::Zero) { throw 'CommandLineToArgvW failed.' }
    try {
        $items = @()
        for ($i = 0; $i -lt $count; $i++) {
            $pointer = [Runtime.InteropServices.Marshal]::ReadIntPtr($argv, $i * [IntPtr]::Size)
            $items += [Runtime.InteropServices.Marshal]::PtrToStringUni($pointer)
        }
        return ,$items
    } finally { [void][NativeCommandLine]::LocalFree($argv) }
}
```

Build a minimal unsafe-shape reproduction from a directory ending in `\`, then compare it with a candidate fix. Assert that the PowerShell executable, `-File`, entry path, and every forwarded argument occupy the expected separate vector elements. Do not rely on counting words in a printed command string.

## 4. Choose The Smallest Repair

1. **Prefer removing the starting-directory argument when it is unnecessary.** If the launcher already passes an absolute `.ps1` entry path and the app does not require a special working directory, omit `-d` / `--startingDirectory`. This avoids the fragile argument entirely.
2. **If a starting directory is required, preserve it with a tested representation.** Remove the terminal separator from the variable or choose another representation only after testing it with the actual parser and supported host/shell. Never blindly add or remove backslashes based on visual appearance.
3. **Keep executable and arguments separate.** Invoke the selected PowerShell executable with an absolute entry path and discrete parameters using the project's supported launcher architecture. Preserve user arguments without concatenating them into untrusted shell text.
4. **Do not rewrite the whole launcher to fix one boundary.** Preserve current-terminal behavior, recursion detection, runtime fallback, cancellation, argument forwarding, and the chosen window host.

There is no blanket ban on `-d`; it is valid when needed and passed safely. Do not recommend routing an environment-variable reference through a child `cmd.exe` as a default workaround unless a focused end-to-end test proves that exact route works.

## 5. Behavioral Regression Test

A useful launcher test has two distinct parts:

1. **Parsing:** a real Windows parser or an executable test double receives the actual boundary and confirms the expected argument vector.
2. **Execution:** the fake terminal/test harness launches the parsed child PowerShell against a disposable probe `.ps1`; the probe emits a unique marker. Assert marker, exact argument values, exit code, and cleanup.

The fake must parse and execute. A stub that only logs `Environment.CommandLine` is diagnostic output, not acceptance evidence. A fake-terminal child test is still not a native Windows Terminal visual test.

Cover only the cases relevant to that launcher, usually:

- Directory values with and without a trailing separator.
- Spaces, parentheses, ampersands, and Unicode path components where supported.
- A PowerShell executable under a directory containing spaces.
- An absolute entry script path and original forwarded arguments arriving intact.
- `WT_SESSION` / current-terminal routing and recursion prevention.
- Missing or broken `wt.exe` and the documented runtime/host fallback.
- Exit code propagation, non-admin/admin path when implemented, and native elevated launch only if that behavior is in scope.

Report native Windows Terminal and elevation checks separately. If they were not run on the real host, mark them `UNVERIFIED`; a sandbox stub, CI process, or parser-only test cannot prove terminal UI or integrity-level inheritance.

## 6. Rule Out Other Causes

Investigate these only as the evidence directs; change one boundary at a time:

- `wt.exe` missing, unresolved App Execution Alias, or a stale PATH result.
- Incorrect Windows Terminal `-w` / `new` grammar or shell-specific argument handling.
- Missing executable/script, wrong current directory, or a relative path assumption.
- Other quoting/special-character boundaries or broken `%*` forwarding.
- `WT_SESSION` recursion/current-tab detection.
- Integrity-level mismatch, UAC, profile defaults, or Windows Terminal version behavior.
- Encoding only when the parsed value differs from the original.

Error `0x80070002` says a requested file was not found; first identify **which** executable or script was missing. Do not force the trailing-backslash diagnosis onto a correctly separated argument vector.

## 7. Completion Checklist

- [ ] Project launcher and runtime values were inspected under the project's rules.
- [ ] The exact process-boundary command was reconstructed with a real parser.
- [ ] The trailing-backslash hypothesis was reproduced or explicitly disproved.
- [ ] The minimal repair was tested without weakening unrelated behavior.
- [ ] A child PowerShell probe proved the intended `.ps1` ran and received intact arguments.
- [ ] Existing routing/fallback/launcher tests still pass.
- [ ] Real Windows Terminal/elevated behavior is `PASS`, `FAIL`, or `UNVERIFIED` based on an actual host run.
- [ ] Unicode was not named as the cause unless evidence established it.
