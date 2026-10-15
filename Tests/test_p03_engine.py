from __future__ import annotations

import json
import subprocess
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "Core-Engine"))
from aipm_core.domain import CommandEnvelope, CoreEngine
from aipm_core.storage import initialize_project_state


class CoreEngineTests(unittest.TestCase):
    def test_cli_lists_pointer_only_registry_as_json(self) -> None:
        with tempfile.TemporaryDirectory(dir=ROOT / ".test-workspace") as temporary:
            registry = Path(temporary) / "registry.json"
            registry.write_text(json.dumps({"schema_version":"1.0","projects":[{"project_id":"one","root_path":"C:/One","alias":"One"}],"preferences":{}}))
            result = subprocess.run([sys.executable, str(ROOT / "Core-Engine" / "aipm.py"), "list", "--registry", str(registry)], capture_output=True, text=True, check=True)
            self.assertEqual(json.loads(result.stdout)["projects"][0]["project_id"], "one")
    def test_state_read_and_revisioned_event_write_are_idempotent(self) -> None:
        with tempfile.TemporaryDirectory(dir=ROOT / ".test-workspace") as temporary:
            project = initialize_project_state(Path(temporary) / "Managed", "managed", "Managed")
            engine = CoreEngine({"managed": project})
            initial = engine.execute(CommandEnvelope("request-001", "state.read", "tester", "managed", 0, None, {}))
            self.assertEqual(initial["status"], "PASS")
            command = CommandEnvelope("request-002", "state.set-next-action", "tester", "managed", 0, "idem-1", {"next_action": "Run Tests"})
            changed = engine.execute(command)
            replay = engine.execute(command)
            self.assertEqual(changed["revision"], 1)
            self.assertEqual(replay["status"], "PASS")
            self.assertTrue(replay["replayed"])
            self.assertEqual(replay["revision"], 1)
            self.assertEqual(len(list((project.state_root / "History" / "Events").glob("*.json"))), 1)

    def test_revision_conflict_is_blocked_without_state_overwrite(self) -> None:
        with tempfile.TemporaryDirectory(dir=ROOT / ".test-workspace") as temporary:
            project = initialize_project_state(Path(temporary) / "Managed", "managed", "Managed")
            engine = CoreEngine({"managed": project})
            result = engine.execute(CommandEnvelope("request-003", "state.set-next-action", "tester", "managed", 4, None, {"next_action": "Unsafe"}))
            manifest = json.loads((project.state_root / "State-Manifest.json").read_text())
            self.assertEqual(result["status"], "BLOCKED")
            self.assertEqual(manifest["revision"], 0)


if __name__ == "__main__":
    unittest.main()
