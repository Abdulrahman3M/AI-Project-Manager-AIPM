"""P04 task phase plans and evidence-based completion gates."""
from __future__ import annotations
from dataclasses import dataclass

VALID_RESULTS = {"PASS", "FAIL", "UNVERIFIED"}


class VerificationError(ValueError): pass


@dataclass
class Acceptance:
    identifier: str
    weight: int
    result: str
    def __post_init__(self) -> None:
        if self.weight <= 0 or self.result not in VALID_RESULTS:
            raise VerificationError("acceptance requires positive weight and PASS, FAIL, or UNVERIFIED")


@dataclass
class Phase:
    phase_id: str
    dependencies: tuple[str, ...]
    acceptance: list[Acceptance]
    report: bool = False


class TaskPlan:
    def __init__(self, task_id: str, phases: list[Phase]) -> None:
        self.task_id, self.phases = task_id, phases
        known: set[str] = set()
        for phase in phases:
            if any(dependency not in known for dependency in phase.dependencies):
                raise VerificationError("phase dependency must precede its dependent phase")
            known.add(phase.phase_id)

    def progress(self) -> int:
        acceptance = [item for phase in self.phases for item in phase.acceptance]
        total = sum(item.weight for item in acceptance)
        passed = sum(item.weight for item in acceptance if item.result == "PASS")
        return int(passed * 100 / total) if total else 0

    def can_complete(self, phase_id: str) -> bool:
        target = next((phase for phase in self.phases if phase.phase_id == phase_id), None)
        if target is None or not target.report or any(item.result != "PASS" for item in target.acceptance): return False
        by_id = {phase.phase_id: phase for phase in self.phases}
        return all(by_id[dependency].report and all(item.result == "PASS" for item in by_id[dependency].acceptance) for dependency in target.dependencies)
