"""Source-selected K02 stage coset + genuine same-job retry singleword donor.
Run: python agents/agent34/k04_k02_samejob_retry_singleword_sft.py
No selected ACK payload used. Original K04 hash tested only on completed candidates.
"""
import hashlib
import itertools
import re
from pathlib import Path
import k04_k02_k05_twist_donor_sft as t

ROOT = Path(__file__).resolve().parents[2]
path = ROOT/'resources/evidence/print/spool-reconstruction.log'
raw = path.read_bytes()
assert hashlib.sha256(raw).hexdigest()=='7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083'
lines = [x for x in raw.splitlines() if b'PAYLOAD=' in x]
assert len(lines)==133
assert all(x in lines[128] for x in (b'JOB=PS-261003-0417',b'ATTEMPT=1',b'STATE=REQUESTED',b'CLASS=RECOVER'))
assert all(x in lines[130] for x in (b'JOB=PS-261003-0417',b'ATTEMPT=3',b'STATE=REQUESTED',b'CLASS=RECOVER'))
assert t.mt.STARTS[128]==947 and t.mt.STARTS[130]==955
left=bytes.fromhex(re.search(rb'PAYLOAD=([A-F0-9]{32})',lines[128]).group(1).decode())
right=bytes.fromhex(re.search(rb'PAYLOAD=([A-F0-9]{32})',lines[130]).group(1).decode())
assert left.hex().upper()=='CD3E4F216ADB2FB180DA2AA90B33F7A4'
assert right.hex().upper()=='44D53DFC29D7943A95D89371DA58EC64'

# The historical same-job REQUESTED prints are not ACKs; hypothesize their
# individual source words or matching-lane XOR as selected-coupon word donors.
raw_words=[]
for lane in range(4):
    a=left[4*lane:4*lane+4]
    b=right[4*lane:4*lane+4]
    raw_words.append(('A1',lane,a))
    raw_words.append(('A3',lane,b))
    raw_words.append(('XOR',lane,bytes(x^y for x,y in zip(a,b))))
assert len(raw_words)==12
checks=compatible=cosets=hashes=0
matches=[]
for donor in t.STAGES:
    for mode in itertools.product(('big','little'),(False,True),(False,True),(False,True)):
        b=t.impose(t.orig,donor,t.pair_words(t.K02,mode))
        assert b.rank==15493
        for origin,lane,raw_word in raw_words:
            for endian,native in itertools.product(('big','little'),(False,True)):
                checks += 1
                v=int.from_bytes(raw_word,endian)
                word=v if native else t.mt.untemper(v)
                source_compatible=True
                for j,eq in enumerate(t.mt.get(t.symbolic,951)):
                    prediction=b.predict(eq)
                    if prediction is not None and prediction != ((word>>j)&1):
                        source_compatible=False
                        break
                if not source_compatible:continue
                compatible += 1
                joint=t.copy_basis(b)
                for bit,eq in enumerate(t.mt.get(t.symbolic,951)):
                    joint.insert(eq,(word>>bit)&1)
                dim,count,hits=t.full_candidates(joint,limit_dim=16)
                assert dim==1 and count==2
                cosets += 1
                hashes += count
                if hits:
                    matches.append((donor,mode,origin,lane,endian,native,hits))
print('SAME_JOB_REQUESTED_SINGLEWORD',checks,'consistent',compatible,'cosets',cosets,'actual_K04_SHA_checks',hashes,'accepted',matches)
assert checks==len(t.STAGES)*16*len(raw_words)*4
assert compatible==checks and cosets==checks and hashes==checks*2
assert not matches
print('SOURCE_INDEPENDENT_CONTROLS: original spool SHA, job/attempt, MT rank, full coupon reduction PASS')
