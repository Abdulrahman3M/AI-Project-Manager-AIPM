"""Exercise Core's real GitHub attestation verifier against a CI-issued receipt."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "Core-Engine"))

from aipm_core.domain import CommandEnvelope, CoreEngine  # noqa: E402
from aipm_core.storage import initialize_project_state  # noqa: E402
from aipm_core.task_ops import TaskOperations  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--receipt", required=True, type=Path)
    parser.add_argument("--source-digest", required=True)
    parser.add_argument("--temp-root", required=True, type=Path)
    args = parser.parse_args()
    receipt = json.loads(args.receipt.read_text(encoding="utf-8-sig"))
    if receipt.get("task_id") != "Task-AIPM-Verified-Completion" or receipt.get("source_commit") != args.source_digest:
        raise SystemExit("CI receipt does not match the requested task and source commit")
    args.temp_root.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="aipm-verified-completion-", dir=args.temp_root) as temporary:
        project = initialize_project_state(Path(temporary) / "managed-project", "managed", "Managed Project")
        engine = CoreEngine({"managed": project})
        ops = TaskOperations(engine, project)
        task_id = receipt["task_id"]
        create = CommandEnvelope("attested-task-create", "task.create", "ci-attestation-test", "managed", 0, "attested-task-create", {
            "task_id": task_id, "title": "Verified Completion Attestation", "scope": "Validate an authentic CI-signed test result."
        })
        if engine.execute(create).get("status") != "PASS":
            raise SystemExit("Core could not create the isolated attestation test task")
        task = project.state_root / "Operations" / "Tasks" / task_id
        ops.write_artifact(task, "References/Completion-Receipt.json", args.receipt.read_bytes())
        state = ops._request("state.read", {})
        ops._request("state.record-git-observation", {
            "branch": "ci-attestation", "head_sha": args.source_digest,
            "diff_fingerprint": hashlib.sha256(args.receipt.read_bytes()).hexdigest(),
        }, revision=state["revision"], mutation=True)
        ops.verify(task, "PASS", "GitHub Actions signed the passing full-suite result.", attestation={
            "receipt": "References/Completion-Receipt.json", "source_digest": args.source_digest,
        })
        ops.report(task, "The task/source-bound test attestation was cryptographically verified by AIPM Core.")
        final = ops.status(task)
        if final.get("status") != "COMPLETE":
            raise SystemExit("Core rejected a valid signed task/source-bound attestation")
        print(json.dumps({"status": "PASS", "task_id": task_id, "source_digest": args.source_digest,
                          "core_status": final["status"], "tests_run": receipt["tests_run"]}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
