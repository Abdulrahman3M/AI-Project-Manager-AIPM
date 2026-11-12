import json
import argparse
import hashlib
import importlib.util
import os
import subprocess
import sys
import tempfile
import unittest
import stat
from contextlib import contextmanager
from pathlib import Path
from unittest import mock

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "safe_file_ops.py"

class SafeFileOpsTests(unittest.TestCase):
    def run_tool(self, *args):
        return subprocess.run([sys.executable, str(SCRIPT), *map(str,args)], text=True, capture_output=True)

    def test_clear_readonly_rejects_nested_link_without_touching_external_file(self):
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            root = base / 'project'
            folder = root / 'inside'
            folder.mkdir(parents=True)
            outside = base / 'outside.txt'
            outside.write_text('canary', encoding='utf-8')
            outside.chmod(stat.S_IREAD)
            try:
                try:
                    (folder / 'link.txt').symlink_to(outside)
                except OSError as error:
                    self.skipTest(f'Symbolic links unavailable: {error}')
                result = self.run_tool('clear-readonly', folder, '--project-root', root,
                                       '--confirm', 'CLEAR-READONLY')
                self.assertNotEqual(result.returncode, 0)
                self.assertFalse(outside.stat().st_mode & stat.S_IWUSR)
            finally:
                outside.chmod(stat.S_IWRITE)

    @unittest.skipUnless(os.name == 'nt', 'Windows handle implementation')
    def test_clear_readonly_updates_regular_files(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            folder = root / 'inside'
            folder.mkdir()
            item = folder / 'item.txt'
            item.write_text('canary', encoding='utf-8')
            item.chmod(stat.S_IREAD)
            try:
                result = self.run_tool('clear-readonly', folder, '--project-root', root,
                                       '--confirm', 'CLEAR-READONLY')
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertTrue(item.stat().st_mode & stat.S_IWUSR)
            finally:
                item.chmod(stat.S_IWRITE)

    @unittest.skipUnless(os.name == 'nt', 'Windows handle implementation')
    def test_clear_readonly_rejects_nested_protected_metadata(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            folder = root / 'inside'
            metadata = folder / '.git'
            metadata.mkdir(parents=True)
            item = metadata / 'config'
            item.write_text('canary', encoding='utf-8')
            item.chmod(stat.S_IREAD)
            try:
                result = self.run_tool('clear-readonly', folder, '--project-root', root,
                                       '--confirm', 'CLEAR-READONLY')
                self.assertNotEqual(result.returncode, 0)
                self.assertFalse(item.stat().st_mode & stat.S_IWUSR)
            finally:
                item.chmod(stat.S_IWRITE)

    def test_quarantine_and_restore(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            target = root / "temp-work"
            target.mkdir()
            (target / "data.txt").write_text("x", encoding="utf-8")
            r = self.run_tool("quarantine", target, "--project-root", root)
            self.assertEqual(r.returncode, 0, r.stderr)
            payload = json.loads(r.stdout)
            record = Path(payload["record"])
            self.assertFalse(target.exists())
            self.assertTrue(record.exists())
            r = self.run_tool("restore", record, "--project-root", root)
            self.assertEqual(r.returncode, 0, r.stderr)
            self.assertTrue((target / "data.txt").exists())

    def test_path_escape_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td) / "project"
            root.mkdir()
            outside = root.parent / "outside"
            outside.mkdir()
            r = self.run_tool("diagnose", outside, "--project-root", root)
            self.assertNotEqual(r.returncode, 0)
            self.assertIn("escapes project root", r.stderr)

    def test_forged_record_cannot_restore_unrelated_file(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            canary = root / "canary.txt"
            canary.write_bytes(b"original canary")
            record = root / "forged.json"
            record.write_text(json.dumps({"quarantined_path": "canary.txt", "original_path": "moved.txt"}), encoding="utf-8")
            result = self.run_tool("restore", record, "--project-root", root)
            self.assertNotEqual(result.returncode, 0, result.stdout)
            self.assertEqual(canary.read_bytes(), b"original canary")
            self.assertFalse((root / "moved.txt").exists())

    def test_quarantine_dry_run_does_not_create_state(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            canary = root / "canary.txt"
            canary.write_bytes(b"original canary")
            result = self.run_tool("quarantine", canary, "--project-root", root, "--dry-run")
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(canary.read_bytes(), b"original canary")
            self.assertFalse((root / "Shared-Project-State").exists())

    def test_restore_and_purge_dry_runs_preserve_record_and_item(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            source = root / "canary.txt"
            source.write_bytes(b"original canary")
            quarantined = self.run_tool("quarantine", source, "--project-root", root)
            self.assertEqual(quarantined.returncode, 0, quarantined.stderr)
            payload = json.loads(quarantined.stdout)
            record = Path(payload["record"])
            item = root / payload["quarantined_path"]
            before = record.read_bytes()
            before_names = sorted(p.name for p in record.parent.iterdir())
            for command in (("restore",), ("purge", "--confirm", "PURGE-QUARANTINE")):
                result = self.run_tool(command[0], record, "--project-root", root, "--dry-run", *command[1:])
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertEqual(record.read_bytes(), before)
                self.assertEqual(item.read_bytes(), b"original canary")
                self.assertFalse(source.exists())
                self.assertEqual(sorted(p.name for p in record.parent.iterdir()), before_names)

    def test_tampered_original_path_is_not_accepted(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            original = root / "one" / "canary.txt"
            original.parent.mkdir()
            original.write_bytes(b"canary")
            result = self.run_tool("quarantine", original, "--project-root", root)
            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(result.stdout)
            record = Path(payload["record"])
            payload["original_path"] = str(Path("two") / "canary.txt")
            record.write_text(json.dumps(payload), encoding="utf-8")
            result = self.run_tool("restore", record, "--project-root", root)
            self.assertNotEqual(result.returncode, 0, result.stdout)
            self.assertFalse((root / "two" / "canary.txt").exists())
            self.assertTrue((root / payload["quarantined_path"]).is_file())

    def test_restore_replay_is_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            original = root / "canary.txt"
            original.write_bytes(b"first canary")
            result = self.run_tool("quarantine", original, "--project-root", root)
            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(result.stdout)
            record = Path(payload["record"])
            restored = self.run_tool("restore", record, "--project-root", root)
            self.assertEqual(restored.returncode, 0, restored.stderr)
            original.rename(root / "preserved.txt")
            source = root / payload["quarantined_path"]
            source.write_bytes(b"second canary")
            replay = self.run_tool("restore", record, "--project-root", root)
            self.assertNotEqual(replay.returncode, 0, replay.stdout)
            self.assertEqual(source.read_bytes(), b"second canary")
            self.assertEqual((root / "preserved.txt").read_bytes(), b"first canary")

    def test_legacy_record_requires_manual_review_and_preserves_data(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            items = root / "Shared-Project-State" / "Quarantine" / "Items"
            records = root / "Shared-Project-State" / "Quarantine" / "Records"
            items.mkdir(parents=True)
            records.mkdir(parents=True)
            token = "20261111-120000-12345678"
            source = items / f"{token}-canary.txt"
            source.write_bytes(b"legacy canary")
            record = records / f"{token}.json"
            payload = {"schema_version": "1.0", "operation": "quarantine", "created_at": "2026-11-11T00:00:00+00:00",
                       "original_path": "somewhere/canary.txt", "quarantined_path": str(source.relative_to(root)),
                       "restored": False, "purged": False}
            record.write_text(json.dumps(payload), encoding="utf-8")
            before = record.read_bytes()
            for args in (("restore",), ("purge", "--confirm", "PURGE-QUARANTINE")):
                result = self.run_tool(args[0], record, "--project-root", root, *args[1:])
                self.assertNotEqual(result.returncode, 0, result.stdout)
                self.assertEqual(source.read_bytes(), b"legacy canary")
                self.assertEqual(record.read_bytes(), before)

    def test_forged_record_cannot_restore_into_git_metadata(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / ".git").mkdir()
            items = root / "Shared-Project-State" / "Quarantine" / "Items"
            records = root / "Shared-Project-State" / "Quarantine" / "Records"
            items.mkdir(parents=True)
            records.mkdir(parents=True)
            token = "20261111-120000-12345678"
            original = str(Path(".git") / "config")
            digest = hashlib.sha256(original.encode("utf-8")).hexdigest()
            source = items / f"{token}-{digest}"
            source.write_bytes(b"quarantine canary")
            record = records / f"{token}.json"
            payload = {"schema_version": "1.1", "operation": "quarantine", "created_at": "2026-11-11T00:00:00+00:00",
                       "original_path": original, "quarantined_path": str(source.relative_to(root)),
                       "restored": False, "purged": False}
            record.write_text(json.dumps(payload), encoding="utf-8")
            result = self.run_tool("restore", record, "--project-root", root)
            self.assertNotEqual(result.returncode, 0, result.stdout)
            self.assertEqual(source.read_bytes(), b"quarantine canary")
            self.assertFalse((root / ".git" / "config").exists())

    def test_quarantine_rejects_core_state_and_git_metadata(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            for name in (".git", "Shared-Project-State-Manager"):
                directory = root / name
                directory.mkdir()
                canary = directory / "canary.txt"
                canary.write_bytes(b"protected")
                result = self.run_tool("quarantine", canary, "--project-root", root)
                self.assertNotEqual(result.returncode, 0, result.stdout)
                self.assertEqual(canary.read_bytes(), b"protected")

    def test_linked_path_is_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            target = root / "target.txt"
            target.write_bytes(b"target canary")
            link = root / "link.txt"
            try:
                link.symlink_to(target)
            except OSError as exc:
                self.skipTest(f"Symlink creation unavailable: {exc}")
            result = self.run_tool("quarantine", link, "--project-root", root)
            self.assertNotEqual(result.returncode, 0, result.stdout)
            self.assertEqual(target.read_bytes(), b"target canary")

    def test_linked_project_root_is_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            parent = Path(td)
            actual = parent / "actual"
            actual.mkdir()
            (actual / "canary.txt").write_bytes(b"canary")
            alias = parent / "alias"
            try:
                alias.symlink_to(actual, target_is_directory=True)
            except OSError as exc:
                self.skipTest(f"Symlink creation unavailable: {exc}")
            result = self.run_tool("quarantine", "canary.txt", "--project-root", alias, "--dry-run")
            self.assertNotEqual(result.returncode, 0, result.stdout)
            self.assertEqual((actual / "canary.txt").read_bytes(), b"canary")

    @unittest.skipUnless(os.name == "nt", "Windows handle semantics required")
    def test_project_root_is_locked_during_move(self):
        spec = importlib.util.spec_from_file_location("safe_ops_locked_root", SCRIPT)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        with tempfile.TemporaryDirectory() as td:
            parent = Path(td)
            root = parent / "project"
            root.mkdir()
            source = root / "source.txt"
            source.write_bytes(b"original")
            original = module.move_noreplace
            def attempt_root_swap(src, dst, identity):
                with self.assertRaises(OSError):
                    root.rename(parent / "detached")
                return original(src, dst, identity)
            args = argparse.Namespace(project_root=str(root), source=str(source),
                                      destination=str(root / "target.txt"), dry_run=False, retry_seconds=0.0)
            with mock.patch.object(module, "move_noreplace", side_effect=attempt_root_swap):
                self.assertEqual(module.cmd_move(args), 0)
            self.assertEqual((root / "target.txt").read_bytes(), b"original")

    @unittest.skipUnless(os.name == "nt", "Windows handle semantics required")
    def test_project_root_replaced_before_lock_is_rejected(self):
        spec = importlib.util.spec_from_file_location("safe_ops_replaced_root", SCRIPT)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        with tempfile.TemporaryDirectory() as td:
            parent = Path(td)
            root = parent / "project"
            root.mkdir()
            (root / "source.txt").write_bytes(b"original")
            original_lock = module._safe_move.locked_directories
            @contextmanager
            def replace_before_lock(*directories):
                root.rename(parent / "detached")
                root.mkdir()
                (root / "source.txt").write_bytes(b"replacement")
                with original_lock(*directories) as value:
                    yield value
            args = argparse.Namespace(project_root=str(root), source=str(root / "source.txt"),
                                      destination=str(root / "target.txt"), dry_run=False, retry_seconds=0.0)
            with mock.patch.object(module._safe_move, "locked_directories", side_effect=replace_before_lock):
                with self.assertRaises(SystemExit):
                    module.cmd_move(args)
            self.assertEqual((parent / "detached" / "source.txt").read_bytes(), b"original")
            self.assertEqual((root / "source.txt").read_bytes(), b"replacement")
            self.assertFalse((root / "target.txt").exists())

    @unittest.skipUnless(os.name == "nt", "Windows atomic rename behavior required")
    def test_destination_created_during_move_is_not_overwritten(self):
        spec = importlib.util.spec_from_file_location("safe_ops_race", SCRIPT)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            source = root / "source.txt"
            destination = root / "destination.txt"
            source.write_bytes(b"source canary")
            original_rename = module._safe_move._rename_windows_handle
            def create_destination_then_rename(kernel, handle, dst):
                Path(dst).write_bytes(b"racing destination")
                return original_rename(kernel, handle, dst)
            args = argparse.Namespace(project_root=str(root), source=str(source), destination=str(destination),
                                      dry_run=False, retry_seconds=0.0)
            with mock.patch.object(module._safe_move, "_rename_windows_handle", side_effect=create_destination_then_rename):
                result = module.cmd_move(args)
            self.assertNotEqual(result, 0)
            self.assertEqual(source.read_bytes(), b"source canary")
            self.assertEqual(destination.read_bytes(), b"racing destination")

    def test_parent_replaced_by_link_during_move_fails_closed(self):
        spec = importlib.util.spec_from_file_location("safe_ops_parent_race", SCRIPT)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        with tempfile.TemporaryDirectory() as td:
            parent = Path(td)
            root = parent / "project"
            root.mkdir()
            source = root / "source.txt"
            source.write_bytes(b"source canary")
            destination_parent = root / "destination"
            destination_parent.mkdir()
            outside = parent / "outside"
            outside.mkdir()
            probe = root / "link-probe"
            try:
                probe.symlink_to(outside, target_is_directory=True)
                probe.unlink()
            except OSError as exc:
                self.skipTest(f"Symlink creation unavailable: {exc}")
            original_move = module.move_noreplace
            def swap_parent_then_move(src, dst, identity):
                destination_parent.rename(root / "detached-destination")
                destination_parent.symlink_to(outside, target_is_directory=True)
                return original_move(src, dst, identity)
            args = argparse.Namespace(project_root=str(root), source=str(source),
                                      destination=str(destination_parent / "target.txt"),
                                      dry_run=False, retry_seconds=0.0)
            with mock.patch.object(module, "move_noreplace", side_effect=swap_parent_then_move):
                result = module.cmd_move(args)
            self.assertNotEqual(result, 0)
            self.assertTrue(source.is_file())
            self.assertFalse((outside / "target.txt").exists())

    @unittest.skipUnless(os.name == "nt", "Windows handle semantics required")
    def test_parent_cannot_be_replaced_while_handle_bound_move_runs(self):
        spec = importlib.util.spec_from_file_location("safe_ops_locked_parent", SCRIPT)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            source = root / "source.txt"
            source.write_bytes(b"source canary")
            parent = root / "destination"
            parent.mkdir()
            original_rename = module._safe_move._rename_windows_handle
            def attempt_parent_swap(kernel, handle, dst):
                with self.assertRaises(OSError):
                    parent.rename(root / "detached")
                return original_rename(kernel, handle, dst)
            args = argparse.Namespace(project_root=str(root), source=str(source), destination=str(parent / "target.txt"),
                                      dry_run=False, retry_seconds=0.0)
            with mock.patch.object(module._safe_move, "_rename_windows_handle", side_effect=attempt_parent_swap):
                result = module.cmd_move(args)
            self.assertEqual(result, 0)
            self.assertEqual((parent / "target.txt").read_bytes(), b"source canary")

    @unittest.skipUnless(os.name == "nt", "Windows handle semantics required")
    def test_source_replaced_after_preflight_is_not_moved(self):
        spec = importlib.util.spec_from_file_location("safe_ops_source_race", SCRIPT)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            source = root / "source.txt"
            source.write_bytes(b"original canary")
            destination = root / "destination.txt"
            original_move = module.move_noreplace
            def swap_source_then_move(src, dst, identity):
                source.rename(root / "preserved.txt")
                source.write_bytes(b"replacement canary")
                return original_move(src, dst, identity)
            args = argparse.Namespace(project_root=str(root), source=str(source), destination=str(destination),
                                      dry_run=False, retry_seconds=0.0)
            with mock.patch.object(module, "move_noreplace", side_effect=swap_source_then_move):
                result = module.cmd_move(args)
            self.assertNotEqual(result, 0)
            self.assertEqual(source.read_bytes(), b"replacement canary")
            self.assertEqual((root / "preserved.txt").read_bytes(), b"original canary")
            self.assertFalse(destination.exists())

    @unittest.skipUnless(os.name == "nt", "Windows handle semantics required")
    def test_parent_is_locked_while_destination_directory_is_created(self):
        spec = importlib.util.spec_from_file_location("safe_ops_mkdir_race", SCRIPT)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            source = root / "source.txt"
            source.write_bytes(b"source canary")
            parent = root / "destination"
            parent.mkdir()
            target = parent / "newdir" / "target.txt"
            original_mkdir = Path.mkdir
            def attempt_swap_then_mkdir(path, *args, **kwargs):
                if path == target.parent:
                    with self.assertRaises(OSError):
                        parent.rename(root / "detached")
                return original_mkdir(path, *args, **kwargs)
            args = argparse.Namespace(project_root=str(root), source=str(source), destination=str(target),
                                      dry_run=False, retry_seconds=0.0)
            with mock.patch.object(Path, "mkdir", autospec=True, side_effect=attempt_swap_then_mkdir):
                result = module.cmd_move(args)
            self.assertEqual(result, 0)
            self.assertEqual(target.read_bytes(), b"source canary")

    @unittest.skipUnless(os.name == "nt", "Windows handle semantics required")
    def test_replaced_project_root_is_not_accepted_even_with_same_file_identity(self):
        spec = importlib.util.spec_from_file_location("safe_ops_root_race", SCRIPT)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        with tempfile.TemporaryDirectory() as td:
            parent = Path(td)
            root = parent / "project"
            root.mkdir()
            source = root / "source.txt"
            source.write_bytes(b"source canary")
            probe = root / "hardlink-probe"
            try:
                os.link(source, probe)
                probe.unlink()
            except OSError as exc:
                self.skipTest(f"Hardlink creation unavailable: {exc}")
            detached = parent / "detached"
            original_move = module.move_noreplace
            def replace_root_then_move(src, dst, identity):
                root.rename(detached)
                root.mkdir()
                os.link(detached / "source.txt", root / "source.txt")
                return original_move(src, dst, identity)
            args = argparse.Namespace(project_root=str(root), source=str(source), destination=str(root / "target.txt"),
                                      dry_run=False, retry_seconds=0.0)
            with mock.patch.object(module, "move_noreplace", side_effect=replace_root_then_move):
                result = module.cmd_move(args)
            self.assertNotEqual(result, 0)
            self.assertEqual((detached / "source.txt").read_bytes(), b"source canary")
            self.assertFalse((root / "target.txt").exists())

    @unittest.skipUnless(os.name == "nt", "Windows handle semantics required")
    def test_restore_does_not_write_through_swapped_record(self):
        spec = importlib.util.spec_from_file_location("safe_ops_record_race", SCRIPT)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        with tempfile.TemporaryDirectory() as td:
            parent = Path(td)
            root = parent / "project"
            root.mkdir()
            source = root / "source.txt"
            source.write_bytes(b"source canary")
            quarantined = self.run_tool("quarantine", source, "--project-root", root)
            self.assertEqual(quarantined.returncode, 0, quarantined.stderr)
            record = Path(json.loads(quarantined.stdout)["record"])
            outside = parent / "outside.json"
            outside.write_bytes(b"outside canary")
            probe = root / "link-probe"
            try:
                probe.symlink_to(outside)
                probe.unlink()
            except OSError as exc:
                self.skipTest(f"Symlink creation unavailable: {exc}")
            original_move = module.move_noreplace
            def swap_record_then_move(src, dst, identity):
                try:
                    record.rename(record.with_name("detached.json"))
                    record.symlink_to(outside)
                except OSError:
                    pass
                return original_move(src, dst, identity)
            args = argparse.Namespace(project_root=str(root), record=str(record), dry_run=False, retry_seconds=0.0)
            with mock.patch.object(module, "move_noreplace", side_effect=swap_record_then_move):
                result = module.cmd_restore(args)
            self.assertEqual(result, 0)
            self.assertEqual(outside.read_bytes(), b"outside canary")
            self.assertEqual(source.read_bytes(), b"source canary")

    @unittest.skipUnless(os.name == "nt", "Windows handle semantics required")
    def test_purge_does_not_delete_through_swapped_items_directory(self):
        spec = importlib.util.spec_from_file_location("safe_ops_purge_race", SCRIPT)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        with tempfile.TemporaryDirectory() as td:
            parent = Path(td)
            root = parent / "project"
            root.mkdir()
            source = root / "source.txt"
            source.write_bytes(b"source canary")
            quarantined = self.run_tool("quarantine", source, "--project-root", root)
            self.assertEqual(quarantined.returncode, 0, quarantined.stderr)
            payload = json.loads(quarantined.stdout)
            record = Path(payload["record"])
            target = root / payload["quarantined_path"]
            outside = parent / "outside"
            outside.mkdir()
            canary = outside / target.name
            canary.write_bytes(b"outside canary")
            probe = root / "link-probe"
            try:
                probe.symlink_to(outside, target_is_directory=True)
                probe.unlink()
            except OSError as exc:
                self.skipTest(f"Symlink creation unavailable: {exc}")
            original_unlink = Path.unlink
            def swap_items_then_unlink(path, *args, **kwargs):
                if path == target:
                    target.parent.rename(target.parent.with_name("Items-detached"))
                    target.parent.symlink_to(outside, target_is_directory=True)
                return original_unlink(path, *args, **kwargs)
            args = argparse.Namespace(project_root=str(root), record=str(record), dry_run=False,
                                      retry_seconds=0.0, confirm="PURGE-QUARANTINE")
            with mock.patch.object(Path, "unlink", autospec=True, side_effect=swap_items_then_unlink):
                module.cmd_purge(args)
            self.assertEqual(canary.read_bytes(), b"outside canary")

    @unittest.skipUnless(os.name == "nt", "Windows handle semantics required")
    def test_purge_rejects_items_directory_swapped_before_handle_open(self):
        spec = importlib.util.spec_from_file_location("safe_ops_purge_parent_race", SCRIPT)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        with tempfile.TemporaryDirectory() as td:
            parent = Path(td)
            root = parent / "project"
            root.mkdir()
            source = root / "source.txt"
            source.write_bytes(b"source canary")
            quarantined = self.run_tool("quarantine", source, "--project-root", root)
            self.assertEqual(quarantined.returncode, 0, quarantined.stderr)
            payload = json.loads(quarantined.stdout)
            record = Path(payload["record"])
            target = root / payload["quarantined_path"]
            outside = parent / "outside"
            outside.mkdir()
            canary = outside / target.name
            canary.write_bytes(b"outside canary")
            probe = root / "link-probe"
            try:
                probe.symlink_to(outside, target_is_directory=True)
                probe.unlink()
            except OSError as exc:
                self.skipTest(f"Symlink creation unavailable: {exc}")
            original_delete = module._safe_move.delete_nofollow
            def swap_items_then_delete(path, identity):
                target.parent.rename(target.parent.with_name("Items-detached"))
                target.parent.symlink_to(outside, target_is_directory=True)
                return original_delete(path, identity)
            args = argparse.Namespace(project_root=str(root), record=str(record), dry_run=False,
                                      retry_seconds=0.0, confirm="PURGE-QUARANTINE")
            with mock.patch.object(module._safe_move, "delete_nofollow", side_effect=swap_items_then_delete):
                result = module.cmd_purge(args)
            self.assertNotEqual(result, 0)
            self.assertEqual(canary.read_bytes(), b"outside canary")
            self.assertEqual((target.parent.with_name("Items-detached") / target.name).read_bytes(), b"source canary")

    def test_quarantined_directory_can_be_purged_and_replay_is_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            source = root / "folder"
            (source / "nested").mkdir(parents=True)
            (source / "nested" / "canary.txt").write_bytes(b"synthetic")
            quarantined = self.run_tool("quarantine", source, "--project-root", root)
            self.assertEqual(quarantined.returncode, 0, quarantined.stderr)
            payload = json.loads(quarantined.stdout)
            record = Path(payload["record"])
            result = self.run_tool("purge", record, "--project-root", root, "--confirm", "PURGE-QUARANTINE")
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertFalse((root / payload["quarantined_path"]).exists())
            self.assertTrue(json.loads(record.read_text(encoding="utf-8"))["purged"])
            replay = self.run_tool("purge", record, "--project-root", root, "--confirm", "PURGE-QUARANTINE")
            self.assertNotEqual(replay.returncode, 0, replay.stdout)

    def test_purge_refuses_link_inside_quarantined_directory(self):
        with tempfile.TemporaryDirectory() as td:
            parent = Path(td)
            root = parent / "project"
            root.mkdir()
            source = root / "folder"
            source.mkdir()
            (source / "inside.txt").write_bytes(b"inside canary")
            outside = parent / "outside.txt"
            outside.write_bytes(b"outside canary")
            try:
                (source / "link.txt").symlink_to(outside)
            except OSError as exc:
                self.skipTest(f"Symlink creation unavailable: {exc}")
            quarantined = self.run_tool("quarantine", source, "--project-root", root)
            self.assertEqual(quarantined.returncode, 0, quarantined.stderr)
            payload = json.loads(quarantined.stdout)
            result = self.run_tool("purge", payload["record"], "--project-root", root, "--confirm", "PURGE-QUARANTINE")
            self.assertNotEqual(result.returncode, 0, result.stdout)
            self.assertEqual(outside.read_bytes(), b"outside canary")
            self.assertEqual((root / payload["quarantined_path"] / "inside.txt").read_bytes(), b"inside canary")

    @unittest.skipUnless(os.name == "nt", "Windows handle semantics required")
    def test_interrupted_record_update_preserves_backup_and_restored_bytes(self):
        spec = importlib.util.spec_from_file_location("safe_ops_record_failure", SCRIPT)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            source = root / "source.txt"
            source.write_bytes(b"source canary")
            quarantined = self.run_tool("quarantine", source, "--project-root", root)
            self.assertEqual(quarantined.returncode, 0, quarantined.stderr)
            record = Path(json.loads(quarantined.stdout)["record"])
            before = record.read_bytes()
            original_write = module._safe_move._LockedRecord.write
            writes = []
            def interrupted_write(handle, data):
                writes.append(data)
                if len(writes) == 2:
                    original_write(handle, b"partial")
                    raise OSError("simulated interruption")
                return original_write(handle, data)
            args = argparse.Namespace(project_root=str(root), record=str(record), dry_run=False, retry_seconds=0.0)
            with mock.patch.object(module._safe_move._LockedRecord, "write", autospec=True, side_effect=interrupted_write):
                result = module.cmd_restore(args)
            self.assertNotEqual(result, 0)
            self.assertEqual(source.read_bytes(), b"source canary")
            backups = list(record.parent.glob(f"{record.stem}.before-restore-*.json"))
            self.assertEqual(len(backups), 1)
            self.assertEqual(backups[0].read_bytes(), before)

if __name__ == "__main__":
    unittest.main()
