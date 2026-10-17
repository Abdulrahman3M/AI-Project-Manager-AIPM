#!/usr/bin/env python3
"""Aggregate baseline research QA from source, claim and example ledgers."""
from __future__ import annotations
import argparse, json
from pathlib import Path

def read(path):
    return json.loads(Path(path).read_text(encoding="utf-8")) if path else None

def main()->int:
    ap=argparse.ArgumentParser()
    ap.add_argument("--sources",required=True)
    ap.add_argument("--claims",required=True)
    ap.add_argument("--examples")
    ap.add_argument("--chapters")
    ap.add_argument("--output")
    a=ap.parse_args()
    sources=read(a.sources).get("sources",[])
    claims=read(a.claims).get("claims",[])
    coverage=read(a.examples) if a.examples else None
    chapters=read(a.chapters) if a.chapters else None
    critical_major=[c for c in claims if c.get("importance") in {"critical","major"}]
    unsupported=[c.get("claim_id") for c in critical_major if c.get("status")=="UNVERIFIED"]
    disputed=[c.get("claim_id") for c in claims if c.get("status")=="DISPUTED"]
    source_ids={s.get("source_id") for s in sources}
    missing_refs=[]
    for c in claims:
        for sid in c.get("supporting_source_ids",[])+c.get("contradictory_source_ids",[]):
            if sid not in source_ids: missing_refs.append({"claim":c.get("claim_id"),"missing_source":sid})
    example_pct=None
    if coverage:
        reqs=coverage.get("requirements",[])
        mapped={e.get("requirement_id") for e in coverage.get("examples",[])}
        example_pct=0 if not reqs else round(sum(1 for r in reqs if r.get("id") in mapped)/len(reqs)*100,1)
    blockers=[]
    if unsupported: blockers.append(f"{len(unsupported)} unverified critical/major claim(s)")
    if missing_refs: blockers.append(f"{len(missing_refs)} claim reference(s) point to missing source IDs")
    if example_pct is not None and example_pct<100: blockers.append("normative example coverage below 100%")
    metrics={"sources":len(sources),"claims":len(claims),"critical_major_claims":len(critical_major),
             "unverified_critical_major":len(unsupported),"disputed_claims":len(disputed),
             "missing_source_links":len(missing_refs),"example_coverage_percent":example_pct,
             "chapters":len(chapters.get("chapters",[])) if chapters else None}
    report={"status":"FAIL" if blockers else "PASS","metrics":metrics,"blockers":blockers,
            "warnings":["This baseline QA does not replace factual verification, Word field refresh, accessibility review, or page-by-page visual inspection."]}
    txt=json.dumps(report,indent=2,ensure_ascii=False)+"\n"
    print(txt,end="")
    if a.output: Path(a.output).write_text(txt,encoding="utf-8")
    return 1 if blockers else 0

if __name__=="__main__":
    raise SystemExit(main())
