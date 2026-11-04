import importlib.util
import json
import os
from pathlib import Path
import subprocess
import tempfile
import time
import unittest
from unittest.mock import patch

HERE=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('firg',HERE/'tools/firg.py')
f=importlib.util.module_from_spec(spec);spec.loader.exec_module(f)
SCRATCH=Path(os.environ.get('FIRG_TEST_WORKSPACE', str(HERE.parent/'Shared-Project-State-Manager'/'Test-Workspace')))

@unittest.skipUnless(SCRATCH.is_dir(), 'Test workspace unavailable; create or configure an authorized disposable test workspace before running FIRG self-tests')
class FirgTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(prefix='firg-اختبار ',dir=SCRATCH)
        self.root=Path(self.tmp.name); self.old=(f.ROOT,f.FIRG,f.REG,f.LEDGER)
        f.ROOT=self.root;f.FIRG=self.root/'FIRG';f.REG=f.FIRG/'registry';f.LEDGER=f.FIRG/'FIX-HISTORY.md'
        f.REG.mkdir(parents=True)
        subprocess.run(['git','init','-q',str(self.root)],check=True)
        subprocess.run(['git','-C',str(self.root),'config','user.email','fixture@example.invalid'],check=True)
        subprocess.run(['git','-C',str(self.root),'config','user.name','Fixture'],check=True)
        (self.root/'source').mkdir();(self.root/'source'/'a.txt').write_text('old')
        self.git('add','.');self.git('commit','-qm','base');self.base=self.git('rev-parse','HEAD').strip()
        (self.root/'source'/'a.txt').rename(self.root/'source'/'b.txt')
        self.git('add','-A');self.git('commit','-qm','rename');self.head=self.git('rev-parse','HEAD').strip()
    def tearDown(self):
        f.ROOT,f.FIRG,f.REG,f.LEDGER=self.old
        for attempt in range(15):
            try:
                self.tmp.cleanup()
                break
            except PermissionError:
                if attempt == 14: raise
                time.sleep(0.2)
    def git(self,*args): return subprocess.run(['git','-C',str(self.root),*args],check=True,capture_output=True,text=True).stdout
    def record(self,ident='2026.11.04-01'):
        return {'schema_version':1,'id':ident,'title':'Fixture','issue_date':'2026.11.04','issue_date_known':True,'recorded_at':'2026-11-04T00:00:00Z','updated_at':'2026-11-04T00:00:00Z','source':{'kind':'local','person_or_team':'fixture','repository_or_provider':None,'issue_or_pr_reference':None},'commits':[self.base],'problem':'Fixture problem.','affected_components':['source/a.txt'],'expected_behavior':'Fixture behavior.','implementation_summary':'Fixture change.','tests':[{'name':'fixture','command_or_reference':'fixture command','result':'PASS','evidence':'fixture output'}],'status':'active','related_fix_ids':[],'native_history_refs':[],'review_reference':None}
    def write(self,r,name=None): (f.REG/(name or r['id']+'.json')).write_text(json.dumps(r),encoding='utf-8')
    def test_dates_and_ids(self):
        self.assertEqual(f.ident('2024.02.29-100')[1],100)
        for x in ('2023.02.29-01','2026.11.04-00','2026.13.01-01'):
            with self.assertRaises(f.Error): f.ident(x)
    def test_sort_sync_and_tamper(self):
        for n in (100,2,1,3): self.write(self.record(f'2026.11.04-{n:02}'))
        f.sync(); before=f.LEDGER.read_bytes()
        acl = subprocess.run(['icacls', str(f.LEDGER)], capture_output=True, text=True, errors='replace', check=True).stdout if os.name == 'nt' else None
        f.sync();self.assertEqual(before,f.LEDGER.read_bytes()); f.sync(True)
        if acl is not None:
            self.assertEqual(acl, subprocess.run(['icacls', str(f.LEDGER)], capture_output=True, text=True, errors='replace', check=True).stdout)
        self.assertLess(before.index(b'04-03'),before.index(b'04-100'))
        f.LEDGER.write_text('tamper')
        with self.assertRaises(f.Error): f.sync(True)
    def test_invalid_records(self):
        r=self.record();r['status']='bad'
        with self.assertRaises(f.Error): f.check_record(r)
        r=self.record();r['related_fix_ids']=['2026.11.04-02'];self.write(r)
        with self.assertRaises(f.Error): f.records()
        (f.REG/(r['id']+'.json')).unlink();self.write(self.record(),'wrong.json')
        with self.assertRaises(f.Error): f.records()
        (f.REG/'wrong.json').write_text('{bad')
        with self.assertRaises(f.Error): f.records()
    def test_rename_impact(self):
        b,h,paths=f.changes(self.base,self.head)
        self.assertEqual({b,h},{self.base,self.head});self.assertIn('source/a.txt',paths);self.assertIn('source/b.txt',paths)
        self.assertEqual(f.impact(paths,[self.record()])[0]['id'],'2026.11.04-01')
    def test_test_evidence_and_duplicate_keys(self):
        with self.assertRaises(f.Error): f.check_test({'name':'x','command_or_reference':'x','result':'UNKNOWN','evidence':'x'})
        x=f.REG/'duplicate.json';x.write_text('{"id":1,"id":2}')
        with self.assertRaises(f.Error): f.load(x)
    def test_gate_blocks_missing_review_and_allows_docs(self):
        import types
        (self.root/'AGENTS.md').write_text('rules')
        for name in ('AGENTS.md','README.md','policies/INTEGRATION.md','tools/firg.py','tests/test_firg.py','schemas/fix-record.schema.json'):
            path=f.FIRG/name;path.parent.mkdir(parents=True,exist_ok=True);path.write_text('{}')
        (f.FIRG/'config.json').write_text(json.dumps({'schema_version':1,'timezone':'UTC','functional_include':['source/**'],'functional_exclude':[],'broader_tests':[]}))
        f.sync()
        a=types.SimpleNamespace(base=self.base,head=self.head,source='upstream',review=None)
        with self.assertRaises(f.Error): f.gate(a)
        a.source='unknown'
        with self.assertRaises(f.Error): f.gate(a)
        a.base=self.base;a.head=self.base
        f.gate(a)
        f.LEDGER.write_text('stale')
        with self.assertRaises(f.Error): f.gate(a)
    def test_gate_rejects_failed_or_unverified_review(self):
        import types
        (self.root/'AGENTS.md').write_text('rules')
        for name in ('AGENTS.md','README.md','policies/INTEGRATION.md','tools/firg.py','tests/test_firg.py','schemas/fix-record.schema.json'):
            path=f.FIRG/name;path.parent.mkdir(parents=True,exist_ok=True);path.write_text('{}')
        (f.FIRG/'config.json').write_text(json.dumps({'schema_version':1,'timezone':'UTC','functional_include':['source/**'],'functional_exclude':[],'broader_tests':[]}));f.sync()
        review={'base':self.base,'head':self.head,'source':'upstream','disposition':'approved','rationale':'fixture','reference':'fixture','fix_ids':[],'tests':[{'name':'fixture','command_or_reference':'fixture','result':'FAIL','evidence':'fixture'}]}
        path=self.root/'review.json';a=types.SimpleNamespace(base=self.base,head=self.head,source='upstream',review=str(path))
        for result in ('FAIL','UNVERIFIED'):
            review['tests'][0]['result']=result;path.write_text(json.dumps(review))
            with self.assertRaises(f.Error): f.gate(a)
    def test_exclusive_create(self):
        p=f.REG/'2026.11.04-01.json';p.write_text('original')
        with self.assertRaises(FileExistsError):
            f.atomic_create_record(p, {'replacement': True})
        self.assertEqual(p.read_text(),'original')
        if os.name == 'nt':
            other=f.REG/'2026.11.04-02.json'
            with patch.object(f.os, 'link', side_effect=PermissionError('hard links denied')):
                f.atomic_create_record(other, {'created': True})
                with self.assertRaises(FileExistsError): f.atomic_create_record(other, {'replacement': True})
            self.assertEqual(json.loads(other.read_text(encoding='utf-8')), {'created': True})
        failure=f.REG/'2026.11.04-03.json'
        with patch.object(f.os, 'link', side_effect=OSError('publish failed')):
            with self.assertRaises(OSError): f.atomic_create_record(failure, {'not': 'published'})
        self.assertFalse(failure.exists())
        self.assertEqual(list(f.REG.glob('.firg-record-*.tmp')), [])

if __name__=='__main__': unittest.main()
