"""SFT: exact Hamming/byte distance from the copied K04 ACK to Agent1 K02 donor cosets.

Run from the repository root: python agents/agent26/k04_k02_copy_distance_sft.py
Requires Python standard library only. Regenerates both source-pinned affine datasets.
"""
import hashlib
import json
import re
import subprocess
import sys
import tempfile
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SPOOL_HASH = "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"
DATA_HASHES = {
    1178: "3bcf827847aa2905d4efa4747d2048d3a542a0edcf3cab3b49478388aa26f61d",
    1405: "6f114714bcc3393a7ab23235fd1424331e8e4b63b2acf12088dcb628632738a3",
}
STAGES = {
    1178: ("k04_k02_raw_future_coupon_sft.py", "k02_donor_affine.dat", (39, 12, 28)),
    1405: ("k04_k02_raw_stage1405_coupon_sft.py", "k02_donor_stage1405_affine.dat", (39, 11, 25)),
}
PATCH = bytes.fromhex("02110844")


def xor(a, b):
    return bytes(x ^ y for x, y in zip(a, b))


def rank(values):
    pivots = {}
    for item in values:
        value = item if isinstance(item, int) else int.from_bytes(item, "little")
        while value:
            p = value.bit_length() - 1
            if p not in pivots:
                pivots[p] = value
                break
            value ^= pivots[p]
    return len(pivots)


def affine_member(diff, deltas):
    pivots = {}
    for delta in deltas:
        value = int.from_bytes(delta, "little")
        while value:
            p = value.bit_length() - 1
            if p not in pivots:
                pivots[p] = value
                break
            value ^= pivots[p]
    value = int.from_bytes(diff, "little")
    while value:
        p = value.bit_length() - 1
        if p not in pivots:
            return False
        value ^= pivots[p]
    return True


def distances(stage, data, copied, target_hash):
    assert hashlib.sha256(data).hexdigest() == DATA_HASHES[stage]
    entries = [bytes.fromhex(s) for s in data.decode().splitlines()]
    assert len(entries) == 49
    bases, deltas = entries[:16], entries[16:]
    assert rank(deltas) == 33
    assert len({x[8:] for x in bases}) == 16
    assert all(d[8:] == bytes(8) for d in deltas)
    projections = Counter(d[4:8] for d in deltas)
    assert projections == {bytes(4): 31, PATCH: 2}
    first_only = [d[:4] for d in deltas if d[4:8] == bytes(4)]
    mixed = [d for d in deltas if d[4:8] == PATCH]
    first_only.append(xor(mixed[0][:4], mixed[1][:4]))
    assert rank(first_only) == 32

    assert affine_member(xor(deltas[0], deltas[1]), deltas)
    assert not affine_member(bytes(8) + bytes.fromhex("0100000000000000"), deltas)

    rows = []
    for i, base in enumerate(bases):
        suffix_bits = sum((x ^ y).bit_count() for x, y in zip(base[8:], copied[8:]))
        assert all(x != y for x, y in zip(base[8:], copied[8:]))
        for patch in (bytes(4), PATCH):
            middle = xor(base[4:8], patch)
            nearest = copied[:4] + middle + base[8:]
            assert affine_member(xor(nearest, base), deltas)
            changed_bits = sum((x ^ y).bit_count() for x, y in zip(nearest, copied))
            changed_bytes = sum(x != y for x, y in zip(nearest, copied))
            rows.append((changed_bits, changed_bytes, suffix_bits, i, patch.hex(),
                         nearest.hex().upper(),
                         hashlib.sha256(nearest).hexdigest() == target_hash))

    mins = (min(x[0] for x in rows), min(x[1] for x in rows), min(x[2] for x in rows))
    assert mins == STAGES[stage][2], (stage, mins)
    assert sum(x[-1] for x in rows) == 0
    print("STAGE", stage, "modes", 16, "affine_dim", 33,
          "min_bit_errors", mins[0], "min_byte_errors", mins[1],
          "min_fixed_suffix_bits", mins[2], "nearest_sha256_hits", 0, flush=True)
    print("BIT_NEAREST", min(rows), flush=True)


def main():
    source = (ROOT / "resources/evidence/print/spool-reconstruction.log").read_bytes()
    assert hashlib.sha256(source).hexdigest() == SPOOL_HASH
    lines = re.findall(rb"PAYLOAD=([0-9A-F]{32})", source)
    assert len(lines) == 133
    copy = bytes.fromhex(lines[129].decode())
    assert copy.hex().upper() == "A9A9DC5731A5E2AE879C47215C2559D5"
    route = json.loads((ROOT / "resources/evidence/recovery-routing.json").read_text())
    mask = bytes.fromhex(route["K04"]["masked_component"])
    copied_component = xor(copy, mask)
    assert copied_component.hex().upper() == "2CFF149C50E54557228E7DE60B3EB7C9"
    target_hash = json.loads((ROOT / "resources/acceptance.json").read_text())["slot_sha256"]["K04"]
    assert target_hash == "930a52a1bab97ca2966332137c99e99298ea6182fb32ab63a3421dfb4fd8c9e0"

    with tempfile.TemporaryDirectory(prefix="h17-k02-copy-") as temp:
        for stage, (script, datafile, _) in STAGES.items():
            subprocess.run([sys.executable, str(ROOT / "agents/agent1" / script),
                            str(ROOT / "resources"), temp],
                           check=True, stdout=subprocess.DEVNULL)
            distances(stage, (Path(temp) / datafile).read_bytes(),
                      copied_component, target_hash)
    print("PASS: original data pinned; both affine-space exact distances verified", flush=True)


if __name__ == "__main__":
    main()
