"""P04 human-editable task artifacts and verification gates."""
from __future__ import annotations
from datetime import date
from pathlib import Path

class TaskOperations:
 def __init__(self, root: Path): self.root=root
 def create(self, title: str, scope: str) -> Path:
  task=self.root/"Tasks"/f"Task-{date.today():%Y-%m-%d}-{title.replace(' ','-')}"; task.mkdir(parents=True)
  (task/"Task-Plan.md").write_text(f"# {title}\n\n{scope}\n",encoding="utf-8"); (task/"Blockers.md").write_text("",encoding="utf-8"); return task
 def plan(self, task: Path, text: str)->None: (task/"Task-Plan.md").write_text(text,encoding="utf-8")
 def add_blocker(self, task: Path, text: str)->None: (task/"Blockers.md").write_text(text,encoding="utf-8")
 def clear_blockers(self, task: Path)->None: (task/"Blockers.md").write_text("",encoding="utf-8")
 def verify(self, task: Path, result: str, evidence: str)->None:
  if result not in {"PASS","FAIL","UNVERIFIED"}: raise ValueError("invalid verification")
  (task/"Test-Status.md").write_text(f"{result}\n{evidence}\n",encoding="utf-8")
 def report(self, task: Path, text: str)->None: (task/"Final-Report.md").write_text(text,encoding="utf-8")
 def status(self, task: Path)->dict:
  if (task/"Blockers.md").read_text(encoding="utf-8").strip(): return {"status":"BLOCKED"}
  verified=(task/"Test-Status.md").exists() and (task/"Test-Status.md").read_text(encoding="utf-8").startswith("PASS")
  return {"status":"COMPLETE" if verified and (task/"Final-Report.md").exists() else "IN-PROGRESS"}
