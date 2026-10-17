#!/usr/bin/env python3
"""Produce 26 ORIGINAL schematic, non-factual SVG and PNG visual examples.
Icons, chart values, map positions and bibliography entries are deliberately illustrative.
"""
import html
from pathlib import Path
try: import cairosvg
except ImportError: cairosvg=None
ROOT=Path(__file__).resolve().parent.parent
OUT=ROOT/'assets/visual-examples';OUT.mkdir(parents=True,exist_ok=True)
COL={'navy':'#20324E','teal':'#237A7A','ink':'#263B50','muted':'#637688','pale':'#EDF4F5','amber':'#FFF3E4','orange':'#DB8935','red':'#BE4E49','line':'#D9E3E6','bg':'#F3F6F8'}
items=[('01-cover','Cover and introduction','Professional publication identity'),('02-toc','Auto-updating contents','Dot leaders and navigation'),('03-header-footer','Running heads and page fields','Section title and page number'),('04-icon-rule','Semantic icons','Icon + explicit text label'),('05-annotated-image','Annotated teaching image','Explain a physical object'),('06-illustration','Educational schematic','Show internal construction'),('07-process-flow','Ordered process','Sequence without ambiguity'),('08-decision','Decision diagram','State if/else conditions'),('09-mindmap','Concept map','Non-sequential relationships'),('10-comparison','Criteria comparison','Same criteria, consistent layout'),('11-data-chart','Sourced chart grammar','Honest axes and clear units'),('12-timeline','Chronological timeline','Specific dated stages'),('13-map','Verified map grammar','Data provenance mandatory'),('14-callouts','Semantic callout library','RTL-safe notes and warnings'),('15-inline-code','Inline code span','Selectable literal identifiers'),('16-code-block','Editable code block','Whitespace and direction safe'),('17-cross-reference','Internal cross-reference','Word REF and SEQ fields'),('18-no-visual','Text is enough','Avoid decorative filler'),('19-citation','In-text citation','Numbered verifiable evidence'),('20-bibliography','Bibliography','Only verified entries'),('21-list-of-figures','List of figures','Field-generated captions'),('22-accessibility','Accessible reading','Labels, alt text, headers'),('23-multilingual','Language editions','RTL, LTR and term fidelity'),('24-html-companion','Separate interactive HTML','Static DOCX counterpart'),('25-review-diff','Review changes','Honest diff vs Track Changes'),('26-render-qa','Render and inspect','Every page visual QA')]

def rect(x,y,w,h,fill='white',r=10,stroke='none',sw=1): return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>'
def txt(x,y,s,size=19,color=COL['ink'],weight='normal',anchor=None): return f'<text x="{x}" y="{y}" font-family="DejaVu Sans, sans-serif" font-size="{size}" fill="{color}" font-weight="{weight}"'+(f' text-anchor="{anchor}"' if anchor else '')+'>'+html.escape(str(s))+'</text>'
def line(x1,y1,x2,y2,color=None,sw=2,dash=''):return f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{color or COL["line"]}" stroke-width="{sw}" '+(f'stroke-dasharray="{dash}"' if dash else '')+'/>'
def circle(x,y,r,fill,stroke='none'):return f'<circle cx="{x}" cy="{y}" r="{r}" fill="{fill}" stroke="{stroke}" stroke-width="2"/>'
def poly(points,color=COL['teal'],width=3):return f'<polyline points="{points}" fill="none" stroke="{color}" stroke-width="{width}" stroke-linecap="round" stroke-linejoin="round"/>'
def arrow(x1,y1,x2,y2,color=COL['teal']):return line(x1,y1,x2,y2,color,3)+f'<polygon points="{x2},{y2} {x2-12},{y2-7} {x2-12},{y2+7}" fill="{color}"/>'
def para(x,y,n=3,w=375,col=COL['line']):return ''.join(rect(x,y+j*17,w-33*(j%3),5,col,2) for j in range(n))
def card(x,y,w,h,t,sub=None,color=None):return rect(x,y,w,h,'#fff',13,COL['line'])+rect(x,y,5,h,color or COL['teal'],0)+txt(x+17,y+31,t,18,COL['navy'],'bold')+(txt(x+17,y+58,sub,13,COL['muted']) if sub else '')

def contents(key):
 S='';t=COL['teal'];n=COL['navy'];m=COL['muted'];p=COL['pale'];a=COL['amber'];rd=COL['red']
 if key=='01-cover':
  S+=rect(245,112,420,348,'#fff',2,COL['line'])+rect(245,112,420,14,n,0)+txt(284,209,'FIELD GUIDE',18,t,'bold')+txt(284,257,'The Water',36,n,'bold')+txt(284,299,'Filter System',36,n,'bold')+line(284,328,625,328,t,3)+txt(284,366,'Illustrated educational report',16,m)+txt(284,426,'Research notes  |  Edition 3',14,m)
 elif key=='02-toc':
  S+=rect(185,110,540,345,'white',3,COL['line'])+txt(222,167,'Contents',31,n,'bold')
  for j,(sec,pn) in enumerate([('Introduction','02'),('Filter components','04'),('How the process works','09'),('References','17')]):
   y=219+j*54;S+=txt(224,y,sec,18,n)+line(390 if j<2 else 487,y-4,642,y-4,m,1,'2 5')+txt(664,y,pn,18,t,'bold')
 elif key=='03-header-footer':
  S+=rect(190,114,525,350,'white',2,COL['line'])+txt(221,149,'FIELD GUIDE  /  FILTER COMPONENTS',13,t,'bold')+line(221,162,680,162,m,1)+txt(226,222,'How the filter works',24,n,'bold')+para(226,254,5,420)+line(222,422,680,422,m,1)+txt(226,445,'EDUCATIONAL SERIES',12,m)+txt(654,446,'07',18,t,'bold')
 elif key=='04-icon-rule':
  for j,(ic,label) in enumerate([('i','INFORMATION'),('!','IMPORTANT'),('✓','CHECK RESULT')]):
   y=146+j*100;S+=rect(210,y,490,77,'white',12,COL['line'])+circle(254,y+39,23,[t,COL['orange'],n][j])+txt(254,y+45,ic,21,'white','bold','middle')+txt(296,y+46,label,21,n,'bold')
 elif key in ('05-annotated-image','06-illustration'):
  S+=rect(223,142,405,245,'white',14,COL['line'])+rect(345,172,180,170,p,35,t,3)+rect(360,186,150,43,'#D0E7E5',0)+rect(360,229,150,46,'#B3CAC4',0)+rect(360,275,150,50,'#D7C4A1',0)+line(530,201,670,170,t)+txt(570,160,'Intake',16,t)+line(530,260,678,252,COL['orange'])+txt(574,244,'Layer',16,COL['orange'])+line(337,318,209,352,n)+txt(150,376,'Output',15,n)
 elif key=='07-process-flow':
  for j,x in enumerate([170,373,576]):S+=card(x,202,151,104,['01  INTAKE','02  FILTER','03  OUTPUT'][j],['Input','Process','Result'][j]);
  S+=arrow(326,251,368,251)+arrow(531,251,571,251)
 elif key=='08-decision':
  S+=rect(342,139,216,68,'white',15,t)+txt(370,180,'Check the input',18,n,'bold')+line(450,207,450,240,t,3)+f'<polygon points="450,231 533,291 450,353 368,291" fill="{p}" stroke="{t}" stroke-width="3"/>'+txt(449,295,'Valid?',18,n,'bold','middle')+line(368,291,250,291,t,3)+line(533,291,646,291,t,3)+txt(280,275,'NO',14,rd,'bold')+txt(581,275,'YES',14,t,'bold')+card(117,291,205,77,'Fix input',color=rd)+card(583,291,193,77,'Proceed')
 elif key=='09-mindmap':
  # Connector endpoints MUST stop at node boundaries; draw edges BEFORE nodes so
  # no connector can cross the central text or cover any foreground node.
  for x1,y1,x2,y2 in [(381,221,304,193),(527,221,591,194),(380,294,306,351),(528,294,603,350)]:
   S+=line(x1,y1,x2,y2,t,3)
  S+=rect(356,221,196,73,n,20)+txt(454,265,'CONCEPT',18,'white','bold','middle')
  for x,y,v in [(138,131,'Composition'),(576,132,'Function'),(144,351,'Safety'),(585,350,'Maintenance')]:
   xmid=x+82;S+=rect(x,y,180,62,'white',14,t,2)+txt(xmid,y+38,v,15,n,'bold','middle')
 elif key=='10-comparison':
  S+=rect(156,148,600,266,'white',6,COL['line'])+rect(156,148,600,54,n,0)
  for j,v in enumerate(['CRITERION','METHOD A','METHOD B']):S+=txt(176+j*188,180,v,16,'white','bold')
  for i,(a1,b,c) in enumerate([('Cost','Low','Medium'),('Speed','Moderate','Fast'),('Reuse','Yes','Limited')]):
   y=248+i*66;S+=line(157,y+14,754,y+14,COL['line'])
   for j,v in enumerate([a1,b,c]):S+=txt(178+j*189,y,v,16,n)
 elif key=='11-data-chart':
  S+=line(266,362,678,362,m)+line(266,162,266,362,m)
  for j,h in enumerate([71,128,178]):
   x=335+j*119;S+=rect(x,360-h,62,h,[t,'#609EA0',n][j],4)+txt(x+27,389,['A','B','C'][j],17,n,'bold')
  S+=txt(269,148,'Illustrative values only',16,rd,'bold')+txt(269,419,'Always add real units, dates and source',14,m)
 elif key=='12-timeline':
  S+=line(198,270,704,270,t,6)
  for j,(x,v,t2) in enumerate([(222,'2021','Baseline'),(449,'2023','Upgrade'),(679,'2026','Review')]):S+=circle(x,270,14,n)+txt(x,234,v,23,n,'bold','middle')+txt(x,322,t2,18,m,'normal','middle')
 elif key=='13-map':
  S+=rect(178,117,558,314,'#EAF3F1',10,COL['line'])
  for pts in ['230,170 340,210 420,145 520,210 677,175','260,377 344,320 445,360 564,293 660,339'] :S+=poly(pts,'#B9CECD',12)
  S+=poly('292,339 365,249 504,278 609,190',t,5)+circle(292,339,10,n)+circle(609,190,10,n)+txt(214,404,'Verified coordinates / licensed basemap only',15,n)
 elif key=='14-callouts':
  for j,(tag,bg,c) in enumerate([('INFO',p,t),('IMPORTANT',a,COL['orange']),('WARNING','#FCEDEB',rd)]):
   y=126+j*103;S+=rect(212,y,473,82,bg,8)+rect(212,y,7,82,c,0)+txt(235,y+30,tag,18,c,'bold')+txt(235,y+56,'A short actionable explanation.',15,n)
 elif key in ('15-inline-code','16-code-block'):
  S+=rect(190,138,540,280,'white',10,COL['line'])+txt(216,196,'Type',20,n)+rect(274,166,188,43,'#E9EFF4',6)+txt(291,195,'filter(input)',18,t,'bold')+txt(476,195,'to run the function.',19,n)
  if key=='16-code-block':S+=rect(216,235,483,138,'#233146',9)+txt(242,272,'def filter(data):',19,'#D9F4E8')+txt(270,303,'return clean(data)',18,'#FFFFFF')+txt(244,342,'# editable, never a screenshot',13,'#B9CDDC')
 elif key=='17-cross-reference':
  S+=rect(204,126,503,307,'white',5,COL['line'])+txt(234,198,'See Figure 2 for the process',22,n)+line(275,207,357,207,t,2)+rect(262,253,370,98,p,12)+txt(288,299,'Figure 2: sequence diagram',19,t,'bold')+txt(244,397,'Word REF field + figure caption',15,m)
 elif key=='18-no-visual':
  S+=rect(212,127,480,315,'white',6,COL['line'])+txt(246,182,'Clear prose needs no ornament',22,n,'bold')+para(245,219,7,415)+txt(245,383,'No additional image is needed.',15,t)
 elif key=='19-citation':
  S+=rect(200,142,511,261,'white',6,COL['line'])+txt(234,201,'State a verified claim, then cite [3].',19,n)+rect(621,172,36,37,a,4)+txt(627,198,'[3]',18,rd,'bold')+para(232,241,4,443)+txt(234,365,'[3] must resolve to a real source.',15,m)
 elif key=='20-bibliography':
  S+=rect(190,115,529,326,'white',4,COL['line'])+txt(230,168,'References',29,n,'bold')
  for j in range(3):
   y=212+j*72;S+=txt(234,y,f'[{j+1}] Verified author / organization',17,n)+txt(273,y+26,'Actual title, publication year, DOI or URL',14,m)
 elif key=='21-list-of-figures':
  S+=rect(182,122,544,299,'white',4,COL['line'])+txt(221,177,'List of Figures',29,n,'bold')
  for j,(name,num) in enumerate([('Figure 1. System cutaway','03'),('Figure 2. Process flow','07'),('Figure 3. Data comparison','09')]):
   y=240+j*61;S+=txt(224,y,name,17,n)+line(491,y-4,658,y-4,m,1,'2 5')+txt(668,y,num,17,t,'bold')
 elif key=='22-accessibility':
  S+=card(177,150,542,66,'Heading 1 → Heading 2 → Body')+card(177,229,542,66,'Meaningful image alt text')+card(177,308,542,66,'Readable table headers + contrast')
 elif key=='23-multilingual':
  S+=card(161,160,278,220,'Arabic / RTL',color=t)+card(472,160,278,220,'English / LTR',color=n)
  S+=txt(185,252,'RIGHT ← FLOW',18,n,'bold')+txt(500,252,'FLOW → RIGHT',18,n,'bold')+txt(192,325,'Preserve names: API',15,m)+txt(503,325,'Localize captions',15,m)
 elif key=='24-html-companion':
  S+=card(141,145,278,235,'DOCX / static','Printable comparison',t)+card(483,145,279,235,'HTML / interactive','Separate accessible file',n)+arrow(422,261,479,261)
 elif key=='25-review-diff':
  S+=card(162,160,285,230,'BEFORE',color=m)+card(465,160,285,230,'AFTER',color=t)+txt(181,260,'Step 1: check.',18,n)+txt(484,260,'Step 1: validate.',18,t,'bold')+txt(243,346,'Text diff is NOT Word Track Changes',14,rd)
 elif key=='26-render-qa':
  for j,x in enumerate([142,336,531]):
   S+=rect(x,146,162,224,'white',6,COL['line'])+rect(x+13,162,134,11,n,1)+para(x+13,190,6,133)
   S+=circle(x+129,337,17,t)+txt(x+129,344,'✓',19,'white','bold','middle')
  S+=txt(251,417,'Check ALL rendered pages at 100%',17,n,'bold')
 return S

for key,title,subtitle in items:
 body=''.join([rect(0,0,900,540,COL['bg'],0),rect(0,0,900,91,COL['navy'],0),txt(35,41,title,23,'white','bold'),txt(35,70,subtitle,14,'#C3DEDD'),contents(key),line(28,483,872,483,COL['line'],1),txt(34,512,'PROFESSIONAL WORD DESIGNER  |  V4 VISUAL REFERENCE',13,COL['muted'])])
 svg=f'<svg xmlns="http://www.w3.org/2000/svg" width="900" height="540" viewBox="0 0 900 540">{body}</svg>'
 (OUT/(key+'.svg')).write_text(svg,encoding='utf-8')
 if cairosvg:
  cairosvg.svg2png(bytestring=svg.encode('utf8'),write_to=str(OUT/(key+'.png')),output_width=900,output_height=540)
print('created',len(items),'visual reference SVGs and', len(list(OUT.glob('*.png'))),'PNGs')
