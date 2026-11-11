"""Evaluate caller-supplied scope records; never intercept or access files."""


def edit_decision(path, authorized_paths):
    """Check exact lexical membership only; caller must resolve actual filesystem paths."""
    if not isinstance(path, str) or not path or not isinstance(authorized_paths, list):
        return False
    if "\\" in path or ":" in path or path.startswith("/"):
        return False
    if any(part in ("", ".", "..") for part in path.split("/")):
        return False
    return path in authorized_paths


def read_decision(reason, revision, previous_revision, ranges=None, previous_ranges=None):
    """Classify a proposed read using caller-supplied evidence and identity."""
    if not isinstance(reason, str) or not reason.strip():
        return "DENY"
    if not isinstance(revision, str) or not revision.strip():
        return "UNVERIFIED"
    for value in (ranges, previous_ranges):
        if value is not None and (not isinstance(value, (tuple, list)) or len(value) != 2
                                  or any(type(number) is not int for number in value)
                                  or value[0] < 1 or value[1] < value[0]):
            return "UNVERIFIED"
    if previous_revision == revision:
        if previous_ranges is None:
            return "REDUNDANT"
        if ranges is not None and previous_ranges[0] <= ranges[0] <= ranges[1] <= previous_ranges[1]:
            return "REDUNDANT"
    return "ALLOW"


def retry_decision(new_hypothesis, attempt, limit, previous_hypothesis, previous_evidence=None, current_evidence=None):
    """Decide whether a documented retry is within its budget."""
    if (not isinstance(new_hypothesis, str) or not new_hypothesis.strip()
            or not isinstance(previous_hypothesis, str) or not previous_hypothesis.strip()
            or type(attempt) is not int or type(limit) is not int or not 0 <= attempt < limit):
        return False
    changed_hypothesis = new_hypothesis.strip() != previous_hypothesis.strip()
    changed_evidence = (isinstance(previous_evidence, str) and bool(previous_evidence.strip())
                        and isinstance(current_evidence, str) and bool(current_evidence.strip())
                        and previous_evidence.strip() != current_evidence.strip())
    return changed_hypothesis or changed_evidence


def quality_gate(items, required_ids):
    """Aggregate reported evidence statuses; callers must verify the evidence itself."""
    if not isinstance(items, list) or not isinstance(required_ids, list) or not required_ids:
        return "UNVERIFIED"
    if any(isinstance(item, dict) and item.get("status") == "FAIL" for item in items):
        return "FAIL"
    if any(not isinstance(identifier, str) or not identifier.strip() for identifier in required_ids):
        return "UNVERIFIED"
    if len(set(required_ids)) != len(required_ids):
        return "UNVERIFIED"
    if any(not isinstance(item, dict) or not isinstance(item.get("id"), str)
           or not item["id"].strip() for item in items):
        return "UNVERIFIED"
    identifiers = [item["id"] for item in items]
    if len(set(identifiers)) != len(identifiers) or not set(required_ids).issubset(identifiers):
        return "UNVERIFIED"
    if any(item.get("status") != "PASS" or item.get("supported") is not True
           or not isinstance(item.get("evidence"), str) or not item["evidence"].strip()
           for item in items):
        return "UNVERIFIED"
    return "PASS"
