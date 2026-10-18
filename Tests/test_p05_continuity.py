from __future__ import annotations
from pathlib import Path
import sys, tempfile, unittest
ROOT=Path(__file__).resolve().parents[1]; from test_support import CORE_ROOT; sys.path.insert(0,str(CORE_ROOT))
from aipm_core.continuity import ContinuityManager, LockError
from aipm_core.storage import initialize_project_state

class ContinuityTests(unittest.TestCase):
 def test_handoff_snapshot_and_state_only_restore(self):
  with tempfile.TemporaryDirectory(dir=ROOT/".test-workspace") as temporary:
   project=initialize_project_state(Path(temporary)/"Managed","managed","Managed"); manager=ContinuityManager(project)
   manager.checkpoint("actor","Verify Tests","tests: PASS", token_usage=None); handoff=manager.handoff()
   self.assertEqual(handoff["next_action"],"Verify Tests"); self.assertIsNone(handoff["token_usage"])
   snapshot=manager.snapshot(); (project.state_root/"Current-State.md").write_text("changed")
   manager.restore(snapshot); self.assertNotEqual((project.state_root/"Current-State.md").read_text(),"changed")
 def test_contested_lock_requires_matching_nonce_to_release(self):
  with tempfile.TemporaryDirectory(dir=ROOT/".test-workspace") as temporary:
   manager=ContinuityManager(initialize_project_state(Path(temporary)/"Managed","managed","Managed")); nonce=manager.acquire_lock("task","actor")
   with self.assertRaises(LockError): manager.acquire_lock("task","other")
   with self.assertRaises(LockError): manager.release_lock("task","bad")
   manager.release_lock("task",nonce)
if __name__=="__main__": unittest.main()
