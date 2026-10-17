#!/usr/bin/env python3
"""Validate package references, produce checksums + deterministic zip from master folder."""
import hashlib,zipfile,argparse,json
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent

def build(dest):
 paths=sorted(x for x in ROOT.rglob('*') if x.is_file() and '__pycache__' not in x.parts and '.pytest_cache' not in x.parts and x.name not in ('.DS_Store','checksums.sha256','manifest.txt') and not x.suffix=='.pyc')
 rel=[x.relative_to(ROOT).as_posix() for x in paths]
 (ROOT/'manifest.txt').write_text('\n'.join(rel)+'\n',encoding='utf-8')
 (ROOT/'checksums.sha256').write_text(''.join(hashlib.sha256(p.read_bytes()).hexdigest()+'  '+p.relative_to(ROOT).as_posix()+'\n' for p in paths),encoding='utf-8')
 paths=sorted([*paths,ROOT/'manifest.txt',ROOT/'checksums.sha256'])
 with zipfile.ZipFile(dest,'w',zipfile.ZIP_DEFLATED,compresslevel=8) as z:
  for p in paths:z.write(p,arcname='professional-word-designer/'+p.relative_to(ROOT).as_posix())
 with zipfile.ZipFile(dest) as z:
  assert z.testzip() is None
  assert len(z.namelist())==len(paths)
 print(json.dumps({'zip':str(dest),'files':len(paths),'bytes':dest.stat().st_size,'sha256':hashlib.sha256(dest.read_bytes()).hexdigest()},indent=2))
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('output');a=p.parse_args();build(Path(a.output).resolve())
