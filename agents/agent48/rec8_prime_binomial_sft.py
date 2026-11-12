"""Original REC8 cross-slot two-erasure reconstruction: prime fields and binomial integer rings.

A source-pinned, read-only SFT. Source stages are 6 genuine accepted components
and optional raw pre-reducer K02/K03/K07 words. Neither target K04 nor K08
is used to fit any model. All complete outputs face original full SHA checks.
"""
import hashlib
import itertools
import json
import random
from math import comb
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2] / "resources"
KNOWN = {
 0:"049AAB2E1CDE7A82CD7C60234303C91A",
 1:"0D7E3AB56FB75DA3EB0E2E06786D239E",
 2:"1384AF96E25D6ADA666209CB55E062FA",
 4:"FF8B78200A56E8586DCDA00EF01E4572",
 5:"5DBF40EE52FAAED9A536D3326CF0D95A",
 6:"93495F5E425AB8E592123DABAEB68545",
}
RAW = {
 1:"E1A5E474BAD7E853A2E8C71D3317D507",
 2:"D7DAD6BC9714519B7DAD0AD4BE8E87FD",
 6:"8947CEDCB9CC73BAB7E87BE63302C5C9",
}
MASK = bytes.fromhex("8556C8CB6140A7F9A5123AC7571BEE1C")
PRIMES = {
 8:257, 16:65537, 32:4294967311,
 64:18446744073709551629,
 128:340282366920938463463374607431768211507,
}
COORDS=(tuple(range(8)), tuple(1<<i for i in range(8)),
        tuple(2*i+1 for i in range(8)))


def split(raw, bits, endian, reverse):
 if reverse:raw=raw[::-1]
 n=bits//8
 return tuple(int.from_bytes(raw[i:i+n],endian) for i in range(0,16,n))


def join(words,bits,endian,reverse):
 n=bits//8
 raw=b"".join(word.to_bytes(n,endian) for word in words)
 return raw[::-1] if reverse else raw


def lagrange(xs,ys,x,p):
 acc=0
 for i,xi in enumerate(xs):
  a=b=1
  for j,xj in enumerate(xs):
   if i!=j:
    a=a*(x-xj)%p
    b=b*(xi-xj)%p
  acc=(acc+ys[i]*a*pow(b,-1,p))%p
 return acc


def binomial_options(known,bits):
 mod=1<<bits
 c=tuple((-1)**(6-j)*comb(6,j) for j in range(7))
 options=[]
 for lane in range(128//bits):
  rhs=sum(c[j]*known[j][lane] for j in (0,1,2,4,5,6))%mod
  if rhs%4:return ()
  base=(rhs//4*pow(5,-1,mod//4))%(mod//4)
  options.append(tuple(base+k*(mod//4) for k in range(4)))
 return tuple(options)


def binomial_k8(known,k4,bits):
 mod=1<<bits
 return tuple((-known[1][i]+6*known[2][i]-15*k4[i]
               +20*known[4][i]-15*known[5][i]+6*known[6][i])%mod
              for i in range(len(k4)))


def accepted(value,slot,inventory):
 return hashlib.sha256(value).hexdigest()==inventory["slot_sha256"][slot]


def planted():
 rng=random.Random(0x4847313720323036)
 keep=(0,1,2,4,5,6)
 for bits,p in PRIMES.items():
  for _ in range(128//bits):
   while True:
    coeff=[rng.randrange(1<<bits) for i in range(6)]
    vals=[sum(coeff[j]*pow(t,j,p) for j in range(6))%p for t in range(8)]
    if all(v<(1<<bits) for v in vals):break
   assert all(lagrange(keep,[vals[i] for i in keep],j,p)==vals[j]
              for j in (3,7))
   mod=1<<bits
   coeff=[rng.randrange(mod) for i in range(6)]
   vals=[sum(coeff[j]*comb(t,j) for j in range(6) if t>=j)%mod
         for t in range(8)]
   source={i:(vals[i],) for i in keep}
   c=tuple((-1)**(6-j)*comb(6,j) for j in range(7))
   rhs=sum(c[j]*source[j][0] for j in keep)%mod
   assert rhs==20*vals[3]%mod and rhs%4==0
   base=(rhs//4*pow(5,-1,mod//4))%(mod//4)
   assert vals[3] in (base+k*(mod//4) for k in range(4))
   assert binomial_k8(source,(vals[3],),bits)==(vals[7],)
 return 5


def main():
 inventory=json.loads((ROOT/"acceptance.json").read_text())
 for i,value in KNOWN.items():
  assert accepted(bytes.fromhex(value),f"K{i+1:02d}",inventory)
 assert hashlib.sha256(bytes.fromhex(RAW[1])).digest()[:16]==bytes.fromhex(KNOWN[1])
 assert hashlib.sha256(bytes.fromhex(RAW[6])).digest()[:16]==bytes.fromhex(KNOWN[6])
 seal="SG-D7DAD6BC|SG-9714519B|SG-7DAD0AD4|SG-BE8E87FD"
 assert hashlib.sha256(seal.encode("ascii")).digest()[:16]==bytes.fromhex(KNOWN[2])
 assert bytes.fromhex(RAW[2])==bytes.fromhex(seal.replace("SG-","").replace("|",""))
 assert planted()==5
 prime_models=binomial_models=0
 prime_candidates=set()
 binomial_candidates=set()
 solvable_binomial=0
 hits=[]
 ids=(0,1,2,4,5,6)
 for stages in itertools.product((False,True),repeat=3):
  values={i:bytes.fromhex(h) for i,h in KNOWN.items()}
  for pos,i in enumerate((1,2,6)):
   if stages[pos]:values[i]=bytes.fromhex(RAW[i])
  for bits,endian,reverse in itertools.product(PRIMES,("big","little"),(False,True)):
   parsed={i:split(data,bits,endian,reverse) for i,data in values.items()}
   options=binomial_options(parsed,bits)
   if options:
    solvable_binomial+=1
    for k4 in itertools.product(*options):
     b4=join(k4,bits,endian,reverse)
     b8=join(binomial_k8(parsed,k4,bits),bits,endian,reverse)
     binomial_models+=1
     for candidate in (b4,bytes(a^b for a,b in zip(b4,MASK))):
      binomial_candidates.add((candidate,b8))
      if accepted(candidate,"K04",inventory) or accepted(b8,"K08",inventory):
       hits.append(("binomial",stages,bits,candidate.hex(),b8.hex()))
   for coords,reverse_slots in itertools.product(COORDS,(False,True)):
    xs=[coords[7-i if reverse_slots else i] for i in ids]
    targetxs=[coords[7-i if reverse_slots else i] for i in (3,7)]
    outputs=[]
    p=PRIMES[bits]
    for x in targetxs:
     lanes=tuple(lagrange(xs,[parsed[i][j] for i in ids],x,p)
                 for j in range(128//bits))
     if any(y>=(1<<bits) for y in lanes):break
     outputs.append(join(lanes,bits,endian,reverse))
    if len(outputs)!=2:continue
    prime_models+=1
    b4,b8=outputs
    for candidate in (b4,bytes(a^b for a,b in zip(b4,MASK))):
     prime_candidates.add((candidate,b8))
     if accepted(candidate,"K04",inventory) or accepted(b8,"K08",inventory):
      hits.append(("prime",stages,bits,candidate.hex(),b8.hex()))
 assert prime_models==948 and len(prime_candidates)==426
 assert solvable_binomial==6 and binomial_models==48
 assert len(binomial_candidates)==48
 assert not hits,hits
 print(json.dumps({
  "six_original_SHA256":"PASS",
  "raw_K02_K03_K07_reducer_controls":"PASS",
  "synthetic_true_polynomial_controls":5,
  "prime_complete_source_models":prime_models,
  "prime_distinct_complete_K04_K08_pairs":len(prime_candidates),
  "binomial_solvable_presentations":solvable_binomial,
  "binomial_complete_source_models":binomial_models,
  "binomial_distinct_complete_K04_K08_pairs":len(binomial_candidates),
  "original_commitment_hits":len(hits),
  "REC8_complete":False
 },sort_keys=True))


if __name__=="__main__":
 main()
