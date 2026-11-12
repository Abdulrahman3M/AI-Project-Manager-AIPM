"""Verify externally issued test-result attestations; this module never runs tests."""
from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import subprocess
import stat
from pathlib import Path
from typing import Any, Callable

TRUSTED_REPOSITORY = "Abdulrahman3M/AI-Project-Manager-AIPM"
TRUSTED_WORKFLOW = "github.com/Abdulrahman3M/AI-Project-Manager-AIPM/.github/workflows/verified-completion.yml"
PREDICATE_TYPE = "https://aipm.dev/attestations/verified-completion/v1"
TEST_SUITE = "AIPM-Python-Unittest-Discover"
TEST_COMMAND = "python -m unittest discover -s Tests -p test_*.py -v && pwsh -NoProfile -File TUI/AI-Project-Manager/tests/Run-Tests.ps1"
RECEIPT_RELATIVE_PATH = "References/Completion-Receipt.json"
_TASK_ID = re.compile(r"Task-[A-Za-z0-9][A-Za-z0-9_-]{0,159}\Z")
_SOURCE_DIGEST = re.compile(r"[0-9a-f]{40}\Z")


class AttestationError(ValueError):
    """The test-result attestation is missing, invalid, or untrusted."""


def _trusted_gh_cli() -> str:
    candidate = shutil.which("gh")
    if not candidate:
        raise AttestationError("GitHub CLI Is Not Available; Result Is UNVERIFIED")
    executable = Path(candidate).resolve(strict=True)
    if os.name == "nt":
        powershell = shutil.which("pwsh.exe") or shutil.which("pwsh") or shutil.which("powershell.exe") or shutil.which("powershell")
        if not powershell:
            raise AttestationError("Windows Signature Verification Is Not Available")
        env = os.environ.copy()
        env["AIPM_GH_SIGNATURE_TARGET"] = str(executable)
        script = "$s=Get-AuthenticodeSignature -LiteralPath $env:AIPM_GH_SIGNATURE_TARGET; if ($s.Status -ne 'Valid' -or $s.SignerCertificate.Subject -notmatch 'CN=\"GitHub, Inc.\"') { exit 1 }; exit 0"
        try:
            signed = subprocess.run([powershell, "-NoProfile", "-NonInteractive", "-Command", script],
                                    capture_output=True, text=True, timeout=15, check=False, shell=False, env=env)
        except (OSError, subprocess.SubprocessError) as error:
            raise AttestationError("GitHub CLI Authenticode Signature Could Not Be Checked") from error
        if signed.returncode != 0:
            raise AttestationError("GitHub CLI Is Not Authenticode-Signed By GitHub, Inc.")
    elif os.name == "posix":
        metadata = executable.stat()
        if metadata.st_uid != 0 or metadata.st_mode & (stat.S_IWGRP | stat.S_IWOTH):
            raise AttestationError("GitHub CLI Is Not Installed In A Root-Controlled, Read-Only Location")
    else:
        raise AttestationError("GitHub CLI Trust Cannot Be Established On This Platform")
    return str(executable)


def verify_completion_attestation(
    subject_path: Path,
    *,
    task_id: str,
    source_digest: str,
    run: Callable[..., Any] = subprocess.run,
) -> dict[str, Any]:
    """Cryptographically verify a GitHub Actions attestation and its bound test receipt."""
    if not isinstance(task_id, str) or not _TASK_ID.fullmatch(task_id):
        raise AttestationError("Invalid Task Identity")
    if not isinstance(source_digest, str) or not _SOURCE_DIGEST.fullmatch(source_digest):
        raise AttestationError("Invalid Source Digest")
    artifact = Path(subject_path)
    if artifact.is_symlink() or not artifact.is_file():
        raise AttestationError("Attested Test Receipt Is Missing Or Linked")
    gh = _trusted_gh_cli()
    command = [
        gh, "attestation", "verify", str(artifact),
        "--repo", TRUSTED_REPOSITORY,
        "--signer-workflow", TRUSTED_WORKFLOW,
        "--source-digest", source_digest,
        "--signer-digest", source_digest,
        "--predicate-type", PREDICATE_TYPE,
        "--format", "json",
    ]
    try:
        completed = run(command, capture_output=True, text=True, timeout=60, check=False, shell=False)
    except (OSError, subprocess.SubprocessError) as error:
        raise AttestationError("Attestation Verification Could Not Be Completed") from error
    if completed.returncode != 0:
        raise AttestationError("Attestation Signature Or Trusted Identity Was Rejected")
    try:
        verified = json.loads(completed.stdout)
    except (TypeError, json.JSONDecodeError) as error:
        raise AttestationError("GitHub CLI Returned Invalid Verification Data") from error
    if not isinstance(verified, list) or not verified:
        raise AttestationError("No Verified Attestation Was Returned")
    digest = hashlib.sha256(artifact.read_bytes()).hexdigest()
    for item in verified:
        result = item.get("verificationResult") if isinstance(item, dict) else None
        statement = result.get("statement") if isinstance(result, dict) else None
        if not isinstance(statement, dict) or statement.get("predicateType") != PREDICATE_TYPE:
            continue
        subjects = statement.get("subject")
        if not isinstance(subjects, list) or not any(
            isinstance(subject, dict)
            and isinstance(subject.get("digest"), dict)
            and subject["digest"].get("sha256") == digest
            for subject in subjects
        ):
            continue
        predicate = statement.get("predicate")
        if not isinstance(predicate, dict):
            continue
        if (
            predicate.get("task_id") == task_id
            and predicate.get("source_commit") == source_digest
            and predicate.get("test_suite") == TEST_SUITE
            and predicate.get("test_command") == TEST_COMMAND
            and predicate.get("result") == "PASS"
            and type(predicate.get("tests_run")) is int
            and predicate["tests_run"] > 0
            and type(predicate.get("failures")) is int
            and predicate["failures"] == 0
            and type(predicate.get("python_skipped")) is int
            and predicate["python_skipped"] >= 0
            and type(predicate.get("powershell_tests_run")) is int
            and predicate["powershell_tests_run"] > 0
            and type(predicate.get("powershell_failures")) is int
            and predicate["powershell_failures"] == 0
            and type(predicate.get("powershell_unverified")) is int
            and predicate["powershell_unverified"] == 0
        ):
            return {"result": "PASS", "task_id": task_id, "source_digest": source_digest,
                    "subject_sha256": digest, "test_suite": TEST_SUITE,
                    "tests_run": predicate["tests_run"], "failures": 0,
                    "signer_workflow": TRUSTED_WORKFLOW}
    raise AttestationError("Verified Attestation Does Not Match This Task, Source, Or Test Result")
