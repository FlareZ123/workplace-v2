"""H17 K04: 128-ordinary-row CLASS/DEST source-bit encoding trial.

Read-only original-source exploration. The 128 ordinary printer jobs make a
natural candidate 128-bit carrier; all Boolean maps of the 3x3 class/dest pairs
and standard symbol packings are tested. No printer-authoring mechanism for
these encodings is historically attested, and no selected ACK2 copy is used.
"""
from collections import Counter
from hashlib import sha256, md5, sha1, sha512, sha3_256, blake2b
from itertools import permutations
from pathlib import Path
import json
import re

ROOT=Path(__file__).resolve().parents[2]/"resources"
PIN="7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"
RX=re.compile(rb"JOB=PS-\d{6}-(\d+)\s+ATTEMPT=(\d+)\s+STATE=(\w+)\s+CLASS=(\w+)\s+PAYLOAD=([0-9A-F]{32})\s+DEST=(\w+)")
RADIX_HASHES=(md5,sha1,sha256,sha512,sha3_256,blake2b)
BITS_REVERSE=bytes(int(f"{n:08b}"[::-1],2) for n in range(256))
MASK128=(1<<128)-1

def fixture():
    original=(ROOT/"evidence/print/spool-reconstruction.log").read_bytes()
    assert sha256(original).hexdigest()==PIN
    rows=[]
    for line in original.splitlines():
        if b"PAYLOAD=" not in line:
            continue
        m=RX.search(line)
        assert m,line
        rows.append((int(m[1]),int(m[2]),m[3].decode(),m[4].decode(),
                     bytes.fromhex(m[5].decode()),m[6].decode()))
    assert len(rows)==133
    ordinary=rows[:128]
    assert [(r[0],r[1],r[2]) for r in ordinary]==[(300+i,1,"ACK") for i in range(128)]
    assert rows[129][0:4]==(417,2,"ACK","RECOVER")
    route=json.loads((ROOT/"evidence/recovery-routing.json").read_text())
    acceptance=json.loads((ROOT/"acceptance.json").read_text())
    return ordinary,bytes.fromhex(route["K04"]["masked_component"]),bytes.fromhex(acceptance["slot_sha256"]["K04"])

def pack(ids,width,shift,reverse):
    seq=ids[::-1] if reverse else ids
    seq=seq[shift:]+seq[:shift]
    v=0
    for k in seq:
        v=(v<<width)|k
    assert (len(seq)*width)%8==0
    return v.to_bytes(len(seq)*width//8,"big")

def rotate128(x,offset):
    return ((x<<offset)|(x>>(128-offset)))&MASK128 if offset else x

def candidates(ordinary):
    classes=sorted({r[3] for r in ordinary})
    dests=sorted({r[5] for r in ordinary})
    assert classes==["LABEL","RECOVER","STORES"]
    assert dests==["bench","desk","store"]
    pairs=[classes.index(r[3])*3+dests.index(r[5]) for r in ordinary]
    bitmaps=set()
    seen=set()
    assignments=0
    for truth in range(512):
        value=0
        for pair in pairs:
            value=(value<<1)|((truth>>pair)&1)
        for shift in range(128):
            data=rotate128(value,shift).to_bytes(16,"big")
            views=(data,data[::-1],data.translate(BITS_REVERSE),
                   data[::-1].translate(BITS_REVERSE))
            for view in views:
                bitmaps.add(view)
                assignments+=1
    assert assignments==262144 and len(bitmaps)==261122,(assignments,len(bitmaps))
    seen.update(bitmaps)
    counts=Counter()

    def emit(value,family):
        assert len(value)==16
        seen.add(bytes(value))
        counts[family]+=1

    def emit_block(raw,family):
        if len(raw)>=16:
            emit(raw[:16],family)
            emit(raw[-16:],family)
            for i in range(16):
                if len(raw)>=32 and i+16<=len(raw):
                    emit(raw[i:i+16],family)
            if len(raw)%16==0:
                accum=bytes(16)
                for i in range(0,len(raw),16):
                    accum=bytes(a^b for a,b in zip(accum,raw[i:i+16]))
                emit(accum,family)
        for hf in RADIX_HASHES:
            d=hf(raw).digest()
            emit(d[:16],family)
            emit(d[-16:],family)
            emit(d[::-1][:16],family)

    codebooks=list(permutations(range(4),3))
    for axis,labels,field in (("CLASS",classes,3),("DEST",dests,5)):
        cat=[labels.index(r[field]) for r in ordinary]
        for book in codebooks:
            encoded=[book[v] for v in cat]
            for reverse in (False,True):
                for shift in (0,117):
                    raw=pack(encoded,2,shift,reverse)
                    emit_block(raw,"2bit-"+axis)
                    emit_block(raw[::-1],"2bit-"+axis)
                    for bit in (0,1):
                        value=0
                        for code in encoded:
                            value=(value<<1)|((code>>bit)&1)
                        emit(value.to_bytes(16,"big"),"bitplane-"+axis)

    for cb in codebooks:
        first=[cb[classes.index(r[3])] for r in ordinary]
        for db in codebooks:
            second=[db[dests.index(r[5])] for r in ordinary]
            for class_first in (False,True):
                encoded=[(a*4+b) if class_first else (b*4+a)
                         for a,b in zip(first,second)]
                for reverse in (False,True):
                    for shift in (0,117):
                        raw=pack(encoded,4,shift,reverse)
                        emit_block(raw,"joint4bit")
                        emit_block(raw[::-1],"joint4bit")

    for axis in ("CLASS","DEST","JOINT"):
        books=list(permutations(range(3))) if axis!="JOINT" else [
            (x,y) for x in permutations(range(3)) for y in permutations(range(3))]
        for book in books:
            if axis=="CLASS":
                vals=[book[classes.index(r[3])] for r in ordinary]
                radix=3
            elif axis=="DEST":
                vals=[book[dests.index(r[5])] for r in ordinary]
                radix=3
            else:
                cb,db=book
                vals=[cb[classes.index(r[3])]*3+db[dests.index(r[5])] for r in ordinary]
                radix=9
            for reverse in (False,True):
                v=0
                for digit in (vals[::-1] if reverse else vals):
                    v=v*radix+digit
                raw=v.to_bytes((v.bit_length()+7)//8 or 1,"big")
                emit_block(raw,"base"+str(radix))
                emit_block(raw[::-1],"base"+str(radix))

    for separator in ("",",","|"," ","\n"):
        for order in (ordinary,list(reversed(ordinary))):
            for labels in (
                [r[3] for r in order],
                [r[5] for r in order],
                [r[3]+"/"+r[5] for r in order],
                [r[3][0]+r[5][0] for r in order],
            ):
                emit_block(separator.join(labels).encode(),"text-categories")

    assert len(seen)==595332,(len(seen),len(bitmaps),dict(counts))
    assert len(seen-bitmaps)==334210
    return seen,bitmaps,counts


def multiset_rank(seq,alphabet):
    from math import factorial
    counts=Counter(seq)
    n=len(seq)
    m=factorial(n)
    for count in counts.values():
        m//=factorial(count)
    value=0
    for x in seq:
        for a in alphabet:
            if a==x:
                break
            if counts[a]:
                value+=m*counts[a]//n
        m=m*counts[x]//n
        counts[x]-=1
        n-=1
    assert m==1 and n==0
    return value

def lehmer_rank(order):
    remaining=list(range(len(order)))
    result=0
    for item in order:
        pos=remaining.index(item)
        result=result*len(remaining)+pos
        del remaining[pos]
    return result

def rank_candidate_bytes(n):
    raw=n.to_bytes((n.bit_length()+7)//8 or 1,"big")
    strings={raw,raw[::-1],str(n).encode(),n.to_bytes(max(16,len(raw)),"big")}
    for s in (str(n).encode(),raw,raw[::-1]):
        for fun in RADIX_HASHES:
            digest=fun(s).digest()
            strings.update((digest[:16],digest[-16:],digest[::-1][:16]))
    pool=set()
    for s in strings:
        if len(s)>=16:
            pool.update((s[:16],s[-16:]))
            for k in (0,4,8,len(s)//2-8,len(s)-16):
                if k>=0 and k+16<=len(s):
                    pool.add(s[k:k+16])
            if len(s)%16==0:
                value=bytes(16)
                for k in range(0,len(s),16):
                    value=bytes(a^b for a,b in zip(value,s[k:k+16]))
                pool.add(value)
        else:
            pool.update((s.ljust(16,b"\x00"),s.rjust(16,b"\x00")))
    assert all(len(v)==16 for v in pool)
    return pool

def enumerative_metadata_candidates(ordinary):
    classes=["LABEL","RECOVER","STORES"]
    dests=["bench","desk","store"]
    category_orders=list(permutations(range(3)))
    enumerative=set()
    permutational=set()
    variants=Counter()
    for axis in ("CLASS","DEST","JOINT"):
        cfgs=category_orders if axis!="JOINT" else [
            (a,b,o) for a in category_orders for b in category_orders for o in (0,1)]
        for cfg in cfgs:
            if axis=="CLASS":
                code=[cfg[classes.index(r[3])] for r in ordinary]
                alphabet=[0,1,2]
            elif axis=="DEST":
                code=[cfg[dests.index(r[5])] for r in ordinary]
                alphabet=[0,1,2]
            else:
                ca,da,order=cfg
                code=[(ca[classes.index(r[3])]*3+da[dests.index(r[5])]
                       if order==0 else da[dests.index(r[5])]*3+ca[classes.index(r[3])])
                      for r in ordinary]
                alphabet=list(range(9))
            for reverse in (False,True):
                for shift in (0,1,117,127):
                    seq=code[::-1] if reverse else code[:]
                    seq=seq[shift:]+seq[:shift]
                    erank=multiset_rank(seq,alphabet)
                    indices=list(range(128))
                    if reverse:
                        indices=indices[::-1]
                    indices=indices[shift:]+indices[:shift]
                    prank=lehmer_rank(sorted(indices,key=lambda i:code[i]))
                    enumerative.update(rank_candidate_bytes(erank))
                    permutational.update(rank_candidate_bytes(prank))
                    variants[axis]+=1
    assert variants==Counter({"CLASS":48,"DEST":48,"JOINT":576})
    assert len(enumerative)==44150 and len(permutational-enumerative)==40022
    return enumerative|permutational,variants

def main():
    ordinary,mask,target=fixture()
    pool,bitmaps,counts=candidates(ordinary)
    ranks,rank_variants=enumerative_metadata_candidates(ordinary)
    pool.update(ranks)
    assert len(pool)==679504,len(pool)
    direct=0
    masked=0
    for payload in pool:
        if sha256(payload).digest()==target:
            direct+=1
        if sha256(bytes(x^y for x,y in zip(payload,mask))).digest()==target:
            masked+=1
    assert direct==masked==0,(direct,masked)
    # Independently planted complete source-bit mapping and route-mask reduction.
    classes=["LABEL","RECOVER","STORES"]
    dests=["bench","desk","store"]
    codes=[classes.index(r[3])*3+dests.index(r[5]) for r in ordinary]
    value=0
    for c in codes:
        value=(value<<1)|((0x12C>>c)&1)
    planted=rotate128(value,17).to_bytes(16,"big").translate(BITS_REVERSE)
    assert planted in bitmaps
    seeded_commit=sha256(bytes(a^b for a,b in zip(planted,mask))).digest()
    planted_hits=[x for x in pool
                  if sha256(bytes(a^b for a,b in zip(x,mask))).digest()==seeded_commit]
    assert planted_hits==[planted], "enumerated synthetic full-coupon oracle failed"
    print("ORIGINAL_SOURCE_SHA256",PIN)
    print("BOOLEAN_MAPS",512,"CYCLIC_ALIGNMENTS",128,"BIT_LAYOUTS",4)
    print("BOOLEAN_ASSIGNMENTS",262144,"BOOLEAN_DISTINCT",len(bitmaps))
    print("OTHER_ENCODINGS",dict(counts))
    print("CATEGORY_RANK_VARIANTS",dict(rank_variants),"CATEGORY_RANK_NEW_CANDIDATES",84172)
    print("UNIQUE_SOURCE_COMPONENTS",len(pool),"TOTAL_COMPLETE_HASHES",2*len(pool))
    print("ORIGINAL_K04_DIRECT_HITS",direct,"ORIGINAL_K04_ROUTE_MASKED_HITS",masked)
    print("PLANTED_FULL_COUPON_CONTROL PASS")

if __name__=="__main__":
    main()
