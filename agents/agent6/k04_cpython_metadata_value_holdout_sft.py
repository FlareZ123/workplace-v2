#!/usr/bin/env python3
"""Frozen CPython metadata-value holdout test for the conditional p951 stream.

Uses only intact source payloads in the training split. It does not read the
selected ACK2 payload (row 129), K04 mask, acceptance commitments, or verifier.
The p951 STARTS array is a candidate stage-label model, not an independently
established historical chronology.
"""
from __future__ import annotations
import argparse, collections, hashlib, json, random, sys
from pathlib import Path

STARTS = [
    0,7,16,22,30,37,45,54,64,72,80,88,95,108,116,122,130,136,142,148,154,164,170,176,
    182,188,194,203,209,218,224,230,237,244,250,257,265,272,284,294,301,307,314,324,
    335,342,348,354,360,366,372,378,384,394,401,408,416,423,429,435,446,454,460,470,
    477,485,491,503,511,518,524,531,539,556,562,568,576,582,588,595,602,608,617,624,
    632,638,644,650,658,666,672,678,686,693,701,710,717,729,736,743,755,762,770,776,
    782,788,795,801,813,819,825,831,837,846,853,861,870,876,884,891,899,905,912,918,
    924,930,936,942,947,951,955,959,963,
]
ORIGIN, LAST = -1100, 1040
U32, MATRIX_A = 0xFFFFFFFF, 0x9908B0DF
CLASS_LIST, DEST_LIST = ["LABEL", "RECOVER", "STORES"], ["bench", "desk", "store"]
CLASS_CODE = {v:i for i,v in enumerate(CLASS_LIST)}
DEST_CODE = {v:i for i,v in enumerate(DEST_LIST)}
HOLDOUT = set(range(7,128,8))
TRAIN = [i for i in range(128) if i not in HOLDOUT]

def parse_source(path):
    raw=path.read_bytes()
    lines=[line.decode("ascii") for line in raw.splitlines() if line.startswith(b"2026-")]
    if len(lines)!=133: raise ValueError(f"expected 133 spool rows, found {len(lines)}")
    rows,payloads=[],[]
    for i,line in enumerate(lines):
        fields={}
        for token in line.split():
            if "=" not in token: continue
            key,value=token.split("=",1)
            if i==129 and key=="PAYLOAD": continue
            fields[key]=value
        rows.append(fields)
        if i==129: payloads.append(None)
        else:
            payloads.append(bytes.fromhex(fields["PAYLOAD"]))
            fields.pop("PAYLOAD",None)
    return raw,rows,payloads

def untemper(x):
    for k,left,mask in ((18,False,U32),(15,True,0xEFC60000),(7,True,0x9D2C5680),(11,False,U32)):
        y=x
        for _ in range(6): y=x^(((y<<k)&mask) if left else (y>>k))
        x=y&U32
    return x

def temper_word(y):
    y^=y>>11; y^=(y<<7)&0x9D2C5680; y^=(y<<15)&0xEFC60000; y^=y>>18
    return y&U32

def symbolic_words():
    words=[[1<<(32*i+j) for j in range(32)] for i in range(624)]
    for i in range(624,LAST-ORIGIN+1):
        t=i-624
        words.append([
            words[t+397][j]^(words[t][31] if j==30 else (words[t+1][j+1] if j<30 else 0))
            ^(words[t+1][0] if (MATRIX_A>>j)&1 else 0)
            for j in range(32)
        ])
    return words

def get_sym(words,pos):
    if not ORIGIN<=pos<=LAST: raise IndexError(pos)
    return words[pos-ORIGIN]

def temper_expr(v):
    a=[v[j]^(v[j+11] if j+11<32 else 0) for j in range(32)]
    b=[a[j]^(a[j-7] if j>=7 and (0x9D2C5680>>j)&1 else 0) for j in range(32)]
    c=[b[j]^(b[j-15] if j>=15 and (0xEFC60000>>j)&1 else 0) for j in range(32)]
    return [c[j]^(c[j+18] if j+18<32 else 0) for j in range(32)]

class Basis:
    def __init__(self): self.rows,self.rank={},0
    def add(self,expression,value):
        v,b=expression,value
        while v:
            p=v.bit_length()-1
            if p not in self.rows: self.rows[p]=(v,b); self.rank+=1; return True
            row,rhs=self.rows[p]; v^=row; b^=rhs
        return b==0
    def predict(self,expression):
        v,value=expression,0
        while v:
            p=v.bit_length()-1
            if p not in self.rows: return None
            row,rhs=self.rows[p]; v^=row; value^=rhs
        return value
    def clone(self):
        other=Basis(); other.rows=dict(self.rows); other.rank=self.rank; return other

def fixed_randbits(words,basis,pos,k):
    out=temper_expr(get_sym(words,pos))
    bits=[basis.predict(out[31-j]) for j in range(k)]
    if any(bit is None for bit in bits): return None
    value=0
    for bit in bits: value=(value<<1)|bit
    return value

def add_randbits2(words,basis,pos,value):
    out=temper_expr(get_sym(words,pos))
    if not basis.add(out[31],(value>>1)&1): return False
    return basis.add(out[30],value&1)

def parse_gap(words,basis,positions):
    values=[]
    for pos in positions:
        value=fixed_randbits(words,basis,pos,2)
        if value is None: return {"status":"underdetermined","fixed_words":len(values),"gap_words":len(positions)}
        values.append(value)
    j,decoded=0,[]
    for _ in range(2):
        while j<len(values) and values[j]==3: j+=1
        if j>=len(values): return {"status":"rejection-exhausted","values":values,"decoded":decoded}
        decoded.append(values[j]); j+=1
    if j!=len(values): return {"status":"leftover","values":values,"decoded":decoded,"leftover":values[j:]}
    return {"status":"parsed","values":values,"decoded":decoded}

def payload_fixed(words,basis,row):
    return sum(basis.predict(expr) is not None for lane in range(4) for expr in get_sym(words,STARTS[row]+lane))

def fit_training_metadata(words,train_basis,rows):
    gaps=[i for i in range(127) if i in TRAIN and i+1 in TRAIN]
    class_last=[]
    for i in gaps:
        value=fixed_randbits(words,train_basis,STARTS[i+1]-1,2)
        class_last.append((i,value,CLASS_CODE[rows[i+1]["CLASS"]]))
    fit=train_basis.clone(); class_conflicts=[]
    for i in gaps:
        if STARTS[i+1]-STARTS[i]-4<2:
            class_conflicts.append((i,"gap-short")); continue
        if not add_randbits2(words,fit,STARTS[i+1]-1,CLASS_CODE[rows[i+1]["CLASS"]]):
            class_conflicts.append((i,"class-conflict"))
    def candidates(i,current):
        g=STARTS[i+1]-STARTS[i]-4
        if g<2: return []
        start=STARTS[i]+4; dest=DEST_CODE[rows[i]["DEST"]]; cls=CLASS_CODE[rows[i+1]["CLASS"]]
        found=[]
        for accepted_pos in range(g-1):
            vals=[3]*g; vals[accepted_pos]=dest; vals[-1]=cls
            trial=current.clone()
            if all(add_randbits2(words,trial,start+off,val) for off,val in enumerate(vals)):
                found.append((accepted_pos,vals,trial))
        return found
    unresolved=set(gaps); chosen={}; zero=[]
    while True:
        progress=False
        for i in sorted(tuple(unresolved)):
            c=candidates(i,fit)
            if len(c)==0: zero.append(i); unresolved.remove(i); progress=True
            elif len(c)==1:
                j,vals,trial=c[0]; fit=trial; chosen[i]=(j,vals); unresolved.remove(i); progress=True
        if not progress: break
    return {"gaps":gaps,"class_last":class_last,"class_conflicts":class_conflicts,
            "chosen":chosen,"ambiguous":sorted(unresolved),"zero":zero,"fit":fit}

class LoggedRandom(random.Random):
    def __init__(self,seed): super().__init__(seed); self.calls=[]
    def getrandbits(self,k):
        value=super().getrandbits(k); self.calls.append((k,value)); return value

def decode_two(draws):
    j,decoded=0,[]
    for _ in range(2):
        while j<len(draws) and draws[j]==3: j+=1
        if j>=len(draws): raise AssertionError("rejection exhausted")
        decoded.append(draws[j]); j+=1
    if j!=len(draws): raise AssertionError("leftover metadata draws")
    return decoded

def synthetic_positive():
    rng=LoggedRandom(0xA17E); rows,starts,gaps=[],[],[]
    current_class=rng.choice(CLASS_LIST)
    for i in range(129):
        start=len(rng.calls); payload=[rng.getrandbits(32) for _ in range(4)]
        gap_begin=len(rng.calls); dest=rng.choice(DEST_LIST)
        next_class=rng.choice(CLASS_LIST) if i<128 else None
        draws=[v for k,v in rng.calls[gap_begin:]]
        if any(k!=2 for k,_ in rng.calls[gap_begin:]): raise AssertionError("wrong synthetic draw width")
        rows.append({"CLASS":current_class,"DEST":dest,"PAYLOAD":payload})
        starts.append(start); gaps.append(draws); current_class=next_class
    for i in range(128):
        decoded=decode_two(gaps[i])
        assert DEST_LIST[decoded[0]]==rows[i]["DEST"]
        assert CLASS_LIST[decoded[1]]==rows[i+1]["CLASS"]
        assert starts[i+1]==starts[i]+4+len(gaps[i])
    return {
        "runtime":sys.version.split()[0],"seed":"0xA17E","rows":129,"inter_payload_gaps_exact":128,
        "heldout_metadata_exact":all(
            DEST_LIST[decode_two(gaps[i])[0]]==rows[i]["DEST"]
            and CLASS_LIST[decode_two(gaps[i-1])[1]]==rows[i]["CLASS"] for i in HOLDOUT),
        "payload_start_predictions_exact":True,
        "rejected_draws":sum(v==3 for gap in gaps[:128] for v in gap),
        "gap_length_counts":dict(collections.Counter(len(g) for g in gaps[:128])),
    }

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--spool",type=Path,default=Path("resources/evidence/print/spool-reconstruction.log"))
    args=ap.parse_args()
    raw,rows,payloads=parse_source(args.spool)
    assert payloads[129] is None
    assert sorted({rows[i]["CLASS"] for i in range(128)})==CLASS_LIST
    assert sorted({rows[i]["DEST"] for i in range(128)})==DEST_LIST
    assert {rows[i]["STATE"] for i in range(128)}=={"ACK"}
    assert {rows[i]["ATTEMPT"] for i in range(128)}=={"1"}
    words=symbolic_words(); train=Basis()
    for row in TRAIN:
        for lane in range(4):
            native=untemper(int.from_bytes(payloads[row][4*lane:4*lane+4],"little"))
            for bit,expr in enumerate(get_sym(words,STARTS[row]+lane)):
                if not train.add(expr,(native>>bit)&1): raise AssertionError("inconsistent training basis")
    fit=fit_training_metadata(words,train,rows)
    fixed=[x for x in fit["class_last"] if x[1] is not None]
    matches=sum(value==wanted for _,value,wanted in fixed)
    heldout=[]
    for row in sorted(HOLDOUT):
        c=fixed_randbits(words,fit["fit"],STARTS[row]-1,2)
        class_pred=CLASS_LIST[c] if c is not None and c<3 else None
        following=parse_gap(words,fit["fit"],range(STARTS[row]+4,STARTS[row+1]))
        dest_pred=DEST_LIST[following["decoded"][0]] if following["status"]=="parsed" else None
        heldout.append({"row":row,"job":rows[row]["JOB"],"class_pred":class_pred,"class_actual":rows[row]["CLASS"],
                        "dest_pred":dest_pred,"dest_actual":rows[row]["DEST"],"payload_fixed_bits":payload_fixed(words,fit["fit"],row)})
    late={str(i):payload_fixed(words,fit["fit"],i) for i in (128,130,131,132)}
    first=fixed_randbits(words,fit["fit"],4,2)
    gaps=[STARTS[i+1]-STARTS[i]-4 for i in range(127)]
    high_bit=True
    for seed in (0,1,20261003,0xDEADBEEF):
        a,b=random.Random(seed),random.Random(seed)
        for _ in range(100):
            if a.getrandbits(2)!=(b.getrandbits(32)>>30): high_bit=False; break
    out={
        "test":"frozen CPython metadata-value holdout under conditional p951 chronology",
        "runtime":sys.version.split()[0],"source_sha256":hashlib.sha256(raw).hexdigest(),"source_rows":len(rows),
        "selected_ack2_payload_loaded":False,"k04_mask_or_commitment_used":False,
        "categories":{"CLASS":CLASS_LIST,"DEST":DEST_LIST},
        "dispatch_fields":{"ordinary_STATE":"ACK","ordinary_ATTEMPT":"1","modeled_as_random_draws":False},
        "schedule":"DEST_i then CLASS_(i+1); CPython choice/randrange(3); reject 3; four little-endian 32-bit payload words",
        "holdout_indices":sorted(HOLDOUT),"training_rows":len(TRAIN),
        "training_basis":{"rank":train.rank,"state_bits":19968,"free_bits":19968-train.rank},
        "ordinary_gap_length_counts":dict(collections.Counter(gaps)),"gaps_shorter_than_four":sum(g<4 for g in gaps),
        "training_transition_count":len(fit["gaps"]),
        "class_final_output_check":{"fully_fixed":len(fixed),"matches":matches,"mismatches":len(fixed)-matches,
            "mismatch_indices":[i for i,v,w in fixed if v!=w],
            "additional_linear_conflict_indices":[i for i,k in fit["class_conflicts"] if k=="class-conflict"]},
        "dest_rejection_pattern_fit":{"unique":len(fit["chosen"]),"ambiguous":len(fit["ambiguous"]),"no_candidate":len(fit["zero"]),
            "fit_basis_rank":fit["fit"].rank,"remaining_symbolic_bits":19968-fit["fit"].rank},
        "heldout_predictions":heldout,"heldout_complete_payloads":sum(x["payload_fixed_bits"]==128 for x in heldout),
        "late_control_payload_fixed_bits":late,"late_control_complete_payloads":sum(v==128 for v in late.values()),
        "sequential_start_prediction":{"status":"metadata-underdetermined-at-first-DEST" if first is None else "first-draw-fixed",
            "first_draw_position":4,"first_draw_value":first},
        "cp_python_high_bit_control":high_bit,"synthetic_positive_control":synthetic_positive(),
    }
    print(json.dumps(out,indent=2,sort_keys=True))

if __name__=="__main__": main()
