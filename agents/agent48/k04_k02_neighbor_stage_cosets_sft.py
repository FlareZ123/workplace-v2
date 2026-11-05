"""Source-pinned rank 33 K02 fourword donor neighbor-stage gate; original K04 unmodified."""
from pathlib import Path
from datetime import datetime
import hashlib,json,sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"agent49"))
import k04_p951_symbolic_basis as mt

TELE="3787dbd6bab3930ea5293c25a995175161a1c0d7683daad29f498026e057639f"
def temper(x):
 x^=x>>11;x^=(x<<7)&0x9D2C5680;x^=(x<<15)&0xEFC60000;x^=x>>18
 return x&0xFFFFFFFF
def expression(rows,v):
 val=rem=0
 while v:
  p=v.bit_length()-1
  if p in rows:
   w,b=rows[p];v^=w;val^=b
  else:rem^=1<<p;v^=1<<p
 return rem,val
def pack(native):
 return b"".join(temper((native>>(32*i))&0xFFFFFFFF).to_bytes(4,"little") for i in range(4))
def run(root):
 mt.LAST=3500
 baseline,wordbank=mt.source(root)
 raw=(root/"evidence/telemetry/freeze-export.jsonl").read_bytes()
 assert hashlib.sha256(raw).hexdigest()==TELE
 chosen={}
 for line in raw.splitlines():
  x=json.loads(line)
  if x.get("tag")!="LT-204" or x.get("field")!="DIAG_WORD" or x.get("quality")!="GOOD" or x.get("state")!="HOLD" or x.get("seq") not in range(8):continue
  if not(datetime.fromisoformat("2026-10-03T21:13:40+00:00")<=datetime.fromisoformat(x["ts"])<datetime.fromisoformat("2026-10-03T21:13:48+00:00")):continue
  i=x["seq"]
  if i not in chosen or x["revision"]>chosen[i]["revision"]:chosen[i]=x
 assert sorted(chosen)==list(range(8))
 k02raw=b"".join(int(chosen[i]["value"]).to_bytes(2,"big") for i in range(8))
 assert k02raw.hex().upper()=="E1A5E474BAD7E853A2E8C71D3317D507"
 acceptance=json.loads((root/"acceptance.json").read_text())
 assert hashlib.sha256(hashlib.sha256(k02raw).digest()[:16]).hexdigest()==acceptance["slot_sha256"]["K02"]
 route=json.loads((root/"evidence/recovery-routing.json").read_text())
 mask=bytes.fromhex(route["K04"]["masked_component"])
 assert mask.hex().upper()=="8556C8CB6140A7F9A5123AC7571BEE1C"
 target=[v for stage in range(951,955) for v in mt.get(wordbank,stage)]
 assert all(baseline.predict(v)is None for v in target)
 out=[];rejected=[]
 for stage in (1178,1179,1405,1406):
  for endian in ("big","little"):
   for reverse in (False,True):
    for halves in (False,True):
     parts=[k02raw[i:i+4] for i in (0,4,8,12)]
     if halves:parts=[p[2:]+p[:2] for p in parts]
     if reverse:parts.reverse()
     vals=[int.from_bytes(p,endian) for p in parts]
     for native in (False,True):
      b=mt.Basis();b.rows=baseline.rows.copy();b.rank=baseline.rank
      try:
       for lane,value in enumerate(vals):
        if not native:value=mt.untemper(value)
        for bit,v in enumerate(mt.get(wordbank,stage+lane)):b.insert(v,(value>>bit)&1)
      except AssertionError:
       rejected.append((stage,endian,reverse,halves,native));continue
      pairs=[expression(b.rows,v) for v in target]
      assert sum(r==0 for r,c in pairs)==95
      indep={};basis=[];coeff=[];base=0
      for j,(rem,const) in enumerate(pairs):
       base|=const<<j;tag=0
       while rem:
        p=rem.bit_length()-1
        if p in indep:
         row,mask_tag=indep[p];rem^=row;tag^=mask_tag
        else:
         mask_tag=1<<len(basis);indep[p]=(rem,mask_tag);basis.append(rem);tag^=mask_tag;break
       coeff.append(tag)
      assert len(basis)==33
      coupon=bytes(x^y for x,y in zip(pack(base),mask))
      deltas=[pack(sum(((v>>i)&1)<<j for j,v in enumerate(coeff))) for i in range(33)]
      out.append(dict(stage=stage,mode=(endian,reverse,halves,"native" if native else "tempered"),
                      base=coupon.hex().upper(),deltas=[d.hex().upper() for d in deltas]))
 assert len(out)==42 and len(rejected)==22
 assert [sum(x["stage"]==t for x in out) for t in (1178,1179,1405,1406)]==[16,0,16,10]
 assert out[0]["base"]=="34489314F66E4A22D32AEA1E52228B9D"
 old={x["base"][-16:] for x in out if x["stage"] in (1178,1405)}
 new={x["base"][-16:] for x in out if x["stage"]==1406}
 assert len(old)==32 and len(new)==10 and not(old&new)
 assert all(all(int(d[16:],16)==0 for d in x["deltas"]) for x in out)
 assert all(x["deltas"]==out[0]["deltas"] for x in out)
 print("ORIGINAL_SOURCE_K02_HELDOUT stages=1178:16,1179:0,1405:16,1406:10")
 print("NEW_1406 ten_disjoint_full_coupon_affine_cosets target_dimension=33 candidate_set=85899345920")
 print("CONTRADICTIONS 1179=16 1406=6; SOURCE_1406_NEW_SUFFIXES",sorted(new))
 print("NO original K04 SHA sweep performed; all cosets are conditional on unproven MT shared source")
 return out
if __name__=="__main__":
 rows=run(Path(sys.argv[1]) if len(sys.argv)>1 else Path("resources"))
 if len(sys.argv)>2:
  p=Path(sys.argv[2]);p.write_text(json.dumps(rows,indent=2)+"\n")
  print("DATA_SHA256",hashlib.sha256(p.read_bytes()).hexdigest())
