"""Read-only modern NumPy printer producer fingerprint screen.

python agents/agent28/k04_numpy_producer_sft.py
Requires numpy. The selected ESC-N attempt-2 packet is excluded.
"""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import re
import json
import numpy as np

ROOT=Path(__file__).resolve().parents[2]/"resources"
FILE=ROOT/"evidence/print/spool-reconstruction.log"
rx=re.compile(r"JOB=PS-261003-(\d{4}) .*PAYLOAD=([0-9A-F]{32})")
rows=[(int(m.group(1)),bytes.fromhex(m.group(2)))
      for line in FILE.read_text().splitlines()
      if "+00:00 JOB=" in line if (m:=rx.search(line))]
assert len(rows)==128
assert [j for j,_ in rows]==list(range(300,428))
anchors={
 "K01":"049AAB2E1CDE7A82CD7C60234303C91A",
 "K02":"0D7E3AB56FB75DA3EB0E2E06786D239E",
 "K03":"1384AF96E25D6ADA666209CB55E062FA",
 "K05":"FF8B78200A56E8586DCDA00EF01E4572",
 "K06":"5DBF40EE52FAAED9A536D3326CF0D95A",
 "K07":"93495F5E425AB8E592123DABAEB68545",
 "MASK":"8556C8CB6140A7F9A5123AC7571BEE1C",
 "NONCE":"5F933DA6A1BD03C32DA5CBC25344F497"
}
seeds={}
for label,value in anchors.items():
    b=bytes.fromhex(value)
    for end in ("little","big"):
        seeds[f"{label}-{end}-integer"]=int.from_bytes(b,end)
        seeds[f"{label}-{end}-words"]=[int.from_bytes(b[i:i+4],end)
                                     for i in range(0,16,4)]
seeds.update({"scanner-code":8131,"incident-date":20261003,
              "target-job":417,"first-job":300,"incident-clock":1802,
              "incident-unix":int(datetime(2026,10,3,18,2,
                                         tzinfo=timezone.utc).timestamp())})
assert len(seeds)==38

wanted=set()
for _,packet in rows[:10]:
    for b in (packet[:8],packet[8:]):
        wanted.add(int.from_bytes(b,"little"))
        wanted.add(int.from_bytes(b,"big"))
assert len(wanted)==40
target=np.fromiter(wanted,dtype=np.uint64)
classes=(np.random.PCG64,np.random.PCG64DXSM,
         np.random.Philox,np.random.SFC64)

control=np.random.PCG64(8131)
control.random_raw(4096)
hidden=control.random_raw(2)
recovered=np.random.PCG64(8131).random_raw(4098)[4096:4098]
assert hidden.tobytes()==recovered.tobytes()
assert len(np.intersect1d(np.random.PCG64(8131).random_raw(5000),hidden))==2

hits=[]
for generator in classes:
    for label,seed in seeds.items():
        emitted=generator(seed).random_raw(100000)
        matched=np.intersect1d(emitted,target)
        if len(matched):
            hits.append([generator.__name__,label,[hex(int(x)) for x in matched]])

print(json.dumps({
 "source_sha256":hashlib.sha256(FILE.read_bytes()).hexdigest(),
 "regular_source_records":len(rows),
 "generator_classes":[x.__name__ for x in classes],
 "seed_recipes":len(seeds),
 "generator_seed_models":len(classes)*len(seeds),
 "native_uint64_outputs_per_model":100000,
 "source_64bit_fragments":len(wanted),
 "exact_source_fragment_matches":hits,
 "synthetic_phase4096_control":"PASS"
},indent=2))
