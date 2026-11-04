"""Original-source AX transfer attempt1-to-attempt2 16-bit retry operator holdout."""
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(sys.argv[1]) if len(sys.argv)>1 else Path(__file__).resolve().parents[2]/"resources"
source = (ROOT/"evidence/transfers/transfer-audit.jsonl").read_bytes()
assert hashlib.sha256(source).hexdigest() == "32970ad4431a9d610cc12dcca2813f39dd8fd2e396f9e748dc94b5932cb69adf"
records=[json.loads(x) for x in source.splitlines()]
transfers={}
for transfer in ("AX-7778","AX-7781","AX-7782","AX-7783"):
    pairs=[]
    for seq in range(8):
        rows=[r for r in records if r.get("kind")=="CHUNK" and r["transfer"]==transfer and r["seq"]==seq]
        assert len(rows)==2 and {r["attempt"] for r in rows}=={1,2}
        pairs.append(tuple(int(r["checkpoint"],16) for r in sorted(rows,key=lambda x:x["attempt"])))
    transfers[transfer]=pairs

M=(1<<16)-1
def rol(x,r):
    return ((x<<r)|(x>>(16-r)))&M if r else x

# Learn from first two sequential original checkpoints only; do not adapt on heldouts.
def frozen_models(pairs):
    x0,y0=pairs[0]
    x1,y1=pairs[1]
    xor_pad=y0^x0
    add_pad=(y0-x0)&M
    xor_slope=((y1^x1)-(y0^x0))&M
    add_slope=((y1-x1)-(y0-x0))&M
    result={
        "xor_const":lambda i,x:x^xor_pad,
        "add_const":lambda i,x:(x+add_pad)&M,
        "xor_affine_seq":lambda i,x:x^((xor_slope*i+xor_pad)&M),
        "add_affine_seq":lambda i,x:(x+(add_slope*i+add_pad))&M,
    }
    for r in range(16):
        c1=y0^rol(x0,r)
        c2=(y0-rol(x0,r))&M
        result[f"rol{r}_xor"]=lambda i,x,r=r,c1=c1:rol(x,r)^c1
        result[f"rol{r}_add"]=lambda i,x,r=r,c2=c2:(rol(x,r)+c2)&M
    return result

results={}
for name,pairs in transfers.items():
    models=frozen_models(pairs)
    own={}
    other={}
    for model,fn in models.items():
        own[model]=sum(fn(i,pairs[i][0])==pairs[i][1] for i in range(2,8))
        other[model]={t:sum(fn(i,p[0])==p[1] for i,p in enumerate(rows)) for t,rows in transfers.items() if t!=name}
    results[name]={
        "models":len(models),
        "max_correct_of_six_withheld":max(own.values()),
        "full_six_predictions":[m for m,n in own.items() if n==6],
        "max_correct_of_eight_other":max(max(v.values()) for v in other.values())
    }
# Synthetic affine-sequence secret produces all six genuine unseen predictions.
synthetic=[]
for i in range(8):
    x=(0x1234+i*167)&M
    synthetic.append((x,x^((0xA1B2*i+0x6A4C)&M)))
f=frozen_models(synthetic)["xor_affine_seq"]
assert sum(f(i,synthetic[i][0])==synthetic[i][1] for i in range(2,8))==6
print(json.dumps({"transfer_control_pairs":{
    t:[[f"{x:04X}",f"{y:04X}"] for x,y in pairs] for t,pairs in transfers.items()},
    "source_only_holdout":results,
    "planted_six_of_six_affine_positive":True},indent=2))
