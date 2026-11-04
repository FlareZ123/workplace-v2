"""H17 source-only OpenJDK Random and SplittableRandom 16-byte emitter gates.

OpenJDK 21 nextBytes(16) outputs four nextInt() little-endian words for
Random, or two nextLong() little-endian words for SplittableRandom. The
selected incident RECOVER ACK2 packet and all missing slot commitments
are never consulted. Only original routine job 0300..0427 copies are read.
"""
import hashlib
import os
import re
from pathlib import Path

ROOT=Path(os.environ.get("H17_RESOURCE_ROOT",str(Path(__file__).resolve().parents[2]/"resources")))
P=ROOT/"evidence/print/spool-reconstruction.log"
SHA="7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"
assert hashlib.sha256(P.read_bytes()).hexdigest()==SHA
rows=[]
for line in P.read_text().splitlines():
    m=re.search(r"JOB=PS-261003-(\d+) ATTEMPT=1 STATE=ACK .*? PAYLOAD=([A-F0-9]{32}) ",line)
    if m and 300<=int(m[1])<428: rows.append((int(m[1]),bytes.fromhex(m[2])))
assert len(rows)==128 and [j for j,_ in rows]==list(range(300,428))

# java.util.Random: 48-bit LCG; recover all possible low16 state bits of
# first output then validate the remaining three full nextInt() outputs.
A=0x5DEECE66D; C=0xB; MASK48=(1<<48)-1
def nextbytes(seed):
    state=(seed^A)&MASK48
    result=bytearray()
    for _ in range(4):
        state=(state*A+C)&MASK48
        result.extend((state>>16).to_bytes(4,"little"))
    return bytes(result)

def recover_java(packet,endian,reverse):
    words=[int.from_bytes(packet[i:i+4],endian) for i in (0,4,8,12)]
    if reverse: words.reverse()
    first,second,third,fourth=words
    answers=[]
    for low16 in range(1<<16):
        state=(first<<16)|low16
        state=(state*A+C)&MASK48
        if state>>16 != second: continue
        state=(state*A+C)&MASK48
        if state>>16 != third: continue
        state=(state*A+C)&MASK48
        if state>>16 == fourth: answers.append(low16)
    return answers

assert nextbytes(42).hex().upper()=="359D41BAF78AFE0DE1BBE7AE28C0450C" # independently checked on OpenJDK21
for seed in (0,1,42,424242,0x123456789ABC):
    assert len(recover_java(nextbytes(seed),"little",False))==1
print("JAVA_RANDOM_SYNTHETIC_FULL_48BIT_STATE_POSITIVES 5 PASS")
for endian,reverse in (("little",False),("big",False),("little",True),("big",True)):
    hits=[(job,len(recover_java(packet,endian,reverse))) for job,packet in rows
          if recover_java(packet,endian,reverse)]
    assert not hits
    print("ORIGINAL_JAVA_RANDOM_NEXTBYTES",endian,reverse,"128/128_REJECT")

# java.util.SplittableRandom: reversible Stafford mix64 output on an additive
# 64-bit state. Both nextLong values in a 16-byte nextBytes record determine
# the per-instance additive gamma exactly.
MASK64=(1<<64)-1
M1=0xBF58476D1CE4E5B9
M2=0x94D049BB133111EB
INV1=pow(M1,-1,1<<64)
INV2=pow(M2,-1,1<<64)
GOLDEN=0x9E3779B97F4A7C15
def mix64(x):
    x=((x^(x>>30))*M1)&MASK64
    x=((x^(x>>27))*M2)&MASK64
    return x^(x>>31)

def unright(y,k):
    x=y
    while k<64:
        x ^= x>>k
        k*=2
    return x

def unmix64(y):
    x=unright(y,31)
    x=(x*INV2)&MASK64
    x=unright(x,27)
    x=(x*INV1)&MASK64
    return unright(x,30)

def splitbytes(seed,gamma):
    return b"".join(mix64((seed+gamma*j)&MASK64).to_bytes(8,"little") for j in (1,2))

assert splitbytes(42,GOLDEN).hex().upper()=="956EEB2F2632D7BD03F166B233E3EF28" # independently checked on OpenJDK21
for i in range(200):
    seed=(i*0xFEDCBA987654321)&MASK64
    gamma=(i*GOLDEN+1)&MASK64
    packet=splitbytes(seed,gamma)
    q=unmix64(int.from_bytes(packet[:8],"little"))
    r=unmix64(int.from_bytes(packet[8:],"little"))
    assert ((r-q)&MASK64)==gamma
print("JAVA_SPLITTABLE_MIX64_200_FULL_GAMMA_RECOVERY_POSITIVES PASS")
for endian,reverse in (("little",False),("big",False),("little",True),("big",True)):
    gammas=[]
    for job,packet in rows:
        halves=[packet[:8],packet[8:]]
        if reverse: halves.reverse()
        x=unmix64(int.from_bytes(halves[0],endian))
        y=unmix64(int.from_bytes(halves[1],endian))
        gammas.append((job,(y-x)&MASK64))
    distinct=len({x for _,x in gammas})
    golden=sum(x==GOLDEN for _,x in gammas)
    odd=sum(x&1 for _,x in gammas)
    assert distinct==128 and golden==0 and odd<128
    print("ORIGINAL_SPLITTABLE_NEXTBYTES",endian,reverse,
          "distinct_gamma",distinct,"golden_gamma_matches",golden,
          "odd_gamma",odd,"of_128")
print("SOURCE_PIN",SHA)
