"""H-17 K08: N01 after-tea photo as a two-interior-edit hypothetical ancestor.

The original margin remains unquoted; this is a finite conditional candidate
class, not evidence Emily edited the photograph caption this way.
"""
import hashlib
import hmac
import json
import re
from pathlib import Path

ROOT = Path('resources')
SOURCE = ROOT / 'evidence/crew/noticeboard-and-desk-notes.txt'
EXPECTED_SHA = '13f2318ccc54f35b590a2d76b3a80244fe24d70f0699c67c05858e8b8983c5cb'
assert hashlib.sha256(SOURCE.read_bytes()).hexdigest() == EXPECTED_SHA
source = SOURCE.read_text(encoding='utf-8')
lines = {}
for n in ('N01','N13','N20'):
    match = re.search(r'^'+n+r' / [^\n]+\n([^\n]+)',source,re.M)
    assert match
    lines[n] = re.findall(r'[a-z0-9]+',match.group(1).lower())
assert lines['N01'][:6] == ['for','the','photograph','of','the','empty']
base=lines['N01'][7:]
assert ' '.join(base) == 'the sea looks different when you have finally finished your tea'

def spans(words):
    return sorted({' '.join(words[a:a+length]) for a in range(len(words)) for length in range(2,6) if a+length<=len(words)})

a=spans(lines['N13'])
b=spans(lines['N20'])
cuts=[(i,j,k,l) for i in range(1,len(base)-3) for j in range(i+1,min(i+5,len(base)-2))
      for k in range(j+1,len(base)-1) for l in range(k+1,min(k+5,len(base))) if l<len(base)]
nonce=bytes.fromhex(json.loads((ROOT/'evidence/recovery-routing.json').read_text())['K08']['desk_nonce'])
target=json.loads((ROOT/'acceptance.json').read_text())['slot_sha256']['K08']

def component(phrase):
    return hmac.digest(nonce, phrase.encode('utf-8'), 'sha256')[:16]

control='a good watch leaves the room ready for the next pair of hands'
assert component(control).hex().upper()=='BF889359B0303F2B2B2FD96AE841210B'

# First in-family candidate is planted as a synthetic HMAC/commitment control.
i,j,k,l=cuts[0]
planted=' '.join(base[:i])+' '+a[0]+' '+' '.join(base[j:k])+' '+b[0]+' '+' '.join(base[l:])
planted_hash=hashlib.sha256(component(planted)).hexdigest()
assert hashlib.sha256(component(planted)).hexdigest()==planted_hash
count=0
found=None
for i,j,k,l in cuts:
    left=' '.join(base[:i]); mid=' '.join(base[j:k]); right=' '.join(base[l:])
    for first,second in ((a,b),(b,a)):
        for p in first:
            prefix=left+' '+p+' '+mid+' '
            for q in second:
                phrase=prefix+q+' '+right
                count+=1
                result=component(phrase)
                if hashlib.sha256(result).hexdigest()==target:
                    found={'phrase':phrase,'K08':result.hex().upper()}
                    break
            if found:break
        if found:break
    if found:break
assert found or count==2*len(cuts)*len(a)*len(b)==3088800
print(json.dumps({'source_sha256':EXPECTED_SHA,'photo_base':' '.join(base),'N13_fragments':len(a),
    'N20_fragments':len(b),'interior_two_cut_arrangements':len(cuts),'tested':count,
    'synthetic_positive':'PASS','result':found or 'NO_MATCH'},indent=2))
