"""Bounded deletion-only terminal-edit hypothesis for Emily-authored draft notes.

Each candidate is any nonempty order-preserving token subsequence of one source
sentence N02, N06 or N13, retaining source words exactly. No source mutation.
"""
import hashlib
import hmac
import json
import re
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
ROOT = REPO / 'resources' if (REPO / 'resources').exists() else Path(__file__).resolve().parents[1]
raw_notes = (ROOT/'evidence/crew/noticeboard-and-desk-notes.txt').read_bytes()
assert hashlib.sha256(raw_notes).hexdigest() == '13f2318ccc54f35b590a2d76b3a80244fe24d70f0699c67c05858e8b8983c5cb'
notes = raw_notes.decode('utf-8')
route = json.loads((ROOT/'evidence/recovery-routing.json').read_text())
accept = json.loads((ROOT/'acceptance.json').read_text())
nonce = bytes.fromhex(route['K08']['desk_nonce'])
target = bytes.fromhex(accept['slot_sha256']['K08'])
count = 0
for note_id in ('N02','N06','N13'):
    original = re.search(r'^'+note_id+r' / [^\n]+\n([^\n]+)',notes,re.M)[1]
    if note_id != 'N13':
        original = original.split(':', 1)[1]
    words = re.findall(r'[a-z0-9]+',original.lower())
    n = len(words)
    assert n <= 23
    hit = None
    control = False
    for b in range(1,(1<<n)):
        s = ' '.join(w for i,w in enumerate(words) if b & (1<<i))
        digest = hmac.digest(nonce, s.encode(), 'sha256')[:16]
        count += 1
        if note_id == 'N02' and b == (1<<n)-1:
            assert digest.hex().upper() == 'BF889359B0303F2B2B2FD96AE841210B'
            control = True
            assert hashlib.sha256(digest).digest() == hashlib.sha256(bytes.fromhex('BF889359B0303F2B2B2FD96AE841210B')).digest()
        if hashlib.sha256(digest).digest() == target:
            hit=(note_id,s,digest.hex().upper(),b)
            break
    print(note_id,'original_tokens',n,'tested', (1<<n)-1 if hit is None else 'until match', 'N02 literal positive' if control else '')
    if hit:
        print('PASS', hit)
        break
print('total_checked',count, 'K08_commitment_pass', bool(hit))
