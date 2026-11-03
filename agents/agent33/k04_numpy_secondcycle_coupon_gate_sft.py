"""Conditional source-to-K04-coupon gate for a NumPy four-pool second-cycle seed.

Run with no arguments to check five planted complete-spool controls. For a
genuine second-cycle pool SAT witness, pass four hexadecimal 32bit pool words
and a phase. Selected row129 is omitted before source authenticity checking.
"""
import argparse,hashlib,json,re,struct,sys
from pathlib import Path
import numpy as np

ROOT=Path(__file__).resolve().parents[2]/"resources"
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"agent49"))
from k04_p951_symbolic_basis import STARTS

U=0xffffffff
B0,B1=0x8b51f9dd,0x58f38ded

def producer(pool,count=2400):
    key=np.empty(624,dtype=np.uint32)
    for i in range(624):
        b=B0*pow(B1,i,1<<32)&U
        f=b*B1&U
        v=((pool[i%4]^b)*f)&U
        key[i]=v^(v>>16)
    key[0]=0x80000000
    rng=np.random.MT19937(0)
    rng.state={"bit_generator":"MT19937","state":{"key":key,"pos":623}}
    return [int(x) for x in rng.random_raw(count)]

def packet(stream,phase,row):
    start=625+phase-21+STARTS[row]
    return struct.pack("<4I",*stream[start:start+4])

def check(pool,phase,rows):
    stream=producer(pool)
    good=[i for i in range(133) if i!=129 and packet(stream,phase,i)==rows[i]]
    return good,packet(stream,phase,129)

def main():
    for seed,phase in ((1234,0),(1234,13),(17,99),(5,218),(5,390)):
        pool=tuple(int(x) for x in np.random.SeedSequence(seed).pool)
        s=producer(pool)
        rows=[packet(s,phase,i) for i in range(133)]
        rows[129]=b"UNTRUSTED-COPY!!"
        matched,coupon=check(pool,phase,rows)
        assert len(matched)==132 and coupon==packet(s,phase,129)
    print("SYNTHETIC_FIVE_FULL_SPOOL_PREDICTIONS_PASS")

    ap=argparse.ArgumentParser()
    ap.add_argument("--pool",nargs=4)
    ap.add_argument("--phase",type=int,default=13)
    args=ap.parse_args()
    if args.pool is None:return
    assert 0<=args.phase<393
    spool=(ROOT/"evidence/print/spool-reconstruction.log").read_bytes()
    assert hashlib.sha256(spool).hexdigest()==(
        "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083")
    rows=[bytes.fromhex(x.decode()) for x in
          re.findall(rb"PAYLOAD=([0-9A-F]{32})",spool)]
    assert len(rows)==133
    pool=tuple(int(x,16) for x in args.pool)
    good,coupon=check(pool,args.phase,rows)
    print("ORIGINAL_INTACT_SOURCE_MATCH",len(good),"of 132")
    if len(good)!=132:return

    route=json.loads((ROOT/"evidence/recovery-routing.json").read_text())
    accepted=json.loads((ROOT/"acceptance.json").read_text())
    mask=bytes.fromhex(route["K04"]["masked_component"])
    candidate=bytes(a^b for a,b in zip(coupon,mask))
    match=hashlib.sha256(candidate).hexdigest()==accepted["slot_sha256"]["K04"]
    print("K04_COMPONENT_CANDIDATE",candidate.hex().upper(),"ACCEPTANCE_MATCH",match)

if __name__=="__main__":main()
