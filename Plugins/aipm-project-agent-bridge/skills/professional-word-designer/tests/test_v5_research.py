import json
import subprocess
import sys
from pathlib import Path
from zipfile import ZipFile

ROOT=Path(__file__).resolve().parents[1]

def run_script(name,*args):
    return subprocess.run([sys.executable,str(ROOT/"scripts"/name),*map(str,args)],capture_output=True,text=True)

def test_normative_example_coverage():
    r=run_script("validate_example_coverage.py")
    assert r.returncode==0, r.stdout+r.stderr
    assert "Coverage: 100.0%" in r.stdout

def test_claim_coverage_sample_passes():
    r=run_script("check_claim_coverage.py",ROOT/"examples"/"sample-claim-evidence.json")
    assert r.returncode==0, r.stdout+r.stderr

def test_reference_metadata_sample_passes():
    r=run_script("validate_reference_metadata.py",ROOT/"examples"/"sample-source-ledger-v5.json")
    assert r.returncode==0, r.stdout+r.stderr

def test_chapter_index_uses_external_relative_links(tmp_path):
    manifest=json.loads((ROOT/"examples"/"sample-chapter-manifest.json").read_text(encoding="utf-8"))
    manifest["index_file"]="00-Index.docx"
    mp=tmp_path/"chapter-manifest.json"
    mp.write_text(json.dumps(manifest),encoding="utf-8")
    for c in manifest["chapters"]:
        (tmp_path/c["file"]).write_bytes(b"placeholder")
    out=tmp_path/"00-Index.docx"
    r=run_script("build_chapter_index.py",mp,"--output",out,"--check-files")
    assert r.returncode==0, r.stdout+r.stderr
    assert out.is_file()
    with ZipFile(out) as z:
        rels=z.read("word/_rels/document.xml.rels").decode("utf-8")
    for c in manifest["chapters"]:
        assert c["file"] in rels
    assert 'TargetMode="External"' in rels
