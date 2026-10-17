"""Offline regression tests for original Doc to MD converter."""
import importlib.util
import io
from pathlib import Path
import tempfile
import unittest
import unittest.mock
import zipfile
import json

SRC=Path(__file__).parents[1]/'scripts'/'doc_to_md.py'
spec=importlib.util.spec_from_file_location('doc_to_md',SRC)
mod=importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

def make_zip(files):
    buf=io.BytesIO()
    with zipfile.ZipFile(buf,'w',zipfile.ZIP_DEFLATED) as z:
        for name,data in files.items(): z.writestr(name,data)
    return buf.getvalue()

class ConversionTests(unittest.TestCase):
    def setUp(self): self.c=mod.Conversion()
    def test_english_arabic_cyrillic(self):
        s='العَرَبِيَّة, Привет, hello'
        self.assertIn(s,self.c.convert('sample.txt',s.encode()))
    def test_html_headings_links(self):
        output=self.c.convert('x.html',b'<html><head><title>hidden</title></head><body><h1>Title</h1><p>Hi <a href="https://example.org">link</a></p></body></html>')
        self.assertIn('# Title',output)
        self.assertIn('[link](https://example.org)',output)
        self.assertNotIn('hidden',output)
    def test_csv_empty_and_literals(self):
        output=self.c.convert('x.csv',b'Name,Value\nNull,NA\nZero,0012\nMissing,')
        self.assertIn('Null | NA',output)
        self.assertIn('0012',output)
        self.assertIn('Missing |',output)
    def test_json_unicode(self):
        self.assertIn('مرحباً',self.c.convert('x.json','{"x":"مرحباً"}'.encode()))
    def test_docx_math_and_nested_table(self):
        body='<w:p><w:pPr><w:pStyle w:val="Heading1"/></w:pPr><w:r><w:t>Introduction</w:t></w:r></w:p><w:p><w:r><w:t>Equation</w:t></w:r><m:oMath><m:r><m:t>x</m:t></m:r></m:oMath></w:p><w:tbl><w:tr><w:tc><w:p><w:r><w:t>A</w:t></w:r></w:p></w:tc><w:tc><w:p><w:r><w:t>B</w:t></w:r></w:p></w:tc></w:tr></w:tbl>'
        xml=f'<w:document xmlns:w="{mod.W[1:-1]}" xmlns:m="{mod.M[1:-1]}"><w:body>{body}</w:body></w:document>'
        txt=self.c.convert('a.docx',make_zip({'word/document.xml':xml}))
        self.assertIn('# Introduction',txt)
        self.assertIn('Equation',txt)
        self.assertIn('[MATH: REVIEW REQUIRED]',txt)
        self.assertIn('| A | B |',txt)
        self.assertTrue(any(x['code']=='DOCX_MATH' for x in self.c.findings))
    def test_xlsx_preserves_null_and_integer_raw(self):
        sheets=f'<worksheet xmlns="{mod.S[1:-1]}"><sheetData><row r="1"><c r="A1" t="inlineStr"><is><t>NA</t></is></c><c r="B1" t="n"><v>10000000000001234</v></c></row><row r="2"><c r="A2" t="inlineStr"><is><t>NULL</t></is></c><c r="B2" t="inlineStr"><is><t>00012</t></is></c></row></sheetData></worksheet>'
        txt=self.c.convert('book.xlsx',make_zip({'xl/worksheets/sheet1.xml':sheets}))
        for value in ('NA','NULL','10000000000001234','00012'): self.assertIn(value,txt)
    def test_pptx_order(self):
        def shape(x,y,t): return f'<p:sp><p:spPr><a:xfrm><a:off x="{x}" y="{y}"/></a:xfrm></p:spPr><p:txBody><a:p><a:r><a:t>{t}</a:t></a:r></a:p></p:txBody></p:sp>'
        xml=f'<p:sld xmlns:p="{mod.P[1:-1]}" xmlns:a="{mod.A[1:-1]}"><p:cSld><p:spTree>{shape(1000000,0,"RIGHT")}{shape(0,0,"LEFT")}</p:spTree></p:cSld></p:sld>'
        result=self.c.convert('deck.pptx',make_zip({'ppt/slides/slide1.xml':xml}))
        self.assertLess(result.index('LEFT'),result.index('RIGHT'))
        self.assertTrue(any(x['code']=='PPTX_ORDER' for x in self.c.findings))
    def test_zip_slip(self):
        blob=make_zip({'../danger.txt':'secret'})
        with self.assertRaises(ValueError): self.c.convert('bundle.zip',blob)
    def test_xml_dtd_rejected(self):
        with self.assertRaises(ValueError): self.c.convert('a.xml',b'<!DOCTYPE doc [<!ENTITY x SYSTEM "file:///etc/passwd">]><doc>&x;</doc>')
    def test_missing_ocr_block(self):
        with unittest.mock.patch.object(mod.shutil,'which',return_value=None):
            self.c.convert('x.png',b'not a real image')
        self.assertIn('block',[x['severity'] for x in self.c.findings])
    def test_cli_audit(self):
        with tempfile.TemporaryDirectory() as td:
            file=Path(td)/'content.txt';file.write_text('السلام عليكم hello',encoding='utf-8')
            self.assertEqual(mod.run([str(file)]),0)
            report=json.loads(Path(str(file.with_suffix('.md'))+'.audit.json').read_text())
            self.assertEqual(report['status'],'PASS')
            self.assertIn('sha256',str(report))
    def test_unsupported_not_silently_accepted(self):
        self.assertEqual(self.c.convert('file.exe',b'123'),'')
        self.assertTrue(any(x['severity']=='block' for x in self.c.findings))

    def test_whitespace_preserved_in_markdown_escape(self):
        self.assertIn('a  b',mod.md('a  b'))
    def test_basic_html_table_has_header_separator(self):
        txt=self.c.convert('x.html',b'<table><tr><th>Key</th><th>Value</th></tr><tr><td>A</td><td>B</td></tr></table>')
        self.assertIn('| --- | --- |',txt)
        self.assertIn('| A | B |',txt)
        self.assertTrue(any(x['code']=='HTML_TABLE' for x in self.c.findings))
    def test_docx_deleted_text_not_accepted(self):
        xml=f'<w:document xmlns:w="{mod.W[1:-1]}"><w:body><w:p><w:del><w:r><w:delText>UNSAFE_DELETED</w:delText></w:r></w:del><w:r><w:t>CURRENT</w:t></w:r></w:p></w:body></w:document>'
        txt=self.c.convert('file.docx',make_zip({'word/document.xml':xml}))
        self.assertIn('CURRENT',txt)
        self.assertNotIn('UNSAFE_DELETED',txt)
        self.assertTrue(any(x['code']=='DOCX_REVISIONS' for x in self.c.findings))
    def test_xlsx_sheet_names_are_not_silently_invented(self):
        sheet=f'<worksheet xmlns="{mod.S[1:-1]}"><sheetData><row r="1"><c r="A1"><v>55</v></c></row></sheetData></worksheet>'
        book=f'<workbook xmlns="{mod.S[1:-1]}"><sheets><sheet name="Finance" sheetId="1"/></sheets></workbook>'
        self.c.convert('x.xlsx',make_zip({'xl/worksheets/sheet1.xml':sheet,'xl/workbook.xml':book}))
        self.assertTrue(any(x['code']=='XLSX_SHEET_NAMES' for x in self.c.findings))
    def test_epub_extraction_requires_spine_review(self):
        result=self.c.convert('book.epub',make_zip({'OEBPS/chapter1.xhtml':'<html><body><h1>One</h1></body></html>'}))
        self.assertIn('One',result)
        self.assertTrue(any(x['code']=='EPUB_SPINE' for x in self.c.findings))
    def test_audio_needs_local_model(self):
        result=self.c.convert('voice.mp3',b'audio')
        self.assertEqual(result,'')
        self.assertTrue(any(x['severity']=='block' for x in self.c.findings))
    def test_nested_zip_member_error_blocks(self):
        inner=make_zip({'../unsafe.xml':'<x/>'})
        text=self.c.convert('outer.zip',make_zip({'inner.zip':inner}))
        self.assertTrue(any(x['code']=='ARCHIVE_MEMBER' and x['severity']=='block' for x in self.c.findings))
    def test_archive_member_count_limit(self):
        blob=make_zip({f'{i}.txt':'x' for i in range(mod.MAX_ENTRIES+1)})
        with self.assertRaises(ValueError): self.c.convert('archive.zip',blob)

if __name__=='__main__':unittest.main()
