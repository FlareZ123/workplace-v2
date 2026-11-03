"""K04 one broken serial/parity bitplane across all 16 ACK coupon bytes.

Run from repo root: python agents/agent3/k04_bitplane_fault_sft.py
Source-pinned original ACK, unchanged routing mask and SHA256 commitment.
"""
import hashlib
import json
import re
from pathlib import Path

root=Path(__file__).resolve().parents[2]/"resources"
raw=(root/"evidence/print/spool-reconstruction.log").read_bytes()
assert hashlib.sha256(raw).hexdigest()=="7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"
selected=[s for s in raw.decode().splitlines()
          if "JOB=PS-261003-0417" in s and
          "ATTEMPT=2" in s and "STATE=ACK" in s]
assert len(selected)==1 and "2026-10-03T18:02:00Z" in selected[0]
payload=bytes.fromhex(re.search(r"PAYLOAD=([0-9A-F]{32})",selected[0]).group(1))
assert payload.hex().upper()=="A9A9DC5731A5E2AE879C47215C2559D5"
route=json.loads((root/"evidence/recovery-routing.json").read_text())
accept=json.loads((root/"acceptance.json").read_text())
mask=bytes.fromhex(route["K04"]["masked_component"])
target=bytes.fromhex(accept["slot_sha256"]["K04"])
assert target.hex()=="930a52a1bab97ca2966332137c99e99298ea6182fb32ab63a3421dfb4fd8c9e0"
planted=bytes(x^(1<<2) if i in (0,3,5,9,11,15) else x
              for i,x in enumerate(payload))
planted_digest=hashlib.sha256(bytes(c^m for c,m in zip(planted,mask))).digest()
positives=hits=total=0
for plane in range(8):
    base=bytes(x&~(1<<plane) for x in payload)
    for state in range(1<<16):
        candidate=bytes(x|(((state>>i)&1)<<plane)
                        for i,x in enumerate(base))
        reduced=bytes(c^m for c,m in zip(candidate,mask))
        result=hashlib.sha256(reduced).digest()
        total+=1
        positives+=(result==planted_digest)
        hits+=(result==target)
assert total==524288 and positives==1 and hits==0
print("K04 one-bitplane broken-channel candidate assignments",total,
      "synthetic positive",positives,"original commitment matches",hits)
