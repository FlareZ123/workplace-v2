"""Exact xoroshiro128** state-link SFT for class-separated H-17 printer receipts.

Unlike a test on adjacent *spool* rows, this checks all surviving original
pairs, including nonadjacent RECOVER-only and source-class-separated streams.
The selected printer ACK2, K04 mask and acceptance commitments are excluded.
"""
import hashlib
from pathlib import Path

SOURCE = Path(__file__).resolve().parents[2] / 'resources/evidence/print/spool-reconstruction.log'
assert hashlib.sha256(SOURCE.read_bytes()).hexdigest() == '7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083'
M = (1 << 64) - 1
I5 = pow(5, -1, 1 << 64)
I9 = pow(9, -1, 1 << 64)

def rol(a, k):
    return ((a << k) | (a >> (64 - k))) & M

def ror(a, k):
    return ((a >> k) | (a << (64 - k))) & M

def nxt(s):
    a,b = s
    b ^= a
    a = rol(a,24) ^ b ^ ((b << 16) & M)
    b = rol(b,37)
    return a & M,b

def draw(s):
    return rol((s[0]*5)&M,7)*9&M

def inverse_out(out):
    return ror((out*I9)&M,7)*I5&M

def recover(words):
    a0, a1 = map(inverse_out,words)
    q = a1 ^ rol(a0,24)
    b = q
    b ^= (b << 16)&M
    b ^= (b << 32)&M
    initial = a0, b ^ a0
    assert draw(initial) == words[0]
    intermediate = nxt(initial)
    assert draw(intermediate) == words[1]
    return nxt(intermediate)

packets = []
for line in SOURCE.read_text().splitlines():
    if not line or line.startswith('#'):continue
    f = line.split()
    info = dict(x.split('=',1) for x in f[1:])
    if info['JOB']=='PS-261003-0417' and info['ATTEMPT']=='2' and info['STATE']=='ACK' and info['CLASS']=='RECOVER':
        continue
    packets.append((info,bytes.fromhex(info['PAYLOAD'])))
assert len(packets)==132
assert sum(x[0]['CLASS']=='RECOVER' for x in packets)>20

# Plant a real generator link of 378 missing outputs, then test recovered
# post-packet states rather than merely matching one output word.
seed = 0xDEADBEEF12345678,0xFACEB00CAABBCCDD
first = [draw(seed),draw(nxt(seed))]
after = recover(first)
future = after
for _ in range(378):future = nxt(future)
second = [draw(future),draw(nxt(future))]
assert recover(second) == nxt(nxt(future))
state = after
for _ in range(378):state = nxt(state)
assert state == future
print('GENUINE_SEEDED_POSITIVE: gap378 PASS')

for endian in ('big','little'):
    for reverse in (False,True):
        states=[]
        for info,data in packets:
            words=[int.from_bytes(data[:8],endian),int.from_bytes(data[8:],endian)]
            if reverse:words.reverse()
            states.append(recover(words))
        seen={s:i for i,s in enumerate(states)}
        assert len(seen)==132
        match=[]
        for i,s0 in enumerate(states):
            x=s0
            for gap in range(4097):
                j=seen.get(x)
                if j is not None and j!=i:
                    match.append((i,j,gap,packets[i][0]['CLASS'],packets[j][0]['CLASS']))
                x=nxt(x)
        sameclass=[x for x in match if x[-1]==x[-2]]
        print('ORIGINAL',endian,'reverse',reverse,'pairs_total',len(match),'same_class',len(sameclass),'examples',match[:4])
        assert not match
print('ALL_ORIGINAL_SOURCE_CHAINS: 132 source packets x 4097 states x 4 layouts = 2163216 state checks, zero links')
