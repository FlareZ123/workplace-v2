"""K04 original-source CPython nested SHA256 seed-expander discriminator.

Requires agents/agent15 original-derived key22=FD6A4CF7 and key23=06EDCDAD
under the hypothetical p951 first-cycle CPython bytes-seed inversion.
Selected ACK and original acceptance commitments are never accessed.
"""
import hashlib
import hmac
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
spool=(ROOT/"resources/evidence/print/spool-reconstruction.log").read_bytes()
assert hashlib.sha256(spool).hexdigest()=="7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"
K22=bytes.fromhex("FD6A4CF7")
K23=bytes.fromhex("06EDCDAD")
lengths=[4*n-64 for n in range(606,624)]
inputs={
 b"PS-261003-0417",b"0417",b"ESC-N",b"IR-261003-H17",
 b"H17-IR-261003",b"H17-POL-17/A3",b"FA-17",b"L-29/N",
 b"8131",b"094081106099112",b"ST-094/ST-081/ST-106/ST-099/ST-112",
 b"REC8/1",b"2026-10-03T18:02:00Z",b"2026-10-03 18:02:00",
 bytes.fromhex("5F933DA6A1BD03C32DA5CBC25344F497"),
 bytes.fromhex("8556C8CB6140A7F9A5123AC7571BEE1C"),
 b"5F933DA6A1BD03C32DA5CBC25344F497",
 b"8556C8CB6140A7F9A5123AC7571BEE1C",
}
inputs.update(f"{i:04d}".encode() for i in range(10000))
inputs.update(f"PS-261003-0417:{i:04d}".encode() for i in range(10000))
assert len(inputs)==20016
modes=[(kind,order,style) for kind in ("sha256","hmac")
       for order in (0,1) for style in ("le","be","ascii","ascii4")]
assert len(modes)==16

def expand(seed,mode):
 kind,order,style=mode
 result=[]
 for counter in range((max(lengths)+31)//32):
  if style=="le":suffix=counter.to_bytes(4,"little")
  elif style=="be":suffix=counter.to_bytes(4,"big")
  elif style=="ascii":suffix=str(counter).encode()
  else:suffix=f"{counter:04d}".encode()
  if kind=="sha256":
   data=seed+suffix if order==0 else suffix+seed
   result.append(hashlib.sha256(data).digest())
  elif order==0:result.append(hmac.digest(seed,suffix,"sha256"))
  else:result.append(hmac.digest(suffix,seed,"sha256"))
 return b"".join(result)

# Independent generated-seed signature recognition and altered-input rejection.
planted=expand(b"8131",modes[-1])
L=lengths[5]
expected=(planted[L-28:L-24],planted[L-32:L-28])
def check(data,length,pair):
 return (data[length-28:length-24],data[length-32:length-28])==pair
assert check(planted,L,expected)
assert not check(expand(b"8132",modes[-1]),L,expected)

tested=0
hits=[]
for mode in modes:
 for seed in sorted(inputs):
  data=expand(seed,mode)
  for length in lengths:
   tested+=1
   if check(data,length,(K22,K23)):
    hits.append((mode,seed.decode("ascii",errors="replace"),length))
assert tested==5764608
assert not hits,hits
print("source_sha256_pinned",True,"synthetic_control",True)
print("seed_strings",len(inputs),"SHA256_counter_HMAC_modes",len(modes))
print("complete_source_key22_key23_tests",tested,"original_compatible",len(hits))
print("K04 physical original bytes authenticated",0)
