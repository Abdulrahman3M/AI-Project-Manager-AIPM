#!/usr/bin/env python3
"""FIRG: local, non-destructive fix registry and incoming change checks."""
import argparse
import datetime as dt
import fnmatch
import json
import os
from pathlib import Path
import re
import stat
import subprocess
import sys
from zoneinfo import ZoneInfo
from uuid import uuid4

ROOT = Path(__file__).resolve().parents[2]
FIRG = ROOT / 'FIRG'
REG = FIRG / 'registry'
LEDGER = FIRG / 'FIX-HISTORY.md'
ID = re.compile(r'^(\d{4}\.\d{2}\.\d{2})-(0[1-9]|[1-9]\d+)$')
HEADER = '# FIRG — Master Fix History\n\n> Primary human-readable fix ledger. Generated from `registry/*.json`.\n> Edit the structured record and run `firg sync`; do not edit this generated ledger directly.\n> Dates: YYYY.MM.DD; chronological order: oldest to newest.\n'

class Error(Exception): pass


def temporary_file(directory, prefix):
    """Create an exclusive staging file with inherited directory permissions."""
    for _ in range(10):
        name = str(directory / (prefix + uuid4().hex + '.tmp'))
        try:
            fd = os.open(name, os.O_CREAT | os.O_EXCL | os.O_RDWR | getattr(os, 'O_BINARY', 0), 0o666)
            return fd, name
        except FileExistsError:
            continue
    raise Error('could not allocate a unique staging file')

def pairs(values):
    result = {}
    for k, v in values:
        if k in result: raise Error('duplicate JSON key: ' + k)
        result[k] = v
    return result

def load(path):
    try: return json.loads(path.read_text(encoding='utf-8'), object_pairs_hook=pairs)
    except (OSError, ValueError) as e: raise Error(f'{path}: {e}') from e

def git(*args):
    p = subprocess.run(['git', '-C', str(ROOT), *args], capture_output=True, text=True, encoding='utf-8', errors='replace')
    if p.returncode: raise Error('git: ' + p.stderr.strip())
    return p.stdout


def require_git():
    """FIRG operates only at the root of a usable Git working tree."""
    top = git('rev-parse', '--show-toplevel').strip()
    if not top or Path(top).resolve() != ROOT.resolve():
        raise Error('FIRG requires a Git repository rooted at the project directory')

def date(value):
    try:
        if not isinstance(value, str) or not re.fullmatch(r'\d{4}\.\d{2}\.\d{2}', value): raise ValueError()
        return dt.datetime.strptime(value, '%Y.%m.%d').date()
    except ValueError: raise Error(f'invalid date: {value}')

def ident(value):
    m = ID.fullmatch(value) if isinstance(value, str) else None
    if not m: raise Error(f'invalid ID: {value}')
    date(m.group(1)); return (m.group(1), int(m.group(2)))

def nonempty(value, name):
    if not isinstance(value, str) or not value.strip(): raise Error(f'{name}: nonempty string required')

def config():
    c = load(FIRG / 'config.json')
    if not isinstance(c, dict) or c.get('schema_version') != 1: raise Error('invalid config version')
    try:
        if c['timezone'] != 'UTC': ZoneInfo(c['timezone'])
    except Exception as e: raise Error(f'invalid timezone: {e}') from e
    for field in ('functional_include','functional_exclude','broader_tests'):
        if not isinstance(c.get(field), list) or any(not isinstance(x, str) or not x for x in c[field]): raise Error('invalid config: '+field)
    if not c['functional_include']: raise Error('functional include patterns are empty')
    return c

def check_test(t):
    if not isinstance(t, dict): raise Error('test must be an object')
    for k in ('name','command_or_reference','evidence'): nonempty(t.get(k), 'test.'+k)
    if t.get('result') not in ('PASS','FAIL','UNVERIFIED'): raise Error('invalid test result')

def check_record(r, filename=None):
    if not isinstance(r, dict): raise Error('record must be an object')
    required = ('schema_version','id','title','issue_date','issue_date_known','recorded_at','updated_at','source','commits','problem','affected_components','expected_behavior','implementation_summary','tests','status','related_fix_ids','native_history_refs','review_reference')
    if any(k not in r for k in required): raise Error('missing fields: '+', '.join(k for k in required if k not in r))
    if r['schema_version'] != 1: raise Error('unsupported record schema')
    ident(r['id'])
    if filename and filename != r['id']+'.json': raise Error('filename and ID mismatch: '+filename)
    date(r['issue_date'])
    if type(r['issue_date_known']) is not bool: raise Error('issue_date_known must be boolean')
    for k in ('recorded_at','updated_at'):
        try:
            timestamp = dt.datetime.fromisoformat(r[k].replace('Z','+00:00'))
            if timestamp.utcoffset() is None: raise ValueError()
        except (ValueError, TypeError, AttributeError): raise Error('invalid timezone-aware timestamp: '+k)
    for k in ('title','problem','expected_behavior','implementation_summary'): nonempty(r[k],k)
    s=r['source']
    if not isinstance(s,dict) or s.get('kind') not in ('local','upstream','third_party'): raise Error('invalid source')
    nonempty(s.get('person_or_team'),'source.person_or_team')
    for k in ('repository_or_provider','issue_or_pr_reference'):
        if k not in s or (s[k] is not None and (not isinstance(s[k],str) or not s[k].strip())): raise Error('invalid source.'+k)
    for k in ('commits','affected_components','related_fix_ids','native_history_refs'):
        if not isinstance(r[k],list) or any(not isinstance(x,str) or not x.strip() for x in r[k]): raise Error('invalid list: '+k)
    if not r['affected_components']: raise Error('affected_components is empty')
    for sha in r['commits']:
        if not re.fullmatch(r'[0-9a-f]{40}|[0-9a-f]{64}',sha): raise Error('commit must be a full SHA')
        if git('rev-parse','--verify',sha+'^{commit}').strip()!=sha: raise Error('unverified commit: '+sha)
    if not r['commits']:
        nonempty(s.get('issue_or_pr_reference'),'immutable source reference')
        nonempty(r.get('provenance_reason'),'provenance_reason')
    if not isinstance(r['tests'],list) or not r['tests']: raise Error('tests required, including unavailable evidence')
    for t in r['tests']: check_test(t)
    if r['status'] not in ('active','superseded','reverted'): raise Error('invalid status')
    if r['status'] != 'active':
        nonempty(r.get('transition_rationale'),'transition_rationale')
        if not r['related_fix_ids'] and not r.get('transition_reference'): raise Error('transition reference required')
    if r['review_reference'] is not None and not isinstance(r['review_reference'],str): raise Error('invalid review reference')
    if 'report_reference' in r and r['report_reference'] != 'reports/' + r['id'] + '.md': raise Error('invalid report reference')

def records():
    out=[]; seen=set()
    for path in sorted(REG.glob('*.json')) if REG.exists() else []:
        try:
            r=load(path); check_record(r,path.name)
            if r.get('report_reference') and not (FIRG / r['report_reference']).is_file(): raise Error('missing linked report')
            if r['id'] in seen: raise Error('duplicate ID '+r['id'])
            seen.add(r['id']);out.append(r)
        except Error as e: raise Error(f'{path}: {e}') from e
    for r in out:
        for ref in r['related_fix_ids']:
            ident(ref)
            if ref not in seen: raise Error(r['id']+': broken related fix reference '+ref)
    return sorted(out,key=lambda r:ident(r['id']))


def atomic_create_record(path, record):
    """Publish a complete JSON file without overwriting an existing record."""
    REG.mkdir(exist_ok=True)
    if REG.is_symlink() or not REG.resolve().is_relative_to(FIRG.resolve()) or path.parent != REG:
        raise Error('registry path is unsafe')
    state_scratch = ROOT / 'Shared-Project-State-Manager' / 'Temporary-Files'
    if state_scratch.is_dir() and (state_scratch.is_symlink() or not state_scratch.resolve().is_relative_to(ROOT.resolve())):
        raise Error('temporary workspace is outside the project')
    scratch = state_scratch if state_scratch.is_dir() else REG
    fd, temporary = temporary_file(scratch, '.firg-record-')
    try:
        with os.fdopen(fd, 'w', encoding='utf-8', newline='\n') as out:
            json.dump(record, out, ensure_ascii=False, indent=2)
            out.write('\n'); out.flush(); os.fsync(out.fileno())
        # A hard link publishes the complete bytes atomically and fails on collision.
        # If the filesystem cannot support it, fail without creating a partial record.
        try:
            os.link(temporary, path)
        except PermissionError:
            if os.name != 'nt':
                raise
            # Windows rename fails when the destination already exists and is atomic
            # on the same volume. Some sandboxes deny hard-link creation.
            os.rename(temporary, path)
    finally:
        if os.path.exists(temporary): os.unlink(temporary)

def render(rs):
    text=HEADER+'\n'
    if not rs: return text+'No verified fixes registered yet.\n'
    for r in rs:
        s=r['source']; tests='; '.join(t['name']+' ('+t['result']+')' for t in r['tests'])
        source='; '.join(str(x) for x in (s['kind'],s['person_or_team'],s['repository_or_provider'],s['issue_or_pr_reference']) if x)
        review=('; '+r['review_reference']) if r['review_reference'] else ''
        if r.get('report_reference'): review += '; [report](' + r['report_reference'] + ')'
        text+=f"## {r['id']} — {r['title']}\n- **Issue date:** {r['issue_date']} ({'verified' if r['issue_date_known'] else 'registration fallback'})\n- **Source:** {source}\n- **Git commit(s):** {', '.join(r['commits']) if r['commits'] else 'Unavailable: '+r['provenance_reason']}\n- **Problem:** {r['problem']}\n- **Affected components:** {', '.join(r['affected_components'])}\n- **Expected behavior / changes:** {r['expected_behavior']} {r['implementation_summary']}\n- **Tests:** {tests}\n- **Status:** {r['status']}\n- **Record / review:** [record](registry/{r['id']}.json){review}\n\n"
    return text


def replace_generated(source, target):
    """Replace an existing ledger while preserving its access controls."""
    if not target.exists():
        os.replace(source, target)
    elif os.name == 'nt':
        import ctypes
        from ctypes import wintypes
        kernel = ctypes.WinDLL('kernel32', use_last_error=True)
        replace = kernel.ReplaceFileW
        replace.argtypes = [wintypes.LPCWSTR, wintypes.LPCWSTR, wintypes.LPCWSTR,
                            wintypes.DWORD, wintypes.LPVOID, wintypes.LPVOID]
        replace.restype = wintypes.BOOL
        if not replace(str(target), str(source), None, 0, None, None):
            raise ctypes.WinError(ctypes.get_last_error())
    else:
        info = target.stat()
        source_info = os.stat(source)
        if (source_info.st_uid, source_info.st_gid) != (info.st_uid, info.st_gid):
            os.chown(source, info.st_uid, info.st_gid)
        os.chmod(source, stat.S_IMODE(info.st_mode))
        if hasattr(os, 'listxattr'):
            for name in os.listxattr(target):
                os.setxattr(source, name, os.getxattr(target, name))
        os.replace(source, target)

def sync(check=False):
    expected=render(records())
    if LEDGER.is_symlink() or not LEDGER.resolve().is_relative_to(FIRG.resolve()): raise Error('ledger path is unsafe')
    if check:
        if not LEDGER.exists() or LEDGER.read_text(encoding='utf-8') != expected: raise Error('ledger missing or stale; run sync')
    else:
        # Atomic replacement in the destination directory.
        fd, name=temporary_file(FIRG, '.firg-')
        try:
            with os.fdopen(fd,'w',encoding='utf-8',newline='\n') as f: f.write(expected)
            replace_generated(name,LEDGER)
        finally:
            if os.path.exists(name): os.unlink(name)

def validate():
    config(); load(FIRG/'schemas/fix-record.schema.json')
    for name in ('AGENTS.md','README.md','policies/INTEGRATION.md','tools/firg.py','tests/test_firg.py'):
        if not (FIRG/name).is_file(): raise Error('missing required file: '+name)
    if not (ROOT/'AGENTS.md').is_file(): raise Error('missing root AGENTS.md')
    sync(True)

def resolve(ref):
    if not ref or ref.startswith('-') or '\x00' in ref: raise Error('invalid Git reference')
    result=git('rev-parse','--verify',ref+'^{commit}').strip()
    if not re.fullmatch(r'[0-9a-f]{40}|[0-9a-f]{64}',result): raise Error('invalid resolved reference')
    return result

def changes(base,head):
    b,h=resolve(base),resolve(head)
    raw=git('diff','--name-status','-z','--find-renames',b,h,'--').split('\0'); paths=[]; i=0
    while i < len(raw) and raw[i]:
        kind=raw[i]; i+=1
        count=2 if kind.startswith(('R','C')) else 1
        paths.extend(raw[i:i+count]);i+=count
    return b,h,paths

def overlap(path,component):
    c=component.replace('\\','/').rstrip('/')
    return path==c or path.startswith(c+'/') or fnmatch.fnmatchcase(path,c)

def impact(paths,rs):
    ids={r['id'] for r in rs if any(overlap(p,c) for p in paths for c in r['affected_components'])}
    while True:
        expanded=ids|{r['id'] for r in rs if r['id'] in ids or any(x in ids for x in r['related_fix_ids'])}|{x for r in rs if r['id'] in ids for x in r['related_fix_ids']}
        if expanded==ids: break
        ids=expanded
    return [r for r in rs if r['id'] in ids]

def functional(path,c):
    return any(fnmatch.fnmatchcase(path,x) for x in c['functional_include']) and not any(fnmatch.fnmatchcase(path,x) for x in c['functional_exclude'])

def intake(a):
    c=config(); rs=records(); b,h,paths=changes(a.base,a.head)
    print('Base:',b,'\nHead:',h,'\nSource:',a.source,'\nReference:',a.reference or 'UNVERIFIED')
    print('Changed paths:', '\n  '.join(['']+paths) if paths else '(none)')
    print('Commits:\n'+git('log','--format=%H %an %s',b+'..'+h))
    hits=impact(paths,rs)
    for r in hits:
        print('Relevant fix:',r['id'],r['title'])
        for t in r['tests']: print('  Test:',t['name'],t['command_or_reference'],t['result'])
    print('Broader configured checks:', ', '.join(c['broader_tests']) or 'none')
    print('Potential duplicate patches (manual confirmation required):')
    print(git('cherry',b,h).strip() or '(none identified)')
    print('UNVERIFIED: indirect dependencies, runtime behavior, semantic equivalence and test coverage require review.')

def gate(a):
    validate(); c=config(); rs=records(); b,h,paths=changes(a.base,a.head)
    for r in rs:
        if any(t['result']=='FAIL' for t in r['tests']): raise Error('recorded test failure: '+r['id'])
    relevant=[p for p in paths if functional(p,c)]
    if not relevant: print('PASS: no configured functional paths changed'); return
    if a.source not in ('local','upstream','third_party'): raise Error('UNVERIFIED: explicit known source required')
    if a.source == 'local':
        linked=[r for r in rs if h in r['commits']]
        if not linked: raise Error('UNVERIFIED: no canonical fix record linked to head')
        if any(t['result']!='PASS' for r in linked + impact(relevant,rs) for t in r['tests']): raise Error('UNVERIFIED: relevant tests are not all passing')
        print('PASS: local fix metadata present; semantic coverage still requires review'); return
    if not a.review: raise Error('UNVERIFIED: external functional change requires review')
    review=load(Path(a.review))
    if not isinstance(review,dict) or review.get('base')!=b or review.get('head')!=h or review.get('source')!=a.source: raise Error('review base/head/source mismatch')
    if review.get('disposition')!='approved': raise Error('review is not approved')
    for k in ('rationale','reference'): nonempty(review.get(k),'review.'+k)
    required={r['id'] for r in impact(relevant,rs)}
    ids=review.get('fix_ids')
    if not isinstance(ids,list) or not required.issubset(set(ids)): raise Error('review omits relevant fixes')
    tests=review.get('tests')
    if not isinstance(tests,list) or not tests: raise Error('UNVERIFIED: no review test evidence')
    for t in tests:
        check_test(t)
        if t['result']!='PASS': raise Error('review test is '+t['result'])
    names={t['name'] for t in tests}
    if any(t['name'] not in names for r in impact(relevant,rs) for t in r['tests']): raise Error('UNVERIFIED: missing impacted fix test evidence')
    print('PASS: supplied review metadata and test evidence accepted; residual semantic risk remains')

def commit_status():
    """List actual commits and distinguish those referenced by canonical records."""
    indexed = {}
    for record in records():
        for sha in record['commits']:
            indexed.setdefault(sha, []).append(record['id'])
    head = subprocess.run(['git', '-C', str(ROOT), 'rev-parse', '--verify', 'HEAD^{commit}'], capture_output=True)
    if head.returncode:
        branch = git('symbolic-ref', '--quiet', 'HEAD').strip()
        reference = subprocess.run(['git', '-C', str(ROOT), 'show-ref', '--verify', '--quiet', branch], capture_output=True)
        if reference.returncode != 1:
            raise Error('HEAD cannot be resolved to a commit')
        print('No commits are available yet.')
        return
    output = git('log', '--format=%H%x00%s', '-z')
    fields = output.split('\0')
    for i in range(0, len(fields) - 1, 2):
        sha, subject = fields[i].strip(), fields[i + 1]
        if sha:
            print(('DOCUMENTED ' + ','.join(indexed[sha]) if sha in indexed else 'UNDOCUMENTED') + ' ' + sha + ' ' + subject)


def document_commit(a):
    """Create a canonical record and a human report from supplied facts."""
    settings = config(); sync(True)
    sha = resolve(a.commit)
    existing = records()
    if any(sha in record['commits'] for record in existing):
        raise Error('commit already has a FIRG record; review existing records first')
    for name in ('problem', 'cause', 'expected', 'implementation', 'rationale', 'notes'):
        nonempty(getattr(a, name), name)
    paths = [p for p in git('diff-tree', '--root', '--no-commit-id', '--name-only', '-r', '-z', sha).split('\0') if p]
    if not paths:
        raise Error('commit has no changed paths; document it manually if appropriate')
    title = git('show', '-s', '--format=%s', sha).strip()
    author = git('show', '-s', '--format=%an', sha).strip() or 'Unknown'
    zone = dt.timezone.utc if settings['timezone'] == 'UTC' else ZoneInfo(settings['timezone'])
    now = dt.datetime.now(zone)
    day = now.strftime('%Y.%m.%d')
    stamp = now.isoformat(timespec='seconds')
    ids = [ident(r['id'])[1] for r in existing if r['id'].startswith(day + '-')]
    number = max(ids, default=0) + 1
    REG.mkdir(exist_ok=True)
    reports = FIRG / 'reports'
    reports.mkdir(exist_ok=True)
    if reports.is_symlink() or not reports.resolve().is_relative_to(FIRG.resolve()):
        raise Error('reports path is unsafe')
    while True:
        fix_id = f'{day}-{number:02d}'
        record = {'schema_version': 1, 'id': fix_id, 'title': title,
                  'issue_date': day, 'issue_date_known': False, 'recorded_at': stamp,
                  'updated_at': stamp, 'source': {'kind': 'local', 'person_or_team': author,
                  'repository_or_provider': None, 'issue_or_pr_reference': None},
                  'commits': [sha], 'problem': a.problem, 'root_cause': a.cause,
                  'affected_components': paths, 'expected_behavior': a.expected,
                  'implementation_summary': a.implementation, 'rationale': a.rationale,
                  'notes': a.notes, 'tests': [{'name': 'Verification',
                  'command_or_reference': 'Not supplied', 'result': 'UNVERIFIED',
                  'evidence': 'No test evidence supplied during documentation.'}],
                  'status': 'active', 'related_fix_ids': [], 'native_history_refs': [],
                  'review_reference': None, 'report_reference': 'reports/' + fix_id + '.md'}
        check_record(record)
        report = reports / (fix_id + '.md')
        if (REG / (fix_id + '.json')).exists():
            number += 1; continue
        content = (f'# {fix_id} — {title}\n\n- **Commit:** `{sha}`\n- **Author:** {author}\n'
                   f'- **Issue Date:** Unknown; registration date {day}.\n\n'
                   f'## Problem\n\n{a.problem}\n\n## Cause\n\n{a.cause}\n\n'
                   f'## Affected Components\n\n' + ''.join(f'- `{p}`\n' for p in paths) +
                   f'\n## Expected Behavior\n\n{a.expected}\n\n## Implementation\n\n{a.implementation}\n\n'
                   f'## Rationale\n\n{a.rationale}\n\n## Notes And Related Changes\n\n{a.notes}\n\n'
                   f'## Verification\n\nUNVERIFIED: No test evidence supplied during documentation.\n\n'
                   f'[Canonical Record](../registry/{fix_id}.json)\n')
        try:
            with report.open('x', encoding='utf-8', newline='\n') as out:
                out.write(content)
        except FileExistsError:
            number += 1; continue
        try:
            atomic_create_record(REG / (fix_id + '.json'), record)
        except FileExistsError as exc:
            raise Error('record collision; unregistered report preserved for review: ' + str(report)) from exc
        except OSError as exc:
            raise Error('record could not be published; unregistered report preserved for review: ' + str(report)) from exc
        break
    sync()
    print('Registered:', fix_id, '\nReport:', report, '\nVerification: UNVERIFIED')


def prompt_commit(commit):
    """Ask only in an interactive terminal; a declined prompt never changes Git."""
    if not sys.stdin.isatty() or not sys.stdout.isatty():
        print('FIRG: Interactive terminal unavailable; commit remains undocumented.')
        return
    try:
        answer = input('Document This Commit In FIRG? [y/N] ').strip().lower()
        if answer not in ('y', 'yes'):
            print('FIRG: Documentation skipped; the commit is unchanged.')
            return
        fields = {}
        for key, prompt in (('problem', 'Original Problem'), ('cause', 'Known Cause Or Unknown'),
                            ('expected', 'Expected Behavior'), ('implementation', 'Changes Implemented'),
                            ('rationale', 'Implementation Rationale Or Unknown'), ('notes', 'Notes And Related Changes Or None')):
            value = input(prompt + ': ').strip()
            if not value:
                print('FIRG: Documentation cancelled; the commit is unchanged.')
                return
            fields[key] = value
        document_commit(argparse.Namespace(commit=commit, **fields))
    except (EOFError, KeyboardInterrupt):
        print('\nFIRG: Documentation cancelled; the commit is unchanged.')


def main():
    parser=argparse.ArgumentParser(description=__doc__); sub=parser.add_subparsers(dest='cmd',required=True)
    v=sub.add_parser('validate');v.add_argument('--strict',action='store_true')
    s=sub.add_parser('sync');s.add_argument('--check',action='store_true')
    n=sub.add_parser('next-id');n.add_argument('--date',required=True)
    r=sub.add_parser('register');r.add_argument('--input',required=True)
    sub.add_parser('commit-status')
    p=sub.add_parser('prompt-commit');p.add_argument('--commit',default='HEAD')
    d=sub.add_parser('document-commit');d.add_argument('--commit',default='HEAD')
    for field in ('problem','cause','expected','implementation','rationale','notes'):
        d.add_argument('--'+field, required=True)
    for name in ('intake','gate'):
        x=sub.add_parser(name);x.add_argument('--base',required=True);x.add_argument('--head',required=True);x.add_argument('--source',choices=['local','upstream','third_party','unknown'],default='unknown')
        if name=='intake': x.add_argument('--reference')
        else: x.add_argument('--review')
    a=parser.parse_args()
    require_git()
    if a.cmd=='validate': validate(); print('PASS: validation and ledger')
    elif a.cmd=='sync': sync(a.check); print('PASS: ledger '+('current' if a.check else 'generated'))
    elif a.cmd=='next-id':
        date(a.date); ids=[ident(x['id'])[1] for x in records() if x['id'].startswith(a.date+'-')]; print(f'{a.date}-{max(ids,default=0)+1:02d}'); print('Existing:',', '.join(str(i) for i in ids) or 'none')
    elif a.cmd=='register':
        r=load(Path(a.input));check_record(r);existing=records(); known={x['id'] for x in existing}
        if any(x not in known for x in r['related_fix_ids']): raise Error('broken related fix reference')
        REG.mkdir(exist_ok=True); path=REG/(r['id']+'.json')
        try:
            atomic_create_record(path, r)
        except FileExistsError: raise Error('ID already exists; never overwritten')
        print('Registered:',path,'; run sync')
    elif a.cmd=='commit-status': commit_status()
    elif a.cmd=='prompt-commit': prompt_commit(a.commit)
    elif a.cmd=='document-commit': document_commit(a)
    elif a.cmd=='intake': intake(a)
    else: gate(a)

if __name__=='__main__':
    try: main()
    except (Error, OSError) as e: print('FAIL:',e,file=sys.stderr);sys.exit(1)
