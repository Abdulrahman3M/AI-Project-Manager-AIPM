"""Unit/smoke tests for shipped v3 utilities and format contracts."""
import importlib.util,json,subprocess,sys
from pathlib import Path
from lxml import etree
ROOT=Path(__file__).resolve().parents[1]
def load(name):
 s=importlib.util.spec_from_file_location(name,ROOT/'scripts'/f'{name}.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m

def test_style_profiles_complete():
 names=('academic-research','visual-textbook','technical-guide','infobank-style')
 for n in names:
  d=json.loads((ROOT/'style-profiles'/f'{n}.json').read_text())
  assert d['version']=='3.0.0' and d['body_pt']>=10 and d['tokens']['callout_bg']

def test_gallery_all_26_and_svg_parse():
 import re
 text=(ROOT/'examples'/'ILLUSTRATED_PLAYBOOK.md').read_text()
 for i in range(1,27):
  assets=list((ROOT/'assets'/'visual-examples').glob(f'{i:02d}-*.svg'))
  assert len(assets)==1 and assets[0].with_suffix('.png').exists()
  etree.parse(str(assets[0])); assert assets[0].name in text

def test_build_audit_docx(tmp_path):
 cmd=[sys.executable,str(ROOT/'scripts'/'build_document.py'),'--input',str(ROOT/'examples'/'sample-document.json'),'--output',str(tmp_path/'built.docx')]
 subprocess.run(cmd,check=True,capture_output=True,text=True)
 a=load('audit_docx').audit(tmp_path/'built.docx',True,True)
 assert a['status']=='PASS',a
 assert any('TOC' in i for i in a['facts']['fields']) and a['facts']['page_field_present']

def test_reject_unverified_bibliography(tmp_path):
 from docx import Document
 doc=load('build_document');data={'title':'Test','sections':[],'references':[{'id':'1','citation':'Unknown','verified':False}]}
 try:doc.build(data,tmp_path/'bad.docx',json.loads((ROOT/'style-profiles'/'academic-research.json').read_text()),ROOT)
 except ValueError:return
 assert False,'Unverified source passed validation'

def test_safe_html_companion(tmp_path):
 dest=tmp_path/'companion.html'
 subprocess.run([sys.executable,str(ROOT/'scripts'/'export_html_companion.py'),'--input',str(ROOT/'examples'/'interactive-companion.json'),'--output',str(dest)],check=True,capture_output=True)
 html=dest.read_text();assert '<details>' in html and 'Separate, accessible HTML companion' in html

def test_visual_register_validation_cli():
 r=subprocess.run([sys.executable,str(ROOT/'scripts'/'validate_visual_register.py'),str(ROOT/'examples'/'visual-register.json')],capture_output=True,text=True)
 assert r.returncode==0,r.stdout+r.stderr

def test_arabic_word_note_border_is_right(tmp_path):
 import zipfile
 from docx.oxml.ns import qn
 b=load('build_document');data=json.loads((ROOT/'examples'/'sample-document-ar.json').read_text())
 st=json.loads((ROOT/'style-profiles'/'infobank-style.json').read_text())
 path=b.build(data,tmp_path/'ar.docx',st,(ROOT/'examples'))
 with zipfile.ZipFile(path) as z: xml=z.read('word/document.xml').decode('utf-8')
 assert '<w:right' in xml and 'w:bidi' in xml and '<w:rtl' in xml
 a=load('audit_docx').audit(path,require_rtl=True)
 assert a['status']=='PASS',a


def test_mindmap_edges_never_cross_text_or_cards():
    import sys
    sys.path.insert(0, str(ROOT/'scripts'))
    from validate_diagram_geometry import validate_mindmap
    validate_mindmap()
