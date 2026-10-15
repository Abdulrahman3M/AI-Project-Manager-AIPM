#!/usr/bin/env python3
"""Convert timed SRT into an audio-sync JSON skeleton. Never fabricates word timings."""
import json,re,sys
from pathlib import Path
TIME_RE=re.compile(r"(\d\d):(\d\d):(\d\d),(\d\d\d)")
FONT_RE=re.compile(r"</?font[^>]*>",re.I)
def ms(t):
    h,m,s,x=map(int,TIME_RE.fullmatch(t).groups()); return ((h*60+m)*60+s)*1000+x
def main():
    if len(sys.argv)!=4: raise SystemExit("Usage: srt_to_sync_skeleton.py INPUT.srt AUDIO_FILE DURATION_MS")
    src,audio,duration=Path(sys.argv[1]),sys.argv[2],int(sys.argv[3])
    blocks=re.split(r"\r?\n\r?\n+",src.read_text(encoding="utf-8-sig").strip()); segs=[]
    for n,b in enumerate(blocks,1):
        lines=b.splitlines(); a,btime=[x.strip() for x in lines[1].split("-->")]
        txt=FONT_RE.sub(""," ".join(lines[2:])).strip()
        segs.append({"id":f"seg-{n:03d}","speaker":None,"start_ms":ms(a),"end_ms":ms(btime),"text":txt,"normalized_text":txt,"words":[],"review":"needs_review","confidence":None})
    out={"schema":"audio-sync","version":"1.0.0","audio":{"file":audio,"duration_ms":duration},"alignment":{"language":"und","method":"srt-skeleton","transcript_is_authoritative":True,"speaker_labels_consume_timing":False,"review":"needs_review"},"segments":segs}
    dest=src.with_suffix(".sync.json"); dest.write_text(json.dumps(out,ensure_ascii=False,indent=2)+"\n",encoding="utf-8"); print(dest)
if __name__=="__main__": main()
