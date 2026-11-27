#!/usr/bin/env python3
from __future__ import annotations
import hashlib,re,sys
from pathlib import Path
EXPECTED_SHA='13f2318ccc54f35b590a2d76b3a80244fe24d70f0699c67c05858e8b8983c5cb'

def strip_label(body:str)->str:
    return body.split(':',1)[1].lstrip() if ':' in body else body

def words(s:str): return re.findall(r'[A-Za-z0-9]+',s)

def main(path:str)->None:
    p=Path(path); data=p.read_bytes(); assert hashlib.sha256(data).hexdigest()==EXPECTED_SHA
    raw=data.decode('utf-8'); lines=raw.splitlines(); notes={}
    for i,line in enumerate(lines):
        m=re.fullmatch(r'(N\\d\\d) / ([^[]+) \\[censored\\]',line)
        if m:
            notes[m.group(1)]={'author':m.group(2).strip(),'body':lines[i+1],'body_line':i+2}
    assert len(notes)==24
    chosen={'Simon','Emily','Gabriel'}
    bits=''.join('1' if notes[f'N{i:02d}']['author'] in chosen else '0' for i in range(1,25))
    vals=[sum((int(bits[5*j+k])<<k) for k in range(5)) for j in range(4)]
    text=''.join(chr(ord('A')+v) for v in vals)
    suffix=sum((int(bits[20+k])<<k) for k in range(4))
    assert (bits,text,suffix)==('010011100101110011010111','STOW',14)
    ids=[ord(c)-ord('A')+1 for c in text]
    assert ids==[19,20,15,23]
    cues=['count','line','between','margin']
    for n,cue in zip(ids,cues):
        assert re.search(rf'\\b{cue}\\b',notes[f'N{n:02d}']['body'].lower())
    count_line=notes['N19']['body_line']; margin_line=notes['N23']['body_line']
    between=margin_line-count_line-1
    assert (count_line,margin_line,between)==(59,71,11)
    first11=words(strip_label(notes['N11']['body']))[0].lower()
    first14=words(strip_label(notes['N14']['body']))[0].lower()
    assert (first11,first14)==('even','if')
    david=[f'N{i:02d}' for i in range(1,25) if notes[f'N{i:02d}']['author']=='David']
    counts=[len(words(strip_label(notes[n]['body']))) for n in david]
    low=''.join(chr(ord('A')+v) for v in counts)
    assert david==['N04','N11','N19'] and counts==[11,14,22] and low=='LOW'
    char14=''.join(strip_label(notes[f'N{n:02d}']['body'])[13] for n in ids)
    assert char14==' len'
    print('STOW14 bits=',bits)
    print('STOW A1Z26 note IDs=',ids)
    print('cue words=COUNT LINE BETWEEN MARGIN')
    print('strict physical lines between COUNT body line 59 and MARGIN body line 71=',between)
    print('suffix14 -> N14 first body word=',first14.upper())
    print('line-count11 -> N11 first body word=',first11.upper())
    print('David body counts=',counts,'->',low)
    print('derived directive=',low,first14.upper(),first11.upper())
    print('secondary char14=',repr(char14),'(exploratory; not used in directive)')
if __name__=='__main__':
    if len(sys.argv)!=2: raise SystemExit('usage: script noticeboard-and-desk-notes.txt')
    main(sys.argv[1])
