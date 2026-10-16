#!/usr/bin/env python3
"""Baseline structural audit; does NOT certify layout, scientific accuracy or Word field refresh."""
import argparse,json,re,zipfile,sys
from pathlib import Path
from lxml import etree
W='{http://schemas.openxmlformats.org/wordprocessingml/2006/main}'
WP='{http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing}'
def audit(path,require_toc=False,require_alt=False):
 issues=[];warnings=[];facts={};path=Path(path)
 with zipfile.ZipFile(path) as z:
  if z.testzip():issues.append('ZIP CRC error')
  contents=set(z.namelist());must=['word/document.xml','word/styles.xml','word/_rels/document.xml.rels']
  for x in must:
   if x not in contents:issues.append('Missing '+x)
  if issues:return {'status':'FAIL','critical':issues,'warnings':warnings,'facts':facts}
  root=etree.fromstring(z.read('word/document.xml'));nodes=root.iter()
  fields=[(n.text or '').strip() for n in root.iter(W+'instrText')];joined=' '.join(fields)
  heading_styles={str(e.get(W+'val')) for e in root.iter(W+'pStyle') if (e.get(W+'val') or '').startswith('Heading')}
  facts['headings']=sorted(heading_styles);facts['fields']=fields
  if not heading_styles:warnings.append('No structured heading styles detected')
  if require_toc and not re.search(r'\bTOC\b',joined):issues.append('Missing real TOC field')
  image_props=list(root.iter(WP+'docPr'));facts['images']=len(image_props)
  if require_alt:
   missing=[i for i,p in enumerate(image_props,1) if not (p.get('descr') or p.get('title'))]
   if missing:issues.append('Images lack alt text at positions: '+','.join(map(str,missing)))
  if 'word/footnotes.xml' in contents:facts['footnotes_present']=True
  # Check every embedded relationship target without assuming external links are files.
  relroot=etree.fromstring(z.read('word/_rels/document.xml.rels'))
  for r in relroot:
   target=r.get('Target','');mode=r.get('TargetMode','Internal');rtype=r.get('Type','')
   if mode!='External' and ('/image' in rtype or '/chart' in rtype) and ('word/'+target.lstrip('/')) not in contents:
    issues.append('Broken media relationship: '+target)
  texts=' '.join((n.text or '') for n in root.iter(W+'t'))
  ids=set(re.findall(r'\[(\d+)\]',texts));listed=set(re.findall(r'^\[(\d+)\]',texts,re.M)) # approximate only
  facts['numbered_citations']=sorted(ids);facts['page_field_present']=False
  for member in ('word/footer1.xml','word/footer2.xml'):
   if member in contents:
    footer=etree.fromstring(z.read(member));fs=' '.join((x.text or '') for x in footer.iter(W+'instrText'))
    if 'PAGE' in fs:facts['page_field_present']=True
  if len(texts)<100:warnings.append('Document has less than 100 characters of visible text')
  if any(x in texts for x in ('REPLACE WITH REAL VERIFIED SOURCE','[TODO]')):issues.append('Unresolved editorial placeholder in document text')
 return {'status':'PASS' if not issues else 'FAIL','critical':issues,'warnings':warnings,'facts':facts,'scope':'Only baseline OOXML structure; manual full-page and evidence audits still required'}
def main():
 p=argparse.ArgumentParser();p.add_argument('docx');p.add_argument('--require-toc',action='store_true');p.add_argument('--require-alt',action='store_true');p.add_argument('--json');args=p.parse_args()
 x=audit(args.docx,args.require_toc,args.require_alt);result=json.dumps(x,indent=2,ensure_ascii=False)
 if args.json:Path(args.json).write_text(result+'\n',encoding='utf-8')
 print(result);sys.exit(0 if x['status']=='PASS' else 1)
if __name__=='__main__':main()
