from __future__ import annotations

import base64
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
import zipfile
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
from test_support import CORE_ROOT, CORE_SCRIPT
sys.path.insert(0, str(CORE_ROOT))

from aipm_core.domain import CommandEnvelope, CoreEngine  # noqa: E402
from aipm_core.host_adapters import HostAdapter  # noqa: E402
from aipm_core.storage import ProjectRegistry, StateError, initialize_project_state  # noqa: E402
from aipm_core.task_ops import TaskOperations  # noqa: E402


class TaskArtifactLifecycleTests(unittest.TestCase):
    def setUp(self) -> None:
        workspace = ROOT / ".test-workspace"
        workspace.mkdir(exist_ok=True)
        self.temp = tempfile.TemporaryDirectory(prefix="task-artifacts-", dir=workspace)
        self.project_root = Path(self.temp.name) / "Example-Project"
        self.project_root.mkdir()
        self.project = initialize_project_state(self.project_root, "example-project", "Example Project")
        self.engine = CoreEngine({self.project.project_id: self.project})

    def tearDown(self) -> None:
        self.temp.cleanup()

    def test_three_tasks_resume_from_shared_files_without_copying_project_sources(self) -> None:
        source = self.project_root / "serve.py"
        original_source = b"print('project source stays here')\n"
        source.write_bytes(original_source)
        first_agent = TaskOperations(self.engine, self.project)
        tasks = [first_agent.create(f"Task {name}", f"Scope {name}") for name in ("One", "Two", "Three")]
        first_agent.checkpoint(
            tasks[0],
            last_verified_action="Read the task requirements and inspected the application entry point.",
            next_action="Implement the first acceptance criterion in the original serve.py file.",
            completed_work=["Mapped the existing entry point."],
            changed_files=["serve.py"],
            test_results=["Not run yet; implementation has not started."],
        )
        first_agent.write_artifact(tasks[0], "Instructions/Task-Instructions.md", b"Preserve source files in their original project paths.\n")

        second_agent_engine = CoreEngine({self.project.project_id: self.project})
        second_agent = TaskOperations(second_agent_engine, self.project)
        resumed = second_agent.read_task(tasks[0])
        artifacts = second_agent.list_artifacts(tasks[0])

        self.assertEqual(resumed["next_action"], "Implement the first acceptance criterion in the original serve.py file.")
        self.assertEqual(resumed["completed_work"], ["Mapped the existing entry point."])
        self.assertEqual(resumed["changed_files"], ["serve.py"])
        self.assertIn("Instructions/Task-Instructions.md", [item["path"] for item in artifacts])
        self.assertEqual(second_agent.read_artifact(tasks[0], "Instructions/Task-Instructions.md"), b"Preserve source files in their original project paths.\n")

        state = second_agent_engine.execute(CommandEnvelope("state-read", "state.read", "agent-two", self.project.project_id, 0, None, {}))["state"]
        self.assertEqual(set(state["tasks"]), {task.name for task in tasks})
        self.assertNotIn("serve.py", [item["path"] for item in second_agent.list_artifacts(tasks[0])])
        self.assertTrue(source.is_file())
        self.assertEqual(source.read_bytes(), original_source)
        self.assertEqual([second_agent.status(task)["status"] for task in tasks], ["IN-PROGRESS"] * 3)

    def test_task_artifacts_confine_paths_and_require_matching_hash_for_updates(self) -> None:
        operations = TaskOperations(self.engine, self.project)
        task = operations.create("Artifact Safety", "Keep all task context under the state root.")
        path = "References/design-notes.md"
        original = b"Initial supporting context.\n"
        metadata = operations.write_artifact(task, path, original)
        self.assertEqual(operations.read_artifact(task, path), original)
        self.assertEqual(metadata["sha256"], hashlib.sha256(original).hexdigest())
        with self.assertRaises(StateError):
            operations.write_artifact(task, path, b"Silent overwrite is forbidden.\n")
        updated = operations.write_artifact(task, path, b"Reviewed context.\n", expected_sha256=metadata["sha256"])
        self.assertNotEqual(updated["sha256"], metadata["sha256"])
        with self.assertRaises(StateError):
            operations.write_artifact(task, path, b"Stale writer.", expected_sha256=metadata["sha256"])
        for unsafe in ("../outside.txt", "References/../../outside.txt", "C:/outside.txt", "/outside.txt"):
            with self.subTest(path=unsafe), self.assertRaises(StateError):
                operations.write_artifact(task, unsafe, b"must not escape")
        self.assertFalse((self.project_root / "outside.txt").exists())

    def test_generated_task_projections_never_write_through_a_hardlink_to_project_source(self) -> None:
        operations = TaskOperations(self.engine, self.project)
        task = operations.create("Hard Link Boundary", "Generated task records must not mutate project source files.")
        source = self.project_root / "serve.py"
        original = b"print('immutable project source')\n"
        source.write_bytes(original)
        projection = task / "Task-State.md"
        projection.unlink()
        try:
            projection.hardlink_to(source)
        except OSError as error:
            self.skipTest(f"Hard links are unavailable in this test environment: {error}")

        operations.checkpoint(task, last_verified_action="Created a test checkpoint.", next_action="Continue in the original project files.")

        self.assertEqual(source.read_bytes(), original)
        self.assertNotEqual(projection.read_bytes(), original)
        self.assertEqual(source.stat().st_nlink, 1)

    def test_generated_projections_are_written_by_atomic_path_replacement(self) -> None:
        operations = TaskOperations(self.engine, self.project)
        task = operations.create("Atomic Projection", "Replace managed projections as directory entries.")
        projection = task / "Task-State.md"
        original = projection.read_bytes()
        replace = os.replace
        calls: list[tuple[Path, Path]] = []

        def observe_replace(source: str | Path, target: str | Path) -> None:
            calls.append((Path(source), Path(target)))
            replace(source, target)

        with patch("aipm_core.task_ops.os.replace", side_effect=observe_replace):
            operations.checkpoint(task, last_verified_action="Created an atomic-write checkpoint.", next_action="Resume from the task handoff.")

        self.assertIn(projection, [target for _, target in calls])
        self.assertNotEqual(projection.read_bytes(), original)

    def test_local_host_adapter_reads_and_writes_task_artifacts_without_project_file_api(self) -> None:
        operations = TaskOperations(self.engine, self.project)
        task = operations.create("Agent Bridge", "Share task context between compatible local agents.")
        adapter = HostAdapter(self.engine, self.project.project_id, "local-cli", root=ROOT, allow_mutations=True)
        payload = {"task_id": task.name, "path": "Handoff/Next-Agent.md", "content_base64": base64.b64encode(b"Read current task state before continuing.\n").decode("ascii")}
        written = adapter.execute("task.artifact.write", payload, expected_revision=1, idempotency_key="handoff-v1")
        self.assertEqual(written["status"], "PASS")
        repeated = adapter.execute("task.artifact.write", payload, expected_revision=1, idempotency_key="handoff-v1")
        self.assertTrue(repeated["replayed"])
        read = adapter.execute("task.artifact.read", {"task_id": task.name, "path": "Handoff/Next-Agent.md"})
        self.assertEqual(base64.b64decode(read["content_base64"], validate=True), b"Read current task state before continuing.\n")
        listing = adapter.execute("task.artifact.list", {"task_id": task.name})
        self.assertIn("Handoff/Next-Agent.md", [item["path"] for item in listing["artifacts"]])
        self.assertEqual(adapter.execute("filesystem.write", {"path": str(self.project_root / "serve.py"), "content": "unsafe"})["reason"], "UNSUPPORTED_CAPABILITY")

    def test_existing_legacy_task_records_remain_readable(self) -> None:
        operations = TaskOperations(self.engine, self.project)
        task = operations.create("Compatibility", "Preserve old task records.")
        manifest_path = self.project.state_root / "State-Manifest.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        record = manifest["tasks"][task.name]
        for key in ("last_verified_action", "next_action", "completed_work", "changed_files", "test_results", "status_override"):
            record.pop(key, None)
        manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
        read = operations.read_task(task)
        self.assertEqual(read["next_action"], "Unknown; reconcile the task with current project evidence.")
        second_task = operations.create("Post Legacy Task", "Mutate state when an older task lacks status_override.")
        self.assertEqual(operations.read_task(second_task)["task_status"], "IN-PROGRESS")

    def test_stranded_pending_commit_with_legacy_task_recovers_cleanly(self) -> None:
        operations = TaskOperations(self.engine, self.project)
        first = operations.create("Legacy Task", "Created before status_override existed.")
        manifest_path = self.project.state_root / "State-Manifest.json"
        current = json.loads(manifest_path.read_text(encoding="utf-8"))
        current["tasks"][first.name].pop("status_override", None)
        manifest_path.write_text(json.dumps(current), encoding="utf-8")
        pending_manifest = json.loads(json.dumps(current))
        pending_task_id = "Task-2026-10-23-Recovered-1234567890ab"
        pending_manifest["tasks"][pending_task_id] = {
            "title": "Recovered Task",
            "scope": "Recover from stranded v1.5.0 Pending-Commit.",
            "plan": "# Recovered Task\n\nRecover from stranded v1.5.0 Pending-Commit.\n",
            "blockers": [],
            "verification": None,
            "report": "",
            "status_override": None,
        }
        pending_manifest["task_id"] = pending_task_id
        pending_manifest["task_status"] = "IN-PROGRESS"
        pending_manifest["revision"] = current["revision"] + 1
        pending_manifest["updated_by"] = "aipm-task-operations"
        pending_event = {
            "schema_version": "1.0",
            "request_id": "pending-recovery-test",
            "command": "task.create",
            "actor": "aipm-task-operations",
            "project_id": self.project.project_id,
            "revision": pending_manifest["revision"],
            "idempotency_key": "pending-recovery-test",
            "input": {"task_id": pending_task_id, "title": "Recovered Task", "scope": "Recover from stranded v1.5.0 Pending-Commit."},
        }
        pending_path = self.project.state_root / "History" / "Pending-Commit.json"
        pending_path.write_text(json.dumps({"schema_version": "1.0", "manifest": pending_manifest, "event": pending_event}), encoding="utf-8")
        recovered = operations.read_task(self.project.state_root / "Tasks" / pending_task_id)
        self.assertEqual(recovered["title"], "Recovered Task")
        self.assertFalse(pending_path.exists())

    def test_task_can_be_closed_reopened_and_archived_without_losing_its_record(self) -> None:
        operations = TaskOperations(self.engine, self.project)
        task = operations.create("Close And Archive", "Preserve a completed task as a portable archive.")
        operations.write_artifact(task, "Reports/Completion.md", b"Completed work.\n")

        operations.add_blocker(task, "Unresolved blocker prevents closing.")
        with self.assertRaises(StateError):
            operations.close(task, "Cannot close while blocked.")
        operations.clear_blockers(task)

        operations.close(task, "The task is complete and its evidence is recorded.")
        self.assertEqual(operations.read_task(task)["task_status"], "COMPLETE")
        archive = operations.archive(task)
        self.assertTrue(archive["archive_path"].is_file())
        self.assertTrue(archive["checksum_path"].is_file())
        with zipfile.ZipFile(archive["archive_path"]) as package:
            self.assertIn("Reports/Completion.md", package.namelist())
        self.assertTrue(task.is_dir())

        operations.reopen(task, "Follow-up work is required.")
        self.assertEqual(operations.read_task(task)["task_status"], "IN-PROGRESS")
        operations.verify(task, "PASS", "All checks passed.")
        operations.report(task, "Verified and reported complete.")
        self.assertEqual(operations.read_task(task)["task_status"], "COMPLETE")
        operations.reopen(task, "Reopen after verification pass.")
        self.assertEqual(operations.read_task(task)["task_status"], "IN-PROGRESS")

    def test_existing_work_folder_is_registered_with_an_inventory_artifact(self) -> None:
        operations = TaskOperations(self.engine, self.project)
        work = self.project_root / "Manual-Work"
        work.mkdir()
        (work / "README.md").write_text("Existing task work.\n", encoding="utf-8")
        task = operations.import_work_folder("Imported Work", "Continue the existing work.", work)

        read = operations.read_task(task)
        self.assertIn(str(work.resolve()), read["scope"])
        inventory = operations.read_artifact(task, "References/Existing-Work-Folder.md").decode("utf-8")
        self.assertIn("README.md", inventory)

    def test_cli_creates_checkpoints_and_transfers_task_context_without_source_paths(self) -> None:
        registry_path = Path(self.temp.name) / "User-Data" / "registry.json"
        ProjectRegistry(registry_path).register(self.project)
        def run(*arguments: str, input_bytes: bytes | None = None) -> dict:
            process = subprocess.run(
                [sys.executable, str(CORE_SCRIPT), *arguments, "--registry", str(registry_path), "--project-id", self.project.project_id],
                cwd=ROOT, input=input_bytes, capture_output=True, check=False,
            )
            self.assertEqual(process.returncode, 0, process.stderr.decode(errors="replace"))
            return json.loads(process.stdout)

        created = run("task-create", "--title", "CLI Handoff", "--scope", "Resume without repeating completed work.")
        task_id = created["task"]["task_id"]
        planned = run("task-plan", "--task-id", task_id, "--text", "Inspect, implement, then verify.")
        self.assertEqual(planned["task"]["plan"], "Inspect, implement, then verify.")
        run("task-blocker-add", "--task-id", task_id, "--text", "Waiting for source inspection.")
        cleared = run("task-blocker-clear", "--task-id", task_id)
        self.assertEqual(cleared["task"]["task_status"], "IN-PROGRESS")
        run("task-verify", "--task-id", task_id, "--result", "UNVERIFIED", "--evidence", "Implementation has not started.")
        run("task-report", "--task-id", task_id, "--text", "The task is ready for agent execution.")
        checkpoint = run(
            "task-checkpoint", "--task-id", task_id,
            "--last-verified-action", "Read requirements and inspected source.",
            "--next-action", "Implement the remaining acceptance criterion.",
            "--completed-work", "Inspected source structure.", "--changed-file", "serve.py",
            "--test-result", "UNVERIFIED: implementation not started.",
        )
        self.assertEqual(checkpoint["status"], "PASS")
        content = b"Instructions for the next agent.\n"
        saved = run("task-artifact-write", "--task-id", task_id, "--relative-path", "Handoff/Next-Agent.md", "--stdin", input_bytes=content)
        self.assertEqual(saved["status"], "PASS")
        read = run("task-artifact-read", "--task-id", task_id, "--relative-path", "Handoff/Next-Agent.md")
        self.assertEqual(base64.b64decode(read["content_base64"], validate=True), content)
        reference = Path(self.temp.name) / "Reference-Notes.md"
        reference.write_bytes(b"Reference-only context; implementation remains in project source paths.\n")
        imported = run("task-artifact-write", "--task-id", task_id, "--relative-path", "References/Reference-Notes.md", "--from-file", str(reference))
        self.assertEqual(imported["artifact"]["size_bytes"], reference.stat().st_size)
        self.assertEqual(run("task-artifact-read", "--task-id", task_id, "--relative-path", "References/Reference-Notes.md")["content_base64"], base64.b64encode(reference.read_bytes()).decode("ascii"))
        state = run("task-read", "--task-id", task_id)
        self.assertEqual(state["task"]["next_action"], "Implement the remaining acceptance criterion.")
        self.assertEqual(run("task-list")["tasks"][0]["task_id"], task_id)


if __name__ == "__main__":
    unittest.main()
