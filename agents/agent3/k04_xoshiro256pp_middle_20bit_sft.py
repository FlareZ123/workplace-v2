#!/usr/bin/env python3
"""K04 xoshiro256++ exact middle-fragment inverse, synthetic-only default.
Given LABEL-hypothesized initial s0, intact REQUESTED1 and REQUESTED3 pairs,
fit selected *bit positions* of copied ACK2 without trusting the rest.
No official printer family/witness is known; this is a conditional hypothesis.
Local-only historical mode never accesses the protected PDF and prints counts only.
"""
import argparse,collections,hashlib,json,os,pathlib,random,re
from k04_xoshiro256pp_samejob_label_sft import invert,unpack,pack,RR,MASK,stream
from k04_xoshiro256pp_label_s0_12bit_cubes_sft import solve_bucket
P20=(0,1,2,3,22,23,24,45,46,47)
P24=(0,1,2,3,22,23,24,25,45,46,47,48)

def selected_middle(y2,y3,n):
 positions=P20 if n==20 else P24
 assert n==2*len(positions)
 return {2:{j:(y2>>j)&1 for j in positions},3:{j:(y3>>j)&1 for j in positions}}

def recover(s0,s1,s3,y4,y5,partial,ms=7000,limit=16):
 return solve_bucket((s0,s1,s3,y4,y5,None,ms,limit,partial))

def synthetic():
 positives=collections.Counter();poison=collections.Counter()
 for seed in (3101,3102,3106):
  r=random.Random(seed);s=tuple(r.getrandbits(64) for _ in range(4));ys=stream(s)
  for width in (20,24):
   answer=recover(s[0],s[1],s[3],ys[4],ys[5],selected_middle(ys[2],ys[3],width),7000,1)
   assert s[2] in answer['states'],(seed,width,answer['status'])
   assert stream((s[0],s[1],answer['states'][0],s[3]))==ys
   positives[width]+=1
  if seed in (3101,3102,3106):
   altered=selected_middle(ys[2],ys[3],20);altered[2][0]^=1
   bad=recover(s[0],s[1],s[3],ys[4],ys[5],altered,7000,1)
   assert s[2] not in bad['states']
   poison[bad['status']]+=1
 print({'synthetic_only':True,'planted_fullstate_positive_by_observed_middle_bits':dict(positives),
        'deliberately_wrong_onebit_controls':dict(poison),
        'external_initial_c0_bits':0,'historical_key_recovered':False})

def original(root,escrow,view="all"):
 if os.getenv('CI') or os.getenv('GITHUB_ACTIONS'):
  raise SystemExit('Historical mode forbidden in public CI')
 # No glob/recursive scan: exactly three permitted original inputs.
 spool=(root/'evidence/print/spool-reconstruction.log').read_text()
 route=json.loads((root/'evidence/recovery-routing.json').read_text())
 accept=json.loads((root/'acceptance.json').read_text())
 mask=bytes.fromhex(route['K04']['masked_component']);target=accept['slot_sha256']['K04']
 def src(time,kind,cls):
  rows=[x for x in spool.splitlines() if x.startswith(time) and 'JOB=PS-261003-0417 ' in x and
        f'STATE={kind} ' in x and f'CLASS={cls} ' in x]
  assert len(rows)==1
  return bytes.fromhex(re.search(r'PAYLOAD=([0-9A-F]{32})\b',rows[0]).group(1))
 label=src('2026-10-03T16:45:00+00:00','ACK','LABEL')
 first=src('2026-10-03T18:01:00Z','REQUESTED','RECOVER')
 copied=src('2026-10-03T18:02:00Z','ACK','RECOVER')
 later=src('2026-10-03T18:03:00Z','REQUESTED','RECOVER')
 outcomes=[];all_hits=[]
 for endian in ('big','little'):
  for reverse in (False,True):
   this_view=endian+('-ba' if reverse else '-ab')
   if view!='all' and view!=this_view:continue
   a,_=unpack(label,endian,reverse)
   y0,y1=unpack(first,endian,reverse);y4,y5=unpack(later,endian,reverse)
   suspect2,suspect3=unpack(copied,endian,reverse)
   d=(RR((y0-a)&MASK,23)-a)&MASK
   roots,term=invert(a,y1,ms=12000);assert term=='unsat'
   for width in (20,24):
    tally=collections.Counter()
    for u in roots:
     result=recover(a,d^u,d,y4,y5,selected_middle(suspect2,suspect3,width),12000,16)
     tally[result['status']]+=1
     for c in result['states']:
      ys=stream((a,d^u,c,d))
      for index in range(2,20):
       component=bytes(x^y for x,y in zip(pack(ys[index:index+2],endian,reverse),mask))
       tally['full_coupon_sha_checked']+=1
       if hashlib.sha256(component).hexdigest()==target:
        tally['original_commitment_hits']+=1;all_hits.append(component)
    outcomes.append({'view':endian+('-ba' if reverse else '-ab'),
                     'suspect_copied_bits_conditionally_assumed':width,
                     'firstpacket_states':len(roots),'outcomes':dict(tally)})
 if all_hits:
  p=pathlib.Path(escrow)
  assert p.resolve().is_relative_to(pathlib.Path('/mnt/data').resolve()) and not p.is_symlink()
  fd=os.open(p,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
  with os.fdopen(fd,'w') as w:
   for c in all_hits:w.write(c.hex().upper()+'\n')
 print({'source_private':True,'family':'LABEL_s0_xoshiro256pp_with_partial_copied_ACK2',
        'outcomes':outcomes,'result':'HIT_ESCROWED' if all_hits else 'NO_MATCH_IN_COMPLETED_MODELS',
        'all_copied_bits_untrusted':True})

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--original-root',type=pathlib.Path)
 p.add_argument('--escrow',default='/mnt/data/h17_k04_xoshiro_middle20_hits.txt');p.add_argument('--view',choices=('all','big-ab','big-ba','little-ab','little-ba'),default='all')
 args=p.parse_args()
 if args.original_root:original(args.original_root,args.escrow,args.view)
 else:synthetic()
