"""Source-pinned eight-halfword K02 / native-MT printer writer-phase test.

Run from repository root:
    python agents/agent9/k04_k02_contiguous_source_phase_sft.py --start -1100 --end 0
    python agents/agent9/k04_k02_contiguous_source_phase_sft.py --start -1100 --end 0 --rank-first
Five contiguous stage shards cover [-1100,3493): -1100,0,1100,2200,2850,3493.
Can pass an alternate evidence_root positional argument to use the original ZIP extraction.
Read-only: selected copied ACK row129 is skipped before payload parsing.
"""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import random
import re

SPOOL_SHA = "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"
TELEM_SHA = "3787dbd6bab3930ea5293c25a995175161a1c0d7683daad29f498026e057639f"
ORIGIN, LAST = -1100, 3500
U, MAG = 0xffffffff, 0x9908b0df
STARTS = [0,7,16,22,30,37,45,54,64,72,80,88,95,108,116,122,130,136,142,148,154,164,170,176,182,188,194,203,209,218,224,230,237,244,250,257,265,272,284,294,301,307,314,324,335,342,348,354,360,366,372,378,384,394,401,408,416,423,429,435,446,454,460,470,477,485,491,503,511,518,524,531,539,556,562,568,576,582,588,595,602,608,617,624,632,638,644,650,658,666,672,678,686,693,701,710,717,729,736,743,755,762,770,776,782,788,795,801,813,819,825,831,837,846,853,861,870,876,884,891,899,905,912,918,924,930,936,942,947,951,955,959,963]

class Basis:
    def __init__(self):
        self.rows = {}
        self.rank = 0

    def insert(self, v, bit):
        while v:
            p = v.bit_length()-1
            if p not in self.rows:
                self.rows[p] = (v, bit)
                self.rank += 1
                return
            w,c = self.rows[p]
            v ^= w
            bit ^= c
        assert bit == 0, "original source contradiction"

    def reduce(self, v):
        # Crucial: continue beyond unobserved high pivots. An early return
        # can produce false positive projected parity relationships.
        rhs, free = 0, 0
        while v:
            p = v.bit_length()-1
            if p in self.rows:
                w,c = self.rows[p]
                v ^= w
                rhs ^= c
            else:
                free ^= 1<<p
                v ^= 1<<p
        return free, rhs

def untemper(x):
    for shift,left,mask in ((18,False,U),(15,True,0xefc60000),(7,True,0x9d2c5680),(11,False,U)):
        y = x
        for _ in range(6):
            y = x ^ (((y<<shift)&mask) if left else y>>shift)
        x = y & U
    return x

def temper_int(x):
    x ^= x>>11
    x ^= (x<<7)&0x9d2c5680
    x ^= (x<<15)&0xefc60000
    x ^= x>>18
    return x&U

def symbols():
    a = [[1<<(32*i+j) for j in range(32)] for i in range(624)]
    for i in range(624,LAST-ORIGIN+1):
        t = i-624
        a.append([
            a[t+397][j] ^
            (a[t][31] if j==30 else (a[t+1][j+1] if j<30 else 0)) ^
            (a[t+1][0] if (MAG>>j)&1 else 0)
            for j in range(32)
        ])
    return a

def temper_bits(v):
    a = [v[j]^(v[j+11] if j+11<32 else 0) for j in range(32)]
    b = [a[j]^(a[j-7] if j>=7 and (0x9d2c5680>>j)&1 else 0) for j in range(32)]
    c = [b[j]^(b[j-15] if j>=15 and (0xefc60000>>j)&1 else 0) for j in range(32)]
    return [c[j]^(c[j+18] if j+18<32 else 0) for j in range(32)]

def original(evidence):
    spool = (evidence/"print/spool-reconstruction.log").read_bytes()
    telemetry = (evidence/"telemetry/freeze-export.jsonl").read_bytes()
    assert hashlib.sha256(spool).hexdigest()==SPOOL_SHA
    assert hashlib.sha256(telemetry).hexdigest()==TELEM_SHA
    lines=[l for l in spool.decode("ascii").splitlines() if "PAYLOAD=" in l]
    assert len(lines)==len(STARTS)==133
    assert "JOB=PS-261003-0417 ATTEMPT=2 STATE=ACK CLASS=RECOVER" in lines[129]
    packets={}
    for row,line in enumerate(lines):
        if row==129:
            continue
        m=re.search(r"PAYLOAD=([0-9A-F]{32})",line)
        assert m is not None
        payload=bytes.fromhex(m.group(1))
        packets[row]=[untemper(int.from_bytes(payload[4*j:4*j+4],"little")) for j in range(4)]
    assert len(packets)==132
    beginning=datetime(2026,10,3,21,13,40,tzinfo=timezone.utc)
    end=datetime(2026,10,3,21,13,48,tzinfo=timezone.utc)
    selected={}
    for line in telemetry.decode("utf-8").splitlines():
        row=json.loads(line)
        if row.get("tag")!="LT-204" or row.get("field")!="DIAG_WORD" or row.get("quality")!="GOOD" or row.get("state")!="HOLD":
            continue
        if not beginning<=datetime.fromisoformat(row["ts"])<end:
            continue
        seq=row["seq"]
        if seq not in selected or row["revision"]>selected[seq]["revision"]:
            selected[seq]=row
    assert set(selected)==set(range(8))
    words=[selected[i]["value"] for i in range(8)]
    raw=b"".join(w.to_bytes(2,"big") for w in words)
    assert raw.hex().upper()=="E1A5E474BAD7E853A2E8C71D3317D507"
    assert hashlib.sha256(raw).digest()[:16].hex().upper()=="0D7E3AB56FB75DA3EB0E2E06786D239E"
    return packets,words

def source_basis(a,packets):
    basis=Basis()
    for row,p in packets.items():
        for lane,native in enumerate(p):
            for bit,v in enumerate(a[STARTS[row]+lane-ORIGIN]):
                basis.insert(v,(native>>bit)&1)
    assert basis.rank==15365
    return basis

def view(a,t,upper,tempered):
    bits=temper_bits(a[t-ORIGIN]) if tempered else a[t-ORIGIN]
    return bits[16:32] if upper else bits[:16]

def score(a,basis,t,upper,tempered,values):
    unknown={};fresh=0;bad=0
    for i,num in enumerate(values):
        for bit,v in enumerate(view(a,t+i,upper,tempered)):
            residual,rhs=basis.reduce(v)
            rhs ^= (num>>bit)&1
            while residual:
                p=residual.bit_length()-1
                if p not in unknown:
                    unknown[p]=(residual,rhs)
                    fresh+=1
                    break
                w,c=unknown[p]
                residual ^= w
                rhs ^= c
            if residual==0 and rhs:
                bad+=1
    return 128-fresh,bad

def test_positives(a,basis):
    t=1800
    # Construct a consistent eight-halfword original-source state projection.
    values=[]
    for i in range(8):
        val=0
        for bit,v in enumerate(view(a,t+i,False,True)):
            residual,b=basis.reduce(v)
            val |= b<<bit
        values.append(val)
    known, bad=score(a,basis,t,False,True,values)
    assert (known,bad)==(14,0)
    assert any(score(a,basis,t,False,True,values[:i]+[values[i]^(1<<j)]+values[i+1:])[1]>0
               for i in range(8) for j in range(16))
    # Genuine seeded MT whole-stream producer with held-out selected row129.
    rng=random.Random(0x12468273)
    stream=[untemper(rng.getrandbits(32)) for _ in range(LAST-ORIGIN+1)]
    packets={r:stream[STARTS[r]-ORIGIN:STARTS[r]-ORIGIN+4]
             for r in range(133) if r!=129}
    synthetic=source_basis(a,packets)
    original_writer=[temper_int(stream[t+i-ORIGIN])&0xffff for i in range(8)]
    syn,bad=score(a,synthetic,t,False,True,original_writer)
    assert (syn,bad)==(14,0)
    return known

def insert_rank(rows,v):
    while v:
        pivot=v.bit_length()-1
        if pivot not in rows:
            rows[pivot]=v
            return
        v^=rows[pivot]

def rank_first(a,basis,original_values,start,end):
    target=[basis.reduce(v)[0] for t in range(951,955) for v in a[t-ORIGIN]]
    target_rows={}
    for v in target:insert_rank(target_rows,v)
    assert len(target_rows)==128
    tried=0;linked=0;compatible=0
    best_algebraic=(128,None);best_compatible=(128,None)
    for t in range(start,end):
        for upper in (False,True):
            for tempered in (False,True):
                donor_rows={};union_rows=target_rows.copy()
                for i in range(8):
                    for v in view(a,t+i,upper,tempered):
                        residual=basis.reduce(v)[0]
                        insert_rank(donor_rows,residual)
                        insert_rank(union_rows,residual)
                free=len(union_rows)-len(donor_rows)
                tried+=1
                if free<best_algebraic[0]:
                    best_algebraic=(free,(t,upper,tempered))
                if free>=128:
                    continue
                linked+=1
                for reverse in (False,True):
                    for swap in (False,True):
                        data=original_values[::-1] if reverse else original_values
                        if swap:data=[(v>>8)|((v&255)<<8) for v in data]
                        syndrome,bad=score(a,basis,t,upper,tempered,data)
                        if bad==0:
                            compatible+=1
                            if free<best_compatible[0]:
                                best_compatible=(free,(t,upper,tempered,reverse,swap,syndrome))
    assert best_compatible[0]>=96
    print("RANK_FIRST_STAGE_RANGE",start,end,"PROJECTION_GEOMETRIES",tried)
    print("SELECTED_TARGET_FREE_BEFORE_K02",128)
    print("PROJECTIONS_WITH_TARGET_RANK_OVERLAP",linked)
    print("ORIGINAL_COMPATIBLE_RANK_OVERLAP_ASSIGNMENTS",compatible)
    print("BEST_UNCONDITIONAL_K04_TARGET_FREE",best_algebraic)
    print("BEST_ORIGINAL_COMPATIBLE_K04_TARGET_FREE",best_compatible)

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("evidence_root",nargs="?",default=str(Path(__file__).resolve().parents[2]/"resources/evidence"))
    parser.add_argument("--start",type=int,default=ORIGIN)
    parser.add_argument("--end",type=int,default=LAST-7)
    parser.add_argument("--rank-first",action="store_true")
    args=parser.parse_args()
    assert ORIGIN<=args.start<args.end<=LAST-7
    packets,selected=original(Path(args.evidence_root))
    a=symbols()
    basis=source_basis(a,packets)
    planted=test_positives(a,basis)
    print("SOURCE_RANK",basis.rank,"ORIGINAL_K02",",".join(f"{v:04X}" for v in selected),
          "SEEDED_POSITIVE",planted,flush=True)
    if args.rank_first:
        rank_first(a,basis,selected,args.start,args.end)
        return
    checked=0;rank_eight=0;matching_eight=0;best_good=(-1,None)
    for t in range(args.start,args.end):
        for upper in (False,True):
            for tempered in (False,True):
                for reverse in (False,True):
                    for swap in (False,True):
                        values=selected[::-1] if reverse else selected
                        if swap:values=[(v>>8)|((v&255)<<8) for v in values]
                        dep,bad=score(a,basis,t,upper,tempered,values)
                        checked+=1
                        rank_eight+=dep>=8
                        matching_eight+=dep>=8 and bad==0
                        if bad==0 and dep>best_good[0]:
                            best_good=(dep,(t,upper,tempered,reverse,swap))
    assert matching_eight==0 and best_good[0]<=5
    print("SOURCE_PHASE_RANGE",args.start,args.end,"COMPLETE_ASSIGNMENTS",checked)
    print("INDEPENDENT_PARITY_CHECKS_GE_8",rank_eight,"COMPATIBLE",matching_eight)
    print("MAX_CHECKS_AMONG_COMPATIBLE",best_good)

if __name__=="__main__":
    main()
