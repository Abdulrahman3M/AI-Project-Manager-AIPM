#!/usr/bin/env python3
"""Report likely duplicate references without merging them automatically."""
from __future__ import annotations
import argparse, json, re
from pathlib import Path

def norm(s):
    return re.sub(r"[^a-z0-9]+"," ",(s or "").casefold()).strip()

def norm_doi(s):
    s=(s or "").strip().casefold()
    for p in ("https://doi.org/","http://doi.org/","doi:"):
        if s.startswith(p): s=s[len(p):]
    return s or None

def main()->int:
    ap=argparse.ArgumentParser()
    ap.add_argument("ledger")
    ap.add_argument("--output")
    a=ap.parse_args()
    sources=json.loads(Path(a.ledger).read_text(encoding="utf-8")).get("sources",[])
    pairs=[]; seen_doi={}; seen_title={}
    for s in sources:
        sid=s.get("source_id","?")
        doi=norm_doi(s.get("doi"))
        if doi:
            if doi in seen_doi: pairs.append({"a":seen_doi[doi],"b":sid,"reason":"same DOI"})
            else: seen_doi[doi]=sid
        key=(norm(s.get("title")),str(s.get("date") or "")[:4])
        if key[0]:
            if key in seen_title and seen_title[key]!=sid:
                pairs.append({"a":seen_title[key],"b":sid,"reason":"same normalized title/year; manual review required"})
            else: seen_title[key]=sid
    report={"possible_duplicates":pairs,"count":len(pairs),"note":"No records were merged automatically."}
    txt=json.dumps(report,indent=2,ensure_ascii=False)+"\n"
    print(txt,end="")
    if a.output: Path(a.output).write_text(txt,encoding="utf-8")
    return 0

if __name__=="__main__":
    raise SystemExit(main())
