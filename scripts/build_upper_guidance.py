"""Map the elementary 3–6 curriculum notices to their explicitly stated scopes.

Inputs are the official NCIC PDFs (bookN.pdf.json, one extracted string per
page) and MOE's HWP paragraph text, under tmp/pdfs. Extracts remain
labelled as extracts, not summaries. No semantic assignment is guessed.
"""
import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / 'tmp/pdfs'
OUTPUT = ROOT / 'curriculum-data.js'
MOE = 'https://www.moe.go.kr/boardCnts/viewRenew.do?boardID=141&boardSeq=93458&lev=0&searchType=null&statusYN=W'
BOOKS = {
 5: ('국어', '1UER7JNfY-ZIZmHJLUeqU6HLdnBAHk7cl'),
 6: ('도덕', '11S5V5X307M8WXDR8qsNRHHwoCw2Ja52y'),
 7: ('사회', '1PqHh7kMJ8VH072jSoWw9g-RXGqjmWf2U'),
 8: ('수학', '1a4QhqW1UOC5MuG-jCbELrdUwkf6rwF7z'),
 9: ('과학', '1JxNcH-w_MeQE3cz02ChiTxk_XRAfMixt'),
 10: ('실과', '1Unr9P-hxWKSFFkg4YmbcV9Hs2zOV7JEF'),
 11: ('체육', '1t3oqQSRASYYwa6r7epCOUJYEFD1o7qe6'),
 12: ('음악', '1vNuvlMpA6QPNBdb4aN2K9XOLRvTnhAkW'),
 13: ('미술', '16qgKhlHP6pgEkv6SM5rWDPgTAnd5Bu-b'),
 14: ('영어', '1sw2EX1YkQBcUiEuuhNzMVrH8E18UFVIQ'),
}
CODE = re.compile(r'\[\s*(\d{1,2})\s*([가-힣]+)\s*(\d{2})\s*[-–−－]\s*(\d{2})\s*\]')
HEADING = re.compile(r'^\((\d+)\)\s*(.+)')
BULLET = re.compile(r'^[•●]\s*')

def codes(text):
 return [f'{m[1]}{m[2]}{m[3]}-{m[4]}' for m in CODE.finditer(text)]

def tidy(text):
 text = re.sub(r'\s+', ' ', text).strip()
 text = re.sub(r'\s+([.,;:?!，])', r'\1', text)
 return text

def pdf_paragraphs(pages):
 current = None
 for page, text in enumerate(pages, 1):
  for raw in text.splitlines():
   line = raw.strip()
   if not line or re.fullmatch(r'\d+', line): continue
   if re.fullmatch(r'(?:[가-힣·⋅() /]+과 교육과정|공통 교육과정(?:\s*[–-].*)?)', line): continue
   heading = HEADING.match(line)
   kind = ('heading' if heading else 'mode' if re.match(r'^\([가나다]\)\s*성취기준', line)
           else 'school' if re.match(r'^\[(?:초등학교|중학교|고등학교)', line)
           else 'stop' if re.match(r'^3\.\s*교수', line)
           else 'bullet' if BULLET.match(line)
           else 'declaration' if CODE.match(line)
           else None)
   # Math subtopic labels are headings inside the standards table, not notes.
   if kind is None and re.match(r'^[숔숕숖숗숚숛순숙수]\s+[^\[\]]{1,30}$',line): kind='subtopic'
   if kind:
    if current:yield current
    current={'kind':kind,'text':BULLET.sub('',line),'page':page,'endPage':page}
   elif current:
    current['text'] += ' '+line; current['endPage']=page
 if current:yield current

def hwp_paragraphs(text):
 for line in text.splitlines():
  if not line.strip():continue
  kind=('heading' if HEADING.match(line) else 'mode' if re.match(r'^\([가나다]\)\s*성취기준',line)
        else 'school' if re.match(r'^\[(?:초등학교|중학교|고등학교)',line)
        else 'stop' if re.match(r'^3\.\s*교수',line) else 'paragraph')
  yield {'kind':kind,'text':line,'page':None,'endPage':None}

def build_book(number, subject, drive, payload, include_lower=False):
 source=f'upper-{number}'
 is_hwp=True
 rawpath=INPUT/f'book{number}.hwp.txt'
 pdfpath=INPUT/f'book{number}.pdf.json'
 pages=json.loads(pdfpath.read_text(encoding='utf-8')) if pdfpath.exists() else []
 normalize=lambda t: re.sub(r'\s+','',t).replace('–','-').replace('−','-')
 page_texts=[normalize(p) for p in pages[:80]]
 def locate(text):
  needle=normalize(BULLET.sub('',text))[:100]
  if len(needle)<15:return None
  matches=[i+1 for i,t in enumerate(page_texts) if needle in t]
  return matches[0] if len(matches)==1 else None
 payload['sources'][source]={'title':f'[별책{number}] {subject}과 교육과정' if number!=10 else '[별책10] 실과(기술·가정)/정보과 교육과정',
  'fileId':drive,'notice':'교육부 고시 제2022-33호','grade':'초등학교 3~6학년',
  'officialUrl':MOE,'textType':'원문 발췌','format':'hwp','pdfPageAnchors':bool(pages),
  'textSha256':hashlib.sha256(rawpath.read_bytes()).hexdigest()}
 events=hwp_paragraphs(rawpath.read_text(encoding='utf-8'))
 active=False; title=''; mode='standards'; current_groups=[]; source_counts={'standards':0,'explanations':0,'notes':0,'common':0}
 for item in events:
  text=tidy(BULLET.sub('',item['text']));kind=item['kind']; found=codes(text)
  item['page']=locate(text);item['endPage']=item['page']
  if text.startswith('<표'):
   mode='examples'
   continue
  if kind=='school':
   if '중학교' in text or '고등학교' in text:
    if active:break
   current_groups=[];mode='standards';continue
  if kind=='stop' and active:
   if number!=15:break
   active=False;mode='standards';current_groups=[];continue
  if kind=='heading':
   title=HEADING.match(text)[2];mode='standards';current_groups=[];continue
  if kind=='mode':
   if '해설' in text:mode='explanation'
   elif '고려' in text:mode='notes'
   continue
  declaration=(kind=='declaration' and not is_hwp) or (is_hwp and mode=='standards' and CODE.match(text))
  if declaration:
   # Reference codes in the prose of a declaration are not new standards.
   match=CODE.match(text)
   if not match:continue
   code=codes(match[0])[0]
   if not code.startswith(('2','4','6') if include_lower else ('4','6')):
    if active and code.startswith(('9','10','12')):break
    continue
   active=True;prefix=code.rsplit('-',1)[0]
   if prefix not in payload['groups']:
    band='1~2학년군' if code.startswith('2') else '3~4학년군' if code.startswith('4') else '5~6학년군'
    payload['groups'][prefix]={'title':title,'source':source,'grade':band,'pages':[],'common':[],'commonItems':[],'explanationCommon':[]}
    if number==6:payload['groups'][prefix]['commonScope']='초등학교 3~6학년 · 도덕'
   group=payload['groups'][prefix]
   if item['page'] and item['page'] not in group['pages']:group['pages'].append(item['page'])
   if prefix not in current_groups:current_groups.append(prefix)
   if code not in payload['entries']:
    payload['entries'][code]={'group':prefix,'explanation':None,'notes':[],'links':[],'textType':'원문 발췌','statement':text[match.end():].strip()}
    source_counts['standards']+=1
   continue
  if not active or not current_groups or kind=='subtopic':continue
  if mode not in ('explanation','notes'):continue
  if not is_hwp and kind!='bullet':continue
  if len(text)<8:continue
  # Only an initial code label assigns an extract to an individual standard.
  leading=[];tail=text
  while True:
   m=CODE.match(tail.lstrip(' ,·ㆍ및와과'))
   if not m:break
   stripped=tail.lstrip(' ,·ㆍ및와과');leading.extend(codes(m[0]));tail=stripped[m.end():]
  allowed=[c for c in leading if c in payload['entries'] and payload['entries'][c]['group'] in current_groups]
  entry_item={'text':text,'page':item['page'],'endPage':item['endPage'],'basis':'원문에 코드 명시'}
  if allowed:
   for code in allowed:
    entry=payload['entries'][code]
    if mode=='explanation':
     if entry['explanation']:entry['explanation']['text']+='\n\n'+text;entry['explanation']['endPage']=item['endPage']
     else:entry['explanation']=dict(entry_item)
     source_counts['explanations']+=1
    else:entry['notes'].append(dict(entry_item));source_counts['notes']+=1
  else:
   for prefix in current_groups:
    group=payload['groups'][prefix]
    if mode=='explanation':group['explanationCommon'].append(dict(entry_item))
    else:group['common'].append(text);group['commonItems'].append(dict(entry_item));source_counts['common']+=1
  for prefix in current_groups:
   group=payload['groups'][prefix]
   if item['page'] and item['page'] not in group['pages']:group['pages'].append(item['page'])
 print(number,subject,source_counts)
 return source_counts

def main():
 raw=OUTPUT.read_text(encoding='utf-8');payload=json.loads(raw.split('window.CURRICULUM_GUIDANCE = ',1)[1].rstrip().removesuffix(';'))
 # Rebuild upper grades deterministically while preserving the existing 1–2 mappings.
 payload['entries']={k:v for k,v in payload['entries'].items() if k.startswith('2')}
 payload['groups']={k:v for k,v in payload['groups'].items() if k.startswith('2')}
 payload['sources']={k:v for k,v in payload['sources'].items() if not k.startswith('upper-')}
 totals={}
 for number,(subject,drive) in BOOKS.items():totals[str(number)]=build_book(number,subject,drive,payload)
 payload['version']='2026-10-16-upper';payload['textType']='원문 요약 및 원문 발췌'
 OUTPUT.write_text('/* Official curriculum notices: summaries (grades 1–2), scoped extracts (grades 3–6). */\nwindow.CURRICULUM_GUIDANCE = '+json.dumps(payload,ensure_ascii=False,indent=2)+';\n',encoding='utf-8')
 (ROOT/'tmp/guidance-import-report.json').write_text(json.dumps(totals,ensure_ascii=False,indent=2),encoding='utf-8')
 print('Total',len(payload['entries']),'standards;',len(payload['groups']),'groups')

if __name__=='__main__':main()
