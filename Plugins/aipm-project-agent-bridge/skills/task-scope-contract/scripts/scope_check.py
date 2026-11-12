"""Evaluate scope records and provisional path metadata; never intercept edits."""

import os
from pathlib import Path
import re
import stat


def edit_decision(path, authorized_paths):
    """Check exact lexical membership only; caller must resolve actual filesystem paths."""
    if not isinstance(path, str) or not path or not isinstance(authorized_paths, list):
        return False
    if "\\" in path or ":" in path or path.startswith("/"):
        return False
    if any(part in ("", ".", "..") for part in path.split("/")):
        return False
    return path in authorized_paths


def edit_preflight(project_root, path, authorized_paths):
    """Inspect an existing path provisionally; this cannot authorize or guard a later edit."""
    if not edit_decision(path, authorized_paths) or re.search(r"%(?:2e|2f|5c)", path, re.IGNORECASE):
        return "DENY"
    if any(part.endswith((".", " "))
           or re.match(r"^(?:CON|PRN|AUX|NUL|COM[1-9]|LPT[1-9])(?:\.|$)", part, re.IGNORECASE)
           for part in path.split("/")):
        return "DENY"
    if not isinstance(project_root, (str, os.PathLike)):
        return "UNVERIFIED"
    try:
        root = Path(project_root)
        if not root.is_absolute() or not root.is_dir():
            return "UNVERIFIED"
        candidate = root.joinpath(*path.split("/"))
        paths = [*reversed(root.parents), root]
        current = root
        for part in path.split("/"):
            current = current / part
            paths.append(current)
        for current in paths:
            info = current.lstat()
            if stat.S_ISLNK(info.st_mode) or getattr(info, "st_file_attributes", 0) & getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0x400):
                return "DENY"
        resolved = candidate.resolve(strict=True).relative_to(root.resolve(strict=True))
        if os.name == "nt" and os.path.normcase(str(resolved)) != os.path.normcase(str(Path(*path.split("/")))):
            return "DENY"
    except (OSError, RuntimeError, ValueError, TypeError):
        return "UNVERIFIED"
    return "PROVISIONAL_MATCH"


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
    """Aggregate reports without claiming that their evidence was verified."""
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
    return "REPORTED_PASS"
