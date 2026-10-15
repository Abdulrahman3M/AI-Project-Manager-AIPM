"""P05 state-only continuity, snapshots, and nonce-protected writer leases."""
from __future__ import annotations
from datetime import datetime, timezone, timedelta
import json, secrets, shutil, os
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
 def acquire_lock(self, resource: str, actor: str, lease_seconds: int=300) -> str:
  path=self.project.state_root/"Locks"/f"{resource}.json"
  if path.exists(): raise LockError("LOCK_HELD")
  now=datetime.now(timezone.utc); nonce=secrets.token_urlsafe(16); _atomic_json(path,{"actor":actor,"pid":os.getpid(),"nonce":nonce,"created_at":now.isoformat(),"expires_at":(now+timedelta(seconds=lease_seconds)).isoformat()}); return nonce
 def recover_expired_lock(self, resource: str, pid_is_alive: bool|None=None) -> None:
  path=self.project.state_root/"Locks"/f"{resource}.json"; data=json.loads(path.read_text(encoding="utf-8"))
  alive=pid_is_alive if pid_is_alive is not None else _pid_alive(data.get("pid"))
  if alive or datetime.fromisoformat(data["expires_at"])>datetime.now(timezone.utc): raise LockError("LOCK_NOT_SAFE_TO_RECOVER")
  path.unlink()
 def release_lock(self, resource: str, nonce: str) -> None:
  path=self.project.state_root/"Locks"/f"{resource}.json"
  if not path.exists() or json.loads(path.read_text(encoding="utf-8"))["nonce"]!=nonce: raise LockError("LOCK_NONCE_MISMATCH")
  path.unlink()

def _pid_alive(pid: int|None) -> bool:
 if not pid: return False
 try: os.kill(pid,0); return True
 except OSError: return False
