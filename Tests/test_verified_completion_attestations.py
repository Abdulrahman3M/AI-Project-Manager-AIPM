from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import sys
import tempfile
import unittest
from types import SimpleNamespace
from unittest.mock import Mock, patch

from test_support import CORE_ROOT
sys.path.insert(0, str(CORE_ROOT))
from aipm_core.attestations import (
    AttestationError, PREDICATE_TYPE, TEST_COMMAND, TEST_SUITE,
    TRUSTED_REPOSITORY, TRUSTED_WORKFLOW, _trusted_gh_cli, verify_completion_attestation,
)
from aipm_core.domain import CoreEngine
from aipm_core.storage import initialize_project_state
from aipm_core.task_ops import TaskOperations


class AttestationVerificationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory(dir=Path(__file__).resolve().parents[1] / 'Shared-Project-State-Manager/Test-Workspace')
        self.addCleanup(self.temp.cleanup)
        self.subject = Path(self.temp.name) / 'Completion-Receipt.json'
        self.subject.write_text('{"receipt":"test"}', encoding='utf-8')
        self.task_id = 'Task-Attested'
        self.source_digest = 'a' * 40

    def gh_output(self, **overrides: object) -> str:
        predicate = {
            'task_id': self.task_id, 'source_commit': self.source_digest,
            'test_suite': TEST_SUITE, 'test_command': TEST_COMMAND,
            'result': 'PASS', 'tests_run': 232, 'failures': 0, 'python_skipped': 8,
            'powershell_tests_run': 46, 'powershell_failures': 0, 'powershell_unverified': 0,
        }
        predicate.update(overrides)
        statement = {
            'predicateType': PREDICATE_TYPE,
            'subject': [{'name': self.subject.name, 'digest': {'sha256': hashlib.sha256(self.subject.read_bytes()).hexdigest()}}],
            'predicate': predicate,
        }
        return json.dumps([{'verificationResult': {'statement': statement}}])

    @unittest.skipUnless(os.name == 'nt', 'Authenticode validation is Windows-specific.')
    def test_installed_github_cli_has_valid_github_authenticode_signature(self) -> None:
        self.assertTrue(_trusted_gh_cli().lower().endswith('gh.exe'))

    def test_real_verifier_invokes_pinned_repository_workflow_and_accepts_bound_receipt(self) -> None:
        runner = Mock(return_value=SimpleNamespace(returncode=0, stdout=self.gh_output(), stderr=''))
        with patch('aipm_core.attestations._trusted_gh_cli', return_value='C:/Program Files/GitHub CLI/gh.exe'):
            result = verify_completion_attestation(self.subject, task_id=self.task_id, source_digest=self.source_digest, run=runner)
        self.assertEqual(result['result'], 'PASS')
        self.assertEqual(result['task_id'], self.task_id)
        self.assertEqual(result['source_digest'], self.source_digest)
        command = runner.call_args.args[0]
        self.assertIn('--repo', command)
        self.assertIn(TRUSTED_REPOSITORY, command)
        self.assertIn('--signer-workflow', command)
        self.assertIn(TRUSTED_WORKFLOW, command)
        self.assertIn('--source-digest', command)
        self.assertIn('--signer-digest', command)
        self.assertEqual(runner.call_args.kwargs['shell'], False)

    def test_untrusted_cli_result_or_mismatched_task_source_fails_closed(self) -> None:
        cases = (
            {'task_id': 'Task-Other'}, {'source_commit': 'b' * 40},
            {'result': 'UNVERIFIED'}, {'failures': 1},
            {'tests_run': 0}, {'test_suite': 'unapproved-suite'},
        )
        for override in cases:
            with self.subTest(override=override), patch('aipm_core.attestations._trusted_gh_cli', return_value='gh'):
                runner = lambda command, **kwargs: SimpleNamespace(returncode=0, stdout=self.gh_output(**override), stderr='')
                with self.assertRaises(AttestationError):
                    verify_completion_attestation(self.subject, task_id=self.task_id, source_digest=self.source_digest, run=runner)

    def test_signature_rejection_missing_cli_link_and_invalid_binding_are_unverified(self) -> None:
        with patch('aipm_core.attestations._trusted_gh_cli', return_value='gh'):
            with self.assertRaises(AttestationError):
                verify_completion_attestation(self.subject, task_id=self.task_id, source_digest=self.source_digest,
                                              run=lambda *args, **kwargs: SimpleNamespace(returncode=1, stdout='', stderr='bad signature'))
            with self.assertRaises(AttestationError):
                verify_completion_attestation(self.subject, task_id='invalid-task-id', source_digest=self.source_digest,
                                              run=lambda *args, **kwargs: self.fail('Invalid task IDs must not invoke the verifier'))
        with patch('aipm_core.attestations._trusted_gh_cli', side_effect=AttestationError('GitHub CLI Is Not Available; Result Is UNVERIFIED')):
            with self.assertRaisesRegex(AttestationError, 'UNVERIFIED'):
                verify_completion_attestation(self.subject, task_id=self.task_id, source_digest=self.source_digest)

    def test_core_keeps_fabricated_attestation_unverified_but_accepts_verifier_approved_receipt(self) -> None:
        project = initialize_project_state(Path(self.temp.name) / 'Managed', 'managed', 'Managed')
        ops = TaskOperations(CoreEngine({'managed': project}), project)
        revision = ops._request('state.read', {})['revision']
        ops._request('state.record-git-observation', {
            'branch': 'main', 'head_sha': self.source_digest, 'diff_fingerprint': 'b' * 64,
        }, revision=revision, mutation=True)
        task = ops.create('Attested', 'Only verified CI results may complete this task.')
        receipt = task / 'References' / 'Completion-Receipt.json'
        receipt.parent.mkdir(parents=True, exist_ok=True)
        receipt.write_text(json.dumps({
            'task_id': task.name, 'source_commit': self.source_digest,
            'test_suite': TEST_SUITE, 'test_command': TEST_COMMAND,
            'result': 'PASS', 'tests_run': 232, 'failures': 0, 'python_skipped': 8,
            'powershell_tests_run': 46, 'powershell_failures': 0, 'powershell_unverified': 0,
        }), encoding='utf-8')
        attestation = {'receipt': 'References/Completion-Receipt.json', 'source_digest': self.source_digest}
        ops.verify(task, 'PASS', 'CI receipt', attestation=attestation)
        ops.report(task, 'CI verified the task and source-bound test result.')
        with patch('aipm_core.domain.verify_completion_attestation', side_effect=AttestationError('Invalid signature')):
            self.assertEqual(ops.status(task)['status'], 'UNVERIFIED')
        with patch('aipm_core.domain.verify_completion_attestation', return_value={'result': 'PASS'}) as verifier:
            result = ops.status(task)
            self.assertEqual(verifier.call_count, 1, ops.read_task(task))
            self.assertEqual(result['status'], 'COMPLETE', verifier.call_args)
        self.assertEqual(ops.status(task)['status'], 'UNVERIFIED')


if __name__ == '__main__':
    unittest.main()
