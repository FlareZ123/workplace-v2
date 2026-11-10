"""H-17 source-first AES-CMAC printer writer model, original source left untouched.

A complete 16-byte coupon could be a keyed MAC of job metadata. This tests
AES-CMAC-128 as an independent keyed printer producer, distinct from packet
bit faults, MT stage guesses, and keyed HMAC writers. An exact historical
whole packet must pass before a target coupon is proposed.

Dependencies: cryptography >= 3; original ZIP unmodified.
"""
from __future__ import annotations

from collections import Counter
from pathlib import Path
import hashlib
import re
import sys

from cryptography.hazmat.primitives import cmac
from cryptography.hazmat.primitives.ciphers import algorithms

SOURCE_SHA = "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"
KEYS = {
    "K01": "049AAB2E1CDE7A82CD7C60234303C91A",
    "K02": "0D7E3AB56FB75DA3EB0E2E06786D239E",
    "K03": "1384AF96E25D6ADA666209CB55E062FA",
    "K05": "FF8B78200A56E8586DCDA00EF01E4572",
    "K06": "5DBF40EE52FAAED9A536D3326CF0D95A",
    "K07": "93495F5E425AB8E592123DABAEB68545",
    "ESC_N_MASK": "8556C8CB6140A7F9A5123AC7571BEE1C",
    "DESK_NONCE": "5F933DA6A1BD03C32DA5CBC25344F497",
}
PAT = re.compile(r"^(?P<ts>\S+) JOB=(?P<job>\S+) ATTEMPT=(?P<attempt>\d+) STATE=(?P<state>\S+) CLASS=(?P<cls>\S+) PAYLOAD=(?P<payload>[0-9A-F]{32}) DEST=(?P<dest>\S+)$")

def mac(key: bytes, message: bytes) -> bytes:
    context = cmac.CMAC(algorithms.AES(key))
    context.update(message)
    return context.finalize()

def render(row: dict[str, str]) -> list[bytes]:
    j,a,t,s,c,d = (row[k] for k in ("job", "attempt", "ts", "state", "cls", "dest"))
    t0=t.replace("+00:00", "Z")
    strings = (
        j, j[-4:], t, t0, j+"/"+a, j+"/"+c, j+"/"+d,
        j+"/"+a+"/"+c+"/"+d,
        f"{j}|{a}|{s}|{c}|{d}",
        f"{j}|{t0}|{a}|{c}|{d}",
        f"JOB={j} ATTEMPT={a} STATE={s} CLASS={c} DEST={d}",
        f"{t} JOB={j} ATTEMPT={a} STATE={s} CLASS={c} DEST={d}",
        f"IR-261003-H17|{j}|{a}",
        f"H17-IR-261003|{j}|{a}",
        f"{j}:{a}:{c}:{d}",
        f"{t0}:{j}:{a}:{s}",
    )
    return [x.encode("ascii") for x in strings]

def main(root: Path) -> None:
    original=(root/"evidence/print/spool-reconstruction.log").read_bytes()
    assert hashlib.sha256(original).hexdigest()==SOURCE_SHA
    rows=[]
    for line in original.decode("ascii").splitlines():
        m=PAT.fullmatch(line)
        if m is not None:
            rows.append(m.groupdict())
    assert len(rows)==133
    assert rows[129]["job"]=="PS-261003-0417" and rows[129]["attempt"]=="2"
    # Withhold the disputed original K04 record completely.
    ordinary=rows[:128]
    keys=[(label, bytes.fromhex(hexkey)) for label,hexkey in KEYS.items()]
    versions=["raw", "reverse", "xor_key"]
    configs=[]
    for label,key in keys:
        for template in range(len(render(ordinary[0]))):
            for version in versions:
                configs.append((label,key,template,version))
    assert len(configs)==8*16*3
    def emit(row:dict[str,str],key:bytes,template:int,version:str)->bytes:
        out=mac(key,render(row)[template])
        if version=="reverse":return out[::-1]
        if version=="xor_key":return bytes(a^b for a,b in zip(out,key))
        return out
    first_full=[]
    byte_hist=Counter()
    for label,key,template,version in configs:
        predicted=emit(ordinary[0],key,template,version)
        actual=bytes.fromhex(ordinary[0]["payload"])
        score=sum(a==b for a,b in zip(predicted,actual))
        byte_hist[score]+=1
        if score==16:
            first_full.append((label,key,template,version))
    # Plant an independent whole-printed-packet producer, then recover
    # its model from the first packet and predict a second withheld packet.
    plant=("K02",bytes.fromhex(KEYS["K02"]),9,"xor_key")
    planted0=emit(ordinary[0],*plant[1:])
    planted1=emit(ordinary[1],*plant[1:])
    matches=[config for config in configs
             if emit(ordinary[0],*config[1:])==planted0]
    assert len(matches)==1 and matches[0]==plant
    assert emit(ordinary[1],*matches[0][1:])==planted1
    # RFC 4493 AES-CMAC standard known-answer fixture.
    assert mac(bytes.fromhex("2b7e151628aed2a6abf7158809cf4f3c"), b"") == bytes.fromhex("bb1d6929e95937287fa37d129b756746")
    holdout=[]
    for c in first_full:
        if all(emit(row,*c[1:])==bytes.fromhex(row["payload"]) for row in ordinary[1:]):
            holdout.append(c)
    print("models",len(configs),"source_first_whole_packet_hits",len(first_full),"historical_127_whole_holdout_models",len(holdout))
    print("first_packet_byte_score_hist",sorted(byte_hist.items()))
    print("synthetic_CMAC_RFC4493_PASS")
    if holdout:
        import json
        route=json.loads((root/"evidence/recovery-routing.json").read_text())
        from hashlib import sha256
        mask=bytes.fromhex(route["K04"]["masked_component"])
        for c in holdout:
            coupon=emit(rows[129],*c[1:])
            component=bytes(a^b for a,b in zip(coupon,mask))
            print("target_model",c[0],c[2],c[3],"coupon",coupon.hex().upper(),"component",component.hex().upper(),"commitment",sha256(component).hexdigest())

if __name__ == "__main__":
    default_root=Path(__file__).resolve().parents[2] / "resources"
    main(Path(sys.argv[1]) if len(sys.argv)>1 else default_root)
