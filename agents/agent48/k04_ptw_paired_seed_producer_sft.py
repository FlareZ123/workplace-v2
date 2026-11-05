"""Original-source PTW/PS same-ID CPython MT seed-emitter test for H-17.

Only original serial/job pairs 390..416 are fitted. Disputed 0417 ACK2
physical coupon is never used as an input or source-control value.
"""
from __future__ import annotations
import hashlib
import itertools
import json
import random
import re
import sys
from collections import deque
from pathlib import Path

SEAL_SHA = "c00944558636fbcc7e91b81e8e838ffd13fcd5a30d121b41951888766a8a0e32"
SPOOL_SHA = "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"
MAX_WARMUP = 65535

def checked(path: Path, digest: str) -> str:
    raw = path.read_bytes()
    assert hashlib.sha256(raw).hexdigest() == digest, str(path)
    return raw.decode("utf-8")

def sources(root: Path) -> list[tuple[int, str, bytes]]:
    evidence = root / "evidence"
    seals = [json.loads(x) for x in checked(evidence / "maintenance" / "seal-receipts.jsonl", SEAL_SHA).splitlines()]
    pairs: dict[int, str] = {}
    for row in seals:
        num = int(row["permit"].rsplit("-", 1)[1])
        if 390 <= num <= 416:
            assert num not in pairs
            assert row["state"] == "CLOSED" and row["fitment"] == "AS_LEFT" and row["signed"] is True
            pairs[num] = row["serial"]
    assert len(pairs) == 27
    spool: dict[int, bytes] = {}
    for line in checked(evidence / "print" / "spool-reconstruction.log", SPOOL_SHA).splitlines()[1:]:
        m = re.search(r"\bJOB=PS-261003-(\d+)\b.*?\bPAYLOAD=([0-9A-F]{32})\b", line)
        assert m, line
        num = int(m.group(1))
        if 390 <= num <= 416:
            assert num not in spool
            assert "ATTEMPT=1 STATE=ACK" in line
            spool[num] = bytes.fromhex(m.group(2))
    assert len(spool) == 27
    return [(n, pairs[n], spool[n]) for n in sorted(pairs)]

def seed_forms(num: int, serial: str) -> list[tuple[str, int | bytes | str]]:
    assert re.fullmatch(r"SG-[0-9A-F]{8}", serial)
    raw = bytes.fromhex(serial[3:])
    return [
        ("int_be", int.from_bytes(raw, "big")),
        ("int_le", int.from_bytes(raw, "little")),
        ("binary", raw),
        ("hex_text", serial[3:]),
        ("full_text", serial),
        ("record_text", f"PTW-{num}|{serial}"),
    ]

def serialized_words(packet: bytes) -> set[tuple[int, int, int, int]]:
    assert len(packet) == 16
    out: set[tuple[int, int, int, int]] = set()
    for endian in ("little", "big"):
        words = tuple(int.from_bytes(packet[i:i + 4], endian) for i in range(0, 16, 4))
        out.add(words)
        out.add(words[::-1])
    return out

def scan(seed: int | bytes | str, packet: bytes, max_warmup: int) -> tuple[int, list[tuple[int, tuple[int, ...]]]]:
    candidates = serialized_words(packet)
    last_words = {p[3] for p in candidates}
    tail: deque[int] = deque(maxlen=4)
    gate_matches = 0
    whole_matches: list[tuple[int, tuple[int, ...]]] = []
    rng = random.Random(seed)
    for t in range(max_warmup + 4):
        word = rng.getrandbits(32)
        tail.append(word)
        if t < 3 or word not in last_words:
            continue
        gate_matches += 1
        if tuple(tail) in candidates:
            offset = t - 3
            if offset <= max_warmup:
                whole_matches.append((offset, tuple(tail)))
    return gate_matches, whole_matches

def synthetic() -> None:
    packet_num = 402
    serial = "SG-89ABCDEF"
    for label, seed in seed_forms(packet_num, serial):
        rng = random.Random(seed)
        start = 1234
        for _ in range(start):
            rng.getrandbits(32)
        words = [rng.getrandbits(32) for _ in range(4)]
        if label == "int_le":
            words.reverse()
        packet = b"".join(w.to_bytes(4, "big" if label == "hex_text" else "little") for w in words)
        gates, matches = scan(seed, packet, start + 12)
        assert gates >= 1 and any(index == start for index, _ in matches), (label, gates, matches)
    print("PLANTED_CHECKS all_6_seed_forms_match_full_packet_at_known_offset=1234 PASS")

def selected_ptw417_seeds(root: Path) -> list[tuple[str, int | bytes | str]]:
    text = checked(root / "evidence" / "maintenance" / "seal-receipts.jsonl", SEAL_SHA)
    selected: dict[str, dict] = {}
    for line in text.splitlines():
        row = json.loads(line)
        if row["permit"] != "PTW-417" or row["state"] != "CLOSED" or row["fitment"] != "AS_LEFT" or row["signed"] is not True:
            continue
        if row["bay"] not in selected or row["revision"] > selected[row["bay"]]["revision"]:
            selected[row["bay"]] = row
    assert set(selected) == set("ABCD")
    serials = [selected[bay]["serial"] for bay in "BDAC"]
    assert [x[3:] for x in serials] == ["D7DAD6BC", "9714519B", "7DAD0AD4", "BE8E87FD"]
    out: list[tuple[str, int | bytes | str]] = []
    for order in itertools.permutations(range(4)):
        raw = b"".join(bytes.fromhex(serials[i][3:]) for i in order)
        joined = "|".join(serials[i] for i in order)
        tag = "".join(str(i) for i in order)
        out.extend([
            (f"raw_{tag}_binary", raw),
            (f"raw_{tag}_intbig", int.from_bytes(raw, "big")),
            (f"raw_{tag}_intlittle", int.from_bytes(raw, "little")),
            (f"text_{tag}", joined),
        ])
    assert len(out) == 96
    return out

def global_seed_gate(root: Path, first_packet: bytes) -> None:
    seeds = selected_ptw417_seeds(root)
    total_gate = 0
    whole = 0
    details: list[tuple[str, int, int]] = []
    for label, seed in seeds:
        gates, matches = scan(seed, first_packet, MAX_WARMUP)
        total_gate += gates
        whole += len(matches)
        if gates or matches:
            details.append((label, gates, len(matches)))
    print("GLOBAL_PT417_SOURCE_SEED original_selected_permutation_seed_forms=", len(seeds))
    print("GLOBAL_PT417_SOURCE_SEED complete_4word_windows=", len(seeds) * (MAX_WARMUP + 1))
    print("GLOBAL_PT417_SOURCE_SEED gate_hits=", total_gate, "whole_matches=", whole, "details=", details)
    assert whole == 0, "Original source PRNG model matches; investigate target"

def main(root: Path) -> None:
    synthetic()
    pairs = sources(root)
    gate_total = 0
    whole_total = 0
    exceptions: list[tuple[int, str, int, int]] = []
    for num, serial, packet in pairs:
        for label, seed in seed_forms(num, serial):
            gates, matches = scan(seed, packet, MAX_WARMUP)
            gate_total += gates
            whole_total += len(matches)
            if gates or matches:
                exceptions.append((num, label, gates, len(matches)))
    print("ORIGINAL source_pairs=27 forms_per_pair=6 warmup_offsets_per_form=65536")
    print("ORIGINAL total_complete_4word_windows=", len(pairs) * 6 * (MAX_WARMUP + 1))
    print("ORIGINAL gate_hits=", gate_total, "complete_source_matches=", whole_total)
    print("ORIGINAL gate_details=", exceptions)
    assert whole_total == 0, "New historical source emitter match, investigate K04 immediately"
    first = checked(root / "evidence" / "print" / "spool-reconstruction.log", SPOOL_SHA).splitlines()[1]
    first_packet = bytes.fromhex(re.search(r"\bPAYLOAD=([0-9A-F]{32})\b", first).group(1))
    assert first_packet.hex().upper() == "FBBBC54356483F5864BB3F06794518A5"
    global_seed_gate(root, first_packet)
    print("ORIGINAL K04_candidates=0 source-only printer/permit emitter veto. K04 and K08 unresolved")

if __name__ == "__main__":
    main(Path(sys.argv[1]) if len(sys.argv) > 1 else Path("resources"))
