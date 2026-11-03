"""H-17 source-only global MT cross-carrier stage scan.

Compares original 16-checkpoint AX transfer chains and the eight accepted
LT-204 DIAG_WORD values with a hypothetical p951 printer stream, using
complete affine GF2 source constraints, including non-individually-fixed bits.
The copied selected printer row129, K04/K08 commitments and verifier are not read.

Run: python agents/agent39/k04_ax_k02_global_affine_window_sft.py
"""
import datetime
import hashlib
import importlib.util
import json
import random
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location(
    "agent49_source", ROOT/"agents/agent49/k04_p951_symbolic_basis.py"
)
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
m.LAST = 1740
basis, states = m.source(ROOT/"resources")
assert basis.rank == 15365

# Upper16 of a MT-tempered word is 16 GF2 equations, each in original
# 624 register bits. Materialize them once for all trial stage positions.
tempered = {
    pos: m.temper(m.get(states,pos))[16:]
    for pos in range(m.ORIGIN,m.LAST)
}


def affine_window(source, values, start, step):
    """Return dependent checks, new independent bits, contradiction flag."""
    extra = {}
    dependent = unknown = 0
    for index, observed in enumerate(values):
        for bit, expression in enumerate(tempered[start+step*index]):
            v, rhs = expression, (observed>>bit)&1
            while v:
                pivot = v.bit_length()-1
                previous = extra.get(pivot)
                if previous is None:
                    previous = source.rows.get(pivot)
                if previous is None:
                    break
                row, value = previous
                v ^= row
                rhs ^= value
            if v:
                extra[v.bit_length()-1] = (v,rhs)
                unknown += 1
            elif rhs:
                return dependent,unknown,True
            else:
                dependent += 1
    return dependent,unknown,False


# A synthetic genuine CPython MT produces original-layout packets with
# identical symbolic ranks. Heldout 16-word checkpoints must fit exactly.
rng = random.Random(271828)
draws = [rng.getrandbits(32) for _ in range(m.LAST-m.ORIGIN+1)]
synthetic = m.Basis()
for index,position in enumerate(m.STARTS):
    if index == 129:
        continue
    for lane in range(4):
        native = m.untemper(draws[position-m.ORIGIN+lane])
        for bit,expression in enumerate(m.get(states,position+lane)):
            synthetic.insert(expression,(native>>bit)&1)
assert synthetic.rank == 15365
for start,step in ((-157,1),(-141,1),(-157,2)):
    values = [draws[start-m.ORIGIN+step*i]>>16 for i in range(16)]
    dependent,unknown,contradiction = affine_window(synthetic,values,start,step)
    assert not contradiction and dependent+unknown == 256
print("PASS: 3 genuine seeded CPython MT synthetic holdout alignments")

transfer = (ROOT/"resources/evidence/transfers/transfer-audit.jsonl").read_bytes()
assert hashlib.sha256(transfer).hexdigest() == (
    "32970ad4431a9d610cc12dcca2813f39dd8fd2e396f9e748dc94b5932cb69adf"
)
rows = [json.loads(x) for x in transfer.splitlines()]
for name in ("AX-7778","AX-7781","AX-7782","AX-7783"):
    packets = sorted(
        (r for r in rows if r.get("kind")=="CHUNK" and r["transfer"]==name),
        key=lambda r:(r["seq"],r["attempt"])
    )
    assert len(packets)==16
    values = [
        (lambda x:(x>>8)|((x&255)<<8))(int(r["checkpoint"],16))
        for r in packets
    ]
    matches=[]
    tested=0
    for step in range(1,7):
        for start in range(m.ORIGIN,m.LAST-16*step):
            dep,unk,conflict=affine_window(basis,values,start,step)
            tested+=1
            if not conflict and dep:
                matches.append((dep,start,step))
    matches.sort(reverse=True)
    assert tested == 16704
    if name=="AX-7778":
        assert matches == [(126,-157,1)],matches
    else:
        assert matches==[],(name,matches)
    print(name,"candidate stages",tested,
          "with original-source parity checks",matches[:3])

telemetry = [
    json.loads(x) for x in
    (ROOT/"resources/evidence/telemetry/freeze-export.jsonl").read_text().splitlines()
]
t0=datetime.datetime.fromisoformat("2026-10-03T21:13:40+00:00")
t1=datetime.datetime.fromisoformat("2026-10-03T21:13:48+00:00")
selected={}
for row in telemetry:
    if (row.get("tag")=="LT-204" and row.get("field")=="DIAG_WORD" and
        row.get("quality")=="GOOD" and row.get("state")=="HOLD" and
        row.get("seq") in range(8) and
        t0<=datetime.datetime.fromisoformat(row["ts"])<t1):
        seq=row["seq"]
        if seq not in selected or row["revision"]>selected[seq]["revision"]:
            selected[seq]=row
assert sorted(selected)==list(range(8))
values=[int(selected[i]["value"]) for i in range(8)]
assert values==[57765,58484,47831,59475,41704,50973,13079,54535]
for order in ("native","swapped"):
    observed = (values if order=="native"
                else [(x>>8)|((x&255)<<8) for x in values])
    compatible=[]
    for step in range(1,13):
        for start in range(m.ORIGIN,m.LAST-8*step):
            dep,unk,conflict=affine_window(basis,observed,start,step)
            if not conflict and dep:
                compatible.append((dep,start,step))
    assert compatible==[],(order,compatible[:6])
    print("LT-204 source DIAG",order,"no supported shared-stream placement")

print("PASS all originals: only AX-7778 has source-certified fixed-stride"
      " placement; no new K04/K08 authenticated value")
