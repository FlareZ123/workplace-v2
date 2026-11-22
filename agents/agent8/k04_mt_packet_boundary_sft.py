"""H-17 source-pinned MT interpacket-boundary witnesses and complete K04 checks.

Run from the repository checkout with:
    python agents/agent8/k04_mt_packet_boundary_sft.py

The disputed selected ACK2 PAYLOAD is never decoded or inspected. This tests
an exploratory cross-packet four-word continuation hypothesis, not a
historically authenticated printer stage schedule.
"""
from __future__ import annotations

from collections import defaultdict
from hashlib import sha256
from itertools import product
from pathlib import Path
import json
import random
import re

ROOT = Path(__file__).resolve().parents[2]
LOG = ROOT / "resources/evidence/print/spool-reconstruction.log"
ROUTE = ROOT / "resources/evidence/recovery-routing.json"
ACCEPT = ROOT / "resources/acceptance.json"
MASK32 = (1 << 32) - 1


def untemper(v: int) -> int:
    x = v ^ (v >> 18)
    y = x
    x = y ^ ((y << 15) & 0xEFC60000)
    y = x
    for _ in range(6):
        x = y ^ ((x << 7) & 0x9D2C5680)
    y = x
    for _ in range(4):
        x = y ^ (x >> 11)
    return x & MASK32


def temper(v: int) -> int:
    v ^= v >> 11
    v ^= (v << 7) & 0x9D2C5680
    v ^= (v << 15) & 0xEFC60000
    v ^= v >> 18
    return v & MASK32


def twist(left: int, right: int) -> int:
    x = (left & 0x80000000) | (right & 0x7FFFFFFF)
    return (x >> 1) ^ (0x9908B0DF if x & 1 else 0)


def source_words(packets: list[bytes | None], endian: str, reverse: bool) -> list[list[int] | None]:
    words = []
    for packet in packets:
        if packet is None:
            words.append(None)
            continue
        row = [untemper(int.from_bytes(packet[i:i+4], endian)) for i in (0, 4, 8, 12)]
        if reverse:
            row.reverse()
        words.append(row)
    return words


def find_witnesses(words: list[list[int] | None]) -> tuple[list[tuple[int, ...]], list[tuple[int, ...]]]:
    positions = defaultdict(list)
    for l, row in enumerate(words):
        if row is not None:
            for q, w in enumerate(row):
                positions[w].append((l, q))
    intra, boundary = [], []
    for r, row in enumerate(words):
        if row is None:
            continue
        for p in range(1, 4):
            t = twist(row[p-1], row[p])
            for k in range(r+1, len(words)):
                if words[k] is None:
                    continue
                for i, w in enumerate(words[k]):
                    for l, q in positions.get(t ^ w, ()):
                        if l > k:
                            intra.append((r, k, l, p, i, q))
        if r+1 == len(words) or words[r+1] is None:
            continue
        t = twist(row[3], words[r+1][0])
        for k in range(r+2, len(words)):
            if words[k] is None:
                continue
            for i, w in enumerate(words[k]):
                for l, q in positions.get(t ^ w, ()):
                    if l > k:
                        boundary.append((r, k, l, i, q))
    return intra, boundary


def test():
    raw = LOG.read_bytes()
    assert sha256(raw).hexdigest() == "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"
    lines = re.findall(rb"^(\S+) JOB=(\S+) ATTEMPT=(\d+) STATE=(\w+) CLASS=(\w+) PAYLOAD=([0-9A-F]{32}) DEST=(\w+)$", raw, re.M)
    assert len(lines) == 133
    assert lines[129][1:5] == (b"PS-261003-0417", b"2", b"ACK", b"RECOVER")
    packets = [bytes.fromhex(x[5].decode()) if i != 129 else None for i, x in enumerate(lines)]
    route = json.loads(ROUTE.read_bytes())
    accept = json.loads(ACCEPT.read_bytes())
    mask = bytes.fromhex(route["K04"]["masked_component"])
    target = accept["slot_sha256"]["K04"]

    rng = random.Random(0x17A11CE)
    outputs = [rng.getrandbits(32) for _ in range(1250)]
    assert all(temper(untemper(v)) == v for v in outputs)
    for q in range(4):
        actual = temper(untemper(outputs[397+q]) ^ twist(untemper(outputs[q]), untemper(outputs[q+1])))
        assert actual == outputs[624+q]

    full_counts = {}
    for endian in ("little", "big"):
        for reversed_words in (False, True):
            view = f"{endian}_{'reverse' if reversed_words else 'forward'}"
            _, inter = find_witnesses(source_words(packets, endian, reversed_words))
            full_counts[view] = len(inter)
    assert full_counts == {"little_forward": 6, "little_reverse": 2,
                           "big_forward": 0, "big_reverse": 0}, full_counts

    words = source_words(packets, "little", False)
    intra, boundary = find_witnesses(words)
    assert len(intra) == 25 and len(boundary) == 6
    assert boundary == [(3,57,87,3,3), (12,67,97,1,2), (13,68,98,1,3),
                        (33,86,116,2,3), (40,94,125,2,0), (43,97,130,2,3)]
    lane_legacy, lane_new = defaultdict(set), defaultdict(set)
    for r,k,l,p,i,q in intra:
        rr, kk = 129 - (l-r), 129 - (l-r) + (k-r)
        if 0 <= rr < kk < 129:
            lane_legacy[q].add(temper(words[kk][i] ^ twist(words[rr][p-1], words[rr][p])))
    for r,k,l,i,q in boundary:
        rr, kk = 129 - (l-r), 129 - (l-r) + (k-r)
        if 0 <= rr < kk < 129 and rr+1 != 129:
            lane_new[q].add(temper(words[kk][i] ^ twist(words[rr][3], words[rr+1][0])))
    assert [len(lane_legacy[q]) for q in range(4)] == [4, 5, 6, 8]
    assert [len(lane_new[q]) for q in range(4)] == [1, 0, 1, 4]

    counts = {}
    for name, lanes in (("legacy", lane_legacy),
                        ("with_boundary", {q: lane_legacy[q] | lane_new[q] for q in range(4)})):
        count = hits = 0
        planted_digest = None
        planted_hits = 0
        for four in product(*(sorted(lanes[q]) for q in range(4))):
            payload = b"".join(x.to_bytes(4, "little") for x in four)
            coupon = bytes(a ^ b for a,b in zip(payload, mask))
            digest = sha256(coupon).hexdigest()
            if planted_digest is None:
                planted_digest = digest
            planted_hits += digest == planted_digest
            hits += digest == target
            count += 1
        assert hits == 0 and planted_hits >= 1
        counts[name] = count
    assert counts == {"legacy": 960, "with_boundary": 2100}, counts
    # Exhaust complete two-donor native MT constructions at every source
    # ordered row-pair, beyond the historical witness-selected row geometries.
    # The selected row's PAYLOAD remains withheld throughout.
    allpair_counts = {"within_packet_plus_unknown_msb": 0,
                      "adjacent_packets_zero_hidden": 0}
    allpair_hits = 0
    for endian in ("little", "big"):
        for reversed_words in (False, True):
            view_rows = source_words(packets, endian, reversed_words)
            for r in range(129):
                R = view_rows[r]
                if R is None:
                    continue
                for k in range(r+1, 129):
                    K = view_rows[k]
                    if K is None:
                        continue
                    for prev_msb in (0, 0x80000000):
                        out = [temper(K[j] ^ twist(R[j-1] if j else prev_msb, R[j]))
                               for j in range(4)]
                        if reversed_words:
                            out.reverse()
                        raw_coupon = b"".join(w.to_bytes(4, endian) for w in out)
                        masked = bytes(a ^ b for a,b in zip(raw_coupon, mask))
                        allpair_hits += sha256(masked).hexdigest() == target
                        allpair_counts["within_packet_plus_unknown_msb"] += 1
                    if k <= r+1 or view_rows[r+1] is None:
                        continue
                    eight = R + view_rows[r+1]
                    for offset in range(4):
                        five = eight[offset:offset+5]
                        out = [temper(K[j] ^ twist(five[j], five[j+1]))
                               for j in range(4)]
                        if reversed_words:
                            out.reverse()
                        raw_coupon = b"".join(w.to_bytes(4, endian) for w in out)
                        masked = bytes(a ^ b for a,b in zip(raw_coupon, mask))
                        allpair_hits += sha256(masked).hexdigest() == target
                        allpair_counts["adjacent_packets_zero_hidden"] += 1
    assert allpair_counts == {"within_packet_plus_unknown_msb": 66048,
                              "adjacent_packets_zero_hidden": 130048}
    assert allpair_hits == 0
    print("EXHAUSTIVE_ORIGINAL_TWO_DONOR", json.dumps({"counts": allpair_counts,
          "original_k04_hits": allpair_hits, "total": sum(allpair_counts.values())}))

    print(json.dumps({"historical_intra": len(intra), "historical_boundary": len(boundary),
                      "boundary_views": full_counts, "boundary_source_tuples": boundary,
                      "selected_complete_candidates": counts, "original_k04_hits": 0,
                      "seeded_mt_positive": True}, indent=2))


if __name__ == "__main__":
    test()
