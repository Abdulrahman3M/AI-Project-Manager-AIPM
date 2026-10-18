from __future__ import annotations
from pathlib import Path
import json, subprocess, sys, tempfile, unittest, threading
from concurrent.futures import ThreadPoolExecutor
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[1]; from test_support import CORE_ROOT; sys.path.insert(0,str(CORE_ROOT))
from aipm_core.continuity import ContinuityManager, LockError
from aipm_core.storage import initialize_project_state, StateError
from aipm_core.domain import CoreEngine, CommandEnvelope

class HardeningTests(unittest.TestCase):
 def setUp(self):
  self.temp=tempfile.TemporaryDirectory(dir=ROOT/'.test-workspace'); self.addCleanup(self.temp.cleanup)
  self.project=initialize_project_state(Path(self.temp.name)/'Managed','managed','Managed'); self.manager=ContinuityManager(self.project)
 def git(self,*args): return subprocess.check_output(['git','-C',str(self.project.root),*args],stderr=subprocess.STDOUT).decode().strip()
 def repository(self):
  self.git('init','-b','main'); self.git('config','user.name','Test Actor'); self.git('config','user.email','test@example.invalid')
  (self.project.root/'.gitignore').write_text('Shared-Project-State-Manager/\n'); (self.project.root/'tracked.txt').write_text('one\n'); self.git('add','.'); self.git('commit','-m','Initial')
 def test_git_reconcile_detects_branch_head_and_diff_drift(self):
  self.repository(); self.manager=ContinuityManager(self.project,CoreEngine({'managed':self.project})); self.assertEqual(self.manager.record_git_status('actor')['status'],'PASS'); self.assertFalse(self.manager.reconcile_git()['drift'])
  self.git('checkout','-b','feature'); (self.project.root/'tracked.txt').write_text('two\n'); self.git('commit','-am','Second'); (self.project.root/'tracked.txt').write_text('three\n')
  self.assertEqual(set(self.manager.reconcile_git()['changed_fields']),{'branch','head_sha','diff_fingerprint'})
 def test_git_diff_fingerprint_covers_staged_unstaged_and_untracked_changes(self):
  self.repository(); values=[self.manager.git_status()['diff_fingerprint']]
  (self.project.root/'tracked.txt').write_text('staged\n'); self.git('add','tracked.txt'); values.append(self.manager.git_status()['diff_fingerprint'])
  (self.project.root/'tracked.txt').write_text('unstaged\n'); values.append(self.manager.git_status()['diff_fingerprint'])
  (self.project.root/'new.txt').write_text('new\n'); values.append(self.manager.git_status()['diff_fingerprint'])
  (self.project.root/'new.txt').write_text('changed\n'); values.append(self.manager.git_status()['diff_fingerprint']); self.assertEqual(len(set(values)),5)
  before=self.git('status','--porcelain=v1'); self.assertEqual(self.manager.git_status(),self.manager.git_status()); self.assertEqual(before,self.git('status','--porcelain=v1'))
 def test_git_reconcile_supports_detached_head(self):
  self.repository(); self.git('checkout','--detach'); result=self.manager.git_status(); self.assertIsNone(result['branch']); self.assertEqual(result['head_sha'],self.git('rev-parse','HEAD'))
 def test_record_git_status_uses_core_engine_without_altering_task_state(self):
  self.repository(); engine=CoreEngine({'managed':self.project}); self.assertEqual(engine.execute(CommandEnvelope('create','task.create','actor','managed',0,None,{'task_id':'Task-One','title':'Task One','scope':'Test Scope'}))['status'],'PASS')
  before=json.loads((self.project.state_root/'State-Manifest.json').read_text()); self.assertEqual(ContinuityManager(self.project,engine).record_git_status('actor')['revision'],2); after=json.loads((self.project.state_root/'State-Manifest.json').read_text())
  for key in ('task_id','task_status','tasks'): self.assertEqual(before[key],after[key])
  events=sorted((self.project.state_root/'History'/'Events').glob('*.json')); self.assertEqual(len(events),2); self.assertEqual(json.loads(events[-1].read_text())['command'],'state.record-git-observation')
 def test_git_observation_excludes_own_unignored_operational_state(self):
  self.repository(); (self.project.root/'.gitignore').write_text(''); self.git('commit','-am','Remove Ignore'); manager=ContinuityManager(self.project,CoreEngine({'managed':self.project})); self.assertEqual(manager.record_git_status('actor')['status'],'PASS'); self.assertFalse(manager.reconcile_git()['drift'])
 def payload(self):
  source=self.project.state_root/'Tasks'/'Payload'; source.mkdir(); (source/'data.txt').write_bytes(b'preserve\x00\xff'); (source/'Empty').mkdir(); return source
 def test_quarantine_writes_audit_metadata_and_can_restore(self):
  source=self.payload(); record=self.manager.quarantine(source,'Unsafe Input'); audit=record.read_bytes(); self.assertFalse(source.exists()); data=json.loads(audit); self.assertEqual(data['reason'],'Unsafe Input'); self.assertTrue(data['hashes']); self.assertEqual(self.manager.restore_quarantined(record),source); self.assertEqual(record.read_bytes(),audit); self.assertEqual((source/'data.txt').read_bytes(),b'preserve\x00\xff')
 def test_archive_collision_does_not_overwrite(self):
  source=self.payload(); record=self.manager.archive(source,'Release One'); source.mkdir(); (source/'data.txt').write_text('new owner')
  with self.assertRaises(StateError): self.manager.restore_archive(record)
  self.assertEqual((source/'data.txt').read_text(),'new owner'); self.assertTrue(record.exists())
 def test_archive_rejects_path_outside_state_root(self):
  source=self.project.root/'outside.txt'; source.write_text('untouched')
  with self.assertRaises(StateError): self.manager.archive(source,'Outside')
  self.assertEqual(source.read_text(),'untouched')
 def test_archive_can_be_restored_without_hash_change(self):
  source=self.payload(); record=self.manager.archive(source,'Release One'); stored=self.project.state_root/json.loads(record.read_text())['stored_path']; (stored/'data.txt').write_text('tampered')
  with self.assertRaises(StateError): self.manager.restore_archive(record)
  self.assertFalse(source.exists()); (stored/'data.txt').write_bytes(b'preserve\x00\xff'); self.assertEqual(self.manager.restore_archive(record),source); self.assertTrue((source/'Empty').is_dir())
 def test_archive_restore_retries_after_interrupted_move(self):
  source=self.payload(); record=self.manager.archive(source,'Release One')
  with patch('aipm_core.continuity._move_noreplace',side_effect=PermissionError('Injected Move Denial')):
   with self.assertRaises(PermissionError): self.manager.restore_archive(record)
  self.assertEqual(self.manager.restore_archive(record),source)
 def test_archive_restore_recovers_after_post_move_audit_failure(self):
  source=self.payload(); record=self.manager.archive(source,'Release One'); original=self.manager._exclusive_json
  def fail_receipt(path,data):
   if path.name=='Restored.json': raise OSError('Injected Audit Failure')
   return original(path,data)
  with patch.object(self.manager,'_exclusive_json',side_effect=fail_receipt):
   with self.assertRaises(OSError): self.manager.restore_archive(record)
  self.assertEqual(self.manager.restore_archive(record),source)
 def test_archive_record_cannot_restore_outside_root(self):
  source=self.payload(); record=self.manager.archive(source,'Release One'); data=json.loads(record.read_text()); data['source_path']='../../escape'; record.write_text(json.dumps(data))
  with self.assertRaises(StateError): self.manager.restore_archive(record)
 def test_snapshot_collision_preserves_existing_snapshot(self):
  self.manager.checkpoint('actor','Next','Evidence',None); first=self.manager.snapshot(); before=(first/'Current-State.md').read_bytes(); self.manager.checkpoint('actor','Next','Different',None); second=self.manager.snapshot(); self.assertNotEqual(first,second); self.assertEqual((first/'Current-State.md').read_bytes(),before)
 def spawn_owner(self):
  code="import sys,time; from pathlib import Path; sys.path.insert(0,sys.argv[1]); from aipm_core.storage import ManagedProject; from aipm_core.continuity import ContinuityManager; root=Path(sys.argv[2]); p=ManagedProject('managed','Managed',root,root/'Shared-Project-State-Manager'); print(ContinuityManager(p).acquire_lock('task','child'),flush=True); time.sleep(60)"
  process=subprocess.Popen([sys.executable,'-c',code,str(CORE_ROOT),str(self.project.root)],cwd=self.project.root,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True); self.addCleanup(lambda:self.stop(process)); self.assertTrue(process.stdout.readline().strip()); self.expire_lock(); return process
 def expire_lock(self):
  path=self.project.state_root/'Locks'/'task.json'; data=json.loads(path.read_text()); data['expires_at']='2000-01-01T00:00:00+00:00'; path.write_text(json.dumps(data))
 @staticmethod
 def stop(process):
  if process.poll() is None: process.terminate()
  process.wait(timeout=10); process.stdout.close(); process.stderr.close()
 def test_live_process_identity_blocks_expired_lease_recovery(self):
  process=self.spawn_owner()
  with self.assertRaises(LockError): self.manager.recover_expired_lock('task')
  self.assertIsNone(process.poll()); data=json.loads((self.project.state_root/'Locks'/'task.json').read_text()); self.assertIn('creation',data['process_identity']); self.assertIn('session',data['process_identity'])
 def test_terminated_process_allows_expired_lease_recovery(self):
  process=self.spawn_owner(); process.terminate(); process.wait(timeout=10); self.manager.recover_expired_lock('task'); self.assertFalse((self.project.state_root/'Locks'/'task.json').exists())
 def test_pid_reuse_does_not_mistake_new_process_for_lease_owner(self):
  self.manager.acquire_lock('task','actor'); self.expire_lock()
  with patch('aipm_core.continuity._process_identity',return_value={'status':'live','creation':'different','session':'different'}): self.manager.recover_expired_lock('task')
  self.assertFalse((self.project.state_root/'Locks'/'task.json').exists())
 def test_unknown_process_identity_fails_closed(self):
  self.manager.acquire_lock('task','actor'); self.expire_lock()
  with patch('aipm_core.continuity._process_identity',return_value={'status':'unknown'}):
   with self.assertRaises(LockError): self.manager.recover_expired_lock('task')
  self.assertTrue((self.project.state_root/'Locks'/'task.json').exists())
 def test_lock_rejects_invalid_resource_and_nonpositive_lease(self):
  for resource in ('../escape','a/b','a\\b'):
   with self.assertRaises(LockError): self.manager.acquire_lock(resource,'actor')
  for lease in (0,-1):
   with self.assertRaises(LockError): self.manager.acquire_lock('task','actor',lease)
 def test_lock_guard_rejects_reparse_path_before_opening_redirected_target(self):
  # A real junction exercises canonical rejection; the narrow open shim models
  # a file redirect because this Windows token cannot create file symlinks.
  external=Path(self.temp.name)/'External'; external.mkdir(); target=external/'Guard.bin'; target.write_bytes(b'')
  guard=self.project.state_root/'Locks'/'task.guard'
  result=subprocess.run(['cmd','/c','mklink','/J',str(guard),str(external)],capture_output=True,text=True)
  if result.returncode != 0:
   self.skipTest(f'UNVERIFIED: Windows junction creation is denied by this host: {result.stdout} {result.stderr}')
  try:
   self.assertTrue(guard.is_junction()); original=Path.open; opened=[]
   def redirected_open(path,*args,**kwargs):
    if path==guard:
     opened.append(path); return original(target,*args,**kwargs)
    return original(path,*args,**kwargs)
   with patch.object(Path,'open',redirected_open):
    with self.assertRaises(LockError): self.manager.acquire_lock('task','actor')
   self.assertEqual(opened,[],'Guard Was Opened Before Reparse Validation')
   self.assertEqual(target.read_bytes(),b'')
   self.assertFalse((self.project.state_root/'Locks'/'task.json').exists())
  finally: guard.rmdir()
 def test_competing_stale_lock_cleanup_cannot_remove_new_lease(self):
  for operation in ('release','recover'):
   with self.subTest(operation=operation):
    nonce=self.manager.acquire_lock('task','actor'); self.expire_lock(); path=self.project.state_root/'Locks'/'task.json'
    paused, started, replaced=threading.Event(),threading.Event(),threading.Event(); original=Path.unlink
    def pause_unlink(candidate,*args,**kwargs):
     if candidate==path and threading.current_thread().name.startswith('Stale'):
      paused.set(); self.assertTrue(started.wait(5)); replaced.wait(.3)
     return original(candidate,*args,**kwargs)
    def stale():
     if operation=='release': self.manager.release_lock('task',nonce)
     else: self.manager.recover_expired_lock('task')
    def replace():
     self.assertTrue(paused.wait(5)); started.set()
     try: self.manager.release_lock('task',nonce)
     except LockError: pass
     new_nonce=self.manager.acquire_lock('task','replacement'); replaced.set(); return new_nonce
    with patch.object(Path,'unlink',pause_unlink), patch('aipm_core.continuity._process_identity',return_value={'status':'live','creation':'replacement','session':'0'}):
     with ThreadPoolExecutor(1,thread_name_prefix='Stale') as first, ThreadPoolExecutor(1,thread_name_prefix='Replacement') as second:
      old=first.submit(stale); new=second.submit(replace); old.result(timeout=10); new_nonce=new.result(timeout=10)
    self.assertTrue(path.exists(),'Stale Cleanup Deleted A Newly Acquired Lease'); self.assertEqual(json.loads(path.read_text())['nonce'],new_nonce); self.manager.release_lock('task',new_nonce)
 def test_restore_destination_race_preserves_existing_file_and_payload(self):
  source=self.project.state_root/'Tasks'/'Single.txt'; source.write_bytes(b'archive payload'); record=self.manager.archive(source,'Release'); original=Path.mkdir
  def create_destination(candidate,*args,**kwargs):
   result=original(candidate,*args,**kwargs)
   if candidate==source.parent: source.write_bytes(b'concurrent owner')
   return result
  def race_move(candidate,target):
   # Emulate overwrite semantics on POSIX even when running Windows.
   return candidate.replace(target)
  with patch.object(Path,'mkdir',create_destination),patch.object(Path,'rename',race_move):
   with self.assertRaises(StateError): self.manager.restore_archive(record)
  self.assertEqual(source.read_bytes(),b'concurrent owner'); stored=self.project.state_root/json.loads(record.read_text())['stored_path']; self.assertEqual(stored.read_bytes(),b'archive payload')
 def test_resource_guard_serializes_a_real_child_process(self):
  code="import sys; from pathlib import Path; sys.path.insert(0,sys.argv[1]); from aipm_core.storage import ManagedProject; from aipm_core.continuity import ContinuityManager; root=Path(sys.argv[2]); manager=ContinuityManager(ManagedProject('managed','Managed',root,root/'Shared-Project-State-Manager')); print('Ready',flush=True); print(manager.acquire_lock('task','child'),flush=True)"
  with self.manager._lock_guard('task'):
   process=subprocess.Popen([sys.executable,'-c',code,str(CORE_ROOT),str(self.project.root)],cwd=self.project.root,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True); self.addCleanup(lambda:self.stop(process)); self.assertEqual(process.stdout.readline().strip(),'Ready')
   with self.assertRaises(subprocess.TimeoutExpired): process.wait(timeout=.3)
   self.assertFalse((self.project.state_root/'Locks'/'task.json').exists())
  output,error=process.communicate(timeout=10); self.assertEqual(process.returncode,0,error); nonce=output.strip(); self.assertTrue(nonce); self.manager.release_lock('task',nonce)
 def test_malformed_records_and_lock_shapes_fail_with_domain_errors(self):
  source=self.payload(); record=self.manager.archive(source,'Release'); original=record.read_bytes()
  for malformed in ('[]','null','{"category":"Archive"}','{'):
   record.write_text(malformed)
   with self.subTest(record=malformed),self.assertRaises(StateError): self.manager.restore_archive(record)
  record.write_bytes(original); intent=record.parent/'Restore-Intent.json'; intent.write_text('[]')
  with self.assertRaises(StateError): self.manager.restore_archive(record)
  for malformed in ('[]','null','{"nonce":"x"}','{'):
   path=self.project.state_root/'Locks'/'task.json'; path.write_text(malformed)
   with self.subTest(lock=malformed),self.assertRaises(LockError): self.manager.recover_expired_lock('task')
   with self.subTest(release=malformed),self.assertRaises(LockError): self.manager.release_lock('task','x')
