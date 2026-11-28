#!/usr/bin/env python3
"""Target-blind N20 postlabel first-24-character LOW BIT / A1Z26 gate.

Reads one SHA-pinned original crew-note text; no nonce, commitment or PDF.
Run: python agents/agent10/k08_n20_rawbody_mhi_gate_sft.py resources/evidence/crew/noticeboard-and-desk-notes.txt
"""
import hashlib,re,sys
from pathlib import Path
source=Path(sys.argv[1]) if len(sys.argv)>1 else Path('resources/evidence/crew/noticeboard-and-desk-notes.txt')
raw=source.read_bytes()
assert hashlib.sha256(raw).hexdigest()=='13f2318ccc54f35b590a2d76b3a80244fe24d70f0699c67c05858e8b8983c5cb'
notes={int(i):text for i,text in re.findall(r'^N(\d{2}) / [^\n]+\n([^\n]+)',raw.decode('utf8'),re.M)}
assert set(notes)==set(range(1,25))
def body(i):
    line=notes[i]
    return line.split(':',1)[-1].lstrip() if ':' in line else line
def low3(text):
    assert len(text)>=24
    bits=[ord(c)&1 for c in text[:24]]
    return bytes(sum(bits[8*j+k]<<k for k in range(8)) for j in range(3))
assert low3(body(20))==b'MHI'
addresses=[b-64 for b in low3(body(20))]
assert addresses==[13,8,9]
labels=[notes[i].split(':',1)[0] if ':' in notes[i] else 'unlabelled scene' for i in addresses]
assert labels[1]=='Window photograph'
assert labels[2]=='Caption for the galley board'
all_upper=[i for i in range(1,25) if all(65<=x<=90 for x in low3(body(i)))]
assert all_upper==[20]
print('N20 first24 ASCII lowbits=MHI; A1Z26 note IDs=(13,8,9)')
print('Controls: uppercase 3byte starts=1 of 24; SHA pin=PASS; K08 target=NOT READ')
