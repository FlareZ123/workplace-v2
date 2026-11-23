#!/usr/bin/env python3
"""H-17 K04: all-42 alternative-MT complete-output stages, exact source comparison.

One runnable, standard-library-only source-pinned test. Use:
    python agents/agent10/k04_all42_wholewindow_sft.py [resources-directory]

The selected PS-0417 attempt-2 ACK copy is excluded before PAYLOAD decoding.
The historical printer producer and selected output stage remain unverified.
"""
from __future__ import annotations

import hashlib
import json
import re
import sys
from collections import Counter
from pathlib import Path

SPOOL_SHA = "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"
K04_SHA = "930a52a1bab97ca2966332137c99e99298ea6182fb32ab63a3421dfb4fd8c9e0"
MAG = 0x9908B0DF
U32 = 0xFFFFFFFF
SCAN_END = 2096
ALT_STAGES = (0, 10, 14, 23, 32, 43, 47, 54, 67, 80, 84, 92, 99, 110, 119, 124, 130, 134, 138, 151, 155, 160, 167, 177, 182, 189, 195, 204, 211, 215, 224, 230, 237, 242, 251, 258, 263, 275, 288, 297, 305, 311, 318, 328, 337, 345, 350, 360, 366, 370, 378, 385, 389, 394, 402, 411, 417, 425, 430, 434, 445, 458, 463, 472, 481, 489, 495, 505, 514, 520, 532, 537, 542, 548, 558, 565, 572, 581, 592, 596, 604, 613, 617, 624, 632, 641, 645, 652, 662, 666, 677, 682, 689, 696, 705, 714, 721, 731, 739, 745, 751, 755, 767, 771, 779, 784, 792, 796, 804, 811, 822, 833, 842, 846, 853, 861, 871, 877, 885, 891, 903, 909, 914, 921, 927, 934, 940, 947, 951, 952, 957, 961, 966)
P951_STAGES = (0, 7, 16, 22, 30, 37, 45, 54, 64, 72, 80, 88, 95, 108, 116, 122, 130, 136, 142, 148, 154, 164, 170, 176, 182, 188, 194, 203, 209, 218, 224, 230, 237, 244, 250, 257, 265, 272, 284, 294, 301, 307, 314, 324, 335, 342, 348, 354, 360, 366, 372, 378, 384, 394, 401, 408, 416, 423, 429, 435, 446, 454, 460, 470, 477, 485, 491, 503, 511, 518, 524, 531, 539, 556, 562, 568, 576, 582, 588, 595, 602, 608, 617, 624, 632, 638, 644, 650, 658, 666, 672, 678, 686, 693, 701, 710, 717, 729, 736, 743, 755, 762, 770, 776, 782, 788, 795, 801, 813, 819, 825, 831, 837, 846, 853, 861, 870, 876, 884, 891, 899, 905, 912, 918, 924, 930, 936, 942, 947, 951, 955, 959, 963)


def untemper(value: int) -> int:
    for shift, left, mask in ((18, False, U32), (15, True, 0xEFC60000),
                              (7, True, 0x9D2C5680), (11, False, U32)):
        previous = value
        for _ in range(6):
            value = previous ^ (((value << shift) & mask) if left else (value >> shift))
        value &= U32
    return value


def temper(value: int) -> int:
    value ^= value >> 11
    value ^= (value << 7) & 0x9D2C5680
    value ^= (value << 15) & 0xEFC60000
    return (value ^ (value >> 18)) & U32


def symbolic_words(origin: int, exclusive_end: int) -> list[list[int]]:
    assert origin <= 0 and exclusive_end > 624 + origin
    words = [[1 << (32 * i + bit) for bit in range(32)] for i in range(624)]
    for t in range(624, exclusive_end - origin):
        first, second, future = words[t - 624], words[t - 623], words[t - 227]
        words.append([
            future[bit]
            ^ (first[31] if bit == 30 else second[bit + 1] if bit < 30 else 0)
            ^ (second[0] if MAG & (1 << bit) else 0)
            for bit in range(32)
        ])
    return words


def insert_reduce(form: int, rhs: int, basis: dict[int, tuple[int, int]]) -> tuple[int, int]:
    while form:
        known = basis.get(form.bit_length() - 1)
        if known is None:
            break
        old_form, old_rhs = known
        form ^= old_form
        rhs ^= old_rhs
    return form, rhs


def project(form: int, basis: dict[int, tuple[int, int]]) -> tuple[int, int]:
    """Return independent free-bit expression and its observed source parity."""
    free = constant = 0
    while form:
        pivot = form.bit_length() - 1
        known = basis.get(pivot)
        if known is None:
            free ^= 1 << pivot
            form ^= 1 << pivot
        else:
            old_form, rhs = known
            form ^= old_form
            constant ^= rhs
    return free, constant


def build_basis(native: list[tuple[int, ...] | None],
                stages: tuple[int, ...], symbols: list[list[int]], origin: int):
    basis: dict[int, tuple[int, int]] = {}
    for row, packet in enumerate(native):
        if packet is None:
            continue
        for lane, value in enumerate(packet):
            for bit, form in enumerate(symbols[stages[row] + lane - origin]):
                form, rhs = insert_reduce(form, (value >> bit) & 1, basis)
                if form:
                    basis[form.bit_length() - 1] = (form, rhs)
                else:
                    assert rhs == 0, ("contradictory original source", row, lane, bit)
    return basis


def enumerate_windows(symbols: list[list[int]], basis: dict[int, tuple[int, int]],
                      origin: int, max_rank: int):
    projected = [
        [project(form, basis) for form in symbols[q - origin]]
        for q in range(SCAN_END + 4)
    ]
    count = Counter()
    candidates: dict[bytes, tuple[int, int]] = {}
    at_start: dict[int, list[bytes]] = {}
    for q in range(SCAN_END + 1):
        sequence = [bit for stage in projected[q:q + 4] for bit in stage]
        local: dict[int, tuple[int, int]] = {}
        for form, _ in sequence:
            while form:
                pivot = form.bit_length() - 1
                if pivot not in local:
                    local[pivot] = (form, 1 << len(local))
                    break
                form ^= local[pivot][0]
            if len(local) > max_rank:
                break
        rank = len(local)
        if rank > max_rank:
            continue
        count[rank] += 1
        coordinates = []
        for form, rhs in sequence:
            combo = 0
            while form:
                old_form, coord = local[form.bit_length() - 1]
                form ^= old_form
                combo ^= coord
            coordinates.append((combo, rhs))
        at_start[q] = []
        for assignment in range(1 << rank):
            values = [0, 0, 0, 0]
            for bit_index, (combo, rhs) in enumerate(coordinates):
                bit = rhs ^ ((combo & assignment).bit_count() & 1)
                values[bit_index // 32] |= bit << (bit_index % 32)
            coupon = b"".join(temper(v).to_bytes(4, "little") for v in values)
            assert coupon not in candidates, ("duplicate coupon", q)
            candidates[coupon] = (q, assignment)
            at_start[q].append(coupon)
    return count, candidates, at_start


def main() -> None:
    resources = Path(sys.argv[1]) if len(sys.argv) == 2 else Path(__file__).resolve().parents[2] / "resources"
    spool = (resources / "evidence/print/spool-reconstruction.log").read_bytes()
    assert hashlib.sha256(spool).hexdigest() == SPOOL_SHA
    rows = re.findall(
        rb"^(\S+) JOB=(\S+) ATTEMPT=(\d+) STATE=(\w+) CLASS=(\w+) PAYLOAD=([0-9A-F]{32}) DEST=(\w+)$",
        spool, re.M,
    )
    assert len(rows) == len(ALT_STAGES) == len(P951_STAGES) == 133
    assert rows[129][:5] == (
        b"2026-10-03T18:02:00Z", b"PS-261003-0417", b"2", b"ACK", b"RECOVER"
    )
    native = [
        None if row == 129 else tuple(
            untemper(int.from_bytes(bytes.fromhex(record[5].decode())[4 * lane:4 * lane + 4], "little"))
            for lane in range(4)
        )
        for row, record in enumerate(rows)
    ]
    assert native[129] is None

    route = json.loads((resources / "evidence/recovery-routing.json").read_text())
    acceptance = json.loads((resources / "acceptance.json").read_text())
    mask = bytes.fromhex(route["K04"]["masked_component"])
    target = acceptance["slot_sha256"]["K04"]
    assert len(mask) == 16 and target == K04_SHA

    def final_component(packet: bytes) -> bytes:
        return bytes(x ^ y for x, y in zip(packet, mask))

    alternate_forms = symbolic_words(0, SCAN_END + 4)
    alternate_basis = build_basis(native, ALT_STAGES, alternate_forms, 0)
    assert len(alternate_basis) == 15434
    count, candidates, at_start = enumerate_windows(alternate_forms, alternate_basis, 0, 2)
    assert (count[0], count[1], count[2], len(candidates)) == (329, 59, 10, 487)

    earlier_forms = symbolic_words(-1100, SCAN_END + 4)
    earlier_basis = build_basis(native, P951_STAGES, earlier_forms, -1100)
    assert len(earlier_basis) == 15365
    earlier_count, earlier_candidates, _ = enumerate_windows(earlier_forms, earlier_basis, -1100, 1)
    assert (earlier_count[0], earlier_count[1], len(earlier_candidates)) == (268, 97, 462)

    overlap = set(candidates) & set(earlier_candidates)
    fresh = set(candidates) - set(earlier_candidates)
    intact = {bytes.fromhex(r[5].decode()) for i, r in enumerate(rows) if i != 129}
    assert (len(overlap), len(fresh), len(fresh & intact)) == (201, 286, 0)

    planted = bytes.fromhex("66542E68E5C1B1413E78814A64EC32B0")
    assert at_start[1025][3] == planted and len(at_start[1025]) == 4
    planted_digest = hashlib.sha256(final_component(planted)).digest()
    planted_hits = 0
    original_hits = []
    for packet, (q, branch) in candidates.items():
        digest = hashlib.sha256(final_component(packet)).digest()
        planted_hits += digest == planted_digest
        if digest.hex() == K04_SHA:
            original_hits.append({"stage": q, "branch": branch, "component": final_component(packet).hex().upper()})
    assert planted_hits == 1
    assert not original_hits, "An actual original K04 commitment hit requires immediate review"
    print(json.dumps({
        "selected_payload_loaded": False,
        "original_spool_sha256": SPOOL_SHA,
        "all42_source_rank": len(alternate_basis),
        "alt_rank0_rank1_rank2_windows": [count[0], count[1], count[2]],
        "alt_complete_candidate_components": len(candidates),
        "p951_previously_screened_complete_components": len(earlier_candidates),
        "cross_model_identical": len(overlap),
        "genuinely_additional_full_components": len(fresh),
        "additional_equal_to_retained_intact_packet": len(fresh & intact),
        "source_derived_rank2_planted_positive": planted_hits == 1,
        "original_k04_commitment_matches": original_hits
    }, indent=2))


if __name__ == "__main__":
    main()
