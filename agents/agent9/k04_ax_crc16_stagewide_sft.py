"""Original-source AX CRC16 emitter sieve, conditional on p951 MT chronology.

Source-pinned, read-only. Selected printer row129 excluded; neither original
K04/K08 commitment, route mask nor canonical candidate is read. This models
CRC16 over exactly one 32-bit native or tempered generator word per checkpoint.
"""
from __future__ import annotations

import binascii
import hashlib
import json
import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2] / "resources"
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "agent49"))
from k04_p951_symbolic_basis import source, temper, ORIGIN, MAG

AX_PIN = "32970ad4431a9d610cc12dcca2813f39dd8fd2e396f9e748dc94b5932cb69adf"
MAX_STAGE = 5320


def crc_arc(data: bytes, initial: int = 0) -> int:
    value = initial
    for octet in data:
        value ^= octet
        for _ in range(8):
            value = (value >> 1) ^ (0xA001 if value & 1 else 0)
    return value


def laws():
    for name, crc in (("CCITT", binascii.crc_hqx), ("ARC", crc_arc)):
        for order in ("little", "big"):
            weights = [crc((1 << j).to_bytes(4, order), 0) for j in range(32)]
            for initial in (0, 0xFFFF):
                yield (name, order, initial), weights, crc(bytes(4), initial)


def reduce_against_source(basis, value: int):
    known = 0
    while value:
        leading = value.bit_length() - 1
        row = basis.rows.get(leading)
        if row is None:
            break
        vector, bit = row
        value ^= vector
        known ^= bit
    return value, known


def checksum_forms(word_forms, weights, bias):
    forms = []
    for bit in range(16):
        vector, rhs = 0, (bias >> bit) & 1
        for j, weight in enumerate(weights):
            if (weight >> bit) & 1:
                source_vector, source_bit = word_forms[j]
                vector ^= source_vector
                rhs ^= source_bit
        forms.append((vector, rhs))
    return forms


def parity_equations(forms):
    quotient = {}
    parity = []
    for index, (value, rhs) in enumerate(forms):
        observation_mask = 1 << index
        while value:
            leading = value.bit_length() - 1
            prior = quotient.get(leading)
            if prior is None:
                quotient[leading] = (value, observation_mask, rhs)
                break
            vector, mask, bit = prior
            value ^= vector
            observation_mask ^= mask
            rhs ^= bit
        else:
            parity.append((observation_mask, rhs))
    return parity


def violations(parity, observed: int) -> int:
    return sum(((mask & observed).bit_count() & 1) != bit
               for mask, bit in parity)


def original_transfer_views():
    raw = (ROOT / "evidence/transfers/transfer-audit.jsonl").read_bytes()
    assert hashlib.sha256(raw).hexdigest() == AX_PIN
    entries = [json.loads(line) for line in raw.splitlines()]
    views = {}
    for transfer in ("AX-7778", "AX-7781", "AX-7782", "AX-7783"):
        chunks = sorted((x for x in entries
                         if x["transfer"] == transfer and x["kind"] == "CHUNK"),
                        key=lambda x: (x["seq"], x["attempt"]))
        assert len(chunks) == 16
        assert [(x["seq"], x["attempt"]) for x in chunks] == [
            (seq, attempt) for seq in range(8) for attempt in (1, 2)]
        for endian in ("little", "big"):
            views[transfer, endian] = sum(
                int.from_bytes(bytes.fromhex(chunk["checkpoint"]), endian)
                << (16 * i) for i, chunk in enumerate(chunks))
    return views


def run():
    basis, states = source(ROOT)
    assert basis.rank == 15365
    for i in range(len(states), MAX_STAGE - ORIGIN + 1):
        k = i - 624
        a, b, c = states[k + 397], states[k], states[k + 1]
        states.append([
            a[j] ^ (b[31] if j == 30 else (c[j + 1] if j < 30 else 0))
            ^ (c[0] if (MAG >> j) & 1 else 0) for j in range(32)
        ])
    print("Original spool rank", basis.rank, "stage words", len(states), flush=True)
    views = original_transfer_views()

    direct = [
        reduce_against_source(basis, v)
        for offset in range(16)
        for v in temper(states[-157 + offset - ORIGIN])[16:]
    ]
    real_positive = parity_equations(direct)
    assert len(real_positive) == 126
    assert violations(real_positive, views["AX-7778", "little"]) == 0
    print("Real original AX-7778 direct-halfword control 126/126 PASS", flush=True)

    stages = range(-1100, 5301)
    index_forms = {}
    for index in range(-1100, 5316):
        word = states[index - ORIGIN]
        index_forms[index] = (
            [reduce_against_source(basis, value) for value in word],
            [reduce_against_source(basis, value) for value in temper(word)],
        )
    print("Projected", len(index_forms), "native MT output stages", flush=True)

    tested = 0
    informative = 0
    exact = 0
    minima = {16: 257, 32: 257, 64: 257}
    for start in stages:
        for word_view in (0, 1):
            sampled = [index_forms[start + k][word_view] for k in range(16)]
            for label, weights, bias in laws():
                forms = [
                    form for sampled_word in sampled
                    for form in checksum_forms(sampled_word, weights, bias)
                ]
                fixed = [(index, bit) for index, (vector, bit) in enumerate(forms)
                         if vector == 0]
                candidates = []
                for transfer_endian, observation in views.items():
                    tested += 1
                    incompatible = any(
                        ((observation >> index) & 1) != bit for index, bit in fixed)
                    if not incompatible or len(fixed) < 16:
                        candidates.append((transfer_endian, observation))
                if not candidates:
                    continue
                constraints = parity_equations(forms)
                n = len(constraints)
                if n < 16:
                    continue
                informative += 1
                for identity, observation in candidates:
                    errors = violations(constraints, observation)
                    for threshold in minima:
                        if n >= threshold:
                            minima[threshold] = min(minima[threshold], errors)
                    if errors == 0:
                        exact += 1
                        print("SOURCE-COMPATIBLE", start, word_view, label,
                              identity, "independent_checks", n, flush=True)
        if (start + 1100) % 500 == 0:
            print("stage", start, "assignments", tested, "informative",
                  informative, "exact", exact, flush=True)

    assert tested == 6401 * 16 * 8
    assert informative == 6882
    assert minima == {16: 1, 32: 7, 64: 19}, minima
    assert exact == 0
    print("PASS ORIGINAL NEGATIVE:", tested, "assignments,", informative,
          "informative encoder cases, zero compatible donors, minima", minima)

    synthetic = random.Random(20261103).getrandbits(19968)
    for pivot in basis.rows:
        synthetic &= ~(1 << pivot)
    for pivot, (vector, rhs) in sorted(basis.rows.items()):
        synthetic |= (rhs ^ ((vector & synthetic).bit_count() & 1)) << pivot
    assert all((v & synthetic).bit_count() % 2 == rhs
               for v, rhs in basis.rows.values())
    _, weights, bias = next(laws())
    forms = [
        form for k in range(16)
        for form in checksum_forms(index_forms[1347 + k][0], weights, bias)
    ]
    synthetic_view = sum(
        (((vector & synthetic).bit_count() & 1) ^ rhs) << i
        for i, (vector, rhs) in enumerate(forms)
    )
    parity = parity_equations(forms)
    assert len(parity) >= 16
    assert violations(parity, synthetic_view) == 0
    print("PASS planted CRC16 source-consistent synthetic checkpoint")
    print("Original selected coupon and both original commitments UNUSED")


if __name__ == "__main__":
    run()
