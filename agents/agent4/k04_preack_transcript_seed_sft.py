"""H-17 K04 transcript-seeded RECOVER emitter. Source-pinned read-only SFT.
Usage: python agents/agent4/k04_preack_transcript_seed_sft.py h17-archive-dump.zip
"""
import hashlib, hmac, itertools, json, random, re, sys, zipfile
SPOOL_SHA="7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"
K04_SHA="930a52a1bab97ca2966332137c99e99298ea6182fb32ab63a3421dfb4fd8c9e0"
MASK=bytes.fromhex("8556C8CB6140A7F9A5123AC7571BEE1C")
NONCE=bytes.fromhex("5F933DA6A1BD03C32DA5CBC25344F497")
P=re.compile(r'(?P<date>\S+) JOB=(?P<job>\S+) ATTEMPT=(?P<attempt>\d+) STATE=(?P<state>\w+) CLASS=(?P<class>\w+) PAYLOAD=(?P<hex>[0-9A-F]{32}) DEST=(?P<dest>\w+)')
def load(path):
    with zipfile.ZipFile(path) as z:
        source=z.read("evidence/print/spool-reconstruction.log")
        acceptance=json.loads(z.read("acceptance.json"))["slot_sha256"]
    assert hashlib.sha256(source).hexdigest()==SPOOL_SHA and acceptance["K04"]==K04_SHA
    rows=[]
    for line in source.decode().splitlines():
        match=P.fullmatch(line)
        if match:
            record=match.groupdict()
            record["payload"]=bytes.fromhex(record["hex"])
            record["line"]=line
            rows.append(record)
    assert len(rows)==133
    ordinary=rows[:128]
    assert all(int(r["job"][-4:])==300+i and r["attempt"]=="1" and r["state"]=="ACK" for i,r in enumerate(ordinary))
    north,watch=rows[129],rows[132]
    assert (north["job"],north["attempt"],north["state"],north["class"])==("PS-261003-0417","2","ACK","RECOVER")
    assert (watch["job"],watch["attempt"],watch["state"],watch["class"])==("PS-261003-0420","2","ACK","RECOVER")
    return ordinary,north,watch
def views(ordinary):
    output={}
    for name,rows in (("all",ordinary),("first64",ordinary[:64]),("last64",ordinary[64:])):
        output[name+".bytes"]=b"".join(r["payload"] for r in rows)
        output[name+".hex"]=b"".join(r["hex"].encode() for r in rows)
        output[name+".lines"]="".join(r["line"]+"\n" for r in rows).encode()
        output[name+".meta"]="".join(f'{r["job"]}|{r["class"]}|{r["dest"]}\n' for r in rows).encode()
        output[name+".categories"]=bytes(3*("LABEL","STORES","RECOVER").index(r["class"])+("store","desk","bench").index(r["dest"]) for r in rows)
    return output
def contexts(r):
    j=r["job"]
    return {"empty":b"","job":j.encode(),"job_attempt":f'{j}|{r["attempt"]}'.encode(),
            "job_full":f'{j}|{r["attempt"]}|{r["state"]}|{r["class"]}|{r["dest"]}'.encode(),
            "event_time":f'{j}|{r["date"]}'.encode()}
def seed(base,context,kind):
    b=base+b"|"+context if context else base
    if kind=="bytes":return b
    if kind=="int_big":return int.from_bytes(b,"big")
    if kind=="int_little":return int.from_bytes(b,"little")
    if kind in ("sha256","sha512","md5"):return getattr(hashlib,kind)(b).digest()
    if kind=="hmac_nonce":return hmac.new(NONCE,b,hashlib.sha256).digest()
    if kind=="hmac_mask":return hmac.new(MASK,b,hashlib.sha256).digest()
    raise ValueError(kind)
def coupon(seed_value,prefix,layout):
    r=random.Random(seed_value)
    for _ in range(prefix):r.getrandbits(32)
    if layout=="bytes":return r.randbytes(16)
    if layout=="getrandbits128-big":return r.getrandbits(128).to_bytes(16,"big")
    if layout=="getrandbits128-little":return r.getrandbits(128).to_bytes(16,"little")
    if layout=="bytewise":return bytes(r.getrandbits(8) for _ in range(16))
    if layout=="word-big":return b"".join(r.getrandbits(32).to_bytes(4,"big") for _ in range(4))
    if layout=="reversewords":return b"".join(r.getrandbits(32).to_bytes(4,"little") for _ in range(4))[::-1]
    raise ValueError(layout)
def reduced_hash(value):
    return hashlib.sha256(bytes(a^b for a,b in zip(value,MASK))).hexdigest()
def main(path):
    ordinary,north,watch=load(path)
    corpus=views(ordinary)
    kinds=("bytes","int_big","int_little","sha256","sha512","md5","hmac_nonce","hmac_mask")
    layouts=("bytes","getrandbits128-big","getrandbits128-little","bytewise","word-big","reversewords")
    prefixes=(0,1,4,16,64)
    nc,wc=contexts(north),contexts(watch)
    synthetic_t=coupon(seed(corpus["all.bytes"],nc["job_full"],"sha512"),4,"word-big")
    synthetic_w=coupon(seed(corpus["all.bytes"],wc["job_full"],"sha512"),4,"word-big")
    synthetic_digest=reduced_hash(synthetic_t)
    observed=set();target_hits=[];whole_watch_hits=[];positive=0;count=0
    for label,base in corpus.items():
        for kind,context,prefix,layout in itertools.product(kinds,nc,prefixes,layouts):
            predicted_n=coupon(seed(base,nc[context],kind),prefix,layout)
            predicted_w=coupon(seed(base,wc[context],kind),prefix,layout)
            count+=1;observed.add(predicted_n)
            if predicted_w==watch["payload"]:whole_watch_hits.append((label,kind,context,prefix,layout))
            if reduced_hash(predicted_n)==K04_SHA:target_hits.append((label,kind,context,prefix,layout,predicted_n.hex()))
            if predicted_w==synthetic_w and reduced_hash(predicted_n)==synthetic_digest:positive+=1
    assert (len(ordinary),len(corpus),count,len(observed),positive)==(128,15,18000,12000,1)
    print(json.dumps({"ordinary":len(ordinary),"corpus_views":len(corpus),
          "complete_assignments":count,"distinct_north_coupons":len(observed),
          "watch_spare_whole_packet_matches":len(whole_watch_hits),"watch_configs":whole_watch_hits,
          "K04_original_commitment_hits":target_hits,"synthetic_two_event_positive":positive,
          "original_selected_ACK2_excluded":True},sort_keys=True))
if __name__=="__main__":main(sys.argv[1])
