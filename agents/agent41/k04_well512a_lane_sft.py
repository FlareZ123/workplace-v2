"""Original-spool WELL512a 512-state source/selected-lane falsifier.

Reproducer for Agent41, 6 Nov 2026. Python 3 standard library only.
Original selected 18:02 ACK2 excluded. Reproducer assumes repo checkout.
"""
from collections import defaultdict
from hashlib import sha256
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / 'resources/evidence/print/spool-reconstruction.log'
SHA = '7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083'
MASK = 0xffffffff


def well(state, n):
    v, i, out = state.copy(), 0, []
    for _ in range(n):
        j = (i+15)&15
        z1 = (v[i] ^ (v[i]<<16) ^ v[(i+13)&15] ^ (v[(i+13)&15]<<15))&MASK
        z2 = v[(i+9)&15] ^ (v[(i+9)&15]>>11)
        z3 = z1^z2
        z4 = (v[j] ^ (v[j]<<2) ^ z1 ^ (z1<<18) ^ (z2<<28) ^ z3 ^ ((z3<<5)&0xda442d24))&MASK
        v[i],v[j],i = z3,z4,j
        out.append(z4)
    return out


def solve(columns, observed):
    basis, contradictions = {}, 0
    for t, y in enumerate(observed):
        for k in range(32):
            row = sum(((c[t]>>k)&1)<<j for j,c in enumerate(columns))
            rhs = (y>>k)&1
            while row:
                pivot = row.bit_length()-1
                if pivot not in basis:
                    basis[pivot]=(row,rhs)
                    break
                old, val = basis[pivot]
                row, rhs = row^old, rhs^val
            else:
                contradictions += rhs
    state = 0
    for i in sorted(basis):
        row,rhs = basis[i]
        if (((row & ((1<<i)-1) & state).bit_count()&1)^rhs):
            state |= 1<<i
    return len(basis), contradictions, [(state>>(32*j))&MASK for j in range(16)]


def words(payload, endian, reverse):
    a = [int.from_bytes(payload[i:i+4], endian) for i in (0,4,8,12)]
    return a[::-1] if reverse else a


def main():
    data = SOURCE.read_bytes()
    assert sha256(data).hexdigest()==SHA
    lines = [s for s in data.decode().splitlines() if 'PAYLOAD=' in s]
    ordinary = [s for s in lines if s[:16]<'2026-10-03T17:36' and 'PAYLOAD=' in s]
    assert len(ordinary)==128
    groups = defaultdict(list)
    for s in ordinary:
        class_ = s.split('CLASS=')[1].split()[0]
        dest = s.split('DEST=')[1].split()[0]
        payload = bytes.fromhex(s.split('PAYLOAD=')[1].split()[0])
        for key in ('all', 'class='+class_, 'dest='+dest, 'pair='+class_+'_'+dest):
            groups[key].append(payload)
    assert len(groups)==16
    columns = []
    for bit in range(512):
        state=[0]*16
        state[bit//32]=1<<(bit%32)
        columns.append(well(state,24))
    tested = 0
    for lane, rows in sorted(groups.items()):
        assert len(rows)>=6
        for endian in ('little','big'):
            for rev in (False,True):
                observed = [v for p in rows[:6] for v in words(p,endian,rev)]
                rank,bad,state = solve(columns, observed)
                hold = [v for p in rows[6:12] for v in words(p,endian,rev)]
                generated = well(state,24+len(hold))
                errors = sum(x!=y for x,y in zip(hold,generated[24:]))
                assert rank==512 and bad>0 and errors==len(hold)
                print(f'{lane} {endian} rev={int(rev)} rank={rank} violated_train_bits={bad} wrong_heldout_words={errors}/{len(hold)}')
                tested+=1
    state=[(i*0x9e3779b9+0x1234abcd)&MASK for i in range(16)]
    rank,bad,rec=solve(columns,well(state,24))
    assert rank==512 and bad==0 and rec==state and well(rec,100)==well(state,100)
    print(f'ORIGINAL_CONFIGS={tested} SOURCE_FITS=0 PLANTED_COMPLETE_STATE_AND_100_OUTPUTS_PASS')


if __name__=='__main__':
    main()
