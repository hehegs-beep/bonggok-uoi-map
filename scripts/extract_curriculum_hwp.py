"""Read the MOE's official 2022-33 subject archive into paragraph text.

Input: tmp/pdfs/curriculum.zip, attachment 2 of the official notice:
https://www.moe.go.kr/boardCnts/viewRenew.do?boardID=141&boardSeq=93458
Requires olefile. This only extracts source text; it never edits the source.
"""
import sys,zipfile,struct,zlib,re,io
from pathlib import Path
sys.path.insert(0,'tmp/vendor')
import olefile
z=zipfile.ZipFile('tmp/pdfs/curriculum.zip')
items=[(n,z.read(n)) for n in z.namelist()]
if Path('tmp/pdfs/book15.hwp').exists():items.append(('[별책15] 통합교과.hwp',Path('tmp/pdfs/book15.hwp').read_bytes()))
for n,content in items:
 try:name=n.encode('cp437').decode('cp949')
 except UnicodeError:name=n
 m=re.search(r'별책(5|6|7|8|9|10|11|12|13|14|15)\]',name)
 if not m:continue
 o=olefile.OleFileIO(io.BytesIO(content))
 compressed=bool(struct.unpack_from('<I',o.openstream('FileHeader').read(),36)[0]&1)
 texts=[]
 for stream in o.listdir():
  if stream[0]!='BodyText':continue
  b=o.openstream(stream).read()
  if compressed:b=zlib.decompress(b,-15)
  i=0
  while i+4<=len(b):
   h=struct.unpack_from('<I',b,i)[0];i+=4;tag=h&1023;size=h>>20
   if size==4095:size=struct.unpack_from('<I',b,i)[0];i+=4
   data=b[i:i+size];i+=size
   if tag!=67:continue
   chars=struct.unpack('<'+'H'*(len(data)//2),data);out=[];j=0
   while j<len(chars):
    c=chars[j]
    if c<32:
     if c in (9,10,13):out.append(' ')
     j+=8 if c in (1,2,3,4,5,6,7,8,9,11,12,14,15,16,17,18,19,20,21,22,23) else 1
    else:out.append(chr(c));j+=1
   t=''.join(out).encode('utf-16-le','surrogatepass').decode('utf-16-le','replace').strip()
   if t:texts.append(t)
 Path('tmp/pdfs/book'+m[1]+'.hwp.txt').write_text('\n'.join(texts),encoding='utf-8')
 print(m[1],len(texts),'paragraphs')
