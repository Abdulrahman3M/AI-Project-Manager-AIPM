"""Describe an AIPM task bootstrap; this does not intercept host actions."""

EVENTS = frozenset({"NEW", "ACTIVE", "RESUME", "REVISE", "REOPEN", "FIX", "RECHECK"})
SEQUENCE = ("project-manager", "task-scope-contract", "resource-optimization")


def valid_entry(sequence):
    """Validate recorded policy order; this is not a host interception hook."""
    return isinstance(sequence, (list, tuple)) and tuple(sequence) == SEQUENCE


def bootstrap(event, task_key, previous_scope, current_scope):
    """Return an instruction-level routing decision without creating state."""
    if not isinstance(event, str) or event not in EVENTS:
        raise ValueError("Unsupported task event")
    if not isinstance(task_key, str) or not task_key.strip():
        raise ValueError("A task identity is required")
    if not isinstance(current_scope, str) or not current_scope.strip():
        raise ValueError("A current scope revision is required")
    if not isinstance(previous_scope, str):
        raise ValueError("Previous scope revision must be a string")
    return {
        "event": event,
        "task_key": task_key,
        "sequence": list(SEQUENCE),
        "scope_changed": previous_scope != current_scope,
        "enforcement": "INSTRUCTION_ONLY",
    }
