#!/usr/bin/env python3
"""Paragraph-level review summary. Does NOT implement native Track Changes."""
import argparse,difflib
from pathlib import Path
from docx import Document
p=argparse.ArgumentParser();p.add_argument('original');p.add_argument('revised');p.add_argument('--out',required=True);a=p.parse_args()
def paras(x):return [p.text.strip() for p in Document(x).paragraphs if p.text.strip()]
diff='\n'.join(difflib.unified_diff(paras(a.original),paras(a.revised),fromfile=a.original,tofile=a.revised,lineterm=''))
Path(a.out).write_text('# Review Diff (not native Word Track Changes)\n\n```diff\n'+diff+'\n```\n',encoding='utf-8');print(a.out)
