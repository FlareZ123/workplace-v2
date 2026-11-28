#!/usr/bin/env python3
"""K08 COUNT LINE tokenizer sensitivity, pinned source, ID-only output.
No K08 nonce, acceptance digest, candidate text, or quarantined PDF accessed.
Run from repo root: python agents/agent45/k08_countline_tokenizer_coherence_sft.py
"""
from pathlib import Path
import hashlib,re
p=Path(__file__).resolve().parents[2]/'resources/evidence/crew/noticeboard-and-desk-notes.txt'
data=p.read_bytes()
assert hashlib.sha256(data).hexdigest()=='13f2318ccc54f35b590a2d76b3a80244fe24d70f0699c67c05858e8b8983c5cb'
rec=re.findall(r'^N(\d\d) / [^\n]+\n([^\n]+)',data.decode(),re.M)
assert len(rec)==24

def graph(mode):
    counts={}
    for raw,line in rec:
        body=line.partition(': ')[2] if ': ' in line else line
        counts[int(raw)]=len(body.split() if mode=='whitespace' else re.findall(r'[A-Za-z0-9]+',body))
    edges={n:k+int(k%2==0) for n,k in counts.items()}
    path=[];j=9
    while j in edges and j not in path:
        path.append(j);j=edges[j]
    return counts,edges,path,j
w,ew,pw,cw=graph('whitespace')
a,ea,pa,ca=graph('alnum')
assert [n for n in w if w[n]!=a[n]]==[15]
assert (w[15],a[15],ew[15],ea[15])==(9,10,9,11)
assert pw==pa==[9,13,23,21,11,15]
assert (cw,ca)==(9,11)
stow=(19,20,15,23)
assert [w[n] for n in stow]==[22,30,9,21]
assert [a[n] for n in stow]==[22,30,10,21]
selector=lambda d:sum((d[n]&1)<<i for i,n in enumerate(stow))
assert (selector(w),selector(a))==(12,8)
print('N15 source tokenizer dependence: whitespace 9 -> row9; alnum 10 -> row11')
print('STOW source lowbit: whitespace 12 -> row13; alnum 8 -> row9')
print('From N09: whitespace cycle [9,13,23,21,11,15]; alnum cycle [11,15]')
print('No unique complete terminal K08 caption from either operator')
