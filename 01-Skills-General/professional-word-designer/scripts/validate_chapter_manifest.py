#!/usr/bin/env python3
"""Validate Chapter Package manifest structure and optional file presence."""
from __future__ import annotations
import argparse, json
from pathlib import Path

def main()->int:
    ap=argparse.ArgumentParser()
    ap.add_argument("manifest")
    ap.add_argument("--check-files",action="store_true")
    a=ap.parse_args()
    path=Path(a.manifest)
    data=json.loads(path.read_text(encoding="utf-8"))
    chapters=data.get("chapters",[])
    errors=[]
    ids=set(); files=set(); orders=set()
    for c in chapters:
        cid=c.get("chapter_id"); f=c.get("file"); order=c.get("order"); title=c.get("title")
        if not all([cid,f,order,title]): errors.append(f"incomplete chapter record: {c}"); continue
        if cid in ids: errors.append(f"duplicate chapter_id: {cid}")
        if f in files: errors.append(f"duplicate chapter file: {f}")
        if order in orders: errors.append(f"duplicate chapter order: {order}")
        ids.add(cid); files.add(f); orders.add(order)
        if a.check_files and not (path.parent/f).is_file():
            errors.append(f"missing chapter file: {f}")
    expected=list(range(1,len(chapters)+1))
    if sorted(orders)!=expected: errors.append(f"chapter order must be contiguous 1..{len(chapters)}")
    index_file=data.get("index_file")
    if not index_file: errors.append("missing index_file")
    status="FAIL" if errors else "PASS"
    print(json.dumps({"status":status,"chapters":len(chapters),"errors":errors},indent=2,ensure_ascii=False))
    return 1 if errors else 0

if __name__=="__main__":
    raise SystemExit(main())
