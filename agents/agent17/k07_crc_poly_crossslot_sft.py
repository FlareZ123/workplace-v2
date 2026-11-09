"""Probe complete historical AX-7782 checkpoint / REC8-slot CRC16 models.

Python 3 standard-library only. Never modifies original evidence or candidate.
"""
import hashlib
import itertools
import json
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2] / "resources"
KNOWN = {
    1: "049AAB2E1CDE7A82CD7C60234303C91A",
    2: "0D7E3AB56FB75DA3EB0E2E06786D239E",
    3: "1384AF96E25D6ADA666209CB55E062FA",
    5: "FF8B78200A56E8586DCDA00EF01E4572",
    6: "5DBF40EE52FAAED9A536D3326CF0D95A",
    7: "93495F5E425AB8E592123DABAEB68545",
}
SLOTS = tuple(KNOWN)
BIT_REVERSE = bytes(int(f"{i:08b}"[::-1], 2) for i in range(256))


def crc16(data: bytes, poly: int, reflect: bool) -> int:
    state = 0
    for byte in data:
        state ^= byte if reflect else byte << 8
        for _ in range(8):
            if reflect:
                state = (state >> 1) ^ (poly if state & 1 else 0)
            else:
                state = ((state << 1) ^ (poly if state & 0x8000 else 0)) & 65535
    return state


def index(slot: int, phase: int, reverse: bool) -> int:
    return (phase - slot + 1 if reverse else phase + slot - 1) % 8


def load_original():
    path = ROOT / "evidence/transfers/transfer-audit.jsonl"
    assert hashlib.sha256(path.read_bytes()).hexdigest() == "32970ad4431a9d610cc12dcca2813f39dd8fd2e396f9e748dc94b5932cb69adf"
    records = [json.loads(x) for x in path.read_text().splitlines()]
    receipt = [r for r in records if r["kind"] == "COMMIT" and r["transfer"] == "AX-7782"]
    assert len(receipt) == 1 and receipt[0]["dry_run"] is False and receipt[0]["chunks"] == 8
    chosen = {}
    for r in records:
        if r["kind"] == "CHUNK" and r["transfer"] == "AX-7782":
            k = r["seq"]
            if k not in chosen or r["attempt"] > chosen[k]["attempt"]:
                chosen[k] = r
    assert sorted(chosen) == list(range(8)) and all(chosen[k]["attempt"] == 2 for k in range(8))
    assert "".join(chosen[k]["checkpoint"] for k in range(8)) == "8947CEDCB9CC73BAB7E87BE63302C5C9"
    return tuple(int(chosen[k]["checkpoint"], 16) for k in range(8))


def search(checkpoints, only_poly=None):
    hits, first_pair_gates = [], 0
    for backwards in (False, True):
        for bitflip in (False, True):
            sources = {}
            for k, raw in KNOWN.items():
                value = bytes.fromhex(raw)
                value = value[::-1] if backwards else value
                sources[k] = value.translate(BIT_REVERSE) if bitflip else value
            for reflected in (False, True):
                expected = defaultdict(list)
                for phase in range(8):
                    for reverse in (False, True):
                        for swapped in (False, True):
                            values = tuple(checkpoints[index(slot, phase, reverse)] for slot in SLOTS)
                            if swapped:
                                values = tuple(((v & 255) << 8) | (v >> 8) for v in values)
                            expected[values[0] ^ values[1]].append((phase, reverse, swapped, values))
                for poly in ([only_poly] if only_poly is not None else range(1, 65536)):
                    first = crc16(sources[1], poly, reflected)
                    second = crc16(sources[2], poly, reflected)
                    potential = expected.get(first ^ second, ())
                    if not potential:
                        continue
                    first_pair_gates += len(potential)
                    rest = tuple(crc16(sources[k], poly, reflected) for k in SLOTS[2:])
                    for phase, reverse, swapped, values in potential:
                        offset = first ^ values[0]
                        if all((c ^ offset) == v for c, v in zip(rest, values[2:])):
                            hits.append((poly, backwards, bitflip, reflected, phase, reverse, swapped, offset))
    return first_pair_gates, hits


def main():
    checks = json.loads((ROOT / "acceptance.json").read_text())["slot_sha256"]
    assert all(hashlib.sha256(bytes.fromhex(value)).hexdigest() == checks[f"K{slot:02d}"] for slot, value in KNOWN.items())
    original = load_original()
    initial = dict(KNOWN)
    # Original selected pre-reducer source bytes for the three hashed accepted slots.
    source_raw = {
        2: bytes.fromhex("E1A5E474BAD7E853A2E8C71D3317D507"),
        3: b"SG-D7DAD6BC|SG-9714519B|SG-7DAD0AD4|SG-BE8E87FD",
        7: bytes.fromhex("8947CEDCB9CC73BAB7E87BE63302C5C9"),
    }
    assert all(hashlib.sha256(raw).digest()[:16].hex().upper() == KNOWN[slot] for slot, raw in source_raw.items())
    # A planted real CRC16 publisher: all six source values are generated
    # with one polynomial and a shared sixteen-bit pad and mapped into eight checkpoints.
    poly, phase, offset = 0x1021, 3, 0xA537
    planted = [0x8111 + k for k in range(8)]
    for slot, value in KNOWN.items():
        code = crc16(bytes.fromhex(value)[::-1], poly, False) ^ offset
        planted[index(slot, phase, True)] = ((code & 255) << 8) | (code >> 8)
    _, planted_hits = search(tuple(planted), poly)
    assert (poly, True, False, False, phase, True, True, offset) in planted_hits
    print("Original six acceptance controls: 6/6 PASS")
    print("Original eight AX-7782 checkpoints:", "".join(f"{v:04X}" for v in original))
    print("Synthetic original-shaped six-slot CRC16 generator: PASS")
    print("Model layouts per view: 65,535 CRC taps x 2 bit directions x 4 byte-bit layouts x 16 slot placements x 2 checkpoint byte orders")
    for use_raw in itertools.product((False, True), repeat=3):
        for use, slot in zip(use_raw, (2, 3, 7)):
            KNOWN[slot] = source_raw[slot].hex().upper() if use else initial[slot]
        gates, survivors = search(original)
        print("Original K02/K03/K07 prehash views:", use_raw,
              "two-control gates:", gates, "all-six-control survivors:", len(survivors), flush=True)
        for hit in survivors:
            print("SURVIVING ORIGINAL MODEL", hit)
    KNOWN.update(initial)


if __name__ == "__main__":
    main()
