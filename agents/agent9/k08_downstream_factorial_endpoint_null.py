#!/usr/bin/env python3
"""Conditional downstream factorial null for N11 / MAIL13 / bookmark-3.

Run from the workplace-v2 repository root:
    python agents/agent9/k08_downstream_factorial_endpoint_null.py

Conditions on the already-derived CREW4/ALOWBIT front end. It enumerates all
120 accepted-component assignments, 60 bookmark direction/namespace/position
mappings, and 1,024 transfer-ID/retry-mask outputs (7,372,800 combinations).
This is a conditional factorial control, not a full upstream joint null.
"""
from __future__ import annotations
import hashlib,json,re
from itertools import permutations
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
E=ROOT/'resources/evidence'
EXPECTED={
 'acceptance.json':'681739241b757b471acca4c0fef9d9d97e9493883887736d5db3b92bfb0c137f',
 'recovery-routing.json':'f8fcbca73d23bf1066edb88c088f89cd24cf22e7c78a4a412166254a4764d8a5',
 'transfers/transfer-audit.jsonl':'32970ad4431a9d610cc12dcca2813f39dd8fd2e396f9e748dc94b5932cb69adf',
 'h17-supplemental-office-files/retired-office-bookmarks.html':'b9261ac17524e66bb5a6e3f3ce4996df65737aa34564b6d29a87ebab681a6096',
 'mail/13.eml':'80d7b086d77fe7036a596198825dd221fec82e34cbd5a5a43edae74569e171aa',
 'crew/noticeboard-and-desk-notes.txt':'13f2318ccc54f35b590a2d76b3a80244fe24d70f0699c67c05858e8b8983c5cb',
}
def sha(b):return hashlib.sha256(b).hexdigest()
def lowpack(raw):
 bits=[x&1 for x in raw]
 return bytes(sum(bits[i+j]<<j for j in range(min(8,len(bits)-i))) for i in range(0,len(bits),8))
def lowvalue(s):return sum((ord(c)&1)<<i for i,c in enumerate(s))
def main():
 for rel,h in EXPECTED.items():
  path=ROOT/'resources'/rel if rel=='acceptance.json' else E/rel
  actual=sha(path.read_bytes())
  if actual!=h:raise AssertionError(f'hash mismatch {rel}: {actual}')
 candidate=json.loads((ROOT/'candidate.json').read_text())
 acceptance=json.loads((ROOT/'resources/acceptance.json').read_text())
 slots=('K01','K02','K03','K05','K06','K07')
 values={}
 for s in slots:
  raw=bytes.fromhex(candidate[s])
  if sha(raw).upper()!=acceptance['slot_sha256'][s].upper():raise AssertionError(f'{s} commitment mismatch')
  values[s]=raw
 component_rows=[]
 for order in permutations(slots,3):
  chars=''.join(chr(lowpack(values[s][8:])[0]) for s in order)
  component_rows.append({'order':list(order),'lower_text':chars,'selector':lowvalue(chars)})
 component7=[r for r in component_rows if r['selector']==7]

 # Vary the candidate position of the tea-room bookmark, list direction, and
 # namespace. Correctly adjusted 0/1-based indexing is equivalent.
 html=(E/'h17-supplemental-office-files/retired-office-bookmarks.html').read_text()
 anchors=re.findall(r'<A HREF="([^"]+)">([^<]+)</A>',html)
 if len(anchors)!=15 or anchors[2][1]!='Tea-room stock sheets':raise AssertionError('bookmark source changed')
 note_text=(E/'crew/noticeboard-and-desk-notes.txt').read_text()
 note_ids=re.findall(r'^(N\d{2}) /',note_text,re.MULTILINE)
 if note_ids!=[f'N{i:02d}' for i in range(1,25)]:raise AssertionError('expected complete N01-N24 note namespace')
 mail13=(E/'mail/13.eml').read_text()
 if 'AX-7782' not in mail13 or 'transfer receipt' not in mail13.lower():raise AssertionError('MAIL13 transfer receipt changed')
 bookmark_rows=[]
 for direction in ('forward','reverse'):
  for namespace in ('MAIL','NOTE'):
   for index in range(1,16):
    if namespace=='MAIL':
     mapped=(index if direction=='forward' else 16-index)
    else:
     mapped=(index if direction=='forward' else 25-index)
    title=anchors[index-1][1]
    is_mail13=(namespace=='MAIL' and mapped==13)
    is_tea=(title=='Tea-room stock sheets')
    bookmark_rows.append({'direction':direction,'namespace':namespace,'candidate_index':index,
                          'title':title,'mapped_id':mapped,'mapped_record':f'{namespace}{mapped:02d}',
                          'maps_to_MAIL13_receipt':is_mail13,
                          'is_tea_bookmark':is_tea,'tea_bookmark_maps_to_MAIL13':is_tea and is_mail13,
                          'bookmark3_return_target':index})
 bookmark_hits=[r for r in bookmark_rows if r['maps_to_MAIL13_receipt']]
 tea_bookmark_hits=[r for r in bookmark_rows if r['tea_bookmark_maps_to_MAIL13']]
 if len(bookmark_hits)!=2 or len(tea_bookmark_hits)!=1 or tea_bookmark_hits[0]['direction']!='reverse' or tea_bookmark_hits[0]['candidate_index']!=3:
  raise AssertionError('MAIL13/tea-bookmark mapping controls changed')

 rows=[json.loads(line) for line in (E/'transfers/transfer-audit.jsonl').read_text().splitlines() if line.strip()]
 transfers=sorted({r['transfer'] for r in rows if 'transfer' in r})
 transfer_outputs=[]
 for transfer in transfers:
  chunks=[r for r in rows if r.get('transfer')==transfer and r.get('kind')=='CHUNK']
  by_seq={}
  for r in chunks:by_seq.setdefault(int(r['seq']),{})[int(r['attempt'])]=bytes.fromhex(r['checkpoint'])
  if set(by_seq)!=set(range(8)) or any(set(v)!={1,2} for v in by_seq.values()):raise AssertionError('transfer structure changed')
  for mask in range(256):
   raw=b''.join(by_seq[i][2 if (mask>>i)&1 else 1] for i in range(8))
   packed=lowpack(raw); hx=packed.hex().upper()
   first=packed[0]; second=packed[1]
   letter_decimal=(chr(first)+str(second)) if 32<=first<=126 else None
   transfer_outputs.append({
    'transfer':transfer,'mask':mask,'source_valid_mask':mask==255,'raw_hex':raw.hex().upper(),
    'lowpack_hex':hx,'hex_ascii_lowbit_selector':lowvalue(hx),
    'reversed_hex_ascii_lowbit_selector':lowvalue(hx[::-1]),
    'reversed_byte_order_hex_selector':lowvalue(packed[::-1].hex().upper()),
    'packed_bytes_lowbit_selector':lowpack(packed)[0],
    'letter_decimal_render':letter_decimal,
    'letter_decimal_selector':lowvalue(letter_decimal) if letter_decimal else None,
   })
 if len(transfer_outputs)!=1024:raise AssertionError('expected 1024 transfer/mask outputs')
 transfer_ids={t:lowvalue(t.split('-')[-1]) for t in transfers}
 if transfer_ids!={'AX-7778':7,'AX-7781':11,'AX-7782':3,'AX-7783':11}:raise AssertionError('transfer-ID return controls changed')
 if transfer_ids['AX-7782']!=tea_bookmark_hits[0]['candidate_index']:raise AssertionError('AX-7782 does not return to the selected tea bookmark index')
 official=next(r for r in transfer_outputs if r['transfer']=='AX-7782' and r['mask']==255)
 if official['lowpack_hex']!='53D5' or sha(bytes.fromhex(official['raw_hex']))[:32].upper()!=candidate['K07'].upper():raise AssertionError('source-valid AX-7782 mask does not reproduce K07/53D5')

 n11_masks=[r for r in transfer_outputs if r['hex_ascii_lowbit_selector']==11]
 exact=[r for r in transfer_outputs if r['lowpack_hex']=='53D5']
 source_valid_n11=[r for r in transfer_outputs if r['source_valid_mask'] and r['hex_ascii_lowbit_selector']==11]
 total=len(component_rows)*len(bookmark_rows)*len(transfer_outputs)
 n11_hits=len(component7)*len(n11_masks)*len(bookmark_rows)
 mail13_hits=len(component_rows)*len(bookmark_hits)*len(transfer_outputs)
 tea_mail13_hits=len(component_rows)*len(tea_bookmark_hits)*len(transfer_outputs)
 bookmark3_hits=len(component_rows)*len(bookmark_rows)*sum(v==3 for v in transfer_ids.values())*256
 joint_hits=len(component7)*len(tea_bookmark_hits)*sum(1 for r in transfer_outputs if r['transfer']=='AX-7782' and r['hex_ascii_lowbit_selector']==11)
 source_valid_joint_hits=len(component7)*len(tea_bookmark_hits)*len(source_valid_n11)
 exact53d5_joint_hits=len(component7)*len(tea_bookmark_hits)*sum(1 for r in exact if r['transfer']=='AX-7782')
 result={
  'source_sha256':EXPECTED,
  'conditional_scope':'conditions on the upstream CREW4/ALOWBIT front end; downstream factorial only',
  'factorial_space':{'component_assignments':len(component_rows),'bookmark_mappings':len(bookmark_rows),'transfer_mask_outputs':len(transfer_outputs),'total_combinations':total},
  'component_selector_counts':{str(i):sum(r['selector']==i for r in component_rows) for i in range(8)},
  'bookmark_mail13_hits':bookmark_hits,
  'note_namespace':{'record_count':len(note_ids),'forward_bookmark3':'N03','reverse_bookmark3':'N22'},
  'tea_bookmark_mail13_hit':tea_bookmark_hits,
  'transfer_id_return_selectors':transfer_ids,
  'transfer_mask_endpoint_counts':{
   'N11_hex_selector_hits_all_transfers':len(n11_masks),
   'N11_source_valid_mask_hits':len(source_valid_n11),
   'exact_53D5_hits':len(exact),
   'reversed_hex_selector_11_hits':sum(r['reversed_hex_ascii_lowbit_selector']==11 for r in transfer_outputs),
   'reversed_hex_selector_13_hits':sum(r['reversed_hex_ascii_lowbit_selector']==13 for r in transfer_outputs),
   'reversed_byte_order_selector_11_hits':sum(r['reversed_byte_order_hex_selector']==11 for r in transfer_outputs),
   'raw_byte_lsb_selector_3_hits':sum(r['packed_bytes_lowbit_selector']==3 for r in transfer_outputs),
   'letter_decimal_selector_13_hits':sum(r['letter_decimal_selector']==13 for r in transfer_outputs),
   'N11_hits_by_transfer':{t:sum(r['transfer']==t and r['hex_ascii_lowbit_selector']==11 for r in transfer_outputs) for t in transfers},
  },
  'factorial_endpoint_counts':{
   'N11_endpoint_hits':n11_hits,'N11_endpoint_rate':f'{n11_hits}/{total}',
   'MAIL13_endpoint_hits':mail13_hits,'MAIL13_endpoint_rate':f'{mail13_hits}/{total}',
   'tea_bookmark_to_MAIL13_hits':tea_mail13_hits,'tea_bookmark_to_MAIL13_rate':f'{tea_mail13_hits}/{total}',
   'bookmark3_endpoint_hits':bookmark3_hits,'bookmark3_endpoint_rate':f'{bookmark3_hits}/{total}',
   'joint_N11_MAIL13_bookmark3_hits':joint_hits,'joint_rate':f'{joint_hits}/{total}',
   'joint_source_valid_mask_hits':source_valid_joint_hits,'joint_source_valid_rate':f'{source_valid_joint_hits}/{total}',
   'joint_exact_53D5_hits':exact53d5_joint_hits,'joint_exact_53D5_rate':f'{exact53d5_joint_hits}/{total}',
  },
  'all_component_assignment_outputs':component_rows,
  'all_bookmark_mapping_outputs':bookmark_rows,
  'all_transfer_mask_and_rendering_outputs':transfer_outputs,
  'limitations':'Direction/namespace/position, component assignment, transfer ID, and retry mask are independently uniform control dimensions. This is a conditional factorial sensitivity model, not a calibrated p-value or full upstream null; no multiplication with the author/N20 controls is valid.'
 }
 print(json.dumps(result,indent=2,sort_keys=True))
if __name__=='__main__':main()
