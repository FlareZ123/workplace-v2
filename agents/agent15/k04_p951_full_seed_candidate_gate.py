"""K04 hypothetical CPython binary-seed full-source candidate/recovery gate.

Public input: a candidate original binary seed B. Reconstruct 86 original
source-pinned raw seed word domains, 6 SHA512 digest chunks, and two optional
late wrapped digest terms. Only if B passes the *source* check, regenerate
printer output stage 951 and test the unchanged K04 mask + slot commitment.

The actual historical source producer is unproven. Without a candidate B,
this utility asserts no K04 recovery. All source constraints omit ACK2 row129.

For development synthetic controls (no historical claim), invoke with no args.
Pass one existing binary seed path to evaluate the original source/target.
"""
from __future__ import annotations

import hashlib
import json
import random
import re
import sys
from pathlib import Path

import k04_p951_sha512_seed_fingerprint_sft as fingerprint

ROOT=Path(__file__).resolve().parents[2]
U=0xFFFFFFFF


def byte_seed_signature(B: bytes,
                        six_digest_words: dict[int,int],
                        late_terms: dict[int,list[int]],
                        raw_seed_words: dict[int,list[int]]) -> tuple[bool,int]:
    expanded=int.from_bytes(B+hashlib.sha512(B).digest(),"big")
    n=(expanded.bit_length()+31)//32
    if not 606<=n<=623:
        return False,n
    for j,choices in raw_seed_words.items():
        if ((expanded>>(32*j))&U) not in choices:
            return False,n
    for j,word in six_digest_words.items():
        if ((expanded>>(32*j))&U)!=word:
            return False,n
    for j,terms in late_terms.items():
        index=j%n
        term=(((expanded>>(32*index))&U)+index)&U
        if term not in terms:
            return False,n
    return True,n


def predicted_coupon(B: bytes) -> bytes:
    generator=random.Random(B)
    for _ in range(951):
        generator.getrandbits(32)
    return b"".join(generator.getrandbits(32).to_bytes(4,"little")
                    for _ in range(4))


def visible_original_source_domains() -> tuple[dict[int,int],dict[int,list[int]],dict[int,list[int]]]:
    raw=(ROOT/"resources/evidence/print/spool-reconstruction.log").read_bytes()
    assert hashlib.sha256(raw).hexdigest()==fingerprint.SOURCE_SHA
    tokens=re.findall(rb"PAYLOAD=([0-9A-F]{32})",raw)
    assert len(tokens)==len(fingerprint.STARTS)==133
    # Retained selected ACK2 is neither decoded nor part of the fitted equations.
    packets=[b"" if i==129 else bytes.fromhex(t.decode("ascii"))
             for i,t in enumerate(tokens)]
    return fingerprint.derive_seed_digest_words(
        packets,fingerprint.expressions()
    )


def synthetic_controls() -> None:
    expr=fingerprint.expressions()
    for n in (606,607,608,623):
        B=bytes((i*37+5)%256 for i in range(4*n-64))
        draws=random.Random(B)
        raw_outputs=[draws.getrandbits(32) for _ in range(967)]
        packets=[b"".join(raw_outputs[start+lane].to_bytes(4,"little")
                          for lane in range(4))
                 for start in fingerprint.STARTS]
        original_selected=packets[129]
        packets[129]=b""
        six,tails,sparse=fingerprint.derive_seed_digest_words(packets,expr)
        good,count=byte_seed_signature(B,six,tails,sparse)
        assert good and count==n
        changed=bytes((B[0]^1,))+B[1:]
        assert byte_seed_signature(changed,six,tails,sparse)[0] is False
        assert predicted_coupon(B)==original_selected
        print(f"Synthetic genuine Python n={n}: source gate PASS; "
              "altered seed REJECT; complete withheld coupon RESTORED",flush=True)


def check_original_candidate(path: Path) -> None:
    B=path.read_bytes()
    six,tails,sparse=visible_original_source_domains()
    matches,n=byte_seed_signature(B,six,tails,sparse)
    if not matches:
        print(json.dumps({
            "result":"SOURCE_REJECTED",
            "hypothetical_key_array_length":n,
            "historical_generator_authenticated":False,
        },indent=2))
        return
    coupon=predicted_coupon(B)
    routing=json.loads((ROOT/"resources/evidence/recovery-routing.json").read_text())
    acceptance=json.loads((ROOT/"resources/acceptance.json").read_text())
    mask=bytes.fromhex(routing["K04"]["masked_component"])
    part=bytes(a^b for a,b in zip(coupon,mask))
    got=hashlib.sha256(part).hexdigest()
    expected=acceptance["slot_sha256"]["K04"]
    print(json.dumps({
        "result":"ORIGINAL_K04_COMMITMENT_PASS" if got==expected else "K04_COMMITMENT_REJECTED",
        "original_visible_source_constraints_match":True,
        "hypothetical_key_array_length":n,
        "predicted_coupon_hex":coupon.hex().upper(),
        "predicted_component_hex":part.hex().upper(),
        "original_component_sha256":got,
        "historical_generator_authenticated":False,
    },indent=2))


if __name__=="__main__":
    if len(sys.argv)==1:
        synthetic_controls()
    else:
        assert len(sys.argv)==2
        check_original_candidate(Path(sys.argv[1]))
