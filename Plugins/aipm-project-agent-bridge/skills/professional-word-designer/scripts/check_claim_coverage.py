#!/usr/bin/env python3
"""Check a Claim–Evidence Matrix for blocking unsupported claims."""
from __future__ import annotations
import argparse, json
from pathlib import Path

SUPPORTED={"VERIFIED","SUPPORTED-WITH-LIMITATION","DISPUTED"}

def main() -> int:
    p=argparse.ArgumentParser()
    p.add_argument("matrix")
    p.add_argument("--json-report")
    args=p.parse_args()
    data=json.loads(Path(args.matrix).read_text(encoding="utf-8"))
    claims=data.get("claims",[])
    ids=set()
    errors=[]
    blocking=[]
    for c in claims:
        cid=c.get("claim_id")
        if not cid: errors.append("claim missing claim_id"); continue
        if cid in ids: errors.append(f"duplicate claim_id: {cid}")
        ids.add(cid)
        imp=c.get("importance")
        status=c.get("status")
        supporting=c.get("supporting_source_ids",[])
        if status in SUPPORTED and not supporting:
            errors.append(f"{cid}: status {status} but no supporting_source_ids")
        if imp in {"critical","major"} and status=="UNVERIFIED":
            blocking.append(cid)
    report={"claims":len(claims),"errors":errors,"blocking_unverified":blocking,
            "status":"FAIL" if errors or blocking else "PASS"}
    print(json.dumps(report,indent=2,ensure_ascii=False))
    if args.json_report:
        Path(args.json_report).write_text(json.dumps(report,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    return 1 if report["status"]=="FAIL" else 0

if __name__=="__main__":
    raise SystemExit(main())
