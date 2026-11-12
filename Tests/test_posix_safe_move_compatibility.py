from __future__ import annotations

import errno
import importlib.util
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
WORKSPACE = ROOT / "Shared-Project-State-Manager" / "Test-Workspace"
SAFE_MOVE_PATH = ROOT / "01-Skills-General" / "shared-project-state-manager" / "scripts" / "safe_move.py"
SAFE_FILE_OPS_PATH = ROOT / "01-Skills-General" / "shared-project-state-manager" / "scripts" / "safe_file_ops.py"
SPEC = importlib.util.spec_from_file_location("aipm_safe_move_posix_compatibility", SAFE_MOVE_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("Cannot load the state safety implementation")
safe_move = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(safe_move)


@unittest.skipUnless(os.name == "posix", "POSIX fail-closed contract")
class PosixSafeMoveCompatibilityTests(unittest.TestCase):
    def setUp(self) -> None:
        WORKSPACE.mkdir(parents=True, exist_ok=True)
        self.temp = tempfile.TemporaryDirectory(prefix="posix-safe-move-", dir=WORKSPACE)
        self.root = Path(self.temp.name)

    def tearDown(self) -> None:
        self.temp.cleanup()

    def assert_unsupported_without_mutation(self, operation, *args) -> None:
        with self.assertRaises(OSError) as raised:
            operation(*args)
        self.assertEqual(raised.exception.errno, errno.ENOTSUP)

    def test_handle_bound_mutations_fail_closed_and_preserve_inputs(self) -> None:
        record = self.root / "record.json"
        record.write_bytes(b"original record")
        source = self.root / "source.txt"
        source.write_bytes(b"original source")
        destination = self.root / "destination.txt"
        new_directory = self.root / "new-directory"
        before_mode = source.stat().st_mode

        self.assert_unsupported_without_mutation(safe_move.ensure_directory, new_directory)
        self.assertFalse(new_directory.exists())
        with self.assertRaises(OSError) as locked:
            with safe_move.locked_directories(self.root):
                self.fail("POSIX must not enter an unverified handle-locking path")
        self.assertEqual(locked.exception.errno, errno.ENOTSUP)
        with self.assertRaises(OSError) as record_lock:
            with safe_move.locked_record(record):
                self.fail("POSIX must not enter an unverified record-locking path")
        self.assertEqual(record_lock.exception.errno, errno.ENOTSUP)
        self.assert_unsupported_without_mutation(safe_move.move_noreplace, source, destination)
        self.assert_unsupported_without_mutation(safe_move.delete_nofollow, source)
        self.assert_unsupported_without_mutation(safe_move.clear_readonly_nofollow, source)

        self.assertEqual(record.read_bytes(), b"original record")
        self.assertEqual(source.read_bytes(), b"original source")
        self.assertEqual(source.stat().st_mode, before_mode)
        self.assertFalse(destination.exists())

    def test_cli_keeps_diagnostics_and_dry_run_available_but_blocks_real_move(self) -> None:
        source = self.root / "source.txt"
        source.write_text("canary", encoding="utf-8")
        destination = self.root / "destination.txt"

        diagnose = subprocess.run(
            [sys.executable, str(SAFE_FILE_OPS_PATH), "diagnose", str(source), "--project-root", str(self.root)],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(diagnose.returncode, 0, diagnose.stderr)
        self.assertIn('"is_file": true', diagnose.stdout)

        dry_run = subprocess.run(
            [sys.executable, str(SAFE_FILE_OPS_PATH), "move", str(source), str(destination),
             "--project-root", str(self.root), "--dry-run"],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(dry_run.returncode, 0, dry_run.stderr)
        self.assertIn("DRY-RUN", dry_run.stdout)
        self.assertEqual(source.read_text(encoding="utf-8"), "canary")
        self.assertFalse(destination.exists())

        actual = subprocess.run(
            [sys.executable, str(SAFE_FILE_OPS_PATH), "move", str(source), str(destination), "--project-root", str(self.root)],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(actual.returncode, 3, actual.stdout)
        self.assertIn("unavailable on this platform", actual.stderr)
        self.assertEqual(source.read_text(encoding="utf-8"), "canary")
        self.assertFalse(destination.exists())


if __name__ == "__main__":
    unittest.main()
