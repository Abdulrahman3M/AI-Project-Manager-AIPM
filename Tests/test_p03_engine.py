from __future__ import annotations

import json
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "Core-Engine"))
from aipm_core.domain import CommandEnvelope, CoreEngine
from aipm_core.storage import initialize_project_state


class CoreEngineTests(unittest.TestCase):
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
