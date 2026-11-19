#!/usr/bin/env python3
"""Enumerate all contiguous source triples that LOW-BIT-index N20 to 'end of the'.

Run from the workplace-v2 repository root:
    python agents/agent9/k08_n20_source_triple_null.py
This is a source-preserving triple-window control, not a full end-to-end null.
"""
from __future__ import annotations
import hashlib, json, re
from collections import Counter
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
E=ROOT/'resources/evidence'
NOTE='crew/noticeboard-and-desk-notes.txt'
MAIL=E/'mail'
ROUTE=E/'recovery-routing.json'
EXPECTED={
 NOTE:'13f2318ccc54f35b590a2d76b3a80244fe24d70f0699c67c05858e8b8983c5cb',
 'recovery-routing.json':'f8fcbca73d23bf1066edb88c088f89cd24cf22e7c78a4a412166254a4764d8a5',
 'mail/01.eml':'df0729237a3d6d5e90bcaffa95b396d54e511007ec4b0c7e5e8490280aa1d698',
 'mail/02.eml':'a4ac849e45362b93eea9950e61132213494ab3a7cc3967e353850dc221de3a11',
 'mail/03.eml':'3cf886c12e094cb0362999c5a4d93f913c848a64471f833fbddbfdc2d57ff889',
 'mail/04.eml':'c9e83a610f9240c3abd4b4d435588bd9056de34edf6fa3e6d7aca88d8a21f439',
 'mail/05.eml':'29d6d60c6addc16b6f3fd1803b582481a22ce0e757e0a1601a3dc7e116730272',
 'mail/06.eml':'6049994562a82e46afd3f0231e136a1e6911cc3040d848e32eaa5771a6f8c2f3',
 'mail/07.eml':'ee0830aba2e08cc862179aeca034e075f76a08914e5ee6d604ad17f4b806ac22',
 'mail/08.eml':'2da71346103454b6743698103f4d80d79bc0b6013046646e4611c08e8d5f0937',
 'mail/09.eml':'1bda8bbf1e7b661a04fd58c36c38f2b66d2e2410265c311cc09c8e2bf810f08c',
 'mail/10.eml':'ccfc592fe570ca6928a74de813c378443030e841bba169434c0f413721122e48',
 'mail/11.eml':'f4e1b8440582d494fa098d4726d9ad7995d24b7f48f8dc6336364b0c8cf51d29',
 'mail/12.eml':'4cadd373aa676f97e64690a631eea3f3993e0908eaac0aacb86e76ed0c2c68fd',
 'mail/13.eml':'80d7b086d77fe7036a596198825dd221fec82e34cbd5a5a43edae74569e171aa',
 'mail/14.eml':'9c86de086a1727ca09b4df6f12cf5c634eaa22a3949424171cc50b4ef9983be5',
 'mail/15.eml':'249ec45e7c21b66faf0d3310cc742ffdc70e88396a10272932ce821649b7c9e2',
 'mail/16.eml':'02535cc5966a9215d01ecada4a14b6a403d78ca8d09310a5c3cf1a574f817a08',
 'mail/17.eml':'67493c660dcd08de990c2490af5718072ee9e0991476c0272bf9fff9e96e8014',
 'mail/18.eml':'7dc1f122f92ce23c110aa50fd78ae7a471bdf9e60a44e358e3b90e497f664cf0',
 'mail/19.eml':'caff45f8c477f9fa6fc5fae0847c9c7f7842ba83c41319c8a47ddace00bd2fbd',
 'mail/20.eml':'e83391f77c3a41b97cf92c78d93abfa0bebeed0ddf7cbcb9309250973963ac71',
}
TOKEN=re.compile(r'[A-Za-z0-9]+(?:-[A-Za-z0-9]+)?')
def words(s): return TOKEN.findall(s.lower())
def low_value(s): return sum((ord(c)&1)<<i for i,c in enumerate(s))
def parse_notes():
 text=(E/NOTE).read_text()
 out={}
 for n,a,b in re.findall(r'(?ms)^N(\d\d) / ([^\n]+)\n(.+?)(?=\n\nN\d\d /|\Z)',text):
  body=b.strip(); body=body.split(':',1)[1].strip() if ':' in body else body
  out[int(n)]=words(body)
 return out
def flatten(x,prefix=''):
 if isinstance(x,dict):
  for k,v in x.items(): yield from flatten(v,f'{prefix}/{k}')
 elif isinstance(x,list):
  for i,v in enumerate(x): yield from flatten(v,f'{prefix}[{i}]')
 elif isinstance(x,str): yield prefix,x

def main():
 for rel,expected in EXPECTED.items():
  actual=hashlib.sha256((E/rel).read_bytes()).hexdigest()
  if actual!=expected: raise AssertionError(f'hash mismatch {rel}: {actual}')
 notes=parse_notes(); n20=notes[20]
 target=('end','of','the')
 windows=[]
 for p in sorted(MAIL.glob('*.eml')):
  raw=p.read_text(); body=raw.split('\n\n',1)[1] if '\n\n' in raw else raw
  toks=words(body)
  for i in range(max(0,len(toks)-2)):
   tri=toks[i:i+3]; idx=[low_value(w) for w in tri]
   if all(1<=v<=len(n20) for v in idx):
    out=tuple(n20[v-1] for v in idx)
    windows.append({'source':p.name,'offset':i,'tokens':tri,'indices':idx,'N20_output':out})
 route=json.loads(ROUTE.read_text())
 route_windows=[]
 for path,value in flatten(route):
  toks=words(value)
  for i in range(max(0,len(toks)-2)):
   tri=toks[i:i+3]; idx=[low_value(w) for w in tri]
   if all(1<=v<=len(n20) for v in idx):
    out=tuple(n20[v-1] for v in idx)
    route_windows.append({'source':path,'offset':i,'tokens':tri,'indices':idx,'N20_output':out})
 allw=windows+route_windows
 hits=[r for r in allw if r['N20_output']==target]
 valid_counts=Counter(' '.join(r['N20_output']) for r in allw)
 fixed=[]
 for n,body in notes.items():
  if all(1<=v<=len(body) for v in (12,10,11)):
   out=(body[11],body[9],body[10])
   if out==('the','end','of'): fixed.append(n)
 result={
  'source_sha256':EXPECTED,
  'email_three_word_windows':len(windows),'route_value_three_word_windows':len(route_windows),
  'valid_source_windows':len(allw),'N20_end_of_the_hits':hits,
  'N20_target_hit_count':len(hits),'most_common_N20_outputs':valid_counts.most_common(15),\n  'all_1054_source_windows':allw,
  'fixed_12_10_11_exact_the_end_of_notes':fixed,
  'n20_word_count':len(n20),
 }
 print(json.dumps(result,indent=2,sort_keys=True))
if __name__=='__main__': main()
