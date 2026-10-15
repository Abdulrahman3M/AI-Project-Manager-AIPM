"""P05 state-only continuity, snapshots, and nonce-protected writer leases."""
from __future__ import annotations
from datetime import datetime, timezone
import json, secrets, shutil
from pathlib import Path
from .storage import ManagedProject, _atomic_json

class LockError(RuntimeError): pass

class ContinuityManager:
 def __init__(self, project: ManagedProject): self.project=project
 def checkpoint(self, actor: str, next_action: str, evidence: str, token_usage: int|None) -> None:
  data={"actor":actor,"next_action":next_action,"last_verified_action":evidence,"token_usage":token_usage,"created_at":datetime.now(timezone.utc).isoformat()}
  _atomic_json(self.project.state_root/"History"/"Events"/"checkpoint.json",data)
  (self.project.state_root/"Current-State.md").write_text(f"# Current State\n\n{evidence}\n",encoding="utf-8")
 def handoff(self) -> dict:
  return json.loads((self.project.state_root/"History"/"Events"/"checkpoint.json").read_text(encoding="utf-8"))
 def snapshot(self) -> Path:
  target=self.project.state_root/"History"/"Snapshots"/"state-snapshot"
  if target.exists(): shutil.rmtree(target)
  shutil.copytree(self.project.state_root,target,ignore=shutil.ignore_patterns("Snapshots"))
  return target
 def restore(self, snapshot: Path) -> None:
  source=snapshot/"Current-State.md"; target=self.project.state_root/"Current-State.md"
  if source.exists(): target.write_bytes(source.read_bytes())
 def acquire_lock(self, resource: str, actor: str) -> str:
  path=self.project.state_root/"Locks"/f"{resource}.json"
  if path.exists(): raise LockError("LOCK_HELD")
  nonce=secrets.token_urlsafe(16); _atomic_json(path,{"actor":actor,"nonce":nonce,"created_at":datetime.now(timezone.utc).isoformat()}); return nonce
 def release_lock(self, resource: str, nonce: str) -> None:
  path=self.project.state_root/"Locks"/f"{resource}.json"
  if not path.exists() or json.loads(path.read_text(encoding="utf-8"))["nonce"]!=nonce: raise LockError("LOCK_NONCE_MISMATCH")
  path.unlink()
