#!/usr/bin/env python3
"""Validate an actual Visual Register against release-gating schema (not copyright clearance)."""
import argparse,json,sys
from pathlib import Path
required=['figure_id','section','learning_goal','visual_type','trigger','source_ledger_ids','asset_license','caption','alt_text','direction','editability','word_fallback','review_status']
p=argparse.ArgumentParser();p.add_argument('register');p.add_argument('--release',action='store_true');a=p.parse_args()
data=json.loads(Path(a.register).read_text(encoding='utf8'));errors=[]
for i,x in enumerate(data.get('visuals',[]),1):
 for key in required:
  if key not in x or x[key] is None or (x[key]=='' and key not in ['alt_text']): errors.append(f'figure {i}: missing {key}')
 if x.get('visual_type') in ('sourced-chart','measured-chart','verified-map') and not x.get('source_ledger_ids'):errors.append(f'figure {i}: factual data/geo source required')
 if a.release and x.get('review_status') not in ('approved','pass'):errors.append(f'figure {i}: release review not approved')
 if x.get('direction') not in ('RTL','LTR'):errors.append(f'figure {i}: invalid direction')
print(json.dumps({'status':'PASS' if not errors else 'FAIL','count':len(data.get('visuals',[])),'issues':errors},indent=2));sys.exit(bool(errors))
