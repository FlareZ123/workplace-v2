"""Source-only nested seed generator tests for H-17 K04. No disputed coupon or acceptance digest is read.
Run: python agents/agent29/k04_nested_seed_linear128_sft.py
"""
from __future__ import annotations
import hashlib
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "agents" / "agent15"))
import k04_p951_sha512_seed_fingerprint_sft as source

MASK = (1 << 32) - 1
TIMES = (0, 1, 579, 580)
CROSSCHECK = 12
SOURCE_SHA = "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"

def rotl(x: int, k: int) -> int:
    return ((x << k) | (x >> (32 - k))) & MASK

def rotr(x: int, k: int) -> int:
    return ((x >> k) | (x << (32 - k))) & MASK

def step_xorshift(st: tuple[int, int, int, int]) -> tuple[int, int, int, int]:
    x, y, z, w = st
    t = x ^ ((x << 11) & MASK)
    return y, z, w, (w ^ (w >> 19) ^ t ^ (t >> 8)) & MASK

def step_xoshiro(st: tuple[int, int, int, int]) -> tuple[int, int, int, int]:
    a, b, c, d = st
    t = (b << 9) & MASK
    c ^= a
    d ^= b
    b ^= c
    a ^= d
    c ^= t
    return a, b, c, rotl(d, 11)

def xoshiro_scramble(s1: int) -> int:
    return (rotl((s1 * 5) & MASK, 7) * 9) & MASK

def xoshiro_unscramble(v: int) -> int:
    return (rotr((v * pow(9, -1, 1 << 32)) & MASK, 7) * pow(5, -1, 1 << 32)) & MASK

def emit_linear(st: tuple[int, int, int, int], family: str, count: int) -> list[int]:
    result = []
    for _ in range(count):
        if family == "xorshift128":
            st = step_xorshift(st)
            result.append(st[3])
        else:
            result.append(st[1])
            st = step_xoshiro(st)
    return result

def raw_from_linear(word: int, family: str) -> int:
    return word if family == "xorshift128" else xoshiro_scramble(word)

def linear_from_raw(word: int, family: str) -> int:
    return word if family == "xorshift128" else xoshiro_unscramble(word)

def swap32(v: int) -> int:
    return int.from_bytes(v.to_bytes(4, "big"), "little")

def state_tuple(bits: int) -> tuple[int, int, int, int]:
    return tuple((bits >> (32 * k)) & MASK for k in range(4))

def full_rank_solve(columns: list[int], target: int) -> tuple[int, int]:
    basis = [0] * 128
    witnesses = [0] * 128
    for bit, column in enumerate(columns):
        witness = 1 << bit
        for pivot in range(127, -1, -1):
            if not (column >> pivot) & 1:
                continue
            if basis[pivot]:
                column ^= basis[pivot]
                witness ^= witnesses[pivot]
            else:
                basis[pivot] = column
                witnesses[pivot] = witness
                break
    rank = sum(x != 0 for x in basis)
    value = 0
    for pivot in range(127, -1, -1):
        if (target >> pivot) & 1:
            assert basis[pivot]
            target ^= basis[pivot]
            value ^= witnesses[pivot]
    assert target == 0
    return rank, value

def columns_for(family: str) -> list[int]:
    cols = []
    for bit in range(128):
        words = emit_linear(state_tuple(1 << bit), family, max(TIMES) + 1)
        cols.append(sum(words[t] << (32 * i) for i, t in enumerate(TIMES)))
    return cols

def decoded_state(columns: list[int], family: str, words: list[int], endian: str) -> tuple[int, int]:
    observed = [v if endian == "big" else swap32(v) for v in words]
    linear = [linear_from_raw(v, family) for v in observed]
    return full_rank_solve(columns, sum(v << (32 * i) for i, v in enumerate(linear)))

def source_domains() -> dict[int, list[int]]:
    raw = (ROOT / "resources/evidence/print/spool-reconstruction.log").read_bytes()
    assert hashlib.sha256(raw).hexdigest() == SOURCE_SHA
    encoded = re.findall(rb"PAYLOAD=([0-9A-F]{32})", raw)
    assert len(encoded) == len(source.STARTS) == 133 and source.STARTS[129] == 951
    packets = [b"" if i == 129 else bytes.fromhex(token.decode("ascii"))
               for i, token in enumerate(encoded)]
    _, _, domains = source.derive_seed_digest_words(packets, source.expressions())
    assert len(domains) == 86
    assert domains[602] == [0x64589C88, 0xE4589C88]
    assert domains[601] == [0x49342EC0]
    assert domains[590] == [0x6425CF5B, 0xE425CF5B]
    assert domains[23] == [0x06EDCDAD]
    assert domains[22] == [0xFD6A4CF7]
    return domains

def positive_control(family: str, endian: str, columns: list[int]) -> None:
    planted = (0x12345678, 0x87654321, 0xDEADBEEF, 0x0BADF00D)
    generated = [raw_from_linear(v, family)
                 for v in emit_linear(planted, family, max(TIMES) + 1)]
    paper = [v if endian == "big" else swap32(v) for v in generated]
    rank, state = decoded_state(columns, family, [paper[t] for t in TIMES], endian)
    assert rank == 128 and state_tuple(state) == planted
    recovered = raw_from_linear(emit_linear(state_tuple(state), family, CROSSCHECK + 1)[CROSSCHECK], family)
    if endian == "little":
        recovered = swap32(recovered)
    assert recovered == paper[CROSSCHECK]

def main() -> None:
    domains = source_domains()
    report = {"source_sha256": SOURCE_SHA,
              "source_fixed_or_one-bit-ambiguous_key_words": len(domains),
              "fit_key_positions": [602, 601, 23, 22],
              "unfitted_crosscheck_key_position": 590,
              "unfitted_source_allowed": [f"{w:08X}" for w in domains[590]],
              "families": {}}
    for family in ("xorshift128", "xoshiro128**"):
        columns = columns_for(family)
        cases = []
        for endian in ("big", "little"):
            positive_control(family, endian, columns)
            for first in domains[602]:
                word_sequence = [first, domains[601][0], domains[23][0], domains[22][0]]
                rank, state = decoded_state(columns, family, word_sequence, endian)
                assert rank == 128
                predicted = raw_from_linear(
                    emit_linear(state_tuple(state), family, CROSSCHECK + 1)[CROSSCHECK], family
                )
                if endian == "little":
                    predicted = swap32(predicted)
                assert predicted not in domains[590]
                cases.append({"key602": f"{first:08X}", "endian": endian,
                              "rank": rank, "predicted_key590": f"{predicted:08X}",
                              "key590_source_match": False})
        report["families"][family] = cases
    print(json.dumps(report, indent=2))
    print("PASS: planted generators predict their heldouts; original fails each fifth-word check")

if __name__ == "__main__":
    main()
