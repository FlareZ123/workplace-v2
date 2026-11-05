"""Original-source K08 HMAC known-label transport across all surviving evidence windows.

Hypothesis: at least two of N02/N06/N17/N18 normalized caption HMAC16s
were stored in the archive under a shared 128-bit XOR or additive pad,
with one common word layout. Test all genuine raw 16-byte file windows and
contiguous 32+-hex-character decoded windows. Source/read-only; a synthetic
common-pad positive is checked by the same matching machinery.
"""
import hashlib
import hmac
import json
import re
from itertools import combinations
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2] / 'resources'
NOTES = ROOT / 'evidence/crew/noticeboard-and-desk-notes.txt'
SPOOL = ROOT / 'evidence/print/spool-reconstruction.log'
assert hashlib.sha256(NOTES.read_bytes()).hexdigest() == '13f2318ccc54f35b590a2d76b3a80244fe24d70f0699c67c05858e8b8983c5cb'
assert hashlib.sha256(SPOOL.read_bytes()).hexdigest() == '7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083'
nonce = bytes.fromhex(json.loads((ROOT/'evidence/recovery-routing.json').read_text())['K08']['desk_nonce'])
notes = {int(n): text.split(':',1)[-1].strip() for n, text in re.findall(r'^N(\d+) / Emily \[censored\]\n(.+)$', NOTES.read_text(), re.M)}
def normalize(s):
    return ' '.join(re.sub(r'[^a-z0-9\s]', ' ',s.lower()).split())
def h16(s):
    return hmac.digest(nonce,normalize(s).encode(),'sha256')[:16]
control = {id:h16(notes[id]) for id in (2,6,17,18)}
assert control[2].hex().upper()=='BF889359B0303F2B2B2FD96AE841210B'
assert notes[17]=='Leave the light on for the next watch.'
assert notes[18]=='Back before the first boat.'

# Evidence-only byte stream and decoded 32+ hex-string windows.
raw_windows=[]
hex_windows=[]
input_files=[]
for file in sorted((ROOT/'evidence').rglob('*')):
    if not file.is_file():
        continue
    data=file.read_bytes()
    if file==SPOOL:
        # Retained selected ACK2 is not an authenticated physical coupon.
        lines=data.splitlines(keepends=True)
        actual = [s for s in lines if b'JOB=PS-261003-0417 ATTEMPT=2 STATE=ACK CLASS=RECOVER' in s]
        assert len(actual)==1
        data=b''.join(s for s in lines if s not in actual)
    input_files.append((file.relative_to(ROOT).as_posix(), len(data)))
    raw_windows.extend(data[i:i+16] for i in range(len(data)-15))
    for m in re.finditer(rb'(?<![0-9A-Fa-f])[0-9A-Fa-f]{32,}(?![0-9A-Fa-f])',data):
        text=m.group(0)
        if len(text)%2: text=text[:-1]
        decoded=bytes.fromhex(text.decode('ascii'))
        hex_windows.extend(decoded[i:i+16] for i in range(len(decoded)-15))
raw_windows=list(set(raw_windows));hex_windows=list(set(hex_windows))
assert len(input_files)==42

LAYOUTS = {'native':lambda b:b,
           'reverse16':lambda b:b[::-1],
           'reverse_words':lambda b:b[12:16]+b[8:12]+b[4:8]+b[:4],
           'reverse_each_word':lambda b:b[0:4][::-1]+b[4:8][::-1]+b[8:12][::-1]+b[12:16][::-1]}
MASK=(1<<128)-1

def expected_other(left, first, second, kind):
    if kind=='xor':
        return bytes(x^y^z for x,y,z in zip(left,first,second))
    if kind=='add128':
        delta=int.from_bytes(first,'big')-int.from_bytes(second,'big')
        return ((int.from_bytes(left,'big')-delta)&MASK).to_bytes(16,'big')
    if kind=='byteadd':
        return bytes((v-(a-b))&255 for v,a,b in zip(left,first,second))
    raise AssertionError(kind)

def probe(name, corpus):
    represented=set(corpus)
    total=0
    matches=[]
    for kind in ('xor','add128','byteadd'):
        for label_pair in combinations(control,2):
            a,b=(control[i] for i in label_pair)
            for layname,layout in LAYOUTS.items():
                ax,bx=layout(a),layout(b)
                for left in represented:
                    right=expected_other(left,ax,bx,kind)
                    total+=1
                    if right in represented and right!=left:
                        matches.append((kind,label_pair,layname,left.hex(),right.hex()))
    print('CORPUS',name,'input_files',len(input_files),
          'windows',len(represented),'comparison_left_assignments',total,
          'complete_matches',len(matches),flush=True)
    if matches:
        print('ORIGINAL_CALIBRATION_MATCHES',matches[:10],flush=True)
    return matches

# Two genuine synthetic old-caption ciphertexts share a nonzero secret XOR
# pad, and the same pair-difference matching mechanism must find them.
pad=bytes.fromhex('91DA5C0F861E67A62B4508D3C214B795')
a=bytes(x^y for x,y in zip(control[17],pad))
b=bytes(x^y for x,y in zip(control[18],pad))
assert a!=b and expected_other(a,control[17],control[18],'xor')==b
synthetic = probe('synthetic', (a, b))
assert any(m[0]=='xor' and m[1]==(17,18) and m[2]=='native' for m in synthetic)
all_raw_matches=probe('raw',raw_windows)
all_hex_matches=probe('decoded_hex',hex_windows)
combined_matches=probe('combined',raw_windows+hex_windows)
assert not all_raw_matches and not all_hex_matches and not combined_matches
print('PLANTED_TWO_LABEL_COMMON_PAD_POSITIVE=PASS ORIGINAL_SOURCE_NO_MATCH=PASS')
