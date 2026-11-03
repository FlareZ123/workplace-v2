"""Role-matched ACK2 stage-retiming falsifier for H-17 p951 hypothetical MT source.

Withhold BOTH attempt-2 ACK RECOVER copied rows from original source fit:
selected PS-261003-0417 at row129 and later PS-261003-0420 at row132.
Probe whether common deferred-output +227 or +454 native-stage hypotheses
fit the remaining 131 actual original printer packets. Read-only source.
Run python agents/agent38/k04_ack2_role_mate_retime_sft.py resources
"""
import hashlib,re,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"agent49"))
import k04_p951_symbolic_basis as mt
mt.LAST=1500
root=Path(sys.argv[1]) if len(sys.argv)>1 else Path("resources")
raw=(root/"evidence/print/spool-reconstruction.log").read_bytes()
assert hashlib.sha256(raw).hexdigest()=="7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"
rows=[bytes.fromhex(x.decode()) for x in re.findall(rb"PAYLOAD=([0-9A-F]{32})",raw)]
assert len(rows)==len(mt.STARTS)==133
assert mt.STARTS[129]==951 and mt.STARTS[132]==963
assert rows[129].hex().upper()=="A9A9DC5731A5E2AE879C47215C2559D5"
assert rows[132].hex().upper()=="432475F72A62DB39F3D5693E2C937FA4"
sym=mt.words();source=mt.Basis()
for i,(payload,pos) in enumerate(zip(rows,mt.STARTS)):
    if i in (129,132):continue
    for lane in range(4):
        native=mt.untemper(int.from_bytes(payload[lane*4:lane*4+4],"little"))
        for j,v in enumerate(mt.get(sym,pos+lane)):
            source.insert(v,(native>>j)&1)
assert source.rank==15300
target=[v for lane in range(4) for v in mt.get(sym,951+lane)]
def reduce(b,v):
    out=0
    while v:
        p=v.bit_length()-1
        if p in b.rows:v^=b.rows[p][0]
        else:out^=1<<p;v^=1<<p
    return out
def test(placements):
    b=mt.Basis();b.rows=source.rows.copy();b.rank=source.rank
    try:
        for row,stage in placements:
            for lane in range(4):
                word=mt.untemper(int.from_bytes(rows[row][lane*4:lane*4+4],"little"))
                for j,v in enumerate(mt.get(sym,stage+lane)):b.insert(v,(word>>j)&1)
    except AssertionError:return None
    residual=[reduce(b,v) for v in target]
    pivots={};dimension=0
    for v in residual:
        while v:
            p=v.bit_length()-1
            if p in pivots:v^=pivots[p]
            else:pivots[p]=v;dimension+=1;break
    return dict(added_rank=b.rank-source.rank,target_dim=dimension,individual_fixed=sum(not v for v in residual))
cases={
 "both_shift227":[(129,1178),(132,1190)],
 "both_shift454":[(129,1405),(132,1417)],
 "selected227_other454":[(129,1178),(132,1417)],
 "selected454_other227":[(129,1405),(132,1190)],
 "selected227_other_nominal":[(129,1178),(132,963)],
 "selected454_other_nominal":[(129,1405),(132,963)]
}
for name,positions in cases.items():
    got=test(positions);print(name,got,flush=True)
    if name.endswith("other_nominal"):
        assert got==dict(added_rank=193,target_dim=33,individual_fixed=95)
    else:assert got is None
print("PASS: both ACK2 shared late-stage shifts contradicted by 131 original intact source packets")
