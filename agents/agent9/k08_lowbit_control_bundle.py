#!/usr/bin/env python3
"""One-command stage-wise LOW BIT control bundle for K08.

Run from the workplace-v2 repository root:
    python agents/agent9/k08_lowbit_control_bundle.py

This aggregates independent, source-pinned controls. It is NOT a joint null and
must not be used to multiply stage-specific rates into one p-value.
"""
from __future__ import annotations
import hashlib, json, subprocess, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
SCRIPTS={
 'author_null':'agents/agent9/k08_crew4_author_null.py',
 'partial_component_transfer_print':'agents/agent9/k08_lowbit_partial_controls.py',
 'mail_bookmark_loop':'agents/agent9/k08_mail_bookmark_loop_controls.py',
 'n20_source_triples':'agents/agent9/k08_n20_source_triple_null.py',
 'k05_low_even':'agents/agent20/k08_k05_low_even_independent_review.py',
 'email_common_target':'agents/agent25/k08_12_10_11_common_target_sft.py',
 'n20_two_cell_route':'agents/agent43/k08_n20_two_cell_transition_sft.py',
}
def run(name,path):
 full=ROOT/path
 if not full.is_file(): raise FileNotFoundError(f'missing control script {path}')
 digest=hashlib.sha256(full.read_bytes()).hexdigest()
 proc=subprocess.run([sys.executable,str(full)],cwd=ROOT,capture_output=True,text=True)
 if proc.returncode:
  raise RuntimeError(f'{name} failed ({proc.returncode}):\n{proc.stderr[-4000:]}')
 output=proc.stdout.strip()
 if name in {'author_null','partial_component_transfer_print','mail_bookmark_loop','n20_source_triples'}:
  return {'script':path,'script_sha256':digest,'result':json.loads(output)}
 return {'script':path,'script_sha256':digest,'result_text':output}
def main():
 controls={name:run(name,path) for name,path in SCRIPTS.items()}
 a=controls['author_null']['result']
 p=controls['partial_component_transfer_print']['result']
 b=controls['mail_bookmark_loop']['result']
 n=controls['n20_source_triples']['result']
 k5=controls['k05_low_even']['result_text']
 email=controls['email_common_target']['result_text']
 n20=controls['n20_two_cell_route']['result_text']
 # Assert cross-script invariants so a future source/code change fails loudly.
 assert a['p_joint_exact_CREW4_fourth_David_LOW']=='1/169975520'
 assert a['valid_one_row_plus_one_edits']==7
 assert p['components']['assignments']==120 and len(p['components']['exact_YEA_lower_assignments'])==1\n assert len(p['components']['selector_7_lower_assignments'])==24
 assert p['transfers']['AX-7782']['masks_to_selector_11']==64
 assert p['transfers']['AX-7781']['masks_to_selector_11']==72
 assert sum(v['masks_to_selector_11'] for v in p['transfers'].values())==136
 assert sum(v['official_selector']==11 for v in p['transfers'].values())==1
 assert p['print_payloads']['selector_counts']['11']==5
 assert p['print_payloads']['rows']==133 and p['print_payloads']['valid_note_ids_1_to_15']==122
 assert b['bookmark_count']==15 and b['reverse_ordinal_transfer_receipt_hits']==1
 assert b['transfer_id_lowbit_controls']['AX-7782']==3
 assert n['valid_source_windows']==1054 and n['N20_target_hit_count']==2
 assert 'M10_MASKS [8, 10]' in k5 and 'M10_IS_NOT_A_UNIQUE_SELECTOR' in k5
 assert 'EMAIL_CONTROL_REACH_N13=19/20' in email and 'K08_MATCH=NO' in email
 assert 'MAIL11_LONG_WATCH_WITH=10,11,3->END OF THE' in n20
 assert 'ROUTE_LATE_WATCH_RATHER=10,11,18->END OF THE' in n20
 summary={
  'author_joint_conditional_null':a['p_joint_exact_CREW4_fourth_David_LOW'],
  'valid_Emily_plus_one_edits':a['valid_one_row_plus_one_edits'],
  'unique_ATEALBIT_and_ALOWBIT_edit':'N10->N11',
  'component_assignments':p['components']['assignments'],
  'assignments_yielding_YEA':len(p['components']['exact_YEA_lower_assignments']),\n  'assignments_yielding_selector7':len(p['components']['selector_7_lower_assignments']),
  'AX7782_masks_to_N11_selector':'64/256',
  'AX7781_masks_to_N11_selector':'72/256',
  'N11_all_transfer_retry_masks':'136/1024',
  'N11_source_valid_transfer_vectors':'1/4',
  'N11_print_payloads':'5/133',
  'print_payloads_in_N01_to_N15':'122/133',
  'print_payloads_to_N05':'13/133',
  'bookmark_reverse_ordinal_transfer_receipt':'1/15',
  'transfer_IDs_returning_bookmark_3':'1/4',
  'N20_source_triples_to_END_OF_THE':'2/1054',
  'K05_M10_masks':'2/16',
  'email_bodies_reaching_N13':'19/20',
  'joint_null':'NOT_COMPUTED; stage rates are dependent and must not be multiplied',
  'K04_coupon':'NOT_RECOVERED',
  'K08_phrase':'NOT_RECOVERED',
 }
 print(json.dumps({'scope':'stage-wise control bundle; not a full joint null',
                   'summary':summary,'controls':controls},indent=2,sort_keys=True))
if __name__=='__main__': main()
