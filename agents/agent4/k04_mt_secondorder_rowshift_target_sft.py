"""Source-pinned K04 second-order row-shift test; selected ACK2 is withheld."""
import hashlib
import itertools
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SPOOL_SHA = '7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083'
ROUTE_SHA = 'f8fcbca73d23bf1066edb88c088f89cd24cf22e7c78a4a412166254a4764d8a5'
ACCEPT_SHA = '681739241b757b471acca4c0fef9d9d97e9493883887736d5db3b92bfb0c137f'
K04_SHA = '930a52a1bab97ca2966332137c99e99298ea6182fb32ab63a3421dfb4fd8c9e0'
MASK = bytes.fromhex('8556C8CB6140A7F9A5123AC7571BEE1C')
LOW31 = 0xBFFFFFFF


def temper(v):
    v ^= v >> 11
    v ^= (v << 7) & 0x9D2C5680
    v ^= (v << 15) & 0xEFC60000
    return (v ^ (v >> 18)) & 0xFFFFFFFF


def untemper(v):
    for step,left,mask in ((18,False,0xFFFFFFFF),(15,True,0xEFC60000),
                           (7,True,0x9D2C5680),(11,False,0xFFFFFFFF)):
        base = v
        for _ in range(6):
            v = base ^ (((v << step) & mask) if left else (v >> step))
        v &= 0xFFFFFFFF
    return v


def low_mix(v):
    return ((v & 0x7FFFFFFF) >> 1) ^ (0x9908B0DF if v & 1 else 0)


def source():
    b = (ROOT / 'resources/evidence/print/spool-reconstruction.log').read_bytes()
    assert hashlib.sha256(b).hexdigest() == SPOOL_SHA
    rows = [s for s in b.decode('ascii').splitlines() if s and not s.startswith('#')]
    assert len(rows) == 133
    assert all(s in rows[129] for s in
               ('JOB=PS-261003-0417','ATTEMPT=2','STATE=ACK','CLASS=RECOVER'))
    result = []
    for row,line in enumerate(rows):
        if row == 129:
            result.append(None)
            continue
        m = re.search(r'\bPAYLOAD=([0-9A-F]{32})\b',line)
        assert m,row
        raw = bytes.fromhex(m.group(1))
        result.append(tuple(untemper(int.from_bytes(raw[4*j:4*j+4],'little'))
                            for j in range(4)))
    return result


def predict(w,r,k,m,a,b,c):
    return (w[m][c] ^ low_mix(w[r][a]) ^ low_mix(w[k][b])) & LOW31


def main():
    route = ROOT/'resources/evidence/recovery-routing.json'
    accept = ROOT/'resources/acceptance.json'
    assert hashlib.sha256(route.read_bytes()).hexdigest() == ROUTE_SHA
    assert hashlib.sha256(accept.read_bytes()).hexdigest() == ACCEPT_SHA
    assert bytes.fromhex(json.loads(route.read_text())['K04']['masked_component']) == MASK
    assert json.loads(accept.read_text())['slot_sha256']['K04'] == K04_SHA
    for v in (0,1,0x12345678,0xFFFFFFFF):
        assert untemper(temper(v)) == v
    w = source()
    a = ((2,0,0,0),(3,1,1,1))
    b = ((1,1,0,1),(2,2,1,2),(3,3,2,3))
    for x,y,z,q in a:
        assert predict(w,9,40,63,x,y,z) == (w[124][q] & LOW31)
    for x,y,z,q in b:
        assert predict(w,10,41,64,x,y,z) == (w[125][q] & LOW31)
    print('ORIGINAL_REINFORCED controls=A2+B3 exact adjacent 31-bit relations')
    found = {}
    for label,lanes in (('A',a),('B',b)):
        for x,y,z,q in lanes:
            found.setdefault(q,[]).append((label,predict(w,14,45,68,x,y,z)))
    assert sorted(found) == [0,1,2,3]
    conflict = (found[1][0][1] ^ found[1][1][1]) & LOW31
    assert conflict.bit_count() == 16
    print('LANE_LOW31', {q:[(tag,f'{v:08X}') for tag,v in vals]
                          for q,vals in found.items()})
    original_hits = 0
    for label,word1 in found[1]:
        values = (found[0][0][1],word1,found[2][0][1],found[3][0][1])
        candidates = []
        for bitmap in range(16):
            words = [values[i] ^ (((bitmap >> i) & 1) << 30) for i in range(4)]
            coupon = b''.join(temper(v).to_bytes(4,'little') for v in words)
            component = bytes(x ^ y for x,y in zip(coupon,MASK))
            candidates.append(component)
            if hashlib.sha256(component).hexdigest() == K04_SHA:
                original_hits += 1
                print('ORIGINAL_K04_HIT',label,component.hex().upper())
        plant = hashlib.sha256(candidates[5]).digest()
        assert sum(hashlib.sha256(v).digest()==plant for v in candidates) == 1
        print('BRANCH',label,'SHA256_CHECKS',len(candidates),'PLANTED_HITS',1)
    assert original_hits == 0
    print('RESULT full_component_assignments=32 original_K04_hits=0',
          'q1_conflict_bits=16')


if __name__ == '__main__':
    main()
