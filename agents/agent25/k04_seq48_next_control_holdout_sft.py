"""Original seq48 heldout for conditional node50 p951 45/46/47 placement.

Run from repository checkout:
    python agents/agent25/k04_seq48_next_control_holdout_sft.py
Reads only intact 132 printer ACK rows and original CRC-valid recorder.
Selected row129, K04/K08 mask/acceptance/verifier excluded.
"""
from pathlib import Path
import importlib.util

ROOT = Path(__file__).resolve().parents[2]
src = Path(__file__).resolve().parent / "k04_seq46_47_joint_stage_sft.py"
spec = importlib.util.spec_from_file_location("h17_joint",src)
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

b,s=m.source(ROOT/"resources")
c=m.recorder_controls()
assert {45,46,47,48}.issubset(c)
fit46=m.insert_control(b,s,-531,c[46])
assert fit46 is not None and fit46.rank-b.rank == 32
fit47=m.insert_control(fit46,s,-523,c[47])
assert fit47 is not None and fit47.rank-b.rank == 63
assert len(b.rows) == 15365
native48=m.untemper(int.from_bytes(c[48],"little"))
counts=[]
for at in range(-520,-511):
    predictions=[b.predict(term) for term in m.get(s,at)]
    known=sum(bit is not None for bit in predictions)
    misses=sum(bit is not None and bit!=((native48>>i)&1)
               for i,bit in enumerate(predictions))
    compatible=m.insert_control(fit47,s,at,c[48]) is not None
    assert compatible==(misses==0)
    counts.append((at,known,misses,compatible))
assert counts == [
    (-520,0,0,True),(-519,0,0,True),
    (-518,2,2,False),(-517,32,14,False),
    (-516,32,15,False),(-515,32,14,False),
    (-514,32,19,False),(-513,9,4,False),
    (-512,0,0,True)
],counts
# A full 45->46->47->48 chain with per-record gap in [5,10]
# cannot preserve seq47=-523; seq48 needs a gap <=4 or >=11.
assert not any(item[3] for item in counts if 5 <= item[0]-(-523) <= 10)
assert m.insert_control(fit47,s,-512,c[48]) is not None
print("Source-only heldout node50 seq48 controls: ",counts)
print("Conditional seq47=-523 requires seq48 gap<=4 or >=11")
print("No authentic K04 selected coupon bits or exact K08 caption words")
