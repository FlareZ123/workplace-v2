"""Exact original K04 copied-ACK distance for newly discovered stage1406 MT/K02 cosets.

Run: python agents/agent21/k04_stage1406_copy_distance_sft.py
Read-only original source; reuses Agent48's original-source reconstruction.
The MT/K02 stage link remains hypothetical; this is a conditional copy-stage test.
"""
from __future__ import annotations

import hashlib
import json
import re
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "agents/agent48"))
from k04_k02_neighbor_stage_cosets_sft import run as original_cosets  # type: ignore

SPOOL_SHA = "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"
K04_SHA = "930a52a1bab97ca2966332137c99e99298ea6182fb32ab63a3421dfb4fd8c9e0"
PATCH = bytes.fromhex("02110844")
EXPECTED_SUFFIXES = {
    "E41E42AEC0CB3C1B", "740B24D4BA875953", "816ED1B13ED5DD01",
    "D31B24254B8749F4", "201D6AD99C14245F", "819F76A12E722C01",
    "B3332C5B7330F7B9", "CB240B6B53B866BA", "AED16E9E013C343E",
    "F393B52633906EC4",
}


def xor(a: bytes, b: bytes) -> bytes:
    return bytes(x ^ y for x, y in zip(a, b))


def rank(values: list[bytes]) -> int:
    pivot = {}
    for value in values:
        v = int.from_bytes(value, "little")
        while v:
            p = v.bit_length() - 1
            if p in pivot:
                v ^= pivot[p]
            else:
                pivot[p] = v
                break
    return len(pivot)


def span_contains(diff: bytes, generators: list[bytes]) -> bool:
    pivots = {}
    for gen in generators:
        v = int.from_bytes(gen, "little")
        while v:
            p = v.bit_length() - 1
            if p in pivots:
                v ^= pivots[p]
            else:
                pivots[p] = v
                break
    v = int.from_bytes(diff, "little")
    while v:
        p = v.bit_length() - 1
        if p not in pivots:
            return False
        v ^= pivots[p]
    return True


def main() -> None:
    raw = (ROOT / "resources/evidence/print/spool-reconstruction.log").read_bytes()
    assert hashlib.sha256(raw).hexdigest() == SPOOL_SHA
    coupons = re.findall(rb"PAYLOAD=([0-9A-F]{32})", raw)
    assert len(coupons) == 133
    assert coupons[129] == b"A9A9DC5731A5E2AE879C47215C2559D5"
    route = json.loads((ROOT / "resources/evidence/recovery-routing.json").read_text())
    mask = bytes.fromhex(route["K04"]["masked_component"])
    assert mask.hex().upper() == "8556C8CB6140A7F9A5123AC7571BEE1C"
    copied_component = xor(bytes.fromhex(coupons[129].decode()), mask)
    acceptance = json.loads((ROOT / "resources/acceptance.json").read_text())
    assert acceptance["slot_sha256"]["K04"] == K04_SHA

    data = [item for item in original_cosets(ROOT / "resources")
            if item["stage"] == 1406]
    assert len(data) == 10
    assert {item["base"][-16:] for item in data} == EXPECTED_SUFFIXES
    deltas = [bytes.fromhex(s) for s in data[0]["deltas"]]
    assert all([bytes.fromhex(s) for s in item["deltas"]] == deltas for item in data)
    assert rank(deltas) == 33
    assert all(d[8:] == bytes(8) for d in deltas)
    assert Counter(d[4:8] for d in deltas) == {bytes(4): 31, PATCH: 2}
    firstword = [d[:4] for d in deltas if d[4:8] == bytes(4)]
    coupled = [d for d in deltas if d[4:8] == PATCH]
    firstword.append(xor(coupled[0][:4], coupled[1][:4]))
    assert rank(firstword) == 32

    results = []
    for index, item in enumerate(data):
        base = bytes.fromhex(item["base"])
        for patch in (bytes(4), PATCH):
            nearest = copied_component[:4] + xor(base[4:8], patch) + base[8:]
            assert span_contains(xor(base, nearest), deltas)
            bits = sum((x ^ y).bit_count()
                       for x, y in zip(nearest, copied_component))
            changed_bytes = sum(x != y for x, y in zip(nearest, copied_component))
            suffix_bits = sum((x ^ y).bit_count()
                              for x, y in zip(base[8:], copied_component[8:]))
            accepted = hashlib.sha256(nearest).hexdigest() == K04_SHA
            results.append((bits, changed_bytes, suffix_bits, index,
                            patch.hex(), nearest.hex().upper(), accepted))
    assert len(results) == 20
    assert not any(item[-1] for item in results)
    assert (min(x[0] for x in results),
            min(x[1] for x in results),
            min(x[2] for x in results)) == (39, 12, 27)

    # Positive: any derived complete coupon is in its original 33-bit coset.
    witness = bytes.fromhex(data[0]["base"])
    positive = witness
    for i in (0, 4, 19, 32):
        positive = xor(positive, deltas[i])
    assert span_contains(xor(witness, positive), deltas)
    artificial_commitment = hashlib.sha256(positive).hexdigest()
    assert hashlib.sha256(positive).hexdigest() == artificial_commitment
    print("STAGE1406 exact_min_bit_flips=39 exact_min_byte_substitutions=12 "
          "minimum_fixed_suffix_bit_mismatches=27")
    print("BIT_NEAREST", min(results, key=lambda x: (x[0], x[1], x[2])))
    print("NO_ORIGINAL_K04_HIT among 20 proximity representatives")
    print("PLANTED_AFFINE_MEMBERSHIP_PASS", positive.hex().upper())


if __name__ == "__main__":
    main()
