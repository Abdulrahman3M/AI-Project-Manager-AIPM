import subprocess
import shutil
import importlib.util
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "route_transient_state.py"
WRAPPER = SCRIPT.with_name("Route-Transient-State.ps1")


class TransientRoutingSafetyTests(unittest.TestCase):
    def run_tool(self, root, *args):
        return subprocess.run([sys.executable, str(SCRIPT), "--project-root", str(root), *args],
                              text=True, capture_output=True)

    def test_template_matches_routing_script(self):
        template = SCRIPT.parent.parent / "templates" / "Route-Transient-State.py"
        self.assertEqual(template.read_bytes(), SCRIPT.read_bytes())
        self.assertEqual((template.parent / "safe_move.py").read_bytes(), (SCRIPT.parent / "safe_move.py").read_bytes())

    @unittest.skipUnless(os.name == "nt", "Windows handle semantics required")
    def test_sweep_holds_project_root_during_mutation(self):
        spec = importlib.util.spec_from_file_location("router_root_lock", SCRIPT)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        with tempfile.TemporaryDirectory() as td:
            parent = Path(td)
            root = parent / "project"
            root.mkdir()
            state = root / "Shared-Project-State"
            state.mkdir()
            original = module.ensure_transient_structure
            def try_swap(path):
                with self.assertRaises(OSError):
                    root.rename(parent / "detached")
                with self.assertRaises(OSError):
                    state.rename(root / "detached-state")
                return original(path)
            with mock.patch.object(module, "ensure_transient_structure", side_effect=try_swap):
                self.assertEqual(module.sweep_project(root, state), 0)

    def test_sweep_does_not_traverse_protected_metadata_at_any_depth(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / 'Shared-Project-State').mkdir()
            files = []
            for relative in ('.agents/scratch_secret.tmp', 'nested/.codex/scratch_secret.tmp',
                             'nested/.git/scratch_secret.tmp'):
                item = root / relative
                item.parent.mkdir(parents=True, exist_ok=True)
                item.write_bytes(b'protected canary')
                files.append(item)
            result = self.run_tool(root, '--sweep')
            self.assertEqual(result.returncode, 0, result.stderr)
            for item in files:
                self.assertEqual(item.read_bytes(), b'protected canary')

    def test_dry_run_does_not_create_state(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            for args in (("--sweep", "--dry-run"), ("--clean", "--dry-run"), ("--status",), ("--env", "powershell")):
                with self.subTest(args=args):
                    result = self.run_tool(root, *args)
                    self.assertEqual(result.returncode, 0, result.stderr)
                    self.assertEqual(list(root.iterdir()), [])

    def test_sweep_does_not_replace_existing_destination(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            source = root / "src" / "__pycache__"
            source.mkdir(parents=True)
            (source / "new.txt").write_bytes(b"new canary")
            destination = root / "Shared-Project-State-Manager" / "Cache" / "Python" / "pycache_src___pycache__"
            destination.mkdir(parents=True)
            (destination / "old.txt").write_bytes(b"old canary")
            result = self.run_tool(root, "--sweep")
            self.assertNotEqual(result.returncode, 0, "An incomplete sweep must not report success")
            self.assertEqual((destination / "old.txt").read_bytes(), b"old canary")
            self.assertEqual((source / "new.txt").read_bytes(), b"new canary")
            repeat = self.run_tool(root, "--sweep")
            self.assertNotEqual(repeat.returncode, 0, "A repeated collision must remain visible")
            self.assertEqual((destination / "old.txt").read_bytes(), b"old canary")
            self.assertEqual((source / "new.txt").read_bytes(), b"new canary")

    def test_sweep_preserves_occupied_file_destination(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            state = root / "Shared-Project-State"
            destination = state / "Temporary-Files" / "._scratch_note.txt"
            destination.parent.mkdir(parents=True)
            destination.write_bytes(b"old canary")
            source = root / "scratch_note.txt"
            source.write_bytes(b"new canary")
            result = self.run_tool(root, "--sweep")
            self.assertNotEqual(result.returncode, 0, "An occupied destination must report an incomplete sweep")
            self.assertEqual(destination.read_bytes(), b"old canary")
            self.assertEqual(source.read_bytes(), b"new canary")

    def test_explicit_root_does_not_discover_parent_state(self):
        with tempfile.TemporaryDirectory() as td:
            parent = Path(td)
            (parent / "Shared-Project-State").mkdir()
            child = parent / "child"
            child.mkdir()
            result = self.run_tool(child, "--status")
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn(str(child / "Shared-Project-State").casefold(), result.stdout.casefold())
            self.assertEqual(list(child.iterdir()), [])

    def test_ambiguous_state_roots_fail_closed(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / "Shared-Project-State").mkdir()
            (root / "Shared-Project-State-Manager").mkdir()
            result = self.run_tool(root, "--sweep")
            self.assertNotEqual(result.returncode, 0)
            self.assertEqual(len(list(root.iterdir())), 2)

    def test_linked_destination_is_not_followed(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            source = root / "src" / "__pycache__"
            source.mkdir(parents=True)
            (source / "new.txt").write_bytes(b"new canary")
            external = root / "external"
            external.mkdir()
            canary = external / "old.txt"
            canary.write_bytes(b"old canary")
            cache = root / "Shared-Project-State" / "Cache"
            cache.mkdir(parents=True)
            try:
                (cache / "Python").symlink_to(external, target_is_directory=True)
            except OSError as exc:
                self.skipTest(f"Symlink creation unavailable: {exc}")
            result = self.run_tool(root, "--sweep")
            self.assertNotEqual(result.returncode, 0)
            self.assertEqual(canary.read_bytes(), b"old canary")
            self.assertEqual((source / "new.txt").read_bytes(), b"new canary")

    @unittest.skipUnless(shutil.which("pwsh"), "PowerShell unavailable")
    def test_powershell_dry_run_is_read_only(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            result = subprocess.run([shutil.which("pwsh"), "-NoProfile", "-File", str(WRAPPER),
                                     "-ProjectRoot", str(root), "-Sweep", "-DryRun"],
                                    text=True, capture_output=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(list(root.iterdir()), [])

    @unittest.skipUnless(os.name == "nt", "Windows atomic rename behavior required")
    def test_sweep_does_not_overwrite_destination_created_during_move(self):
        spec = importlib.util.spec_from_file_location("router_race", SCRIPT)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            state = root / "Shared-Project-State"
            state.mkdir()
            source = root / "scratch_race.txt"
            source.write_bytes(b"source canary")
            destination = state / "Temporary-Files" / "._scratch_race.txt"
            original_rename = module._safe_move._rename_windows_handle
            def create_destination_then_rename(kernel, handle, dst):
                Path(dst).write_bytes(b"racing destination")
                return original_rename(kernel, handle, dst)
            with mock.patch.object(module._safe_move, "_rename_windows_handle", side_effect=create_destination_then_rename):
                module.sweep_project(root, state)
            self.assertEqual(source.read_bytes(), b"source canary")
            self.assertEqual(destination.read_bytes(), b"racing destination")

    def test_sweep_rejects_parent_replaced_by_link(self):
        spec = importlib.util.spec_from_file_location("router_parent_race", SCRIPT)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        with tempfile.TemporaryDirectory() as td:
            parent = Path(td)
            root = parent / "project"
            root.mkdir()
            state = root / "Shared-Project-State"
            state.mkdir()
            source = root / "scratch_race.txt"
            source.write_bytes(b"source canary")
            outside = parent / "outside"
            outside.mkdir()
            probe = root / "probe"
            try:
                probe.symlink_to(outside, target_is_directory=True)
                probe.unlink()
            except OSError as exc:
                self.skipTest(f"Symlink creation unavailable: {exc}")
            original_move = module.move_noreplace
            def swap_parent_then_move(src, dst, identity):
                dest_parent = state / "Temporary-Files"
                dest_parent.rename(state / "detached")
                dest_parent.symlink_to(outside, target_is_directory=True)
                return original_move(src, dst, identity)
            with mock.patch.object(module, "move_noreplace", side_effect=swap_parent_then_move):
                module.sweep_project(root, state)
            self.assertEqual(source.read_bytes(), b"source canary")
            self.assertEqual(list(outside.iterdir()), [])

    def test_clean_refuses_linked_item_and_preserves_target(self):
        with tempfile.TemporaryDirectory() as td:
            parent = Path(td)
            root = parent / "project"
            root.mkdir()
            temp = root / "Shared-Project-State" / "Temporary-Files"
            temp.mkdir(parents=True)
            outside = parent / "outside.txt"
            outside.write_bytes(b"outside canary")
            link = temp / "link.txt"
            try:
                link.symlink_to(outside)
            except OSError as exc:
                self.skipTest(f"Symlink creation unavailable: {exc}")
            result = self.run_tool(root, "--clean")
            self.assertNotEqual(result.returncode, 0)
            self.assertEqual(outside.read_bytes(), b"outside canary")
            self.assertTrue(link.is_symlink())

    def test_clean_removes_explicit_synthetic_files_and_directories(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            temp = root / "Shared-Project-State" / "Temporary-Files"
            nested = temp / "nested"
            nested.mkdir(parents=True)
            (nested / "item.txt").write_bytes(b"synthetic")
            (temp / "item.txt").write_bytes(b"synthetic")
            result = self.run_tool(root, "--clean")
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(list(temp.iterdir()), [])

    @unittest.skipUnless(os.name == "nt", "Windows handle semantics required")
    def test_clean_rejects_parent_swapped_before_delete(self):
        spec = importlib.util.spec_from_file_location("router_clean_race", SCRIPT)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        with tempfile.TemporaryDirectory() as td:
            parent = Path(td)
            root = parent / "project"
            root.mkdir()
            state = root / "Shared-Project-State"
            temp = state / "Temporary-Files"
            temp.mkdir(parents=True)
            (temp / "item.txt").write_bytes(b"inside canary")
            outside = parent / "outside"
            outside.mkdir()
            (outside / "item.txt").write_bytes(b"outside canary")
            probe = root / "probe"
            try:
                probe.symlink_to(outside, target_is_directory=True)
                probe.unlink()
            except OSError as exc:
                self.skipTest(f"Symlink creation unavailable: {exc}")
            original_delete = module._safe_move.delete_nofollow
            def swap_parent_then_delete(path, identity):
                temp.rename(state / "detached")
                temp.symlink_to(outside, target_is_directory=True)
                return original_delete(path, identity)
            with mock.patch.object(module._safe_move, "delete_nofollow", side_effect=swap_parent_then_delete):
                result = module.clean_transient(state)
            self.assertNotEqual(result, 0)
            self.assertEqual((outside / "item.txt").read_bytes(), b"outside canary")
            self.assertEqual((state / "detached" / "item.txt").read_bytes(), b"inside canary")


if __name__ == "__main__":
    unittest.main()
