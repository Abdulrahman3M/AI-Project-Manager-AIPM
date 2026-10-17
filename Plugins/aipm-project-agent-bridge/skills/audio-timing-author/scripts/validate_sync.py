#!/usr/bin/env python3
import json, sys
from pathlib import Path
def fail(msg):
    print("FAIL:", msg); raise SystemExit(1)
def main():
    if len(sys.argv)!=2: fail("Usage: validate_sync.py FILE.sync.json")
    data=json.loads(Path(sys.argv[1]).read_text(encoding="utf-8-sig"))
    if data.get("schema")!="audio-sync": fail("schema must be audio-sync")
    dur=data["audio"]["duration_ms"]; prev_end=-1
    for i,seg in enumerate(data["segments"],1):
        s,e=seg["start_ms"],seg["end_ms"]
        if not (0<=s<e<=dur): fail(f"segment {i} invalid range {s}..{e} / {dur}")
        if s<prev_end: fail(f"segment {i} overlaps previous segment")
        prev_end=e; wprev=s
        for j,w in enumerate(seg["words"],1):
            ws,we=w["start_ms"],w["end_ms"]
            if not (s<=ws<we<=e): fail(f"segment {i} word {j} outside parent")
            if ws<wprev: fail(f"segment {i} word {j} is not monotonic")
            wprev=we
    print("PASS: timing structure is valid")
if __name__=="__main__": main()
