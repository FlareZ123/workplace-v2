#!/usr/bin/env python3
"""Source-private K04 producer authentication test: fixed chronology holdouts.

Fit ONLY PS0417 REQUESTED1's complete original 16-byte packet to a private
xoroshiro128++ 128-bit state in big/BA serialization. Each retained spool
record is conditionally one successive two-output packet, with zero hidden
draws. Test four predeclared independent historical ACK packets at relative
row offsets -11,-1,+3,+4, i.e. native word offsets -22,-2,+6,+8.
The disputed PS0417 selected ACK2, subsequent REQUESTED3, original K04
target and copied coupon do not enter model selection or scoring.
This is a conditional model, NOT a historically authenticated producer.
Run original only locally; never place private state, source words or historical
candidate in public Actions/commits.
"""
import argparse,hashlib,json,os,random
from pathlib import Path
MASK=(1<<64)-1
SOURCE_SHA='7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083'

def rol(x,n):return ((x<<n)|(x>>(64-n)))&MASK
def ror(x,n):return ((x>>n)|(x<<(64-n)))&MASK
def step(s):
 a,b=s;t=a^b
 return rol(a,49)^t^((t<<21)&MASK),rol(t,28)
def inverse(s):
 a,b=s;t=ror(b,28);v=ror(a^t^((t<<21)&MASK),49)
 return v,v^t
def advance(s,n):
 for _ in range(abs(n)):s=step(s) if n>0 else inverse(s)
 return s
def packet(s):
 a,b=s
 y0=(rol((a+b)&MASK,17)+a)&MASK
 a,b=step(s)
 y1=(rol((a+b)&MASK,17)+a)&MASK
 return y1.to_bytes(8,'big')+y0.to_bytes(8,'big')
def synthetic():
 rng=random.Random(202611281233)
 for _ in range(16):
  state=(rng.getrandbits(64),rng.getrandbits(64))
  assert inverse(step(state))==state
  for delta in (-22,-2,4,6,8):
   expected=packet(advance(state,delta))
   assert expected==packet(advance(advance(state,-20),delta+20))
   assert bytes([expected[0]^1])+expected[1:]!=expected
 print({'source_free_controls':80,'inverse_roundtrip':True,
        'original_source_read':False},flush=True)
def historical(root,private_state):
 if os.environ.get('CI') or os.environ.get('GITHUB_ACTIONS'):
  raise RuntimeError('Do not run original source in GitHub Actions or CI')
 if private_state.is_symlink() or not private_state.is_file() or private_state.stat().st_mode&0o077:
  raise ValueError('Requires a nonsymlink mode0600 private state')
 if private_state.resolve().is_relative_to(root.resolve()):
  raise ValueError('Source state must be outside repository')
 spool=root/'evidence/print/spool-reconstruction.log'
 assert hashlib.sha256(spool.read_bytes()).hexdigest()==SOURCE_SHA
 lines=[x for x in spool.read_text().splitlines() if ' JOB=' in x]
 assert len(lines)==133
 records=[dict(tok.split('=',1) for tok in row.split()[1:]) for row in lines]
 state_data=json.loads(private_state.read_text())
 assert len(state_data)==1 and len(state_data[0])==2
 state=tuple(int(x,16) if isinstance(x,str) else int(x) for x in state_data[0])
 assert all(0<=x<=MASK for x in state)
 anchor=records[128]
 assert (anchor['JOB'],anchor['ATTEMPT'],anchor['STATE'],anchor['CLASS'])==(
        'PS-261003-0417','1','REQUESTED','RECOVER')
 assert packet(state)==bytes.fromhex(anchor['PAYLOAD'])
 controls=((117,'PS-261003-0417','samejob_label'),
           (127,'PS-261003-0427','prior_ack'),
           (131,'PS-261003-0448','later_south_ack'),
           (132,'PS-261003-0420','later_spare_ack'))
 counts={'full_ack_controls':0,'full16_exact_matches':0,'matching_bytes':0,
         'no_REQUESTED3_alternate_matches':0}
 details=[]
 for idx,job,label in controls:
  row=records[idx]
  assert row['JOB']==job and row['STATE']=='ACK'
  true=bytes.fromhex(row['PAYLOAD'])
  delta=(idx-128)*2
  predicted=packet(advance(state,delta))
  equal=sum(a==b for a,b in zip(true,predicted))
  hit=predicted==true
  alternate=(packet(advance(state,delta-2))==true) if idx>130 else None
  counts['full_ack_controls']+=1
  counts['full16_exact_matches']+=int(hit)
  counts['matching_bytes']+=equal
  if alternate:counts['no_REQUESTED3_alternate_matches']+=1
  details.append({'source_role':label,'row_index':idx,'native_offset':delta,
                  'full16_exact':hit,'matching_bytes_of16':equal,
                  'later_no_REQUESTED3_alternate_exact':alternate})
 print('SOURCE_SAFE_HOLDOUT',json.dumps(
   {'source_sha_pin':'PASS','fitted_original_REQUESTED1':'PASS',
    'source_fixed_conditions':'one 16-byte packet per logged spool row',
    'free_state_bits':128,'source_observed_fitting_bits':128,
    'fitting_to_ANY_historical_ACK_controls':False,
    'original_K04_target_used':False,
    'historical_payload_or_state_printed':False,
    'counts':counts,'holdouts':details},sort_keys=True),flush=True)
if __name__=='__main__':
 parser=argparse.ArgumentParser(description=__doc__)
 parser.add_argument('--synthetic',action='store_true')
 parser.add_argument('--resources-root',type=Path)
 parser.add_argument('--private-state',type=Path)
 a=parser.parse_args()
 synthetic()
 if not a.synthetic:
  if not a.resources_root or not a.private_state:
   parser.error('--resources-root and --private-state required for original test')
  historical(a.resources_root,a.private_state)
