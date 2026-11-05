#!/usr/bin/env python3
"""Offline, read-only structural linter and ZIP integrity verifier for AI handoffs.

No third-party dependencies; Python 3.10+. Does NOT verify diagnosis, code or
actual test outcomes. Exit codes: 0=no blocking findings, 1=lint/integrity fails,
2=invalid invocation or I/O failure.

Examples:
  python handoff-lint.py IMPLEMENTATION-HANDOFF_Task.md --profile ultra
  python handoff-lint.py ./handoff-directory --profile guided --format json
  python handoff-lint.py --verify-package ./handoff.zip
"""
from __future__ import annotations

import argparse
from dataclasses import asdict, dataclass
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import sys
from zipfile import BadZipFile, ZipFile

STAGE_RE = re.compile(r'^\s{0,3}#{1,6}\s+(?:Stage|المرحلة)\s*0?([1-6])\b', re.I | re.M)
HEAD_RE = re.compile(r'^\s{0,3}#{1,6}\s+(.+)$', re.M)
META_RE = re.compile(r'^<!--\s*(HANDOFF-SPEC|MODE|PACKAGE-ROLE):\s*([^>]+?)\s*-->\s*$', re.M)
ID_RE = re.compile(r'\b(REQ|EVID|UNIT|TEST|AC|DEC)-(\d{3})\b')
DEF_RE = re.compile(
    r'^\s*(?:#{1,6}\s+|[-*+]\s+)?(?:\[[ xX]\]\s+)?'
    r'(?:\*\*)?(REQ|EVID|UNIT|TEST|AC|DEC)-(\d{3})(?:\*\*)?\s*(?:[:—–-])',
    re.M)
AC_RE = re.compile(r'^\s*[-*+]\s+\[[ xX]\]\s+(?:\*\*)?AC-\d{3}', re.M)
PLACEHOLDER_RE = re.compile(r'\b(?:TBD|FIXME|TODO\s*:|PLACEHOLDER\s*:)\b|\[(?:INSERT|WRITE|DESCRIBE|ADD)\b[^\]]{0,90}\]', re.I)

SECTION_PATTERNS = {
    'OBJECTIVE': r'objective|الهدف|مرحلة.*الهدف',
    'SCOPE': r'scope|نطاق|non.negotiable.*preservation|source.of.truth',
    'PRESERVE': r'preserv|prohibited|الحفاظ|ممنوع|قواعد الحماية',
    'ACCEPT': r'acceptance criteria|معايير القبول',
    'STOP': r'stop and escalate|decision tree|deterministic decision|التوقف|التصعيد',
    'FINAL': r'final report|completion report|final reporting|التقرير الختامي|التقرير النهائي',
}

@dataclass(frozen=True)
class Finding:
    severity: str
    code: str
    message: str
    line: int | None = None


def line_number(content: str, position: int) -> int:
    return content.count('\n', 0, position) + 1


def mask_code_fences(raw: str) -> str:
    """Ignore examples inside fenced code to avoid counting them as real definitions."""
    out = []
    fence = None
    for line in raw.splitlines(keepends=True):
        match = re.match(r'^\s{0,3}(`{3,}|~{3,})', line)
        if match:
            token = match.group(1)
            if fence is None:
                fence = token
            elif token[0] == fence[0] and len(token) >= len(fence):
                fence = None
            out.append('\n' if line.endswith('\n') else '')
        elif not fence and re.match(r'^\s{0,3}>', line):
            out.append('\n' if line.endswith('\n') else '')
        else:
            if fence:
                out.append('\n' if line.endswith('\n') else '')
            else:
                out.append(line)
    return ''.join(out)


def analyze_text(raw: str, profile: str = 'guided', filename: str = '') -> list[Finding]:
    findings: list[Finding] = []
    text = mask_code_fences(raw)
    metadata = {k: v.strip() for k, v in META_RE.findall(text)}
    role = metadata.get('PACKAGE-ROLE', 'MASTER').upper()
    headings = [re.sub(r'[`*_]', '', h).lower() for h in HEAD_RE.findall(text)]
    stages = [(int(m.group(1)), line_number(text, m.start())) for m in STAGE_RE.finditer(text)]

    if len(text.strip()) < 350:
        findings.append(Finding('ERROR', 'DOC-SHORT', 'Document is too short to function as an independent handoff.'))
    if metadata.get('HANDOFF-SPEC') != '1':
        findings.append(Finding('WARNING', 'SPEC-META', 'Missing <!-- HANDOFF-SPEC: 1 --> metadata comment.'))
    mode = metadata.get('MODE', '').upper()
    if mode not in ('GUIDED', 'ULTRA', 'ULTRA-STRICT', 'STANDARD'):
        findings.append(Finding('ERROR', 'MODE-META', 'Missing or unrecognized MODE metadata.'))
    elif {'STANDARD': 0, 'GUIDED': 1, 'ULTRA': 2, 'ULTRA-STRICT': 2}[mode] < {'standard': 0, 'guided': 1, 'ultra': 2}[profile]:
        findings.append(Finding('ERROR', 'MODE-MISMATCH', f'Document mode {mode} is weaker than requested {profile}.'))
    if [n for n, _ in stages] != [1, 2, 3, 4, 5, 6]:
        findings.append(Finding('ERROR', 'STAGES', 'Expected six distinct Stage 01..06 headings in this exact order; found ' + repr([n for n, _ in stages]) + '.'))

    combined_headings = '\n'.join(headings)
    for section, pattern in SECTION_PATTERNS.items():
        if role == 'PHASE' and section in ('OBJECTIVE', 'SCOPE'):
            # Phase files have objective and scope in their lead metadata or stages.
            continue
        if not re.search(pattern, combined_headings, re.I):
            severity = 'WARNING' if role == 'PHASE' and section == 'PRESERVE' else 'ERROR'
            findings.append(Finding(severity, 'SECTION-' + section, 'Missing heading for: ' + section + '.'))
    if not re.search(r'AGENTS\.md|agent.instructions|agent instruction|تعليمات الوكلاء', text, re.I):
        findings.append(Finding('WARNING' if role == 'PHASE' else 'ERROR', 'AGENT-RULES', 'No explicit instruction to inspect applicable agent rules.'))
    if not re.search(r'PASS\s*/\s*FAIL\s*/\s*UNVERIFIED', text, re.I):
        findings.append(Finding('ERROR' if role == 'MASTER' else 'WARNING', 'TEST-STATUS', 'Require PASS / FAIL / UNVERIFIED reporting.'))
    if not re.search(r'COMPLETE\b', text) or not re.search(r'BLOCKED\b', text):
        findings.append(Finding('ERROR', 'FINAL-STATUS', 'Include completion and blocked status meanings.'))
    if not re.search(r'stop|block|escalat|توقف|أوقف|تصعيد', text, re.I):
        findings.append(Finding('ERROR', 'STOP-RULE', 'Missing stop/escalation behavior.'))
    if not re.search(r'preserv|do not|ممنوع|الحفاظ|لا تغي', text, re.I):
        findings.append(Finding('ERROR', 'MUST-PRESERVE', 'Explicit preservation and prohibited-change requirements missing.'))
    if not re.search(r'\btest|الاختبار|verification|التحقق', text, re.I):
        findings.append(Finding('ERROR', 'TEST-MISSING', 'No verification or test plan found.'))
    if not re.search(r'\[ \]', text):
        findings.append(Finding('WARNING', 'CHECKBOX', 'No unchecked acceptance checklist found.'))

    for m in list(PLACEHOLDER_RE.finditer(text))[:12]:
        findings.append(Finding('WARNING', 'PLACEHOLDER', 'Potential unresolved placeholder: ' + m.group(0)[:100], line_number(text, m.start())))

    definitions: dict[str, int] = {}
    for m in DEF_RE.finditer(text):
        token = m.group(1) + '-' + m.group(2)
        n = line_number(text, m.start())
        if token in definitions:
            findings.append(Finding('ERROR', 'ID-DUPLICATE', f'{token} already defined on line {definitions[token]}.', n))
        definitions[token] = n

    if role == 'MASTER':
        for kind in ('REQ', 'EVID', 'UNIT', 'TEST', 'AC', 'DEC'):
            if not any(k.startswith(kind + '-') for k in definitions):
                level = 'ERROR' if profile == 'ultra' and kind in ('REQ', 'UNIT', 'TEST', 'AC') else 'WARNING'
                findings.append(Finding(level, 'ID-MISSING-' + kind, f'Missing {kind}-### definitions.'))
        # Prevent phantom trace IDs in master; ranges such as REQ-001–003 are not expanded.
        for m in ID_RE.finditer(text):
            token = m.group(0)
            if token not in definitions:
                findings.append(Finding('ERROR' if profile == 'ultra' else 'WARNING', 'ID-UNDECLARED', f'{token} is referenced but not declared.', line_number(text, m.start())))
        for m in re.finditer(r'^\s*[-*]\s+\[[ xX]\]\s+(?:\*\*)?(AC-\d{3}).*$', text, re.M):
            row = m.group(0)
            if not re.search(r'\bREQ-\d{3}\b', row) or not re.search(r'\bTEST-\d{3}\b', row):
                findings.append(Finding('ERROR' if profile == 'ultra' else 'WARNING', 'AC-TRACE', f'{m.group(1)} should reference a requirement and a test.', line_number(text, m.start())))
        if profile in ('guided', 'ultra') and not AC_RE.search(text):
            findings.append(Finding('ERROR', 'AC-ID', 'Use numbered - [ ] **AC-###:** acceptance criteria.'))
        if profile == 'ultra' and not re.search(r'\bHEAD\b|snapshot|baseline|بصمة', text, re.I):
            findings.append(Finding('ERROR', 'SNAPSHOT', 'Missing repository snapshot/baseline preflight guidance.'))
    else:
        if profile in ('guided', 'ultra') and not re.search(r'P\d{2}-(?:STEP|CHECK|GATE)-\d{3}', text):
            findings.append(Finding('ERROR', 'PHASE-UNITS', 'Phase lacks explicit phase-scoped step/check/gate IDs.'))

    return _deduplicate(findings)


def _deduplicate(findings: list[Finding]) -> list[Finding]:
    unique = []
    seen = set()
    for f in findings:
        key = (f.severity, f.code, f.message, f.line)
        if key not in seen:
            seen.add(key)
            unique.append(f)
    return unique


def is_safe_member_name(name: str) -> bool:
    p = PurePosixPath(name)
    return bool(name and not name.startswith('/') and '\\' not in name
                and ':' not in name and all(part not in ('.', '..', '') for part in p.parts)
                and not name.endswith('/'))


def verify_package(path: Path) -> list[Finding]:
    findings: list[Finding] = []
    with ZipFile(path) as archive:
        names = archive.namelist()
        if len(names) != len(set(names)) or len({n.casefold() for n in names}) != len(names):
            findings.append(Finding('ERROR', 'PKG-DUPLICATE', 'ZIP contains duplicate/case-colliding member names.'))
        for n in names:
            if not n.endswith('/') and not is_safe_member_name(n):
                findings.append(Finding('ERROR', 'PKG-UNSAFE-PATH', f'Unsafe ZIP member: {n!r}'))
        manifest_name = 'HANDOFF-PACKAGE.json'
        if manifest_name not in names:
            return findings + [Finding('ERROR', 'PKG-MANIFEST', 'Missing root HANDOFF-PACKAGE.json.')]
        try:
            manifest = json.loads(archive.read(manifest_name).decode('utf-8'))
        except (json.JSONDecodeError, UnicodeError, KeyError) as exc:
            return findings + [Finding('ERROR', 'PKG-MANIFEST-INVALID', str(exc))]
        if not isinstance(manifest, dict) or manifest.get('schema') != 1 or not isinstance(manifest.get('files'), list):
            return findings + [Finding('ERROR', 'PKG-SCHEMA', 'Invalid manifest schema/files field.')]
        indexed = {}
        for item in manifest['files']:
            if not isinstance(item, dict) or not isinstance(item.get('path'), str) or not isinstance(item.get('sha256'), str):
                findings.append(Finding('ERROR', 'PKG-ENTRY', 'Manifest entry must have path and sha256 strings.'))
                continue
            n = item['path']
            if not is_safe_member_name(n) or n == manifest_name:
                findings.append(Finding('ERROR', 'PKG-ENTRY-PATH', f'Unsafe manifest path: {n!r}'))
                continue
            if n in indexed:
                findings.append(Finding('ERROR', 'PKG-ENTRY-DUP', f'Duplicate manifest path: {n}'))
            indexed[n] = item
            if not re.fullmatch(r'[0-9a-f]{64}', item['sha256']):
                findings.append(Finding('ERROR', 'PKG-SHA-FORMAT', f'Bad SHA-256 string for {n}'))
            elif n not in names:
                findings.append(Finding('ERROR', 'PKG-MISSING-FILE', f'Missing ZIP member: {n}'))
            elif hashlib.sha256(archive.read(n)).hexdigest() != item['sha256']:
                findings.append(Finding('ERROR', 'PKG-HASH-MISMATCH', f'Corrupted or changed member: {n}'))
        for n in names:
            if n.endswith('/') or n == manifest_name:
                continue
            if n not in indexed:
                findings.append(Finding('ERROR', 'PKG-UNTRACKED', f'ZIP member not listed in manifest: {n}'))
        required = ('IMPLEMENTATION-HANDOFF_', 'HOW-TO-VALIDATE-AND-EXECUTE.md', 'handoff-lint.py', 'bundle-handoff.py', 'test_handoff_tools.py', 'PHASE-')
        for r in required:
            if not any(PurePosixPath(n).name.startswith(r) for n in indexed):
                findings.append(Finding('ERROR', 'PKG-REQUIRED', f'Missing required package role/file: {r}'))
    return _deduplicate(findings)


def collect(paths: list[Path]) -> list[Path]:
    result = []
    for p in paths:
        if p.is_dir():
            result += sorted(f for f in p.rglob('*.md')
                             if f.name.startswith(('IMPLEMENTATION-HANDOFF_', 'PHASE-')))
        elif p.is_file() and p.suffix.lower() == '.md':
            result.append(p)
        else:
            raise ValueError(f'Input must be an existing MD file or directory: {p}')
    result = list(dict.fromkeys(p.resolve() for p in result))
    if not result:
        raise ValueError('No master/phase Markdown files found.')
    return result


def run(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('paths', nargs='*', type=Path, help='Handoff Markdown file(s) or directory')
    p.add_argument('--profile', choices=('standard', 'guided', 'ultra', 'ultra-strict'), default='guided')
    p.add_argument('--format', choices=('text', 'json'), default='text')
    p.add_argument('--fail-on-warning', action='store_true')
    p.add_argument('--verify-package', type=Path, help='Verify a bundled ZIP manifest and member hashes')
    args = p.parse_args(argv)
    if args.profile == 'ultra-strict':
        args.profile = 'ultra'
    if not args.paths and args.verify_package is None:
        p.error('Provide handoff paths and/or --verify-package ZIP.')
    reports = []
    try:
        for f in collect(args.paths) if args.paths else []:
            findings = analyze_text(f.read_text(encoding='utf-8-sig'), args.profile, f.name)
            reports.append({'target': str(f), 'findings': [asdict(x) for x in findings]})
        if args.verify_package is not None:
            findings = verify_package(args.verify_package)
            reports.append({'target': str(args.verify_package), 'findings': [asdict(x) for x in findings]})
    except (ValueError, OSError, UnicodeError, BadZipFile, json.JSONDecodeError) as exc:
        print(f'TOOL ERROR: {exc}', file=sys.stderr)
        return 2
    failures = sum(f['severity'] == 'ERROR' or (args.fail_on_warning and f['severity'] == 'WARNING')
                   for r in reports for f in r['findings'])
    warnings = sum(f['severity'] == 'WARNING' for r in reports for f in r['findings'])
    if args.format == 'json':
        print(json.dumps({'passed': not bool(failures), 'profile': args.profile, 'reports': reports}, ensure_ascii=False, indent=2))
    else:
        for r in reports:
            print('\nTarget:', r['target'])
            if not r['findings']:
                print('PASS: No applicable structural/integrity findings.')
            for f in r['findings']:
                print(f"{f['severity']:7} {f['code']}: {f['message']}" + (f" (line {f['line']})" if f['line'] else ''))
        print(f'\nGATE: {"FAIL" if failures else "PASS"}; warnings={warnings}; blocking_findings={failures}')
        print('Structural PASS does NOT prove semantic correctness, repository compatibility, or executed tests.')
    return 1 if failures else 0


if __name__ == '__main__':
    raise SystemExit(run())
