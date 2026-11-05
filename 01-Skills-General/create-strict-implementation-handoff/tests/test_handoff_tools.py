#!/usr/bin/env python3
"""Deterministic offline tests for the handoff checker and packager."""
from __future__ import annotations
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import tempfile
import unittest
from zipfile import ZipFile, ZIP_DEFLATED

ROOT = Path(__file__).resolve().parents[1]


def load_module(name: str, path: Path):
    import sys
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


LINT = load_module('strict_handoff_lint', ROOT / 'scripts' / 'handoff-lint.py')
BUNDLE = load_module('strict_handoff_bundle', ROOT / 'scripts' / 'bundle-handoff.py')
VALID = (ROOT / 'tests' / 'fixture-master.md').read_text(encoding='utf-8')


def codes(findings):
    return [f.code for f in findings]


class HandoffToolTests(unittest.TestCase):
    def test_ultra_master_valid(self):
        self.assertEqual([], [f for f in LINT.analyze_text(VALID, 'ultra') if f.severity == 'ERROR'])

    def test_missing_stage_fails(self):
        broken = VALID.replace('## Stage 04 — Preflight Verification', '## Preflight Verification', 1)
        self.assertIn('STAGES', codes(LINT.analyze_text(broken, 'ultra')))

    def test_profile_mismatch_fails(self):
        self.assertIn('MODE-MISMATCH', codes(LINT.analyze_text(VALID.replace('MODE: ULTRA-STRICT', 'MODE: STANDARD'), 'ultra')))

    def test_invalid_manifest_shape_fails(self):
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / 'invalid.zip'
            with ZipFile(path, 'w') as z:
                z.writestr('HANDOFF-PACKAGE.json', '[]')
            self.assertIn('PKG-SCHEMA', codes(LINT.verify_package(path)))

    def test_duplicate_requirement_fails(self):
        broken = VALID.replace('## Stage 02 — Solution Blueprint', '**REQ-001:** repeated artificial requirement\n\n## Stage 02 — Solution Blueprint', 1)
        self.assertIn('ID-DUPLICATE', codes(LINT.analyze_text(broken, 'ultra')))

    def test_unknown_requirement_reference_fails(self):
        broken = VALID.replace('**AC-001:**', '**AC-001:** REQ-999 ', 1)
        self.assertIn('ID-UNDECLARED', codes(LINT.analyze_text(broken, 'ultra')))

    def test_code_fence_does_not_create_definition(self):
        broken = VALID + '\n```md\n**REQ-001:** shown as an example\n```\n'
        self.assertNotIn('ID-DUPLICATE', codes(LINT.analyze_text(broken, 'ultra')))

    def test_quoted_example_does_not_create_definition(self):
        self.assertNotIn('ID-DUPLICATE', codes(LINT.analyze_text(VALID + '\n> **REQ-001:** example\n', 'ultra')))

    def test_utf8_arabic(self):
        content = VALID.replace('The inspected skill', 'المهارة الحالية التي فُحصت')
        self.assertEqual([], [f for f in LINT.analyze_text(content, 'ultra') if f.severity == 'ERROR'])

    def test_package_integrity(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d) / 'pack'
            root.mkdir()
            (root / 'IMPLEMENTATION-HANDOFF_Demo.md').write_text(VALID, encoding='utf-8')
            (root / 'PHASE-01.md').write_text('# Phase 01\n', encoding='utf-8')
            output = Path(d) / 'package.zip'
            manifest = BUNDLE.build(root, output)
            self.assertEqual(8, len(manifest['files']))
            self.assertEqual([], LINT.verify_package(output))
            corrupt = Path(d) / 'tampered.zip'
            with ZipFile(output) as z1, ZipFile(corrupt, 'w', ZIP_DEFLATED) as z2:
                for name in z1.namelist():
                    raw = z1.read(name)
                    if name == 'PHASE-01.md':
                        raw += b' unauthorized edit'
                    z2.writestr(name, raw)
            self.assertIn('PKG-HASH-MISMATCH', codes(LINT.verify_package(corrupt)))

    def test_package_unsafe_traversal(self):
        with tempfile.TemporaryDirectory() as d:
            evil = Path(d) / 'evil.zip'
            with ZipFile(evil, 'w', ZIP_DEFLATED) as z:
                z.writestr('../bad.md', 'danger')
                z.writestr('HANDOFF-PACKAGE.json', json.dumps({'schema': 1, 'files': []}))
            self.assertIn('PKG-UNSAFE-PATH', codes(LINT.verify_package(evil)))

    def test_missing_manifest_fails(self):
        with tempfile.TemporaryDirectory() as d:
            empty = Path(d) / 'bad.zip'
            with ZipFile(empty, 'w') as z:
                z.writestr('PHASE-01.md', 'example')
            self.assertIn('PKG-MANIFEST', codes(LINT.verify_package(empty)))

    def test_tool_error_on_missing_input(self):
        self.assertEqual(2, LINT.run([str(ROOT / 'does-not-exist.md')]))

    def test_template_has_six_stages(self):
        sample = (ROOT / 'templates' / 'OUTPUT-SMALL-SAMPLE.md').read_text(encoding='utf-8')
        errors = [x.code for x in LINT.analyze_text(sample, 'guided') if x.severity == 'ERROR']
        self.assertFalse(errors, f'Template errors: {errors}')


if __name__ == '__main__':
    unittest.main(verbosity=2)
