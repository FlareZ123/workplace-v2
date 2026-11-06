"""H-17 metadata-radix full-candidate screen. Portable stdlib SFT.
Usage: python k04_k08_metadata_radix_channel_sft.py h17-archive-dump.zip
Original 46-member evidence ZIP and all commitments remain read-only.
"""
import hashlib, hmac, itertools, json, re, sys, zipfile
SPOOL_SHA="7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"
K04="930a52a1bab97ca2966332137c99e99298ea6182fb32ab63a3421dfb4fd8c9e0"
K08="285eb6b4196d21eaf47e251449e61e0bce28749881ccc5a065ca733b0c3fd747"
MASK=bytes.fromhex("8556C8CB6140A7F9A5123AC7571BEE1C")
NONCE=bytes.fromhex("5F933DA6A1BD03C32DA5CBC25344F497")
CLASSES=("LABEL","STORES","RECOVER")
DESTS=("store","desk","bench")
def component(coupon):
    return hashlib.sha256(bytes(a^b for a,b in zip(coupon,MASK))).hexdigest()
def normalize(s):
    return " ".join(re.sub(r"[^a-z0-9\s]"," ",s.lower()).split())
def caption_hash(s):
    mac=hmac.new(NONCE,normalize(s).encode(),hashlib.sha256).digest()[:16]
    return hashlib.sha256(mac).hexdigest()
def pack_bits(bits, reverse_rows, reverse_bits):
    out=bytearray(16)
    for i,b in enumerate(bits):
        j=127-i if reverse_rows else i
        out[j//8]|=int(b)<<(j%8 if reverse_bits else 7-j%8)
    return bytes(out)
def radix_groups(seq,width=5,reverse_digits=False):
    out=bytearray()
    for k in range(0,len(seq)-width+1,width):
        group=seq[k:k+width]
        v=0
        for d in (group[::-1] if reverse_digits else group):
            v=v*3+d
        out.append(v)
    return bytes(out)
def radix_integer(seq,reverse_bytes=False):
    x=0
    for d in seq:x=x*3+d
    b=x.to_bytes((x.bit_length()+7)//8,"big")
    return b[::-1] if reverse_bytes else b
def read_rows(path):
    with zipfile.ZipFile(path) as z:
        source=z.read("evidence/print/spool-reconstruction.log")
        targets=json.loads(z.read("acceptance.json"))["slot_sha256"]
    assert hashlib.sha256(source).hexdigest()==SPOOL_SHA
    assert targets["K04"]==K04 and targets["K08"]==K08
    rows=[]
    for line in source.decode().splitlines():
        m=re.search(r"JOB=PS-261003-(\d+) ATTEMPT=(\d+) STATE=(\w+) CLASS=(\w+) PAYLOAD=([A-F0-9]{32}) DEST=(\w+)",line)
        if m and 300<=int(m[1])<=427 and m[2]=="1" and m[3]=="ACK":
            rows.append((m[4],m[6]))
    assert len(rows)==128 and set(c for c,d in rows)<=set(CLASSES)
    assert set(d for c,d in rows)<=set(DESTS)
    return rows
def main(path):
    rows=read_rows(path)
    funcs=(
       lambda a,b:a<b,lambda a,b:a==b,lambda a,b:a>b,
       lambda a,b:(a+b)%2,lambda a,b:(a+b)%3==0,
       lambda a,b:(a^b)&1,lambda a,b:(a*b)&1,
       lambda a,b:(a-b)%3==1,lambda a,b:a==0,
       lambda a,b:a==1,lambda a,b:b==0,lambda a,b:b==1,
    )
    total4=0; distinct4=set(); hits4=[]
    total8=[0,0,0]; phrases=[]; hits8=[]
    def probe8(data,mode):
        for part in re.findall(rb"[\x20-\x7e]{12,}",data):
            s=part.decode("ascii")
            norm=normalize(s)
            if len(norm)<12 or " " not in norm or sum(c.isalpha() for c in norm)<8:
                continue
            phrases.append((mode,s))
            if caption_hash(s)==K08:hits8.append((mode,s))
    for cp in itertools.permutations(range(3)):
      for dp in itertools.permutations(range(3)):
        pairs=[(cp[CLASSES.index(c)],dp[DESTS.index(d)]) for c,d in rows]
        for f in funcs:
          bits=[f(a,b) for a,b in pairs]
          for revrows,revbits in itertools.product((0,1),repeat=2):
            coupon=pack_bits(bits,revrows,revbits)
            total4+=1;distinct4.add(coupon)
            if component(coupon)==K04:hits4.append(coupon.hex())
        for revrows,swap in itertools.product((0,1),repeat=2):
          pp=pairs[::-1] if revrows else pairs
          trits=[d for p in pp for d in (p[::-1] if swap else p)]
          for bit_direction,byte_direction in itertools.product((0,1),repeat=2):
            bits=[v for d in trits for v in ((d&1,d>>1) if bit_direction else (d>>1,d&1))]
            for shift in range(4):
              b=bits[shift:]+bits[:shift]
              blob=bytes(sum(bit<<(j if byte_direction else 7-j) for j,bit in enumerate(b[i:i+8])) for i in range(0,len(b),8))
              total8[0]+=1;probe8(blob,"base4")
          for shift in range(5):
            seq=trits[shift:]+trits[:shift]
            for rev in (0,1):
              total8[1]+=1;probe8(radix_groups(seq,5,bool(rev)),"base3x5")
          for rev in (0,1):
            total8[2]+=1;probe8(radix_integer(trits,bool(rev)),"base3int")
    planted=bytes.fromhex("49359A7C0BE1D64F7268EC10459FBA23")
    planted_bits=[(planted[i//8]>>(7-i%8))&1 for i in range(128)]
    restored=pack_bits([1 if bit else 0 for bit in planted_bits],0,0)
    assert restored==planted and component(restored)==component(planted)
    example="the sea goes quiet and we leave a lamp"
    trits=[]
    for b in example.encode():
        g=[]
        for k in range(5):g.append(b%3);b//=3
        trits.extend(g[::-1])
    assert radix_groups(trits).decode()==example
    assert caption_hash(example)==hashlib.sha256(hmac.new(NONCE,example.encode(),hashlib.sha256).digest()[:16]).hexdigest()
    print(json.dumps({"ordinary_rows":len(rows),"K04_assignments":total4,
        "K04_distinct":len(distinct4),"K04_hits":hits4,
        "K08_views":{"2bit":total8[0],"base3group":total8[1],"base3integer":total8[2]},
        "K08_qualifying_ascii":len(phrases),"K08_hits":hits8,
        "synthetic_full_coupon":planted.hex().upper(),
        "synthetic_full_caption":example},sort_keys=True))
if __name__=="__main__":
    main(sys.argv[1])
