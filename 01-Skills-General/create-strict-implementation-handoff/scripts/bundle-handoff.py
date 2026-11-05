#!/usr/bin/env python3
"""Make a portable handoff ZIP and SHA-256 manifest, with no network/dependencies.

Usage: python bundle-handoff.py /path/to/handoff-directory /path/to/output.zip
Does not modify source files. The ZIP must be outside the source. Missing
standard tools, their test resources and the guide are included from this
helper's installation. Symlinks are forbidden to avoid leakage.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import sys
from zipfile import ZipFile, ZIP_DEFLATED

BANNED_NAMES = {'.env', '.git', '.ssh', 'id_rsa', 'credentials.json', 'secrets.json'}


def build(source: Path, destination: Path) -> dict:
    source = source.resolve()
    destination = destination.absolute()
    if destination.is_symlink():
        raise ValueError('Destination is a symlink.')
    destination = destination.resolve()
    if not source.is_dir():
        raise ValueError(f'Not a source directory: {source}')
    if destination == source or source in destination.parents:
        raise ValueError('Destination must be outside the source directory.')
    if destination.exists():
        raise ValueError(f'Destination already exists; choose a new output path: {destination}')
    paths = []
    for p in sorted(source.rglob('*')):
        if p.is_symlink():
            raise ValueError(f'Symlinks are not permitted in a handoff bundle: {p}')
        if not p.is_file() or p.resolve() == destination:
            continue
        rel = p.relative_to(source)
        if '__pycache__' in rel.parts or p.suffix.lower() == '.pyc':
            continue  # python-generated caches are neither task inputs nor distributable artifacts
        if any(n.lower() in BANNED_NAMES for n in rel.parts):
            raise ValueError(f'Potentially sensitive/internal file refused: {rel}')
        if rel.as_posix() == 'HANDOFF-PACKAGE.json':
            continue  # regenerate manifest when re-packing an extracted bundle
        if p.suffix.lower() in ('.pyc', '.p12', '.pfx', '.pem', '.key'):
            raise ValueError(f'Unsafe generated/secret file type: {rel}')
        paths.append((p, rel.as_posix()))
    # Fill missing portable support files from the skill or an existing package.
    # Never replace a caller-supplied file silently.
    support_root = Path(__file__).resolve().parent.parent
    support = {
        'scripts/handoff-lint.py': support_root / 'scripts/handoff-lint.py',
        'scripts/bundle-handoff.py': support_root / 'scripts/bundle-handoff.py',
        'tests/test_handoff_tools.py': support_root / 'tests/test_handoff_tools.py',
        'tests/fixture-master.md': support_root / 'tests/fixture-master.md',
        'templates/OUTPUT-SMALL-SAMPLE.md': support_root / 'templates/OUTPUT-SMALL-SAMPLE.md',
        'HOW-TO-VALIDATE-AND-EXECUTE.md': support_root / 'references/HOW-TO-VALIDATE-AND-EXECUTE.md',
    }
    if not support['HOW-TO-VALIDATE-AND-EXECUTE.md'].is_file():
        support['HOW-TO-VALIDATE-AND-EXECUTE.md'] = support_root / 'HOW-TO-VALIDATE-AND-EXECUTE.md'
    existing = {name.casefold() for _, name in paths}
    for name, path in support.items():
        if name.casefold() not in existing:
            if not path.is_file() or path.is_symlink():
                raise ValueError(f'Missing safe support file: {path}')
            paths.append((path, name))
    required = ('IMPLEMENTATION-HANDOFF_', 'PHASE-', 'handoff-lint.py', 'bundle-handoff.py', 'test_handoff_tools.py', 'HOW-TO-VALIDATE-AND-EXECUTE.md')
    for token in required:
        if not any(token in n for _, n in paths):
            raise ValueError(f'Package missing required content: {token}')
    manifest = {'schema': 1, 'kind': 'offline-implementation-handoff', 'files': []}
    content = []
    for path, rel in paths:
        raw = path.read_bytes()
        content.append((rel, raw))
        manifest['files'].append({'path': rel, 'sha256': hashlib.sha256(raw).hexdigest(), 'bytes': len(raw)})
    destination.parent.mkdir(parents=True, exist_ok=True)
    with ZipFile(destination, 'x', compression=ZIP_DEFLATED) as z:
        for rel, raw in content:
            z.writestr(rel, raw)
        z.writestr('HANDOFF-PACKAGE.json', json.dumps(manifest, ensure_ascii=False, indent=2) + '\n')
    return manifest


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('source', type=Path)
    p.add_argument('zip_file', type=Path)
    args = p.parse_args(argv)
    try:
        manifest = build(args.source, args.zip_file)
        print(f'Created {args.zip_file}: {len(manifest["files"])} tracked files.')
        return 0
    except (OSError, ValueError) as exc:
        print('ERROR:', exc, file=sys.stderr)
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
