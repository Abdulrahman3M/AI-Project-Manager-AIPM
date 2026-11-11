"""Evaluate resource records; never spawn an agent or query a provider."""

import math
from copy import deepcopy


def delegation_decision(size, approved, plan):
    """Validate an owner-approved plan without launching any subprocess or agent."""
    if size == "SMALL":
        return "DENY"
    if size == "MEDIUM":
        return "SERIAL"
    if size != "HUGE":
        return "DENY"
    if approved is not True:
        return "SERIAL"
    if not isinstance(plan, dict):
        return "DENY"
    for key in ("reason", "collision_avoidance", "overhead", "serial_alternative", "verification"):
        if not isinstance(plan.get(key), str) or not plan[key].strip():
            return "DENY"
    count = plan.get("count")
    if type(count) is not int or count < 1:
        return "DENY"
    for key in ("roles", "boundaries"):
        values = plan.get(key)
        if (not isinstance(values, list) or len(values) != count
                or any(not isinstance(value, str) or not value.strip() for value in values)):
            return "DENY"
    boundaries = []
    for value in plan["boundaries"]:
        path = value.rstrip("/")
        if (not path or path.startswith("/") or any(c in path for c in "\\:*?[]")
                or any(part in ("", ".", "..") for part in path.split("/"))):
            return "DENY"
        boundaries.append(path.casefold())
    for index, left in enumerate(boundaries):
        for right in boundaries[index + 1:]:
            if left == right or left.startswith(right + "/") or right.startswith(left + "/"):
                return "DENY"
    return "ALLOW_PLAN"


def telemetry(value, *, verified=False):
    """Label a caller-supplied measurement without inferring provider quota."""
    if verified is not True or type(value) not in (int, float) or not math.isfinite(value) or value < 0:
        return {"status": "NOT_MEASURED", "value": None}
    return {"status": "MEASURED", "value": value}


def revise_budget(current, changes):
    """Apply target changes while preserving reported observations and required checks."""
    allowed = {"revision", "target_tokens", "target_seconds", "target_calls"}
    if not isinstance(current, dict) or not isinstance(changes, dict) or set(changes) - allowed:
        raise ValueError("Invalid budget or attempted change to protected fields")
    checks = current.get("required_checks")
    if not isinstance(checks, list) or not checks or any(not isinstance(x, str) or not x.strip() for x in checks):
        raise ValueError("Required checks must remain explicitly listed")
    for name, value in changes.items():
        if name == "revision":
            if not isinstance(value, str) or not value.strip():
                raise ValueError("Budget revision must be nonempty")
        elif type(value) not in (int, float) or not math.isfinite(value) or value < 0:
            raise ValueError("Budget targets must be finite and nonnegative")
    result = deepcopy(current)
    result.update(changes)
    return result


def required_checks_continue(*, budget_exhausted):
    """Efficiency budgets cannot waive mandatory verification."""
    if type(budget_exhausted) is not bool:
        raise ValueError("budget_exhausted must be boolean")
    return True
