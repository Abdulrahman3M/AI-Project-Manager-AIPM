#!/usr/bin/env python3
"""Call a trusted external renderer, collect every page, and require manual QA signoff."""
import argparse,subprocess,sys,json,shutil,os
from pathlib import Path

def run(inp,out,renderer=None):
 out.mkdir(parents=True,exist_ok=True)
 if renderer:
  cmd=[sys.executable,renderer,str(inp),'--output_dir',str(out)]
 elif Path('/home/oai/skills/docx/render_docx.py').exists():
  cmd=[sys.executable,'/home/oai/skills/docx/render_docx.py',str(inp),'--output_dir',str(out)]
 elif shutil.which('libreoffice') and shutil.which('pdftoppm'):
  # Word field recalculation and authoritative Microsoft rendering NOT guaranteed.
  p=subprocess.run(['libreoffice','-env:UserInstallation=file:///tmp/ewd-render-profile','--headless','--convert-to','pdf','--outdir',str(out),str(inp)],capture_output=True,text=True)
  if p.returncode:raise RuntimeError(p.stderr or p.stdout)
  pdf=out/(inp.stem+'.pdf');cmd=['pdftoppm','-f','1','-png','-r','130',str(pdf),str(out/'page')]
 else:raise RuntimeError('No renderer: supply --renderer or install LibreOffice and pdftoppm')
 p=subprocess.run(cmd,capture_output=True,text=True)
 if p.returncode:raise RuntimeError(f'Render failed: {p.stderr}\n{p.stdout}')
 imgs=sorted(out.glob('page*.png'))
 if not imgs:raise RuntimeError('Renderer returned success but no page PNGs')
 report={'docx':str(inp),'page_count':len(imgs),'pages':[i.name for i in imgs], 'automatic_render':'PASS', 'visual_qa':'PENDING MANUAL EVERY-PAGE REVIEW','toc_fields_refreshed':'UNVERIFIED — open in field-aware Word app', 'signed_off':False}
 (out/'qa-report.json').write_text(json.dumps(report,indent=2)+'\n');return report
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('docx');p.add_argument('--output-dir',required=True);p.add_argument('--renderer');a=p.parse_args();print(json.dumps(run(Path(a.docx).resolve(),Path(a.output_dir).resolve(),a.renderer),indent=2))
