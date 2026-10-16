#!/usr/bin/env python3
"""Baseline validator for source-ledger metadata. Does not perform network lookup."""
from __future__ import annotations
import argparse, json, re
from pathlib import Path
from urllib.parse import urlparse

DOI_RE=re.compile(r"^10\.\d{4,9}/\S+$",re.I)

def norm_doi(value):
    if not value: return None
    v=value.strip()
    for prefix in ("https://doi.org/","http://doi.org/","doi:"):
        if v.lower().startswith(prefix):
            v=v[len(prefix):]
            break
    return v

def main() -> int:
    ap=argparse.ArgumentParser()
    ap.add_argument("ledger")
    args=ap.parse_args()
    data=json.loads(Path(args.ledger).read_text(encoding="utf-8"))
    sources=data.get("sources",[])
    errors=[]; warnings=[]; ids=set(); dois={}
    for s in sources:
        sid=s.get("source_id")
        if not sid: errors.append("source missing source_id"); continue
        if sid in ids: errors.append(f"duplicate source_id: {sid}")
        ids.add(sid)
        if not s.get("title"): errors.append(f"{sid}: missing title")
        if not s.get("source_class"): errors.append(f"{sid}: missing source_class")
        doi=norm_doi(s.get("doi"))
        if doi:
            if not DOI_RE.match(doi): errors.append(f"{sid}: malformed DOI: {doi}")
            if doi.lower() in dois: warnings.append(f"possible duplicate DOI: {sid} and {dois[doi.lower()]}")
            else: dois[doi.lower()]=sid
        url=s.get("url")
        if url:
            parsed=urlparse(url)
            if parsed.scheme not in {"http","https"} or not parsed.netloc:
                errors.append(f"{sid}: malformed URL")
    out={"sources":len(sources),"errors":errors,"warnings":warnings,"status":"FAIL" if errors else "PASS"}
    print(json.dumps(out,indent=2,ensure_ascii=False))
    return 1 if errors else 0

if __name__=="__main__":
    raise SystemExit(main())
