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
        m=re.fullmatch(r'(N\d\d) / ([^[]+) \[censored\]',line)
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
        assert re.search(rf'\b{cue}\b',notes[f'N{n:02d}']['body'].lower())
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
    cue_initials=''.join(cue[0].upper() for cue in cues)
    cue_initial_bits=[((ord(ch)-ord('A')+1)&1) for ch in cue_initials]
    cue_initial_selector=sum(bit<<i for i,bit in enumerate(cue_initial_bits))
    assert cue_initials=='CLBM' and cue_initial_bits==[1,0,0,1] and cue_initial_selector==9
    cue_positions=[]
    for n,cue in zip(ids,cues):
        ww=[w.lower() for w in words(strip_label(notes[f'N{n:02d}']['body']))]
        cue_positions.append([i+1 for i,w in enumerate(ww) if w==cue])
    assert cue_positions==[[5,10],[4],[8],[5]]
    # First COUNT occurrence gives parity 1,0,0,1 -> 9 directly. The second
    # occurrence gives 0,0,0,1 -> 8, and LOW IF EVEN resolves 8 downward to 9.
    cue_selector_first=sum(((pos[0]&1)<<i) for i,pos in enumerate(cue_positions))
    cue_selector_second=((cue_positions[0][1]&1)<<0) | sum(((cue_positions[i][0]&1)<<i) for i in range(1,4))
    assert (cue_selector_first,cue_selector_second)==(9,8)
    assert (cue_selector_first if cue_selector_first%2 else cue_selector_first+1)==9
    assert (cue_selector_second if cue_selector_second%2 else cue_selector_second+1)==9
    selected_counts=[len(words(strip_label(notes[f'N{n:02d}']['body']))) for n in ids]
    count_bits=[v&1 for v in selected_counts]
    count_low=sum(bit<<i for i,bit in enumerate(count_bits))
    assert selected_counts==[22,30,10,21] and count_bits==[0,0,0,1] and count_low==8
    lowered=count_low+1 if count_low%2==0 else count_low
    assert lowered==9
    assert strip_label(notes['N08']['body']).startswith('By daylight the water')
    n09_label=notes['N09']['body'].split(':',1)[0]
    n09_label_words=words(n09_label)
    assert n09_label=='Caption for the galley board' and n09_label_words==['Caption','for','the','galley','board']
    n09_head_initial_bits=[((ord(w[0].upper())-ord('A')+1)&1) for w in n09_label_words]
    n09_head_initial_selector=sum(bit<<i for i,bit in enumerate(n09_head_initial_bits))
    n09_head_length_bits=[len(w)&1 for w in n09_label_words]
    n09_head_length_selector=sum(bit<<i for i,bit in enumerate(n09_head_length_bits))
    assert n09_head_initial_bits==[1,0,0,1,0] and n09_head_initial_selector==9
    assert n09_head_length_bits==[1,1,1,0,1] and n09_head_length_selector==23
    rawbits=[ord(ch)&1 for ch in n09_label]
    n09_head_octets=bytes(sum(rawbits[i+j]<<j for j in range(8)) for i in range(0,24,8))
    assert n09_head_octets==b'3B3' and int(n09_head_octets.decode(),16)==947
    # Specificity control over every colon-prefix heading: N09 alone self-indexes
    # under first-five A1Z26 initial low bits. (Short headings use all words.)
    self_head=[]
    for i in range(1,25):
        body=notes[f'N{i:02d}']['body']
        if ':' not in body: continue
        hw=words(body.split(':',1)[0])[:5]
        v=sum((((ord(w[0].upper())-ord('A')+1)&1)<<j) for j,w in enumerate(hw))
        if v==i: self_head.append(i)
    assert self_head==[9]
    long_hex=[]
    for i in range(1,25):
        body=notes[f'N{i:02d}']['body']
        if ':' not in body: continue
        label=body.split(':',1)[0]
        if len(label)<24: continue
        bb=[ord(ch)&1 for ch in label]
        oct3=bytes(sum(bb[k+j]<<j for j in range(8)) for k in (0,8,16))
        if all(chr(x) in '0123456789ABCDEFabcdef' for x in oct3): long_hex.append((i,oct3.decode()))
    assert long_hex==[(9,'3B3')]
    assert strip_label(notes['N09']['body']).startswith('Nobody should have to make their first cup')
    lineage=[]
    cur=9
    for _ in range(2):
        cnt=len(words(strip_label(notes[f'N{cur:02d}']['body'])))
        nxt=cnt+1 if cnt%2==0 else cnt
        lineage.append((cur,cnt,nxt))
        cur=nxt
    assert lineage==[(9,13,13),(13,22,23)]
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
    print('cue initials=',cue_initials,'A1Z26 low bits=',cue_initial_bits,'-> N%02d'%cue_initial_selector)
    print('cue word positions=',cue_positions,'parity selectors=',cue_selector_first,cue_selector_second,'-> N09 after LOW IF EVEN')
    print('STOW note word counts=',selected_counts,'low bits=',count_bits,'-> N%02d'%count_low)
    print('LOW IF EVEN -> N%02d'%lowered,'=',strip_label(notes['N09']['body']))
    print('N09 heading initial low bits=',n09_head_initial_bits,'-> N%02d'%n09_head_initial_selector,'unique heading self-index=',self_head)
    print('N09 heading word-length low bits=',n09_head_length_bits,'-> N%02d'%n09_head_length_selector)
    print('N09 heading ASCII low-bit full octets=',n09_head_octets.decode(),'-> hex stage',int(n09_head_octets.decode(),16),'(cross-slot locator clue only)')
    print('long-heading three-octet printable-hex controls=',long_hex)
    print('COUNT LINE / LOW IF EVEN lineage=',lineage,'=> N23 final-margin record')
    print('secondary char14=',repr(char14),'(exploratory; not used in directive)')
if __name__=='__main__':
    if len(sys.argv)!=2: raise SystemExit('usage: script noticeboard-and-desk-notes.txt')
    main(sys.argv[1])
