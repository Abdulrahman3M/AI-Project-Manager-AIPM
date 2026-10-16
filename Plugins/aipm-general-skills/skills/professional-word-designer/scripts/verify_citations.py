#!/usr/bin/env python3
"""Cross-check numbered citations in DOCX with a verified JSON source ledger."""
import argparse,json,re,sys
from pathlib import Path
from docx import Document
p=argparse.ArgumentParser();p.add_argument('docx');p.add_argument('--ledger',required=True);a=p.parse_args()
entries=json.loads(Path(a.ledger).read_text(encoding='utf8')).get('sources',[])
sources={str(s['id']):s for s in entries};issues=[]
text='\n'.join(p.text for p in Document(a.docx).paragraphs)
body=text.split('References')[0].split('المصادر')[0]
used=set(re.findall(r'\[(\d+)\]',body));
for x in sorted(used):
 if x not in sources:issues.append(f'Citation [{x}] lacks source ledger record')
 elif not sources[x].get('verified'):issues.append(f'Citation [{x}] uses unverified source')
for s in sources.values():
 if str(s['id']) in used and not (s.get('url') or s.get('doi') or s.get('publisher')):issues.append(f"Source [{s['id']}] lacks an identifiable publisher/DOI/URL")
print(json.dumps({'status':'PASS' if not issues else 'FAIL','used_citations':sorted(used),'issues':issues,'scope':'Identifier crosscheck only; verify real sources manually'},indent=2));sys.exit(bool(issues))
