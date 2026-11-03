"""Two exact CPython rejection-sampler stage paths across node50 seq43..45.

Read-only: python agents/agent28/k04_node50_three_record_branch_sft.py
Printer-only p951 basis; selected row129 ACK2 absent from source().
"""
from pathlib import Path
import hashlib
import struct
import sys
import zlib

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"agent49"))
from k04_p951_symbolic_basis import source,get,temper,untemper,Basis
ROOT=Path(__file__).resolve().parents[2]/"resources"
REC_HASH="5ebc6204ed773102237dd287772de96d19740e163b49b4075537d937888657ba"

def recorder():
    raw=(ROOT/"evidence/recorder/trip-recorder.raw").read_bytes()
    assert hashlib.sha256(raw).hexdigest()==REC_HASH
    result={}
    for i in range(88):
        offset=16+i*24
        t,node,e,l,seq,control,aux,crc=struct.unpack_from(
            "<IHBBI4sII",raw,offset)
        if node==50:
            assert zlib.crc32(raw[offset:offset+20])==crc
            result[seq]=(t,e,l,untemper(int.from_bytes(control,"little")),aux)
    assert len(result)==72
    return result

def add_high(b,s,index,k,code):
    for j,expr in enumerate(temper(get(s,index))[32-k:]):
        b.insert(expr,(code>>j)&1)

def add_control(b,s,index,native):
    for j,expr in enumerate(get(s,index)):
        b.insert(expr,(native>>j)&1)

def fixed_top(b,s,index,k):
    v=mask=0
    for j,expr in enumerate(temper(get(s,index))[32-k:]):
        prediction=b.predict(expr)
        if prediction is not None:
            v|=prediction<<j
            mask|=1<<j
    return v,mask

def target_residual_rank(b,s):
    # Reduce the 128 selected coupon directions against source observations.
    tmp={}
    for p in range(951,955):
        for expr in get(s,p):
            v=expr
            while v:
                pivot=v.bit_length()-1
                if pivot not in b.rows:break
                v^=b.rows[pivot][0]
            while v:
                pivot=v.bit_length()-1
                if pivot not in tmp:
                    tmp[pivot]=v
                    break
                v^=tmp[pivot]
    return len(tmp)

def main():
    printer,states=source(ROOT)
    assert printer.rank==15365 and target_residual_rank(printer,states)==128
    observed=recorder()
    # Control-index anchors are independently selected from control words,
    # without inspecting timestamp, event, latch or AUX.
    anchored=((43,-552),(44,-545),(45,-540))
    for seq,pos in anchored:
        code=observed[seq][3]
        candidate=[]
        for p in range(-1100,-1):
            value=mask=0
            for j,expr in enumerate(get(states,p)):
                bit=printer.predict(expr)
                if bit is not None:
                    value|=bit<<j
                    mask|=1<<j
            if mask.bit_count()>=16 and ((value^code)&mask)==0:
                candidate.append(p)
        assert candidate==[pos],(seq,candidate)

    # These original complete six-bit event codes are source-fixed and are
    # rejected by CPython randrange(39): 49,52,39 are all outside 0..38.
    for p,code in ((-555,49),(-554,52),(-548,39)):
        assert fixed_top(printer,states,p,6)==(code,63)

    for branch in ("A","B"):
        b=Basis()
        b.rows=printer.rows.copy()
        b.rank=printer.rank
        for seq,pos in anchored:
            add_control(b,states,pos,observed[seq][3])
        fields=(
          (-557,9,observed[43][0]-1791061742),
          (-556,6,observed[43][1]-1),
          (-553,3,observed[43][2]),
          (-550 if branch=="A" else -551,13,observed[43][4]-2000),
          (-549 if branch=="A" else -550,9,observed[44][0]-1791061742),
          (-547,6,observed[44][1]-1),
          (-546,3,observed[44][2]),
          (-544,13,observed[44][4]-2000),
          (-543,9,observed[45][0]-1791061742),
          (-542,6,observed[45][1]-1),
          (-541,3,observed[45][2]),
        )
        for p,k,code in fields:add_high(b,states,p,k,code)
        assert b.rank==15405 and target_residual_rank(b,states)==128
        candidates=(
           [(-551,13,6000)] if branch=="A" else [(-549,6,39)]
        )
        for p,k,bound in candidates:
            value,mask=fixed_top(b,states,p,k)
            possible_max=value|(((1<<k)-1)^mask)
            assert possible_max>=bound,(branch,p,possible_max,bound)
        print(branch,"source-consistent",b.rank-printer.rank,
              "added independent equations; target ambiguity remains 128")

    print("PASS two exact original 3-recorder rejection-sampler paths")
    print("A: AUX43 reject -551, accept -550; timestamp44 -549")
    print("B: AUX43 accept -551; timestamp44 -550, event reject -549")
    print("Both: EVENT43 reject -555/-554, EVENT44 reject -548")
    print("No authenticated target bits or K08 words")

if __name__=="__main__":main()
