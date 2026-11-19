#!/usr/bin/env python3
"""Exhaustively screen retained spool payloads against the K04 XOR commitment.

Run from the workplace-v2 repository root:
    python agents/agent9/k04_spool_payload_exhaustive_screen.py
This is a negative source-bounded screen, not an alternate K04 selection rule.
"""
from __future__ import annotations
import hashlib,json,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
E=ROOT/'resources/evidence'
EXPECTED={
 'acceptance.json':'681739241b757b471acca4c0fef9d9d97e9493883887736d5db3b92bfb0c137f',
 'recovery-routing.json':'f8fcbca73d23bf1066edb88c088f89cd24cf22e7c78a4a412166254a4764d8a5',
 'print/spool-reconstruction.log':'7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083',
}
PATTERN=re.compile(r'JOB=(\S+) ATTEMPT=(\d+) STATE=(\S+) CLASS=(\S+) PAYLOAD=([0-9A-F]{32}) DEST=(\S+)')
def sha(b):return hashlib.sha256(b).hexdigest()
def main():
 for rel,h in EXPECTED.items():
  p=ROOT/'resources'/rel if rel=='acceptance.json' else E/rel
  actual=sha(p.read_bytes())
  if actual!=h:raise AssertionError(f'hash mismatch {rel}: {actual}')
 acceptance=json.loads((ROOT/'resources/acceptance.json').read_text())
 route=json.loads((E/'recovery-routing.json').read_text())['K04']
 mask=bytes.fromhex(route['masked_component'])
 target=acceptance['slot_sha256']['K04'].lower()
 rows=[]
 for line_no,line in enumerate((E/'print/spool-reconstruction.log').read_text().splitlines(),1):
  m=PATTERN.search(line)
  if not m:continue
  job,attempt,state,cls,payload,dest=m.groups()
  raw=bytes.fromhex(payload)
  candidate=bytes(a^b for a,b in zip(raw,mask))
  digest=sha(candidate)
  rows.append({'line':line_no,'job':job,'attempt':int(attempt),'state':state,'class':cls,
               'dest':dest,'payload_hex':payload,'xor_candidate_hex':candidate.hex().upper(),
               'candidate_sha256':digest,'matches_K04':digest.lower()==target})
 if len(rows)!=133:raise AssertionError(f'expected 133 spool payloads, got {len(rows)}')
 job_rows=[r for r in rows if r['job']=='PS-261003-0417' and r['class']=='RECOVER']
 ack_rows=[r for r in job_rows if r['state']=='ACK']
 if len(ack_rows)!=1 or ack_rows[0]['attempt']!=2:
  raise AssertionError('PS-261003-0417 last RECOVER ACK is not attempt 2')
 result={
  'source_sha256':EXPECTED,
  'K04_route':route,
  'acceptance_K04_sha256':target,
  'retained_payload_count':len(rows),
  'XOR_candidates_matching_K04':sum(r['matches_K04'] for r in rows),
  'PS0417_RECOVER_rows':job_rows,
  'PS0417_last_ACK':ack_rows[0],
  'all_133_payload_xor_outputs':rows,
  'conclusion':'No retained spool payload XOR masked_component matches the K04 commitment. The source-directed PS-261003-0417 RECOVER ACK attempt 2 is present and is not a match; no K04 component is recovered.',
 }
 print(json.dumps(result,indent=2,sort_keys=True))
if __name__=='__main__':main()
