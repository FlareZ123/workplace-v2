#!/usr/bin/env python3
"""Enumerate byte/hex/character-order alternatives in the K08 source map."""
from __future__ import annotations
import hashlib, itertools, json
from datetime import datetime
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
E=ROOT/"resources/evidence"

def sha(b):
    return hashlib.sha256(b).hexdigest()

def lowpack(raw, order):
    bits=[x&1 for x in raw]
    out=[]
    for i in range(0,len(bits),8):
        block=bits[i:i+8]
        out.append(sum(v<<j for j,v in enumerate(block)) if order=="LSB" else sum(v<<(7-j) for j,v in enumerate(block)))
    return bytes(out)

def lowvalue(s, order):
    bits=[ord(c)&1 for c in s]
    return sum(v<<i for i,v in enumerate(bits)) if order=="LSB" else sum(v<<(len(bits)-1-i) for i,v in enumerate(bits))

def main():
    pinned={
        ROOT/"resources/acceptance.json":"681739241b757b471acca4c0fef9d9d97e9493883887736d5db3b92bfb0c137f",
        E/"recovery-routing.json":"f8fcbca73d23bf1066edb88c088f89cd24cf22e7c78a4a412166254a4764d8a5",
        E/"telemetry/freeze-export.jsonl":"3787dbd6bab3930ea5293c25a995175161a1c0d7683daad29f498026e057639f",
        E/"transfers/transfer-audit.jsonl":"32970ad4431a9d610cc12dcca2813f39dd8fd2e396f9e748dc94b5932cb69adf",
    }
    for path,expected in pinned.items():
        assert sha(path.read_bytes())==expected, f"source hash mismatch: {path}"
    candidate=json.loads((ROOT/"candidate.json").read_text())
    acceptance=json.loads((ROOT/"resources/acceptance.json").read_text())
    slots={k:bytes.fromhex(candidate[k]) for k in ("K01","K05","K06")}
    for k,b in slots.items():
        assert sha(b)==acceptance["slot_sha256"][k]
    route=json.loads((E/"recovery-routing.json").read_text())
    rows=[json.loads(x) for x in (E/"telemetry/freeze-export.jsonl").read_text().splitlines() if x.strip()]
    start=datetime.fromisoformat(route["K02"]["start_utc"])
    end=datetime.fromisoformat(route["K02"]["end_utc_exclusive"])
    chosen={}
    for r in rows:
        if (r.get("tag"),r.get("field"),r.get("quality"),r.get("state")) != ("LT-204","DIAG_WORD","GOOD","HOLD"):
            continue
        ts=datetime.fromisoformat(r["ts"])
        seq=int(r["seq"])
        if start<=ts<end and seq in range(8) and (seq not in chosen or int(r["revision"])>int(chosen[seq]["revision"])):
            chosen[seq]=r
    assert set(chosen)==set(range(8))
    k02=b"".join(int(chosen[i]["value"]).to_bytes(2,"big") for i in range(8))
    assert sha(k02)[:32].upper()==candidate["K02"]
    tr=[json.loads(x) for x in (E/"transfers/transfer-audit.jsonl").read_text().splitlines() if x.strip()]
    chunks=[r for r in tr if r.get("transfer")=="AX-7782" and r.get("kind")=="CHUNK"]
    byseq={}
    for r in chunks:
        byseq.setdefault(int(r["seq"]),{})[int(r["attempt"])]=bytes.fromhex(r["checkpoint"])
    k07=b"".join(byseq[i][2] for i in range(8))
    assert sha(k07)[:32].upper()==candidate["K07"]
    raw={"K01":slots["K01"],"K02":k02,"K05":slots["K05"],"K06":slots["K06"],"K07":k07}
    results=[]
    for bit,byte_order,hex_order,char_order in itertools.product(("LSB","MSB"),("forward","reverse"),("forward","reverse"),("LSB","MSB")):
        mapping={}
        for slot,b in raw.items():
            packed=lowpack(b,bit)
            if byte_order=="reverse":
                packed=packed[::-1]
            hx=packed.hex().upper()
            if hex_order=="reverse":
                hx=hx[::-1]
            mapping[slot]=lowvalue(hx,char_order)
        results.append({"byte_bit_order":bit,"packed_byte_order":byte_order,"hex_character_order":hex_order,
                        "character_weight_order":char_order,"selectors":mapping})
    baseline={"K01":12,"K02":11,"K05":10,"K06":10,"K07":11}
    matches=[r for r in results if r["selectors"]==baseline]
    print(json.dumps({"variants":len(results),"baseline_map":baseline,"baseline_equivalent_variants":matches,
                      "all_variants":results},indent=2,sort_keys=True))

if __name__=="__main__":
    main()
