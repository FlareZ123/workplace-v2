"""Alternative all-42 native MT19937 chronology, exact source consistency.

Original selected ACK2 PAYLOAD is withheld before hexadecimal decoding.
This is a conditional stage assignment, not authenticated printer firmware.
"""
from __future__ import annotations

import hashlib
import json
import re
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE_SHA = "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"
U, MAG = 0xFFFFFFFF, 0x9908B0DF
STAGES = (0, 10, 14, 23, 32, 43, 47, 54, 67, 80, 84, 92, 99, 110, 119, 124, 130,
 134, 138, 151, 155, 160, 167, 177, 182, 189, 195, 204, 211, 215, 224, 230,
 237, 242, 251, 258, 263, 275, 288, 297, 305, 311, 318, 328, 337, 345, 350,
 360, 366, 370, 378, 385, 389, 394, 402, 411, 417, 425, 430, 434, 445, 458,
 463, 472, 481, 489, 495, 505, 514, 520, 532, 537, 542, 548, 558, 565, 572,
 581, 592, 596, 604, 613, 617, 624, 632, 641, 645, 652, 662, 666, 677, 682,
 689, 696, 705, 714, 721, 731, 739, 745, 751, 755, 767, 771, 779, 784, 792,
 796, 804, 811, 822, 833, 842, 846, 853, 861, 871, 877, 885, 891, 903, 909,
 914, 921, 927, 934, 940, 947, 951, 952, 957, 961, 966)


def untemper(value: int) -> int:
    for shift, left, mask in ((18, False, U), (15, True, 0xEFC60000),
                               (7, True, 0x9D2C5680), (11, False, U)):
        first = value
        for _ in range(6):
            value = first ^ (((value << shift) & mask) if left else (value >> shift))
        value &= U
    return value


def twist(a: int, b: int) -> int:
    joined = (a & 0x80000000) | (b & 0x7FFFFFFF)
    return (joined >> 1) ^ (MAG if joined & 1 else 0)


def symbolic_words(count: int) -> list[list[int]]:
    words = [[1 << (32 * i + bit) for bit in range(32)] for i in range(624)]
    for t in range(624, count):
        a, b, c = words[t - 624], words[t - 623], words[t - 227]
        words.append([
            c[bit] ^ (a[31] if bit == 30 else (b[bit + 1] if bit < 30 else 0))
            ^ (b[0] if MAG & (1 << bit) else 0)
            for bit in range(32)
        ])
    return words


def main() -> None:
    spool = (ROOT / "resources/evidence/print/spool-reconstruction.log").read_bytes()
    assert hashlib.sha256(spool).hexdigest() == SOURCE_SHA
    rows = re.findall(
        rb"^(\S+) JOB=(\S+) ATTEMPT=(\d+) STATE=(\w+) CLASS=(\w+) PAYLOAD=([0-9A-F]{32}) DEST=(\w+)$",
        spool, re.M,
    )
    assert len(rows) == len(STAGES) == 133
    assert rows[129][:5] == (
        b"2026-10-03T18:02:00Z", b"PS-261003-0417", b"2", b"ACK", b"RECOVER"
    )
    native = [None if r == 129 else [
        untemper(int.from_bytes(bytes.fromhex(row[5].decode())[i:i+4], "little"))
        for i in range(0, 16, 4)
    ] for r, row in enumerate(rows)]
    assert all(
        (4 <= STAGES[r+1]-STAGES[r] <= 16) if rows[r][3] != b"REQUESTED"
        else (0 <= STAGES[r+1]-STAGES[r] <= 4)
        for r in range(132)
    )

    inverse: dict[int, list[tuple[int, int]]] = defaultdict(list)
    for r, packet in enumerate(native):
        if packet is not None:
            for lane, word in enumerate(packet):
                inverse[word].append((r, lane))
    full = partial = 0
    for r, packet in enumerate(native):
        if packet is None:
            continue
        for k in range(r+1, len(native)):
            if native[k] is None:
                continue
            for lane, value in enumerate(native[k]):
                for p in (1, 2, 3):
                    for l, q in inverse.get(value ^ twist(packet[p-1], packet[p]), ()):
                        if l > k:
                            full += 1
                            assert STAGES[k]-STAGES[r] == 396+p-lane
                            assert STAGES[l]-STAGES[r] == 623+p-q
                for upper in (0, 0x80000000):
                    for l, q in inverse.get(value ^ twist(upper, packet[0]), ()):
                        if l > k:
                            partial += 1
                            assert STAGES[k]-STAGES[r] == 396-lane
                            assert STAGES[l]-STAGES[r] == 623-q
    assert (full, partial) == (25, 17)

    words = symbolic_words(STAGES[-1] + 4)
    basis: dict[int, tuple[int, int]] = {}
    rank = 0
    for r, packet in enumerate(native):
        if packet is None:
            continue
        for lane, value in enumerate(packet):
            for bit, form in enumerate(words[STAGES[r]+lane]):
                v, rhs = form, (value >> bit) & 1
                while v:
                    pivot = v.bit_length()-1
                    if pivot not in basis:
                        basis[pivot] = (v, rhs)
                        rank += 1
                        break
                    old, old_rhs = basis[pivot]
                    v ^= old
                    rhs ^= old_rhs
                else:
                    assert rhs == 0, ("source contradiction", r, lane, bit)
    assert rank == 15434, rank

    target_basis = dict(basis)
    free_bits = 0
    fixed_masks = []
    fixed_values = []
    for lane in range(4):
        mask = value = 0
        for bit, form in enumerate(words[STAGES[129]+lane]):
            v, rhs = form, 0
            while v:
                pivot = v.bit_length()-1
                if pivot not in basis:
                    break
                old, old_rhs = basis[pivot]
                v ^= old
                rhs ^= old_rhs
            if not v:
                mask |= 1 << bit
                value |= rhs << bit
                continue
            while v:
                pivot = v.bit_length()-1
                if pivot not in target_basis:
                    target_basis[pivot] = (v, rhs)
                    free_bits += 1
                    break
                old, old_rhs = target_basis[pivot]
                v ^= old
                rhs ^= old_rhs
        fixed_masks.append(mask)
        fixed_values.append(value)
    assert (free_bits, fixed_masks) == (32, [U, U, U, 0])
    assert fixed_values[:3] == native[128][1:]
    assert STAGES[128:131] == (951, 952, 957)
    assert bytes.fromhex(rows[128][5].decode())[4:] == bytes.fromhex(
        "6ADB2FB180DA2AA90B33F7A4"
    )
    print(json.dumps({
        "selected_ACK2_payload_decoded": False,
        "intact_native_words": 528,
        "full_source_GF2_consistent": True,
        "source_rank": rank,
        "witnesses": {"32bit": full, "31bit": partial},
        "selected_relative_stage": STAGES[129],
        "target_unfixed_bits": free_bits,
        "candidate_raw_template": "6ADB2FB180DA2AA90B33F7A4????????",
        "previous_full_2pow32_original_K04_search_hits": 0,
        "prior_search_report": "results/h17-k04-adjacent-shift-one-word-exhaustive.md",
        "historical_producer_authenticated": False
    }, indent=2))


if __name__ == "__main__":
    main()
