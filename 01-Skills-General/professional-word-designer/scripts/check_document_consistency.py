#!/usr/bin/env python3
"""Baseline consistency checks for plain-text exports from a document/chapter set."""
from __future__ import annotations
import argparse, json, re
from pathlib import Path

def paras(text):
    return [re.sub(r"\s+"," ",p.strip()) for p in re.split(r"\n\s*\n",text) if p.strip()]

def main()->int:
    ap=argparse.ArgumentParser()
    ap.add_argument("files",nargs="+")
    ap.add_argument("--min-duplicate-chars",type=int,default=180)
    ap.add_argument("--output")
    a=ap.parse_args()
    seen={}; duplicates=[]
    for fp in a.files:
        text=Path(fp).read_text(encoding="utf-8")
        for p in paras(text):
            key=p.casefold()
            if len(p)>=a.min_duplicate_chars:
                if key in seen: duplicates.append({"first":seen[key],"second":fp,"sample":p[:160]})
                else: seen[key]=fp
    report={"files":len(a.files),"duplicate_long_paragraphs":duplicates,"status":"WARN" if duplicates else "PASS",
            "note":"This baseline catches exact normalized long-paragraph repetition; semantic contradiction and terminology review still require editorial inspection."}
    txt=json.dumps(report,indent=2,ensure_ascii=False)+"\n"
    print(txt,end="")
    if a.output: Path(a.output).write_text(txt,encoding="utf-8")
    return 0

if __name__=="__main__":
    raise SystemExit(main())
