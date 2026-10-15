#!/usr/bin/env python3
"""Editable DOCX baseline using a validated brief; not a replacement for research/Word field refresh."""
import argparse, json, re
from pathlib import Path
from docx import Document
from docx.shared import Cm, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_CELL_VERTICAL_ALIGNMENT
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
ROOT=Path(__file__).resolve().parent.parent

def color(s): return RGBColor.from_string(s.lstrip('#'))
def field(p,code,cached=''):
 r=p.add_run(); b=OxmlElement('w:fldChar');b.set(qn('w:fldCharType'),'begin');r._r.append(b)
 t=OxmlElement('w:instrText');t.set(qn('xml:space'),'preserve');t.text=code;r._r.append(t)
 s=OxmlElement('w:fldChar');s.set(qn('w:fldCharType'),'separate');r._r.append(s)
 if cached: r=p.add_run(cached)
 r=p.add_run();e=OxmlElement('w:fldChar');e.set(qn('w:fldCharType'),'end');r._r.append(e)
def rtl(p):
 ppr=p._p.get_or_add_pPr();e=OxmlElement('w:bidi');e.set(qn('w:val'),'1');ppr.append(e)
 for r in p.runs: rpr=r._r.get_or_add_rPr();rr=OxmlElement('w:rtl');rr.set(qn('w:val'),'1');rpr.append(rr)
def shade(cell,fill):
 tcPr=cell._tc.get_or_add_tcPr();e=OxmlElement('w:shd');e.set(qn('w:fill'),fill.lstrip('#'));tcPr.append(e)
def stripe(cell,side,hexstr):
 tcPr=cell._tc.get_or_add_tcPr();b=OxmlElement('w:tcBorders');v=OxmlElement('w:'+side);v.set(qn('w:val'),'single');v.set(qn('w:sz'),'28');v.set(qn('w:color'),hexstr.lstrip('#'));b.append(v);tcPr.append(b)
def add_bookmark(p,key):
 i=str(abs(hash(key))%999999);s=OxmlElement('w:bookmarkStart');s.set(qn('w:id'),i);s.set(qn('w:name'),re.sub('[^A-Za-z0-9_]','_',key));p._p.insert(0,s);e=OxmlElement('w:bookmarkEnd');e.set(qn('w:id'),i);p._p.append(e)
def alt_last_image(d,descr):
 for e in d._element.xpath('.//wp:docPr')[-1:]: e.set('descr',descr)
def run_dir(p,text,is_rtl):
 r=p.add_run(text)
 # Place English and code in their own LTR runs even inside an Arabic paragraph.
 rr=OxmlElement('w:rtl');rr.set(qn('w:val'),'0' if re.search('[A-Za-z]',text) else '1' if is_rtl else '0');r._r.get_or_add_rPr().append(rr)
 return r

def build(payload,out,style,base_dir):
 lang=payload.get('language','en');is_rtl=lang.startswith('ar');d=Document(); sec=d.sections[0];sec.page_height=Cm(29.7);sec.page_width=Cm(21)
 margin=style.get('margin_mm',22)/10;sec.left_margin=sec.right_margin=Cm(margin);sec.top_margin=Cm(2.1);sec.bottom_margin=Cm(2.0)
 normal=d.styles['Normal'];normal.font.name='Noto Sans Arabic' if is_rtl else 'Liberation Sans';normal.font.size=Pt(style.get('body_pt',11));normal.font.color.rgb=color(style['tokens']['ink']);normal.paragraph_format.space_after=Pt(7)
 for i,pt in [('Title',29),('Heading 1',20),('Heading 2',14),('Caption',9.5)]:
  st=d.styles[i];st.font.name=normal.font.name;st.font.size=Pt(pt);st.font.color.rgb=color(style['tokens']['accent'] if i=='Heading 2' else style['tokens']['ink'])
 from docx.enum.style import WD_STYLE_TYPE
 if 'Code Inline' not in d.styles: st=d.styles.add_style('Code Inline',WD_STYLE_TYPE.CHARACTER);st.font.name='DejaVu Sans Mono';st.font.size=Pt(9);st.font.color.rgb=color(style['tokens']['accent'])
 if 'Code Block' not in d.styles: st=d.styles.add_style('Code Block',WD_STYLE_TYPE.PARAGRAPH);st.font.name='DejaVu Sans Mono';st.font.size=Pt(9)
 # Different first-page header/footer; real field-based running navigation.
 sec.different_first_page_header_footer=True
 h=sec.header.paragraphs[0];h.alignment=WD_ALIGN_PARAGRAPH.RIGHT if is_rtl else WD_ALIGN_PARAGRAPH.LEFT
 field(h,'STYLEREF "Heading 1"')
 f=sec.footer.paragraphs[0];f.alignment=WD_ALIGN_PARAGRAPH.LEFT if is_rtl else WD_ALIGN_PARAGRAPH.RIGHT
 field(f,'PAGE');f.add_run(' / ');field(f,'NUMPAGES')
 title=payload.get('title','Untitled educational guide');cover=d.add_paragraph(style='Title');cover.add_run(title)
 if is_rtl: rtl(cover);cover.alignment=WD_ALIGN_PARAGRAPH.RIGHT
 subtitle=payload.get('subtitle')
 if subtitle:
  p=d.add_paragraph(subtitle,style='Subtitle');
  if is_rtl:rtl(p)
 p=d.add_paragraph(payload.get('edition_note','Educational illustration — draft sample' if payload.get('sample') else ''))
 if is_rtl:rtl(p)
 if payload.get('cover',True):d.add_page_break()
 if payload.get('toc',True):
  h=d.add_paragraph('جدول المحتويات' if is_rtl else 'Contents',style='Heading 1');
  if is_rtl:rtl(h)
  p=d.add_paragraph();field(p,'TOC \\o "1-3" \\h \\z \\u');
  if is_rtl:rtl(p)
  d.add_page_break()
 for i,section in enumerate(payload.get('sections',[])):
  h=d.add_paragraph(section['heading'],style='Heading 1');add_bookmark(h,section.get('id',f'sec_{i}'))
  if is_rtl:rtl(h);h.alignment=WD_ALIGN_PARAGRAPH.RIGHT
  for component in section.get('content',[]):
   typ=component['type']
   if typ=='paragraph':
    p=d.add_paragraph();run_dir(p,component['text'],is_rtl)
    if component.get('citations'):p.add_run(' '+''.join(f'[{n}]' for n in component['citations']))
    if is_rtl:rtl(p);p.alignment=WD_ALIGN_PARAGRAPH.RIGHT
   elif typ=='subheading':
    p=d.add_paragraph(component['text'],style='Heading 2');
    if is_rtl:rtl(p)
   elif typ=='note':
    tbl=d.add_table(rows=1,cols=1);tbl.alignment=WD_TABLE_ALIGNMENT.CENTER;c=tbl.cell(0,0);c.vertical_alignment=WD_CELL_VERTICAL_ALIGNMENT.CENTER
    shade(c,style['tokens']['callout_bg']);stripe(c,'right' if is_rtl else 'left',style['tokens']['warning_stripe'])
    p=c.paragraphs[0];p.add_run(component.get('label','NOTE')+': ').bold=True;run_dir(p,component['text'],is_rtl)
    if is_rtl:rtl(p);p.alignment=WD_ALIGN_PARAGRAPH.RIGHT
    d.add_paragraph('')
   elif typ=='code':
    p=d.add_paragraph(style='Code Block');p.paragraph_format.left_indent=Cm(.55)
    for j,line in enumerate(component['text'].splitlines()):
     if j:p.add_run('\n')
     r=p.add_run(line);r.font.name='DejaVu Sans Mono'
   elif typ=='inline_code':
    p=d.add_paragraph()
    if component.get('before'):p.add_run(component['before']+' ')
    r=p.add_run(component['code'],style='Code Inline');rpr=r._r.get_or_add_rPr();v=OxmlElement('w:rtl');v.set(qn('w:val'),'0');rpr.append(v)
    if component.get('after'):p.add_run(' '+component['after'])
    if is_rtl:rtl(p)
   elif typ=='table':
    headers=component['headers'];table=d.add_table(rows=1,cols=len(headers));table.style='Light Shading Accent 1';table.autofit=True
    for j,name in enumerate(headers):table.rows[0].cells[j].text=str(name)
    trpr=table.rows[0]._tr.get_or_add_trPr();rep=OxmlElement('w:tblHeader');rep.set(qn('w:val'),'true');trpr.append(rep)
    for row in component['rows']:
     cells=table.add_row().cells
     for j,v in enumerate(row):cells[j].text=str(v)
   elif typ=='figure':
    path=(base_dir/component['path']).resolve()
    if not path.exists():raise FileNotFoundError(f'Figure not found: {path}')
    p=d.add_paragraph();p.alignment=WD_ALIGN_PARAGRAPH.CENTER;p.add_run().add_picture(str(path),width=Cm(component.get('width_cm',14)))
    alt_last_image(d,component['alt'])
    c=d.add_paragraph(style='Caption');c.add_run(component.get('label','Figure')+' ');field(c,'SEQ Figure \\* ARABIC');c.add_run(' — '+component['caption'])
    if is_rtl:rtl(c)
   else: raise ValueError('Unsupported component type: '+str(typ))
 if payload.get('references'):
  h=d.add_paragraph('المصادر' if is_rtl else 'References',style='Heading 1');
  if is_rtl:rtl(h)
  seen=set()
  for src in payload['references']:
   if src['id'] in seen: raise ValueError('Duplicate bibliography IDs');seen.add(src['id'])
   if not src.get('verified'):raise ValueError('Unverified source cannot appear as bibliographic fact')
   p=d.add_paragraph(f"[{src['id']}] {src['citation']}")
   if is_rtl:rtl(p)
 d.core_properties.title=title;d.core_properties.subject='Educational document'
 out.parent.mkdir(parents=True,exist_ok=True);d.save(out);return out

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--input',required=True);ap.add_argument('--output',required=True);ap.add_argument('--profile',default='visual-textbook');args=ap.parse_args()
 inp=Path(args.input).resolve();payload=json.loads(inp.read_text(encoding='utf-8'))
 sp=ROOT/'style-profiles'/f'{args.profile}.json';style=json.loads(sp.read_text())
 print(build(payload,Path(args.output).resolve(),style,inp.parent))
if __name__=='__main__':main()
