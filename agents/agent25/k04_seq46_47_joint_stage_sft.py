"""SFT: conditional original node50 seq46/47 stage versus printer p951.

Run from checkout: python agents/agent25/k04_seq46_47_joint_stage_sft.py
Read-only; selected row129, route mask and acceptance checks excluded.
"""
import hashlib
import itertools
import struct
import sys
import zlib
from functools import lru_cache
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "agents" / "agent49"))
from k04_p951_symbolic_basis import Basis, source, get, untemper, temper

RECORD_SHA = "5ebc6204ed773102237dd287772de96d19740e163b49b4075537d937888657ba"

def recorder_controls():
    raw = (ROOT / "resources/evidence/recorder/trip-recorder.raw").read_bytes()
    assert hashlib.sha256(raw).hexdigest() == RECORD_SHA
    result = {}
    for row in range(88):
        at = 16 + row*24
        stamp,node,event,latch,seq,word,aux,crc = struct.unpack_from("<IHBBI4sII",raw,at)
        if node == 50 and zlib.crc32(raw[at:at+20]) == crc:
            result[seq] = word
    assert result[45].hex().upper() == "4BC25CCB"
    assert result[46].hex().upper() == "49B23079"
    assert result[47].hex().upper() == "98535679"
    return result

def insert_control(basis, symbolic, at, raw):
    out = Basis()
    out.rows = basis.rows.copy()
    out.rank = basis.rank
    native = untemper(int.from_bytes(raw, "little"))
    try:
        for bit,term in enumerate(get(symbolic, at)):
            out.insert(term, (native >> bit) & 1)
    except AssertionError:
        return None
    return out

def target_rank(basis, selected):
    expanded = Basis()
    expanded.rows = {p: (term,0) for p,(term,_) in basis.rows.items()}
    expanded.rank = basis.rank
    for term in selected:
        expanded.insert(term,0)
    return expanded.rank - basis.rank

def possible(basis, symbolic, at, n, observed):
    k = n.bit_length()
    predictions = [basis.predict(term) for term in temper(get(symbolic,at))[32-k:]]
    values = [observed] if observed is not None else range(n,1<<k)
    return any(all(bit is None or bit == ((candidate >> j)&1) for j,bit in enumerate(predictions))
               for candidate in values)

def feasible_orders(basis, symbolic, start, end, aux, time_offset, event, latch):
    fields = {"aux":(6000,aux-2000), "time":(400,time_offset),
              "event":(39,event-1), "latch":(4,latch)}
    checks = {}
    for name,(n,value) in fields.items():
        for at in range(start+1,end):
            checks[name,at,True] = possible(basis,symbolic,at,n,value)
            checks[name,at,False] = possible(basis,symbolic,at,n,None)
    found = []
    for order in itertools.permutations(fields):
        @lru_cache(None)
        def step(i,at):
            if i == 4: return True
            name = order[i]
            for lo in range(at,end):
                for hi in range(lo,end):
                    if checks[name,hi,True] and all(checks[name,p,False] for p in range(lo,hi)):
                        if step(i+1,hi+1): return True
            return False
        if step(0,start+1): found.append(order)
    return found

def main():
    controls = recorder_controls()
    basis,symbolic = source(ROOT/"resources")
    assert basis.rank == 15365
    selected = [term for at in range(951,955) for term in get(symbolic,at)]
    assert target_rank(basis,selected) == 128
    direct = insert_control(basis,symbolic,-523,controls[47])
    assert direct is not None and direct.rank-basis.rank == 31
    assert target_rank(direct,selected) == 127
    viable = []
    for at in range(-536,-523):
        first = insert_control(basis,symbolic,at,controls[46])
        if first is None: continue
        second = insert_control(first,symbolic,-523,controls[47])
        if second is not None:
            viable.append((at, second.rank-basis.rank, target_rank(second,selected)))
    assert viable == [(-531,63,127)],viable
    print("Conditional source placement:",viable)
    middle = insert_control(basis,symbolic,-531,controls[46])
    both = insert_control(middle,symbolic,-523,controls[47])
    for title, fit in (("printer-only",basis),("two-controls-assigned",both)):
        a = feasible_orders(fit,symbolic,-540,-531,5088,172,6,1)
        b = feasible_orders(fit,symbolic,-531,-523,3111,315,4,1)
        print(title,"field orders 45->46",len(a),"46->47",len(b))
        assert a == [] and b == []
    print("PASS: 12 alternate middle placements contradicted; 24 possible four-field orders"
          " cannot explain either adjacent interval, even with latent draws.")
    print("Original selected coupon and original recovery commitments not accessed.")

if __name__ == "__main__":
    main()
