"""MurmurHash3_x86_128 exact native 4x32-state inverse across selected H17 sources.

Five original selected 16byte prehash/direct source objects serve as independent
controls. All public metadata labels are shorter than one full 16-byte block.
Native seed here permits four independent uint32 registers, strictly broader
than standard public x86_128's repeated 32-bit seed.
"""
from pathlib import Path
from collections import Counter
import hashlib
import itertools
import json
import struct

MOD=(1<<32)-1
C=(0x239b961b,0xab0e9789,0x38b34ae5,0xa1e38b93)
ROTS=(15,16,17,18)
INVA=pow(0x85ebca6b,-1,1<<32)
INVB=pow(0xc2b2ae35,-1,1<<32)

def rotl(x,n):
    return ((x<<n)|(x>>(32-n)))&MOD

def fmix(x):
    x^=x>>16;x=(x*0x85ebca6b)&MOD;x^=x>>13
    x=(x*0xc2b2ae35)&MOD;x^=x>>16
    return x

def unfmix(x):
    x^=x>>16;x=(x*INVB)&MOD
    x^=x>>13;x^=x>>26
    x=(x*INVA)&MOD;x^=x>>16
    return x

def mix_tail(msg,i):
    a=msg[4*i:4*i+4]
    if not a:return 0
    v=(int.from_bytes(a,"little")*C[i])&MOD
    return (rotl(v,ROTS[i])*C[(i+1)%4])&MOD

def forward(msg,state):
    assert len(msg)<16
    h=[(v^mix_tail(msg,i)^len(msg))&MOD for i,v in enumerate(state)]
    h[0]=(h[0]+h[1]+h[2]+h[3])&MOD
    for i in (1,2,3):h[i]=(h[i]+h[0])&MOD
    h=[fmix(v) for v in h]
    h[0]=(h[0]+h[1]+h[2]+h[3])&MOD
    for i in (1,2,3):h[i]=(h[i]+h[0])&MOD
    return struct.pack("<4I",*h)

def inverse(msg,packet):
    assert len(msg)<16 and len(packet)==16
    h=list(struct.unpack("<4I",packet))
    for i in (1,2,3):h[i]=(h[i]-h[0])&MOD
    h[0]=(h[0]-h[1]-h[2]-h[3])&MOD
    h=[unfmix(v) for v in h]
    for i in (1,2,3):h[i]=(h[i]-h[0])&MOD
    h[0]=(h[0]-h[1]-h[2]-h[3])&MOD
    return tuple((v^mix_tail(msg,i)^len(msg))&MOD for i,v in enumerate(h))

# Known original MurmurHash3_x86_128 seed-0 vector from Austin Appleby's
# public-domain SMHasher code, independently listed by sml-murmur3.
assert struct.unpack("<4I",forward(b"abc",(0,)*4)) == (
    0x75CDC6D1,0xA2B006A5,0xA2B006A5,0xA2B006A5)
for state in ((0,)*4,(0xffffffff,0,0x91233442,0x12349876)):
    for msg in (b"",b"abc",b"Hello, world!",b"123456789012345"):
        assert inverse(msg,forward(msg,state))==state

root=Path(__file__).resolve().parents[2]/"resources"
accepted=json.loads((root/"acceptance.json").read_text())["slot_sha256"]
sources={
    "K01":bytes.fromhex("049AAB2E1CDE7A82CD7C60234303C91A"),
    "K02":bytes.fromhex("E1A5E474BAD7E853A2E8C71D3317D507"),
    "K05":bytes.fromhex("FF8B78200A56E8586DCDA00EF01E4572"),
    "K06":bytes.fromhex("5DBF40EE52FAAED9A536D3326CF0D95A"),
    "K07":bytes.fromhex("8947CEDCB9CC73BAB7E87BE63302C5C9"),
}
for slot,b in sources.items():
    reduced=hashlib.sha256(b).digest()[:16] if slot in ("K02","K07") else b
    assert hashlib.sha256(reduced).hexdigest()==accepted[slot]
names={
    "K01":("WN-14","WN14","WATCH14","WATCH REGISTER"),
    "K02":("LT-204","LT204","DIAG_WORD","HOLD"),
    "K05":("TRP2","TRP-2","NODE49","EVENT82"),
    "K06":("RC-17","RC17","REVC","SERVICE"),
    "K07":("AX-7782","AX7782","COMMIT","GABRIEL"),
}

def messages(slot):
    out=set()
    for s in names[slot]:
        for v in (s,s.lower(),s.upper()):
            for prefix in ("",slot+"|","H17|","REC8|"):
                msg=(prefix+v).encode("ascii")
                if len(msg)<16:out.add(msg)
    return sorted(out)

def layouts(raw):
    for endian,reverse,byteswap in itertools.product(
            ("little","big"),(False,True),(False,True)):
        parts=[raw[i:i+4] for i in (0,4,8,12)]
        if reverse:parts.reverse()
        if byteswap:parts=[p[::-1] for p in parts]
        words=[int.from_bytes(p,endian) for p in parts]
        yield (endian,reverse,byteswap),struct.pack("<4I",*words)

states={};assignments=0
for slot,raw in sources.items():
    for layout,packet in layouts(raw):
        for msg in messages(slot):
            native=inverse(msg,packet)
            assert forward(msg,native)==packet
            states.setdefault(native,set()).add(slot)
            assignments+=1
matches=[s for s,v in states.items() if len(v)>=2]
stdseed=sum(len(set(s))==1 for s in states)
assert assignments==1232 and len(states)==616
assert stdseed==0 and not matches
print("SOURCE_INVERSION",{
    "assignments":assignments,"distinct_states":len(states),
    "cross_family_native_state_collisions":len(matches),
    "standard_32bit_seed_states":stdseed},flush=True)

planted=(0x42E1A23B,0xB194E7C9,0x173ED022,0x87229A04)
assert inverse(b"WN-14",forward(b"WN-14",planted))==(
    inverse(b"AX-7782",forward(b"AX-7782",planted)))==planted

mask=bytes.fromhex("8556C8CB6140A7F9A5123AC7571BEE1C")
raw_names=("0417","PS-261003-0417","ESC-N","RECOVER","RECOVER|ACK|2",
    "0417|RECOVER|ACK|2","2026-10-03T18:02:00Z","H17-IR-261003")
target_messages=set()
for s in raw_names:
    for prefix in ("","K04|","H17|","REC8|"):
        for v in (s,s.lower(),s.upper()):
            msg=(prefix+v).encode("ascii")
            if len(msg)<16:target_messages.add(msg)
assert len(target_messages)==26
checks=hits=0
for state in states:
    for msg in target_messages:
        coupon=forward(msg,state)
        component=bytes(a^b for a,b in zip(coupon,mask))
        checks+=1
        if hashlib.sha256(component).hexdigest()==accepted["K04"]:
            print("FOUND_K04",state,msg,component.hex().upper(),flush=True)
            hits+=1
assert checks==16016 and hits==0
print("COMPLETE_ORIGINAL_K04",{
    "checks":checks,"hits":hits,"target_messages":len(target_messages),
    "genuine_synthetic_cross_source_positive":"PASS"},flush=True)
