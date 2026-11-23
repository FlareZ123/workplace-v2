"""Exact held-out K04 coupon and category-codebook test for one STORES-stage hypothesis.

Run: python agents/agent40/k04_stores_sourcefull_model_sft.py
Conditional stage map only. Do not construe its source fit as an historical issuer.
"""
from __future__ import annotations
from collections import Counter
from hashlib import sha256
from itertools import combinations,permutations
from json import loads
from pathlib import Path
from k04_stores_conditional_source_gate_sft import load_original,source_words

ROOT=Path(__file__).resolve().parents[2]
STAGES=(0,7,16,23,32,39,45,54,64,72,81,90,98,109,119,126,132,139,145,151,157,165,171,177,184,190,197,203,209,217,223,230,237,244,251,264,272,279,285,294,301,308,316,327,336,345,352,358,364,370,376,382,388,394,401,408,417,425,433,439,446,454,460,470,478,487,494,504,514,522,530,537,545,552,563,569,576,582,589,595,602,609,616,624,632,638,645,652,658,664,672,679,686,693,702,712,720,730,739,747,753,760,769,776,783,789,796,804,811,818,825,831,837,845,853,861,871,877,883,891,898,906,912,918,924,931,938,944,950,950,956,960,966)

MAG=0x9908B0DF

def symbolic_words(n):
    words=[[1<<(i*32+j) for j in range(32)] for i in range(624)]
    for t in range(624,n):
        a,b,c=words[t-624],words[t-623],words[t-227]
        words.append([c[j]^(a[31] if j==30 else (b[j+1] if j<30 else 0))^(b[0] if MAG&(1<<j) else 0) for j in range(32)])
    return words

def insert(basis,form,expected):
    while form:
        lead=form.bit_length()-1
        if lead not in basis:
            basis[lead]=(form,expected)
            return True
        old,old_bit=basis[lead]
        form^=old
        expected^=old_bit
    assert expected==0,'intact original payload contradiction'
    return False

def predict(basis,form):
    out=0
    while form:
        lead=form.bit_length()-1
        if lead not in basis:return None
        old,value=basis[lead]
        form^=old
        out^=value
    return out

def tempered_bits(native):
    a=[native[j]^(native[j+11] if j+11<32 else 0) for j in range(32)]
    b=[a[j]^(a[j-7] if j>=7 and (0x9D2C5680>>j)&1 else 0) for j in range(32)]
    c=[b[j]^(b[j-15] if j>=15 and (0xEFC60000>>j)&1 else 0) for j in range(32)]
    return [c[j]^(c[j+18] if j+18<32 else 0) for j in range(32)]

def call_possible(codes,start,end,width,accepted=None):
    if start>=end:return False
    return (all(any(code>=width for code in allowed) for allowed in codes[start:end-1])
            and any(code<width and (accepted is None or code==accepted) for code in codes[end-1]))

def complete_gap(codes,orders,cl,dst):
    n=len(codes)
    if n<len(orders):return False
    acceptance={'C':(3,cl),'D':(3,dst),'X':(2,None)}
    for cutpoints in combinations(range(1,n),len(orders)-1):
        cuts=(0,)+cutpoints+(n,)
        if all(call_possible(codes,cuts[i],cuts[i+1],*acceptance[call]) for i,call in enumerate(orders)):
            return True
    return False

def source_basis(rows):
    assert len(STAGES)==len(rows)==133
    raw=[None if i==129 else bytes.fromhex(row[5].decode()) for i,row in enumerate(rows)]
    native=source_words(raw)
    for r in range(132):
        lower=0 if rows[r][3]==b'REQUESTED' else 6+int(rows[r][4]==b'STORES')
        assert lower<=STAGES[r+1]-STAGES[r]<=100
    symbolic=symbolic_words(STAGES[-1]+4)
    basis={}
    for r,packet in enumerate(native):
        if packet is None:continue
        for i,word in enumerate(packet):
            for bit,form in enumerate(symbolic[STAGES[r]+i]):
                insert(basis,form,(word>>bit)&1)
    assert len(basis)==15366
    return symbolic,basis,native

def metadata_screen(rows,symbolic,basis):
    codes={}
    for row in range(127):
        out=[]
        for stage in range(STAGES[row]+4,STAGES[row+1]):
            temp=tempered_bits(symbolic[stage])
            bit30=predict(basis,temp[30])
            bit31=predict(basis,temp[31])
            out.append(tuple(v for v in range(4) if (bit30 is None or (v&1)==bit30)
                                                    and (bit31 is None or (v>>1)==bit31)))
        codes[row]=out
    assert sum(len(v) for v in codes.values())==436
    assert sum(len(q)==1 for v in codes.values() for q in v)==121
    assert sum(len(q)==2 for v in codes.values() for q in v)==47
    class_names=(b'LABEL',b'STORES',b'RECOVER')
    dest_names=(b'bench',b'desk',b'store')
    best=0
    survivors=0
    for cls in permutations(range(3)):
        class_map=dict(zip(class_names,cls))
        for dest in permutations(range(3)):
            dest_map=dict(zip(dest_names,dest))
            for ordinary_order in (('C','D'),('D','C')):
                for pos in range(3):
                    stores_order=list(ordinary_order)
                    stores_order.insert(pos,'X')
                    successes=sum(complete_gap(code,
                                    stores_order if rows[r][4]==b'STORES' else ordinary_order,
                                    class_map[rows[r][4]],dest_map[rows[r][6]])
                                  for r,code in codes.items())
                    best=max(best,successes)
                    survivors+=successes==127
    assert (best,survivors)==(80,0),(best,survivors)
    assert complete_gap([(3,),(1,),(3,),(0,),(2,),(1,)],('C','D','X'),1,0)
    return best,survivors

def main():
    rows,witnesses=load_original()
    assert len(witnesses)==42
    for r,k,l,p,i,q in witnesses:
        assert STAGES[k]-STAGES[r]==396+p-i
        assert STAGES[l]-STAGES[r]==623+p-q
    symbolic,basis,native=source_basis(rows)
    assert STAGES[128]==STAGES[129]==950
    assert native[129] is None
    printed=b''.join(sum(predict(basis,form)<<bit for bit,form in enumerate(tempered_bits(symbolic[STAGES[129]+lane])))
                     .to_bytes(4,'little') for lane in range(4))
    assert printed==bytes.fromhex('CD3E4F216ADB2FB180DA2AA90B33F7A4')
    route=loads((ROOT/'resources/evidence/recovery-routing.json').read_text())
    accepted=loads((ROOT/'resources/acceptance.json').read_text())
    mask=bytes.fromhex(route['K04']['masked_component'])
    coupon=bytes(a^b for a,b in zip(printed,mask))
    digest=sha256(coupon).hexdigest()
    assert digest=='b138a3b90d9cfab0f4994e3a38b354bf205265e2bafa2e29b01444b5dfae14ca'
    assert digest!=accepted['slot_sha256']['K04']
    best,survivors=metadata_screen(rows,symbolic,basis)
    print('Original source full GF(2) fit: 132/132 intact packets, rank',len(basis))
    print('Frozen selected ACK2 alternative coupon:',coupon.hex().upper(),'original acceptance: NO')
    print('Global CLASS/DEST high-two-bit codebooks with STORES extra draw: 0 survivors; best',best,'of 127 complete metadata pairs')
    print('K04 still MISSING; no source-authenticated selected bytes recovered')

if __name__=='__main__':main()
