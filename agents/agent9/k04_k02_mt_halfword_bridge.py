"""K04 / K02: source-only all-pair MT19937 three-halfword donor bridge.

Usage: python agents/agent9/k04_k02_mt_halfword_bridge.py source-archive.zip
Reads original spool, telemetry, and K02 route only. Disputed printer row129,
K04 mask, original slot commitments and K08 nonce are never inspected.
"""
import hashlib
import json
import random
import re
import struct
import sys
from datetime import datetime
from pathlib import Path
from zipfile import ZipFile

SPOOL_SHA = "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"
TELEMETRY_SHA = "3787dbd6bab3930ea5293c25a995175161a1c0d7683daad29f498026e057639f"
MASK32 = 0xFFFFFFFF


def undo_right(value, shift):
    result = value
    for _ in range(6):
        result = value ^ (result >> shift)
    return result & MASK32


def undo_left(value, shift, mask):
    result = value
    for _ in range(6):
        result = value ^ ((result << shift) & mask)
    return result & MASK32


def untemper(value):
    return undo_right(undo_left(undo_left(undo_right(value, 18),
                      15, 0xEFC60000), 7, 0x9D2C5680), 11)


def temper(value):
    value ^= value >> 11
    value ^= (value << 7) & 0x9D2C5680
    value ^= (value << 15) & 0xEFC60000
    value ^= value >> 18
    return value & MASK32


def inverse_twist(value):
    high = value >> 31
    result = (((value ^ (0x9908B0DF if high else 0)) << 1) | high) & MASK32
    assert (result >> 1) ^ (0x9908B0DF if result & 1 else 0) == value
    return result


def pair_words(middles, ends):
    mixed = [inverse_twist(a ^ b) for a, b in zip(middles, ends)]
    full = [(mixed[i] & 0x80000000) | (mixed[i-1] & 0x7FFFFFFF)
            for i in range(1, len(mixed))]
    return mixed, full


def main(path):
    gen = random.Random(12345678)
    synthetic = [gen.getrandbits(32) for _ in range(628)]
    states = [untemper(v) for v in synthetic]
    _, reconstructed = pair_words(states[397:401], states[624:628])
    assert reconstructed == states[1:4]
    assert [temper(x) >> 16 for x in reconstructed] == [v >> 16 for v in synthetic[1:4]]

    with ZipFile(path) as archive:
        spool = archive.read("evidence/print/spool-reconstruction.log")
        raw = archive.read("evidence/telemetry/freeze-export.jsonl")
        route = json.loads(archive.read("evidence/recovery-routing.json"))["K02"]
    assert hashlib.sha256(spool).hexdigest() == SPOOL_SHA
    assert hashlib.sha256(raw).hexdigest() == TELEMETRY_SHA
    rows = [list(map(untemper, struct.unpack("<4I", bytes.fromhex(h.decode()))))
            for h in re.findall(rb"PAYLOAD=([0-9A-F]{32})", spool)]
    assert len(rows) == 133
    rows[129] = []  # Selected disputed ACK2 withheld before any fit.
    start = datetime.fromisoformat(route["start_utc"])
    end = datetime.fromisoformat(route["end_utc_exclusive"])
    qualified = []
    for line in raw.decode().splitlines():
        item = json.loads(line)
        if (item["tag"], item["field"], item["quality"], item["state"]) != (
                "LT-204", "DIAG_WORD", "GOOD", "HOLD"):
            continue
        if start <= datetime.fromisoformat(item["ts"]) < end:
            qualified.append(item)
    chosen = [max((row for row in qualified if row["seq"] == seq),
                  key=lambda row: row["revision"])["value"] for seq in range(8)]
    assert chosen == [57765, 58484, 47831, 59475, 41704, 50973, 13079, 54535]
    versions = [("numeric", chosen),
                ("swapped", [(v >> 8) | ((v & 255) << 8) for v in chosen])]
    windows4 = windows3 = 0
    found = []
    for r in range(len(rows)):
        if not rows[r]:
            continue
        for q in range(r+1, len(rows)):
            if not rows[q]:
                continue
            _, full = pair_words(rows[r], rows[q])
            for field in ("upper16", "lower16"):
                observations = [((temper(x) >> 16) if field == "upper16"
                                 else (temper(x) & 0xFFFF)) for x in full]
                for order, values in versions:
                    for i in range(6):
                        windows4 += 1
                        if observations == values[i:i+3]:
                            found.append(("fourword", r, q, field, order, i))
            for offset_r, offset_q in ((0, 1), (1, 0), (1, 1)):
                mixes, two_full = pair_words(rows[r][offset_r:offset_r+3],
                                             rows[q][offset_q:offset_q+3])
                third = mixes[-1] & 0x7FFFFFFF
                possible = [third, third | 0x80000000]
                for field in ("upper16", "lower16"):
                    projection = lambda x: (temper(x) >> 16) if field == "upper16" else (temper(x) & 0xFFFF)
                    pair = [projection(x) for x in two_full]
                    final = {projection(x) for x in possible}
                    for order, values in versions:
                        for i in range(6):
                            windows3 += 1
                            if pair == values[i:i+2] and values[i+2] in final:
                                found.append(("threeword", r, q, offset_r, offset_q, field, order, i))
    assert (windows4, windows3) == (207504, 622512)
    print("synthetic_seeded_mt_positive", True)
    print("spool_sha256", SPOOL_SHA)
    print("telemetry_sha256", TELEMETRY_SHA)
    print("K02_original_raw_u16", " ".join(f"{v:04X}" for v in chosen))
    print("full_three_ancestor_assignments", windows4)
    print("two_full_plus_one_partial_assignments", windows3)
    print("original_three_output_matches", len(found))
    for witness in found:
        print("SOURCE_BRIDGE", witness)
    print("selected_K04_row129_withheld", True)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("usage: python k04_k02_mt_halfword_bridge.py original.zip")
    main(Path(sys.argv[1]))
