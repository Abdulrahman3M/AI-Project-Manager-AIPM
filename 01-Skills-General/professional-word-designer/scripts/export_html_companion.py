#!/usr/bin/env python3
"""Demonstrate an optional separate accessible interactive HTML explainer; not a DOCX converter."""
import argparse,json,html
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--input',required=True);p.add_argument('--output',required=True);a=p.parse_args()
d=json.loads(Path(a.input).read_text(encoding='utf-8'));title=html.escape(d['title']);sections=d.get('sections',[])
assert all(isinstance(s,dict) and 'heading' in s and 'summary' in s for s in sections)
body=''.join(f'<details><summary>{html.escape(x["heading"])}</summary><p>{html.escape(x["summary"])}</p></details>' for x in sections)
page=f'''<!doctype html><html lang="{html.escape(d.get('lang','en'))}" dir="{html.escape(d.get('dir','ltr'))}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>{title}</title><style>body{{font:18px system-ui;max-width:760px;margin:3em auto;padding:1em;line-height:1.6}}details{{margin:1em 0;padding:.8em;border:1px solid #90adaf;border-radius:8px}}summary{{font-weight:700;cursor:pointer}}summary:focus-visible{{outline:3px solid #167b7f}}</style></head><body><h1>{title}</h1><p>Separate, accessible HTML companion; Word receives a static explanation instead.</p>{body}</body></html>'''
Path(a.output).write_text(page,encoding='utf-8');print(a.output)
