#!/usr/bin/env python3
"""Doc to MD: original, fail-closed, offline-first document extraction.

No MarkItDown source code is used. Optional parsers are separately installed.
"""
from __future__ import annotations
import argparse
import csv
import hashlib
import html
from html.parser import HTMLParser
import io
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET
import zipfile

MAX_FILE = 100 * 1024 * 1024
MAX_MEMBER = 40 * 1024 * 1024
MAX_ARCHIVE = 200 * 1024 * 1024
MAX_ENTRIES = 3000
W = '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}'
A = '{http://schemas.openxmlformats.org/drawingml/2006/main}'
P = '{http://schemas.openxmlformats.org/presentationml/2006/main}'
S = '{http://schemas.openxmlformats.org/spreadsheetml/2006/main}'
M = '{http://schemas.openxmlformats.org/officeDocument/2006/math}'
XHTML = '{http://www.w3.org/1999/xhtml}'

def compact(s):
    return re.sub(r'[ \t]+', ' ', s or '').strip()

def md(s):
    return re.sub(r'([\\`*_{}\[\]<>|])', r'\\\1', str(s).strip())

def xml_bytes(data):
    if re.search(rb'<!\s*(?:DOCTYPE|ENTITY)', data, re.I):
        raise ValueError('XML DTD/entities are disabled')
    return ET.fromstring(data)

def zip_members(blob):
    z = zipfile.ZipFile(io.BytesIO(blob))
    infos = z.infolist()
    if len(infos) > MAX_ENTRIES:
        raise ValueError('Too many archive entries')
    total = 0
    for item in infos:
        name = item.filename.replace('\\', '/')
        if name.startswith('/') or '..' in name.split('/') or re.match(r'^[A-Za-z]:', name):
            raise ValueError('Unsafe archive path')
        if ((item.external_attr >> 16) & 0o170000) == 0o120000:
            raise ValueError('Archive symlink is not allowed')
        total += item.file_size
        if item.file_size > MAX_MEMBER or total > MAX_ARCHIVE:
            raise ValueError('Archive exceeds decompression limits')
    return z

def text_of(node):
    return ''.join((e.text or '') for e in node.iter() if e.tag in {W+'t', A+'t', S+'t', M+'t'})

def column_name(n):
    v = ''
    while n:
        n, r = divmod(n - 1, 26)
        v = chr(65+r) + v
    return v

class MDHTML(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.out = []
        self.links = []
        self.skip = 0
        self.in_pre = 0
        self.base = None
        self.table_depth = 0
        self.table_row_count = 0
        self.table_cell_count = 0
    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag in ('script','style','head'):
            self.skip += 1
            return
        if self.skip:
            return
        if tag == 'base' and a.get('href'):
            self.base = a['href']
        if tag in ['h1','h2','h3','h4','h5','h6']:
            self.out.append('\n\n'+'#'*int(tag[1])+' ')
        elif tag in ('p','div','section','article','blockquote'):
            self.out.append('\n\n')
        elif tag == 'br':
            self.out.append('  \n')
        elif tag == 'li':
            self.out.append('\n- ')
        elif tag in ('strong','b'): self.out.append('**')
        elif tag in ('em','i'): self.out.append('*')
        elif tag == 'pre':
            self.in_pre += 1
            self.out.append('\n\n```\n')
        elif tag == 'a':
            self.out.append('[')
            self.links.append(a.get('href',''))
        elif tag == 'img':
            self.out.append('!['+md(a.get('alt',''))+']('+a.get('src','')+')')
        elif tag == 'tr': self.out.append('\n| '); self.table_cell_count = 0
        elif tag in ('td','th'): self.table_cell_count += 1
        elif tag == 'table': self.table_depth += 1; self.table_row_count = 0
    def handle_endtag(self, tag):
        if tag in ('script','style','head'):
            self.skip = max(0,self.skip-1)
            return
        if self.skip: return
        if tag in ('strong','b'): self.out.append('**')
        elif tag in ('em','i'): self.out.append('*')
        elif tag == 'a':
            target=self.links.pop() if self.links else ''
            self.out.append(']('+target+')')
        elif tag == 'pre': self.in_pre=max(0,self.in_pre-1); self.out.append('\n```\n')
        elif tag in ('td','th'): self.out.append(' | ')
        elif tag == 'tr':
            self.table_row_count += 1
            if self.table_row_count == 1 and self.table_cell_count:
                self.out.append('\n| '+' | '.join(['---']*self.table_cell_count)+' |')
        elif tag == 'table': self.table_depth=max(0,self.table_depth-1); self.out.append('\n\n')
    def handle_data(self,data):
        if not self.skip: self.out.append(data if self.in_pre else html.unescape(data))
    def render(self):
        return re.sub(r'\n{3,}', '\n\n', ''.join(self.out)).strip()

class Conversion:
    def __init__(self, ocr_lang='eng', audio_model=None):
        self.findings=[]
        self.stats={'objects_seen':0,'objects_emitted':0}
        self.ocr_lang=ocr_lang
        self.audio_model=audio_model
        self.depth=0
    def flag(self,code,message,severity='review'):
        self.findings.append({'code':code,'message':message,'severity':severity})
    def emit(self,value):
        self.stats['objects_seen']+=1
        if compact(value): self.stats['objects_emitted']+=1
        else: self.flag('EMPTY_OBJECT','Expected object had no extractable text')
        return value
    def convert(self,name,data):
        if len(data)>MAX_FILE: raise ValueError('Input exceeds size limit')
        ext=Path(name).suffix.lower()
        if ext in ('.txt','.md','.markdown','.log','.rst','.yaml','.yml','.toml'):
            return data.decode('utf-8-sig',errors='replace')
        if ext in ('.json','.jsonl'):
            t=data.decode('utf-8-sig')
            if ext=='.jsonl': return '\n'.join(json.dumps(json.loads(line),ensure_ascii=False) for line in t.splitlines() if line.strip())
            return '```json\n'+json.dumps(json.loads(t),ensure_ascii=False,indent=2)+'\n```'
        if ext in ('.csv','.tsv'):
            rows=list(csv.reader(io.StringIO(data.decode('utf-8-sig')),delimiter='\t' if ext=='.tsv' else ','))
            if not rows: return ''
            width=max(map(len,rows))
            safe=lambda x: md(x).replace('|','\\|').replace('\n','<br>')
            out=[]
            for i,row in enumerate(rows):
                out.append('| '+' | '.join(safe(x) for x in (row+['']*width)[:width])+' |')
                if i==0: out.append('| '+' | '.join(['---']*width)+' |')
            return '\n'.join(out)
        if ext in ('.html','.htm','.xhtml'):
            parser=MDHTML(); parser.feed(data.decode('utf-8-sig',errors='replace'))
            if parser.base: self.flag('HTML_BASE','Relative URLs may require resolution against HTML base URL')
            if '<table' in data.decode('utf-8',errors='ignore').lower(): self.flag('HTML_TABLE','Complex HTML table spans require manual verification')
            return parser.render()
        if ext=='.xml':
            elem=xml_bytes(data)
            return '```xml\n'+ET.tostring(elem,encoding='unicode')+'\n```'
        if ext=='.docx': return self.docx(data)
        if ext=='.pptx': return self.pptx(data)
        if ext=='.xlsx': return self.xlsx(data)
        if ext=='.xls': return self.xls(data)
        if ext=='.epub': return self.epub(data)
        if ext=='.zip': return self.archive(data)
        if ext=='.pdf': return self.pdf(data)
        if ext in ('.png','.jpg','.jpeg','.tiff','.tif','.bmp','.webp'): return self.image(data,ext)
        if ext in ('.mp3','.wav','.m4a','.ogg','.flac','.mp4','.mov','.mkv'): return self.audio(data,ext)
        self.flag('UNSUPPORTED',f'No converter for {ext or "extensionless file"}','block')
        return ''
    def docx(self,data):
        z=zip_members(data)
        root=xml_bytes(z.read('word/document.xml'))
        body=root.find(W+'body')
        if body is None: raise ValueError('DOCX has no body')
        out=[]
        for node in body:
            if node.tag==W+'p':
                value=text_of(node)
                pstyle=node.find('./'+W+'pPr/'+W+'pStyle')
                style=pstyle.get(W+'val','') if pstyle is not None else ''
                level=re.search(r'Heading\s*([1-9])',style,re.I)
                if level:
                    n=int(level.group(1))
                    if n>6: self.flag('DEEP_HEADING',f'Heading level {n} represented as bold paragraph')
                    value=('#'*n+' ' if n<=6 else '**')+md(value)+('**' if n>6 else '')
                elif node.find('.//'+W+'numPr') is not None: value='- '+md(value)
                else: value=md(value)
                if node.find('.//'+M+'oMath') is not None or node.find('.//'+M+'oMathPara') is not None:
                    self.flag('DOCX_MATH','OMML math flattened to text; verify formula visually')
                    value+=' [MATH: REVIEW REQUIRED]'
                if node.find('.//'+W+'drawing') is not None: self.flag('DOCX_IMAGE','Embedded image requires independent OCR/alt-text verification')
                if node.find('.//'+W+'hyperlink') is not None: self.flag('DOCX_LINK','Hyperlink relationship may not be preserved; verify targets')
                if node.find('.//'+W+'txbxContent') is not None: self.flag('DOCX_TEXTBOX','Textbox may be omitted or reordered')
                if value.strip(): out.append(self.emit(value))
            elif node.tag==W+'tbl':
                rows=[]
                for tr in node.findall(W+'tr'):
                    cells=[md(' '.join(text_of(p) for p in tc.findall('.//'+W+'p'))).replace('|','\\|') for tc in tr.findall(W+'tc')]
                    rows.append(cells)
                if rows:
                    width=max(map(len,rows))
                    out.append(self.emit('\n'.join('| '+' | '.join((r+['']*width)[:width])+' |' for r in rows[:1])+'\n| '+' | '.join(['---']*width)+' |'+''.join('\n| '+' | '.join((r+['']*width)[:width])+' |' for r in rows[1:])))
                if node.find('.//'+W+'gridSpan') is not None or node.find('.//'+W+'vMerge') is not None:
                    self.flag('DOCX_MERGE','Merged table cells require verification')
        if root.find('.//'+W+'del') is not None or root.find('.//'+W+'ins') is not None:
            self.flag('DOCX_REVISIONS','Tracked revisions present; verify accepted/rejected state in original')
        if any(n.startswith('word/header') or n.startswith('word/footer') or n.startswith('word/comments') for n in z.namelist()):
            self.flag('DOCX_PARTS','Headers, footers or comments require separate extraction and source verification')
        if any(n.startswith('word/media/') for n in z.namelist()): self.flag('DOCX_MEDIA','Media present; extracted text is not a substitute for its contents')
        return '\n\n'.join(out)
    def pptx(self,data):
        z=zip_members(data)
        slidefiles=sorted((n for n in z.namelist() if re.fullmatch(r'ppt/slides/slide\d+\.xml',n)),key=lambda s:int(re.search(r'slide(\d+)',s).group(1)))
        out=[]
        for name in slidefiles:
            root=xml_bytes(z.read(name))
            shapes=[]
            for sp in root.findall('.//'+P+'sp'):
                off=sp.find('.//'+A+'xfrm/'+A+'off')
                x=int(off.get('x',0)) if off is not None else 0
                y=int(off.get('y',0)) if off is not None else 0
                t=text_of(sp)
                if t.strip(): shapes.append((y//125000,x,t))
            for frame in root.findall('.//'+P+'graphicFrame'):
                t=text_of(frame)
                if t.strip():
                    off=frame.find('.//'+A+'xfrm/'+A+'off')
                    shapes.append((int(off.get('y',0))//125000 if off is not None else 0,int(off.get('x',0)) if off is not None else 0,t))
                    self.flag('PPTX_TABLE_CHART','Complex tables/charts in slide need structural review')
            shapes.sort(key=lambda p:(p[0],p[1]))
            texts=[self.emit(md(s)) for _,_,s in shapes]
            out.append('## Slide '+re.search(r'slide(\d+)',name).group(1)+'\n\n'+'\n\n'.join(texts))
            note='ppt/notesSlides/notesSlide'+re.search(r'slide(\d+)',name).group(1)+'.xml'
            if note in z.namelist():
                ns=text_of(xml_bytes(z.read(note)))
                if ns.strip(): out.append('### Speaker notes\n\n'+md(ns))
            if root.find('.//'+P+'pic') is not None: self.flag('PPTX_IMAGE','Picture requires OCR or visual review')
        if not slidefiles: self.flag('NO_SLIDES','No slide files found','block')
        self.flag('PPTX_ORDER','Shape order approximated by geometry; verify reading order')
        return '\n\n'.join(out)
    def xlsx(self,data):
        z=zip_members(data)
        shared=[]
        if 'xl/sharedStrings.xml' in z.namelist():
            root=xml_bytes(z.read('xl/sharedStrings.xml'))
            shared=[''.join(e.text or '' for e in si.iter(S+'t')) for si in root.findall(S+'si')]
        sheets=sorted((s for s in z.namelist() if re.fullmatch(r'xl/worksheets/sheet\d+\.xml',s)),key=lambda s:int(re.search(r'sheet(\d+)',s).group(1)))
        out=[]
        for file in sheets:
            root=xml_bytes(z.read(file))
            rows=[]; maxcol=0
            for row in root.findall('.//'+S+'sheetData/'+S+'row'):
                cells={}
                for cell in row.findall(S+'c'):
                    addr=cell.get('r',''); match=re.match(r'([A-Z]+)',addr)
                    if not match: continue
                    col=0
                    for c in match.group(1): col=col*26+ord(c)-64
                    typ=cell.get('t',''); val=cell.find(S+'v'); inline=cell.find(S+'is'); formula=cell.find(S+'f')
                    raw=val.text if val is not None and val.text is not None else ''
                    if typ=='s':
                        try: raw=shared[int(raw)]
                        except (ValueError,IndexError): self.flag('XLSX_SHARED','Broken shared string index')
                    elif typ=='inlineStr' and inline is not None: raw=''.join(e.text or '' for e in inline.iter(S+'t'))
                    if formula is not None:
                        raw='='+str(formula.text or '')+(' [cached: '+raw+']' if raw else ' [no cached value]')
                        self.flag('XLSX_FORMULA','Formula not evaluated; cached result may be stale')
                    cells[col]=md(raw).replace('|','\\|')
                    maxcol=max(maxcol,col)
                if cells: rows.append(cells)
            label='Sheet '+re.search(r'sheet(\d+)',file).group(1)
            out.append('## '+label)
            if rows and maxcol:
                headings='| '+' | '.join(column_name(c) for c in range(1,maxcol+1))+' |'
                out.extend([headings,'| '+' | '.join(['---']*maxcol)+' |'])
                for row in rows:
                    out.append(self.emit('| '+' | '.join(row.get(c,'') for c in range(1,maxcol+1))+' |'))
                self.flag('XLSX_ROW_INDEX','Blank rows omitted; sheet row indices and merged ranges need verification')
            if root.find('.//'+S+'mergeCells') is not None: self.flag('XLSX_MERGES','Merged ranges need visual review')
        if 'xl/workbook.xml' in z.namelist():
            book = xml_bytes(z.read('xl/workbook.xml'))
            labels=[e.get('name','') for e in book.findall('.//'+S+'sheet')]
            if any(e.get('state','visible')!='visible' for e in book.findall('.//'+S+'sheet')):
                self.flag('XLSX_HIDDEN','Workbook contains hidden sheets; verify contents')
            if labels: self.flag('XLSX_SHEET_NAMES','Sheet numbers used instead of workbook display names: '+', '.join(labels[:20]))
        if not sheets: self.flag('NO_SHEETS','No worksheet found','block')
        return '\n'.join(out)
    def xls(self,data):
        try: import xlrd
        except ImportError:
            self.flag('XLS_DEPENDENCY','Install xlrd for legacy .xls files','block'); return ''
        book=xlrd.open_workbook(file_contents=data)
        out=[]
        for sheet in book.sheets():
            out.append('## '+md(sheet.name))
            if sheet.ncols:
                out.extend(['| '+' | '.join(column_name(j+1) for j in range(sheet.ncols))+' |',
                            '| '+' | '.join('---' for _ in range(sheet.ncols))+' |'])
                for i in range(sheet.nrows):
                    vals=[]
                    for j in range(sheet.ncols):
                        cell=sheet.cell(i,j)
                        if cell.ctype==xlrd.XL_CELL_NUMBER:
                            val=repr(cell.value)
                            self.flag('XLS_NUMERIC','Legacy XLS numeric representation may lose display format')
                        else: val=str(cell.value) if cell.value is not None else ''
                        vals.append(md(val).replace('|','\\|'))
                    out.append(self.emit('| '+' | '.join(vals)+' |'))
        return '\n'.join(out)
    def epub(self,data):
        z=zip_members(data); names=[n for n in z.namelist() if n.lower().endswith(('.xhtml','.html','.htm'))]
        if not names: self.flag('EPUB_EMPTY','No XHTML chapters','block'); return ''
        self.flag('EPUB_SPINE','Chapters ordered by filename, not guaranteed EPUB spine')
        out=[]
        for n in sorted(names): out.append('## '+md(n)+'\n\n'+self.convert(n,z.read(n)))
        return '\n\n'.join(out)
    def archive(self,data):
        if self.depth>=2: self.flag('ARCHIVE_DEPTH','Nested archive depth exceeded','block'); return ''
        z=zip_members(data);out=[]
        self.depth+=1
        try:
            for i in z.infolist():
                if i.is_dir(): continue
                try:
                    t=self.convert(i.filename,z.read(i))
                    out.append('## '+md(i.filename)+'\n\n'+t)
                except Exception as exc:
                    self.flag('ARCHIVE_MEMBER',f'{i.filename}: {type(exc).__name__}: {exc}','block')
        finally: self.depth-=1
        return '\n\n'.join(out)
    def pdf(self,data):
        try: import fitz
        except ImportError:
            self.flag('PDF_DEPENDENCY','Install pymupdf for local PDF extraction','block'); return ''
        document=fitz.open(stream=data,filetype='pdf')
        out=[]
        for i,page in enumerate(document):
            blocks=[]
            for b in page.get_text('blocks'):
                if len(b)>6 and b[6]!=0: continue
                x0,y0,x1,y1,txt=b[:5]
                if compact(txt): blocks.append((x0,y0,x1,y1,compact(txt)))
            if not blocks:
                self.flag('PDF_SCAN',f'Page {i+1}: no embedded text; OCR required')
                if shutil.which('tesseract'):
                    try:
                        png=page.get_pixmap(matrix=fitz.Matrix(2,2)).tobytes('png')
                        ocr=self.image(png,'.png')
                        out.append('## Page '+str(i+1)+'\n\n'+ocr)
                    except Exception as exc:
                        self.flag('PDF_OCR_FAILURE',str(exc),'block')
                        out.append('## Page '+str(i+1)+'\n\n[PAGE OCR FAILED]')
                else:
                    self.flag('OCR_DEPENDENCY',f'Page {i+1}: Tesseract not installed','block')
                    out.append('## Page '+str(i+1)+'\n\n[PAGE NEEDS OCR]')
                continue
            width=page.rect.width
            left=[b for b in blocks if b[2]<width*.56]
            right=[b for b in blocks if b[0]>width*.44]
            col_layout=len(left)>1 and len(right)>1 and len(left)+len(right)>=len(blocks)*.8
            if col_layout:
                self.flag('PDF_COLUMNS',f'Page {i+1}: inferred columns; inspect reading order')
                middle=[b for b in blocks if b not in left and b not in right]
                seq=sorted(left,key=lambda b:b[1])+sorted(right,key=lambda b:b[1])+sorted(middle,key=lambda b:b[1])
            else: seq=sorted(blocks,key=lambda b:(round(b[1]/7),b[0]))
            out.append('## Page '+str(i+1)+'\n\n'+'\n\n'.join(self.emit(md(b[4])) for b in seq))
            if page.get_images(): self.flag('PDF_IMAGES',f'Page {i+1}: embedded images require inspection')
            if hasattr(page,'find_tables'):
                try:
                    if page.find_tables().tables: self.flag('PDF_TABLES',f'Page {i+1}: native table structure requires review')
                except Exception: pass
        return '\n\n'.join(out)
    def image(self,data,ext):
        # OCR always needs human verification; metadata is informational only.
        try:
            from PIL import Image
            with Image.open(io.BytesIO(data)) as im:
                if im.getexif(): self.flag('IMAGE_EXIF','EXIF metadata present; not included in Markdown')
        except ImportError: self.flag('IMAGE_META','Install Pillow if image metadata is required')
        except Exception as exc: self.flag('IMAGE_READ',str(exc),'block'); return ''
        if not shutil.which('tesseract'):
            self.flag('OCR_DEPENDENCY','Install Tesseract and requested language data','block'); return ''
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/('image'+ext); p.write_bytes(data)
            proc=subprocess.run(['tesseract',str(p),'stdout','-l',self.ocr_lang],capture_output=True,text=True,timeout=90)
            if proc.returncode: self.flag('OCR_FAILURE',proc.stderr.strip()[:400],'block'); return ''
            self.flag('OCR_REVIEW','OCR text must be compared against image, especially math/tables')
            return self.emit(proc.stdout.strip())
    def audio(self,data,ext):
        if not self.audio_model:
            self.flag('AUDIO_MODEL','Provide --audio-model-local pointing to a preinstalled local faster-whisper model','block');return ''
        try: from faster_whisper import WhisperModel
        except ImportError: self.flag('AUDIO_DEPENDENCY','Install faster-whisper in isolated environment','block');return ''
        with tempfile.TemporaryDirectory() as d:
            src=Path(d)/('record'+ext);src.write_bytes(data)
            try:
                model=WhisperModel(self.audio_model,device='cpu',compute_type='int8',local_files_only=True)
                segments,_=model.transcribe(str(src),beam_size=5)
                text='\n'.join('[%.2f–%.2f] %s'%(s.start,s.end,s.text.strip()) for s in segments)
            except Exception as e: self.flag('AUDIO_FAILURE',str(e),'block');return ''
            self.flag('AUDIO_REVIEW','Speech recognition must be verified against source; no speaker identity implied')
            return self.emit(text)

def run(argv=None):
    p=argparse.ArgumentParser(description='Offline-first file to Markdown conversion with strict audit')
    p.add_argument('input',type=Path);p.add_argument('-o','--output',type=Path)
    p.add_argument('--ocr-lang',default='eng');p.add_argument('--audio-model-local')
    p.add_argument('--allow-review',action='store_true');p.add_argument('--overwrite',action='store_true')
    args=p.parse_args(argv)
    if not args.input.is_file() or args.input.is_symlink(): p.error('Input must be a regular non-symlink local file')
    dst=args.output or args.input.with_suffix('.md')
    if dst.resolve()==args.input.resolve(): p.error('Output cannot replace the source file')
    if dst.exists() and not args.overwrite: p.error('Output exists (use --overwrite)')
    audit=dst.with_suffix(dst.suffix+'.audit.json')
    if audit.exists() and not args.overwrite: p.error('Audit exists (use --overwrite)')
    src=args.input.read_bytes()
    obj=Conversion(args.ocr_lang,args.audio_model_local)
    try: result=obj.convert(args.input.name,src)
    except Exception as e: obj.flag('FATAL',type(e).__name__+': '+str(e),'block');result=''
    if '\ufffd' in result: obj.flag('ENCODING','Replacement characters detected in decoded text')
    if not result.strip(): obj.flag('EMPTY_RESULT','Conversion yielded no text','block')
    if obj.stats['objects_seen']>obj.stats['objects_emitted']:
        obj.flag('COVERAGE','One or more detected objects have no text')
    codes={f['severity'] for f in obj.findings}
    status='BLOCK' if 'block' in codes else ('REVIEW' if 'review' in codes else 'PASS')
    report={'schema_version':1,'source':args.input.name,'source_sha256':hashlib.sha256(src).hexdigest(),
            'status':status,'counts':obj.stats,'findings':obj.findings,'markdown_sha256':hashlib.sha256(result.encode()).hexdigest(),
            'trust_policy':'A PASS is not a proof of exact visual or semantic fidelity'}
    dst.parent.mkdir(parents=True,exist_ok=True)
    # Prevent partial files. Never delete user source. Report accompanies any output.
    def atomic_write(path,content):
        with tempfile.NamedTemporaryFile(dir=path.parent,prefix='.doc-to-md-',delete=False) as f:
            tmp=Path(f.name); f.write(content)
        try: os.replace(tmp,path)
        finally: tmp.unlink(missing_ok=True)
    atomic_write(dst,result.encode('utf-8'))
    atomic_write(audit,(json.dumps(report,ensure_ascii=False,indent=2)+'\n').encode('utf-8'))
    print(json.dumps({'status':status,'markdown':str(dst),'audit':str(audit)},ensure_ascii=False))
    return 3 if status=='BLOCK' else (2 if status=='REVIEW' and not args.allow_review else 0)

if __name__=='__main__': sys.exit(run())
