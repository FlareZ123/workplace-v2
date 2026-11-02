"""K04 full coupon synthesizer for seven independently known future MT native words.

Source-pinned *hypothetical* p951 MT chronology, selected row129 omitted before
decoding. Includes seven genuine seeded full-stream positive controls. A
separately scoped 7,680 complete-candidate test from six preserved source
blocks checks the unmodified original K04 commitment but does not claim that
those blocks were historically emitted from this printer generator.

Run: python agents/agent39/k04_p951_seven_donor_affine_sft.py
"""
from __future__ import annotations

import hashlib
import importlib.util
import itertools
import json
import random
import re
import struct
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location(
    "agent45_inverse", ROOT / "agents/agent45/k04_p951_seed_residue_inverse_sft.py"
)
prior = importlib.util.module_from_spec(spec)
spec.loader.exec_module(prior)
SOURCE_SHA = "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"
PALETTE = (1179, 1180, 1181, 1347, 1348, 1574, 1575)
B = len(PALETTE) * 32
U = 0xffffffff


def express():
    mt = [[1 << (32*i+b) for b in range(32)] for i in range(624)]
    for index in range(624, 2205):
        p, n, q = mt[index-624], mt[index-623], mt[index-227]
        mt.append([
            q[b]
            ^ (p[31] if b == 30 else n[b+1] if b < 30 else 0)
            ^ (n[0] if (0x9908b0df >> b) & 1 else 0)
            for b in range(32)
        ])
    return mt


def reduce(row, basis):
    while row:
        pivot = row.bit_length()-1
        prior_row = basis.get(pivot)
        if prior_row is None:
            break
        row ^= prior_row
    return row


def source_basis(expressions, packets):
    source = {}
    for i, start in enumerate(prior.STARTS):
        if i == 129:
            continue
        assert len(packets[i]) == 16
        for lane in range(4):
            native = prior.untemper(int.from_bytes(
                packets[i][lane*4:lane*4+4], "little"
            ))
            for bit, term in enumerate(expressions[624+start+lane]):
                residual = reduce((term<<1) | ((native>>bit)&1), source)
                assert residual != 1, "inconsistent intact source"
                if residual > 1:
                    source[residual.bit_length()-1] = residual
    assert len(source) == 15365
    return source


def make_coupon_map(expressions, packets):
    """Affine selected-native-bit = parity(mask AND 224 donor bits) XOR 0/1."""
    source = source_basis(expressions, packets)
    # Variable ordering: original MT 19968 bits, seven independent 32-bit
    # donor words, constant parity. Original MT bits above donor coordinates.
    basis = {
        pivot+B: ((row>>1)<<(B+1)) | (row&1)
        for pivot, row in source.items()
    }
    new = 0
    for index, at in enumerate(PALETTE):
        for bit, term in enumerate(expressions[624+at]):
            row = (term<<(B+1)) | (1 << (1+index*32+bit))
            residual = reduce(row, basis)
            assert residual != 1, "native donor equation contradiction"
            if residual > 1:
                basis[residual.bit_length()-1] = residual
                new += 1
    assert new == B, "seven donors not independent of source"
    coupon = []
    for at in range(951, 955):
        for term in expressions[624+at]:
            residual = reduce(term<<(B+1), basis)
            assert residual.bit_length() <= B+1, "donors do not identify selected"
            coupon.append((residual>>1, residual&1))
    assert len(coupon) == 128
    return coupon


def select_native(coupon, donor_words):
    assert len(donor_words) == 7
    merged = sum((v & U) << (32*i) for i,v in enumerate(donor_words))
    result = [0,0,0,0]
    for i,(mask,bit) in enumerate(coupon):
        outbit = ((merged&mask).bit_count()&1)^bit
        result[i//32] |= outbit << (i%32)
    return result


def temper(x):
    x ^= x >> 11
    x ^= (x << 7) & 0x9d2c5680
    x ^= (x << 15) & 0xefc60000
    x ^= x >> 18
    return x & U


def positive_controls(expressions):
    for words in (1,8,32,127,364,606,623):
        seed = sum(
            ((0x9c084415+k*0x8181)&U) << (32*k)
            for k in range(words)
        )
        rng = random.Random(seed)
        draws = [rng.getrandbits(32) for _ in range(1580)]
        packets = [
            b"".join(draws[at+lane].to_bytes(4,"little")
                     for lane in range(4))
            for at in prior.STARTS
        ]
        packets[129] = b""
        coupon = make_coupon_map(expressions, packets)
        donor = [prior.untemper(draws[at]) for at in PALETTE]
        expected = [prior.untemper(draws[at]) for at in range(951,955)]
        assert select_native(coupon, donor) == expected, words
        assert all(prior.untemper(temper(x)) == x for x in expected)
    print("Seven seeded MT full-coupon holdouts: 7/7 PASS")


def preserved_groups():
    root = ROOT / "resources/evidence"
    telemetry = [
        json.loads(line)
        for line in (root/"telemetry/freeze-export.jsonl").read_text().splitlines()
    ]
    winners = {}
    start = datetime.fromisoformat("2026-10-03T21:13:40+00:00")
    end = datetime.fromisoformat("2026-10-03T21:13:48+00:00")
    for x in telemetry:
        if (x.get("tag") == "LT-204"
            and x.get("field") == "DIAG_WORD"
            and x.get("quality") == "GOOD"
            and x.get("state") == "HOLD"
            and x.get("seq") in range(8)
            and start <= datetime.fromisoformat(x["ts"]) < end):
            i=x["seq"]
            if i not in winners or winners[i]["revision"] < x["revision"]:
                winners[i] = x
    assert sorted(winners)==list(range(8))
    k02=struct.pack(">8H", *(int(winners[i]["value"]) for i in range(8)))
    assert hashlib.sha256(k02).digest()[:16].hex().upper() == "0D7E3AB56FB75DA3EB0E2E06786D239E"

    seals = [
        json.loads(line)
        for line in (root/"maintenance/seal-receipts.jsonl").read_text().splitlines()
    ]
    best={}
    for x in seals:
        if (x.get("permit")=="PTW-417"
            and x.get("state")=="CLOSED"
            and x.get("fitment")=="AS_LEFT" and x.get("signed") is True):
            key=x["bay"]
            if key not in best or best[key]["revision"] < x["revision"]:
                best[key]=x
    serials=[best[bay]["serial"] for bay in "BDAC"]
    assert hashlib.sha256("|".join(serials).encode()).digest()[:16].hex().upper() == "1384AF96E25D6ADA666209CB55E062FA"
    ptw=bytes.fromhex("".join(s.rsplit("-",1)[-1] for s in serials))

    transfers=[
        json.loads(line)
        for line in (root/"transfers/transfer-audit.jsonl").read_text().splitlines()
    ]
    best={}
    for x in transfers:
        if x["kind"]=="CHUNK" and x["transfer"]=="AX-7782":
            k=x["seq"]
            if k not in best or x["attempt"]>best[k]["attempt"]:
                best[k]=x
    assert sorted(best)==list(range(8))
    k07=b"".join(bytes.fromhex(best[i]["checkpoint"]) for i in range(8))
    assert hashlib.sha256(k07).digest()[:16].hex().upper() == "93495F5E425AB8E592123DABAEB68545"

    groups={
        "WN14": bytes.fromhex("049AAB2E1CDE7A82CD7C60234303C91A"),
        "K02raw": k02,
        "PTW417": ptw,
        "K05raw":bytes.fromhex("FF8B78200A56E8586DCDA00EF01E4572"),
        "K06raw":bytes.fromhex("5DBF40EE52FAAED9A536D3326CF0D95A"),
        "K07raw":k07,
    }
    assert all(len(b)==16 for b in groups.values())
    return groups


def interpretation(block, little, is_tempered, reverse, pick):
    parts=[block[i:i+4] for i in range(0,16,4)]
    if reverse:parts.reverse()
    if pick == "first":parts=parts[:3]
    if pick == "last":parts=parts[1:]
    values=[int.from_bytes(p,"little" if little else "big") for p in parts]
    return [prior.untemper(v) if is_tempered else v for v in values]


def original_candidate_sieve(coupon, groups):
    route=json.loads((ROOT/"resources/evidence/recovery-routing.json").read_text())
    accept=json.loads((ROOT/"resources/acceptance.json").read_text())
    mask=bytes.fromhex(route["K04"]["masked_component"])
    commitment=bytes.fromhex(accept["slot_sha256"]["K04"])
    searched=0
    matches=[]
    for left,right in itertools.permutations(groups,2):
        for pick in ("first","last"):
            for a,b,c,d,e,f in itertools.product((False,True),repeat=6):
                left_native=interpretation(groups[left],a,b,c,pick)
                right_native=interpretation(groups[right],d,e,f,"all")
                selected=select_native(coupon,left_native+right_native)
                for order in ("little","big"):
                    payload=b"".join(temper(x).to_bytes(4,order) for x in selected)
                    component=bytes(x^y for x,y in zip(payload,mask))
                    searched+=1
                    if hashlib.sha256(component).digest()==commitment:
                        matches.append((left,right,pick,a,b,c,d,e,f,order,component.hex().upper()))
    assert searched == 7680
    print("Six source blocks, 7,680 complete hypothetical coupons:",len(matches),"matches")
    return matches


def main():
    expressions=express()
    positive_controls(expressions)
    spool=(ROOT/"resources/evidence/print/spool-reconstruction.log").read_bytes()
    assert hashlib.sha256(spool).hexdigest()==SOURCE_SHA
    fields=re.findall(rb"PAYLOAD=([0-9A-F]{32})",spool)
    assert len(fields)==len(prior.STARTS)==133 and prior.STARTS[129]==951
    # No selected original ACK2 bytes are parsed or admitted.
    packets=[
        b"" if i==129 else bytes.fromhex(field.decode())
        for i,field in enumerate(fields)
    ]
    coupon=make_coupon_map(expressions,packets)
    result=original_candidate_sieve(coupon,preserved_groups())
    assert result==[],result
    print("Original selected target bits independently known: 0/128")
    print("The source-only model is not an authenticated historical producer")


if __name__ == "__main__":
    main()
