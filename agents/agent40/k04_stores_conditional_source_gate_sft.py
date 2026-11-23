"""Source-only stage discriminator for a third printer metadata draw.

Run: python agents/agent40/k04_stores_conditional_source_gate_sft.py
Assumes all 42 observed untempered MT19937 recurrences come from one stream.
The selected row129 ACK2 PAYLOAD is withheld before decoding.
No target commitment or copied selected PAYLOAD is used.
"""
from __future__ import annotations
import hashlib
import re
from collections import defaultdict
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
U=0xFFFFFFFF
MAG=0x9908B0DF

def untemper(v):
    v ^= v >> 18
    v ^= (v << 15) & 0xEFC60000
    old=v
    for _ in range(6):v=old^((v<<7)&0x9D2C5680)
    old=v
    for _ in range(4):v=old^(v>>11)
    return v & U

def twist(a,b):
    joined=(a&0x80000000)|(b&0x7FFFFFFF)
    return (joined>>1)^(MAG if joined&1 else 0)

def source_words(packets):
    return [None if packet is None else [
        untemper(int.from_bytes(packet[i:i+4],'little')) for i in (0,4,8,12)
    ] for packet in packets]

def witnesses_from_source(native):
    inverted=defaultdict(list)
    for r,packet in enumerate(native):
        if packet is not None:
            for i,word in enumerate(packet):inverted[word].append((r,i))
    full=[];partial=[]
    for r,packet in enumerate(native):
        if packet is None:continue
        for k in range(r+1,len(native)):
            later=native[k]
            if later is None:continue
            for i,word in enumerate(later):
                for p in (1,2,3):
                    for l,q in inverted.get(word^twist(packet[p-1],packet[p]),()):
                        if l>k:full.append((r,k,l,p,i,q))
                for upper in (0,0x80000000):
                    for l,q in inverted.get(word^twist(upper,packet[0]),()):
                        if l>k:partial.append((r,k,l,0,i,q))
    return full,partial

def integer_feasible(nodes,edges):
    distance=[0]*nodes
    for _ in range(nodes):
        changed=False
        for source,dest,bound in edges:
            new=distance[source]+bound
            if new<distance[dest]:
                distance[dest]=new
                changed=True
        if not changed:return True,[x-distance[0] for x in distance]
    return False,None

SOURCE_SHA='7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083'
REGEX=rb'^(\S+) JOB=(\S+) ATTEMPT=(\d+) STATE=(\w+) CLASS=(\w+) PAYLOAD=([0-9A-F]{32}) DEST=(\w+)$'

def load_original():
    raw=(ROOT/'resources/evidence/print/spool-reconstruction.log').read_bytes()
    assert hashlib.sha256(raw).hexdigest()==SOURCE_SHA
    rows=re.findall(REGEX,raw,re.M)
    assert len(rows)==133
    assert rows[129][:5]==(b'2026-10-03T18:02:00Z',b'PS-261003-0417',b'2',b'ACK',b'RECOVER')
    native=source_words([None if i==129 else bytes.fromhex(row[5].decode('ascii')) for i,row in enumerate(rows)])
    full,partial=witnesses_from_source(native)
    assert (len(full),len(partial))==(25,17)
    return rows,full+partial

def edges(rows,witnesses,field,value,association,requested_min=0):
    out=[]
    for i,row in enumerate(rows[:-1]):
        minimum=requested_min if row[3]==b'REQUESTED' else 6+int(rows[i+(association=='next')][field]==value)
        out.extend(((i,i+1,100),(i+1,i,-minimum)))
    for r,k,l,p,i,q in witnesses:
        for target,difference in ((k,396+p-i),(l,623+p-q)):
            out.extend(((r,target,difference),(target,r,-difference)))
    return out

def main():
    rows,witnesses=load_original()
    expected={
        (4,b'LABEL','current'):False,(4,b'LABEL','next'):False,
        (4,b'RECOVER','current'):False,(4,b'RECOVER','next'):False,
        (4,b'STORES','current'):True,(4,b'STORES','next'):True,
        (6,b'bench','current'):True,(6,b'bench','next'):True,
        (6,b'desk','current'):True,(6,b'desk','next'):True,
        (6,b'store','current'):True,(6,b'store','next'):False,
    }
    for (field,value,association),required in expected.items():
        possible,stages=integer_feasible(len(rows),edges(rows,witnesses,field,value,association))
        assert possible==required,(field,value,association,possible)
        if possible:
            assert stages is not None
            assert all(stages[k]-stages[r]==396+p-i and stages[l]-stages[r]==623+p-q for r,k,l,p,i,q in witnesses)
        print(f'{"CLASS" if field==4 else "DEST"}={value.decode()} {association}: {"FEASIBLE" if possible else "INFEASIBLE"}')
    for association,upper in (('current',2),('next',3)):
        for request_min in range(upper+2):
            feasible,_=integer_feasible(len(rows),edges(rows,witnesses,4,b'STORES',association,requested_min=request_min))
            assert feasible==(request_min<=upper)
        print(f'STORES {association}: REQUESTED row128 must consume <= {upper} draws under these 42 constraints')
    print('Original selected ACK2 withheld; no accepted K04 bytes established.')

if __name__=='__main__':main()
