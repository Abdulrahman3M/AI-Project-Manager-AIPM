#!/usr/bin/env python3
"""Gate for diagrams embedded in educational Word documents.

The mandatory 09-mindmap example is checked geometrically, not just XML-parsed.
For all user-created DOCX diagrams also render each page and perform manual
text/line occlusion review (a general SVG geometric proof is not available).
"""
from pathlib import Path
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
SVG = ROOT / "assets" / "visual-examples" / "09-mindmap.svg"
NS = "{http://www.w3.org/2000/svg}"

def inside(x, y, rect, margin=2):
    rx, ry, rw, rh = rect
    return rx + margin < x < rx + rw - margin and ry + margin < y < ry + rh - margin

def segment_crosses_box(x1, y1, x2, y2, box, samples=1000):
    return any(inside(x1 + (x2-x1)*i/samples, y1 + (y2-y1)*i/samples, box)
               for i in range(1, samples))

def validate_mindmap():
    tree = ET.parse(SVG)
    root = tree.getroot()
    groups = [(356,221,196,73), (138,131,180,62), (576,132,180,62),
              (144,351,180,62), (585,350,180,62)]
    links = []
    for element in root:
        if element.tag != NS+"line" or element.attrib.get("stroke") != "#237A7A":
            continue
        x1,y1,x2,y2 = (float(element.attrib[k]) for k in ("x1","y1","x2","y2"))
        links.append((x1,y1,x2,y2))
        for box in groups:
            assert not segment_crosses_box(x1,y1,x2,y2,box), (
                f"Connector intersects node interior: {(x1,y1,x2,y2)}, {box}"
            )
    assert len(links) == 4, f"Expected 4 routed mindmap connectors, got {len(links)}"
    expected={(381,221,304,193),(527,221,591,194),(380,294,306,351),(528,294,603,350)}
    assert {tuple(map(int, link)) for link in links} == expected
    center = next(e for e in root if e.tag == NS+"text" and (e.text or "").strip()=="CONCEPT")
    assert float(center.get("x")) == 454 and float(center.get("y")) == 265
    assert all(not segment_crosses_box(*l,(403,244,105,30)) for l in links), "Central text occluded"
    # Protect rendering order: edges first, then the central fill and label.
    children=list(root)
    assert max(children.index(e) for e in root if e.tag == NS+"line" and e.get("stroke")=="#237A7A") < next(
      i for i,e in enumerate(children) if e.tag == NS+"text" and (e.text or "").strip()=="CONCEPT"
    )
    print("PASS: mind map connectors stop at node boundaries without obscuring labels.")

if __name__=="__main__":
    validate_mindmap()
