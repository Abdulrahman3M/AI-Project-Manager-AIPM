from __future__ import annotations
from pathlib import Path
import sys, tempfile, unittest
ROOT=Path(__file__).resolve().parents[1]; sys.path.insert(0,str(ROOT/"Core-Engine"))
from aipm_core.continuity import ContinuityManager, LockError
from aipm_core.storage import initialize_project_state
class HardeningTests(unittest.TestCase):
 def test_expired_lock_requires_explicit_safe_recovery(self):
  with tempfile.TemporaryDirectory(dir=ROOT/".test-workspace") as temporary:
   manager=ContinuityManager(initialize_project_state(Path(temporary)/"Managed","managed","Managed")); manager.acquire_lock("task","actor",lease_seconds=-1)
   with self.assertRaises(LockError): manager.recover_expired_lock("task",pid_is_alive=True)
   manager.recover_expired_lock("task",pid_is_alive=False)
   self.assertFalse((manager.project.state_root/"Locks"/"task.json").exists())
