"""Source-pinned K04/K08 printer bit-plane carrier search; read-only SFT."""
import hashlib as hs
import hmac
import itertools as it
from pathlib import Path
import re

root = Path(__file__).resolve().parents[2]
base = root / 'resources' if (root / 'resources').is_dir() else root
spool = (base / 'evidence/print/spool-reconstruction.log').read_bytes()
notes = (base / 'evidence/crew/noticeboard-and-desk-notes.txt').read_bytes()
sha = lambda b: hs.sha256(b).digest()
assert sha(spool).hex() == '7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083'
assert sha(notes).hex() == '13f2318ccc54f35b590a2d76b3a80244fe24d70f0699c67c05858e8b8983c5cb'
nonce = bytes.fromhex('5F933DA6A1BD03C32DA5CBC25344F497')
mask = bytes.fromhex('8556C8CB6140A7F9A5123AC7571BEE1C')
target4 = bytes.fromhex('930a52a1bab97ca2966332137c99e99298ea6182fb32ab63a3421dfb4fd8c9e0')
target8 = bytes.fromhex('285eb6b4196d21eaf47e251449e61e0bce28749881ccc5a065ca733b0c3fd747')
norm = lambda b: b' '.join(re.sub(rb'[^a-z0-9\s]', b' ', b.lower()).split())
red8 = lambda b: hmac.new(nonce, b, hs.sha256).digest()[:16]
assert red8(norm(b'A good watch leaves the room ready for the next pair of hands.')).hex().upper() == 'BF889359B0303F2B2B2FD96AE841210B'
pat = re.compile(rb'(\S+) JOB=(\S+) ATTEMPT=(\d+) STATE=(\w+) CLASS=(\w+) PAYLOAD=([0-9A-F]{32}) DEST=(\w+)')
records = [pat.fullmatch(s).groups() for s in spool.splitlines() if s and not s.startswith(b'#')]
assert len(records) == 133 and all(len(r[5]) == 32 for r in records)
assert [r[5] for r in records if r[:5] == (b'2026-10-03T18:02:00Z', b'PS-261003-0417', b'2', b'ACK', b'RECOVER')] == [b'A9A9DC5731A5E2AE879C47215C2559D5']
intact = [r for r in records if not (r[0] == b'2026-10-03T18:02:00Z' and r[1] == b'PS-261003-0417' and r[2] == b'2')]
groups = {
    'all_except_selected': intact,
    'label': [r for r in intact if r[4] == b'LABEL'],
    'stores': [r for r in intact if r[4] == b'STORES'],
    'recover_except_selected': [r for r in intact if r[4] == b'RECOVER'],
    'pre1800': [r for r in intact if r[0] < b'2026-10-03T18:00:00'],
    'samejob_request': [r for r in intact if r[1] == b'PS-261003-0417' and r[4] == b'RECOVER'],
}
assert tuple(len(groups[x]) for x in groups) == (132, 52, 41, 39, 128, 2)

def plane(packets, reversed_rows=False, reversed_cols=False, transpose=False,
          bit=0, invert=False, width=8, reversed_bits=False, phase=0):
    rows = packets[::-1] if reversed_rows else packets
    cols = range(15, -1, -1) if reversed_cols else range(16)
    vals = ([p[j] for j in cols for p in rows] if transpose else
            [p[j] for p in rows for j in cols])
    bits = [((v >> bit) & 1) ^ invert for v in vals]
    out = bytearray()
    for at in range(phase, len(bits)-width+1, width):
        segment = bits[at:at+width]
        if reversed_bits:
            segment = segment[::-1]
        n = 0
        for b in segment:
            n = (n << 1) | b
        out.append(n)
    return bytes(out)

def embedded(raw):
    bits = [int(c) for b in raw for c in f'{b:08b}']
    bits += [0] * (-len(bits) % 16)
    return [bytes(0xa4 | bit for bit in bits[i:i+16]) for i in range(0, len(bits), 16)]

old = b'Leave the light on for the next watch.'
assert plane(embedded(old))[:len(old)] == old
assert sha(red8(norm(plane(embedded(old))[:len(old)]))) == sha(red8(norm(old)))
synthetic = bytes.fromhex('8FF10002345566778899AABBCCDDEEFF')
assert plane(embedded(synthetic)) == synthetic
assert sha(bytes(a ^ b for a, b in zip(plane(embedded(synthetic)), mask))) == sha(bytes(a ^ b for a, b in zip(synthetic, mask)))
print('SYNTHETIC_CONTROLS_PASS')
seen4, seen8, hits = set(), set(), []
views = 0
for name, members in groups.items():
    packets = [bytes.fromhex(r[5].decode()) for r in members]
    for revrows, revcols, trans, bit, inv, width, revbits in it.product(
        (False, True), (False, True), (False, True), range(8), (False, True), (7, 8), (False, True)
    ):
        for phase in range(width):
            b = plane(packets, revrows, revcols, trans, bit, inv, width, revbits, phase)
            views += 1
            for start in range(len(b) - 15):
                coupon = b[start:start+16]
                if coupon in seen4:
                    continue
                seen4.add(coupon)
                component = bytes(a ^ m for a, m in zip(coupon, mask))
                if sha(component) == target4:
                    hits.append(('K04', name, component.hex().upper()))
            for run in re.finditer(rb"[A-Za-z0-9 ,.!?':;\-]{14,}", b):
                words = norm(run.group()).split()
                for i in range(len(words)):
                    for j in range(i+2, min(i+24, len(words))+1):
                        chosen = words[i:j]
                        if sum(len(w) >= 3 for w in chosen) < 2:
                            continue
                        phrase = b' '.join(chosen)
                        if len(phrase) < 14 or phrase in seen8:
                            continue
                        seen8.add(phrase)
                        if sha(red8(phrase)) == target8:
                            hits.append(('K08', name, phrase.decode('ascii')))
    print('GROUP_COMPLETE', name, len(packets), views, len(seen4), len(seen8), flush=True)
print('RESULT', 'views', views, 'complete_K04', len(seen4), 'complete_K08', len(seen8), 'hits', hits)
assert views == 23040 and len(seen4) == 2333824 and len(seen8) == 74 and not hits
