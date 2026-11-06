"""H-17 CPython k2496 n2 independent source-key projections (selected coupon omitted)."""
from __future__ import annotations
import argparse,hashlib,random,zipfile
from pathlib import Path
MASK=0xffffffff
F1,F2=1664525,1566083941
SOURCE_SHA="7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"
S6,S7,A7=0xE403BB7D,0x1F7B301F,0x2AED5290
G7,G8=0x6C2DCB8F,0xA8E24D0E
M5,V5=0x8000001F,0x00000011
M8,V8=0x09CC1C00,0x008C1000

def mix(x:int)->int:return x^(x>>30)
def k0_from_s5(s5:int)->int:
    a6=((S6+6)&MASK)^(F2*mix(s5)&MASK)
    return (A7-(G7^(F1*mix(a6)&MASK)))&MASK
def k1_from_s8(s8:int)->int:
    a8=((s8+8)&MASK)^(F2*mix(S7)&MASK)
    return (a8-(G8^(F1*mix(A7)&MASK))-1)&MASK
def main(archive:str|None)->None:
    if archive:
        with zipfile.ZipFile(archive) as z:spool=z.read("evidence/print/spool-reconstruction.log")
    else:
        spool=(Path(__file__).resolve().parents[2]/"resources/evidence/print/spool-reconstruction.log").read_bytes()
    assert hashlib.sha256(spool).hexdigest()==SOURCE_SHA
    assert (((S7+7)&MASK)^(F2*mix(S6)&MASK))==A7
    assert M5.bit_count()==6 and M8.bit_count()==9
    for seed in (0x100000001,0x123456789,0xFFFFFFFF00000001,0x1234567890ABCDEF):
        state=random.Random(seed).getstate()[1][:624]
        a7=(((state[7]+7)&MASK)^(F2*mix(state[6])&MASK))
        a6=(((state[6]+6)&MASK)^(F2*mix(state[5])&MASK))
        k0=(a7-(G7^(F1*mix(a6)&MASK)))&MASK
        a8=(((state[8]+8)&MASK)^(F2*mix(state[7])&MASK))
        k1=(a8-(G8^(F1*mix(a7)&MASK))-1)&MASK
        assert (k0,k1)==(seed&MASK,(seed>>32)&MASK)
    invf1,invf2=pow(F1,-1,1<<32),pow(F2,-1,1<<32)
    for free in (0,1,0x01020304,0xFFFFFFE0):
        s5=(free&(~M5&MASK))|V5
        s8=(free&(~M8&MASK))|V8
        k0,k1=k0_from_s5(s5),k1_from_s8(s8)
        a6=mix((invf1*((((A7-k0)&MASK)^G7)))&MASK)
        back5=mix((invf2*(a6^((S6+6)&MASK)))&MASK)
        a8=((G8^(F1*mix(A7)&MASK))+k1+1)&MASK
        back8=((a8^(F2*mix(S7)&MASK))-8)&MASK
        assert (back5,back8)==(s5,s8)
    print("ORIGINAL_SOURCE_SHA",SOURCE_SHA)
    print("GENUINE_CPYTHON_TWO_WORD_KEYS_RECOVERED_4_OF_4")
    print("ORIGINAL_CONDITIONAL_KEY0_DOMAIN",1<<26,"KEY1_DOMAIN",1<<23)
    print("FIRST_PASS_JOIN_SPACE",1<<49)
    print("NO_ACTUAL_SELECTED_K04_COUPON_RECOVERED")
if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--archive")
    main(parser.parse_args().archive)
