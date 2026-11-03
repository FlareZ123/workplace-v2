"""K04: exact original-source GF2 syndrome on two-MT-word CRC16 AX emitters.

Run: python agents/agent45/k04_ax_pair_crc16_symbolic_sft.py resources

Source-only p951 hypothetical common-MT chronology. Selected copied ACK2 row129
is omitted before source equation building. Never reads K04/K08 commitments,
nonce, routing mask, candidate or original suspect selected payload bytes.
Tests genuine target-informative future donor-stage windows plus heldout original
AX transfer checkpoints; emits no official candidate on a negative result.
"""
from pathlib import Path
import binascii
import hashlib
import json
import random
import sys

AGENTS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(AGENTS / "agent49"))
import k04_p951_symbolic_basis as mt

ROOT = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("resources")
AX_SHA = "32970ad4431a9d610cc12dcca2813f39dd8fd2e396f9e748dc94b5932cb69adf"
STAGE_MIN, STAGE_MAX = 1040, 1860
ANCHORS = (1179, 1347, 1574)
MT_LAST = 1860


def ref_crc(first, second, kind, initial, big_endian, flip):
    first, second = (second, first) if flip else (first, second)
    byteorder = "big" if big_endian else "little"
    payload = first.to_bytes(4, byteorder) + second.to_bytes(4, byteorder)
    if kind == "ccitt":
        return binascii.crc_hqx(payload, initial)
    code = initial
    for byte in payload:
        code ^= byte
        for _ in range(8):
            code = ((code >> 1) ^ (0xa001 if code & 1 else 0)) & 65535
    return code


def source_transfer():
    raw = (ROOT / "evidence/transfers/transfer-audit.jsonl").read_bytes()
    assert hashlib.sha256(raw).hexdigest() == AX_SHA
    rows = [json.loads(line) for line in raw.decode("utf8").splitlines()]
    result = {}
    for name in ("AX-7778", "AX-7781", "AX-7782", "AX-7783"):
        chunks = sorted((r for r in rows if r["kind"] == "CHUNK"
                         and r["transfer"] == name),
                        key=lambda x: (x["seq"], x["attempt"]))
        assert len(chunks) == 16
        assert [(x["seq"], x["attempt"]) for x in chunks] == [
            (i, attempt) for i in range(8) for attempt in (1, 2)
        ]
        result[name] = (
            tuple(int.from_bytes(bytes.fromhex(c["checkpoint"]), "big") for c in chunks),
            tuple(int.from_bytes(bytes.fromhex(c["checkpoint"]), "little") for c in chunks),
        )
    return result


def project(word_bits, coefficient):
    value = 0
    while coefficient:
        bit = coefficient & -coefficient
        value ^= word_bits[bit.bit_length() - 1]
        coefficient ^= bit
    return value


def coefficient_masks(kind, big_endian, role):
    impulse = [
        ref_crc((1 << bit) if role == 0 else 0,
                0 if role == 0 else (1 << bit),
                kind, 0, big_endian, False)
        for bit in range(32)
    ]
    return [
        sum(1 << j for j, response in enumerate(impulse) if (response >> out_bit) & 1)
        for out_bit in range(16)
    ]


def reduce_source(basis, vector):
    """Return exact residual native-state equation and known source constant."""
    constant = 0
    residual = 0
    while vector:
        pivot = vector.bit_length() - 1
        row = basis.rows.get(pivot)
        if row is None:
            residual ^= 1 << pivot
            vector ^= 1 << pivot
        else:
            mask, known = row
            vector ^= mask
            constant ^= known
    return residual, constant


def prepared_expressions(basis, symbolic):
    cache = {}
    for view in ("native", "tempered"):
        for kind in ("ccitt", "arc"):
            for byte_order in (False, True):
                for role in (0, 1):
                    weights = coefficient_masks(kind, byte_order, role)
                    expressions = []
                    for stage in range(STAGE_MIN, STAGE_MAX + 1):
                        bits = symbolic[stage - mt.ORIGIN]
                        if view == "tempered":
                            bits = mt.temper(bits)
                        expressions.append(
                            tuple(reduce_source(basis, project(bits, v)) for v in weights)
                        )
                    cache[(view, kind, byte_order, role)] = expressions
    assert len(cache) == 16
    return cache


def syndrome(cache, stage, lag, stride, view, kind, endian, reverse, count):
    left = cache[(view, kind, endian, 1 if reverse else 0)]
    right = cache[(view, kind, endian, 0 if reverse else 1)]
    local = {}
    checks = []
    for sample in range(count):
        first = left[stage + sample*stride - STAGE_MIN]
        second = right[stage + sample*stride + lag - STAGE_MIN]
        for bit, ((u, a), (v, b)) in enumerate(zip(first, second)):
            residual = u ^ v
            parity = a ^ b
            output_combination = 1 << (16*sample + bit)
            while residual:
                pivot = residual.bit_length() - 1
                old = local.get(pivot)
                if old is None:
                    local[pivot] = (residual, parity, output_combination)
                    break
                row, const, combination = old
                residual ^= row
                parity ^= const
                output_combination ^= combination
            else:
                checks.append((output_combination, parity))
    return checks


def normalized_originals(original, kind, endian, initial):
    bias = ref_crc(0, 0, kind, initial, endian, False)
    return {
        (name, orientation): sum((int(word) ^ bias) << (16*i)
                                 for i, word in enumerate(values))
        for name, two_versions in original.items()
        for orientation, values in enumerate(two_versions)
    }


def compatible(checks, output):
    return all(((output & mask).bit_count() & 1) == bit for mask, bit in checks)


def source_consistent_state(basis):
    """Construct one actual MT state satisfying all 132 untouched packets."""
    state = 0
    for pivot in sorted(basis.rows):
        row, expected = basis.rows[pivot]
        bit = expected ^ ((row & state).bit_count() & 1)
        if bit:
            state ^= 1 << pivot
    assert all(((row & state).bit_count() & 1) == expected
               for row, expected in basis.rows.values())
    return state


def native_value(symbolic, state, stage):
    return sum(
        ((word & state).bit_count() & 1) << bit
        for bit, word in enumerate(symbolic[stage - mt.ORIGIN])
    )


def temper_value(x):
    x ^= x >> 11
    x ^= (x << 7) & 0x9d2c5680
    x ^= (x << 15) & 0xefc60000
    x ^= x >> 18
    return x & 0xffffffff


def genuine_source_positives(cache, symbolic, basis):
    state = source_consistent_state(basis)
    from_recovered = 0
    for i, (payload, start) in enumerate(zip(
            [bytes.fromhex(x.decode()) for x in
             __import__("re").findall(rb"PAYLOAD=([0-9A-F]{32})",
                 (ROOT / "evidence/print/spool-reconstruction.log").read_bytes())],
            mt.STARTS)):
        if i == 129:
            continue
        for lane in range(4):
            known = mt.untemper(int.from_bytes(payload[4*lane:4*lane+4], "little"))
            assert native_value(symbolic, state, start + lane) == known
            from_recovered += 1
    assert from_recovered == 528
    print("132 intact printer packets, all 528 native outputs source-exact")
    trials = 0
    for stage in ANCHORS:
        for view in ("native", "tempered"):
            for kind in ("ccitt", "arc"):
                for endian in (False, True):
                    for reverse in (False, True):
                        for initial in (0, 65535):
                            native = [native_value(symbolic, state, stage + k)
                                      for k in range(17)]
                            raw = native if view == "native" else [
                                temper_value(x) for x in native]
                            observed = [
                                ref_crc(raw[k], raw[k+1], kind, initial, endian, reverse)
                                for k in range(16)
                            ]
                            shifted = ref_crc(0, 0, kind, initial, endian, False)
                            value = sum((x ^ shifted) << (16*i)
                                        for i, x in enumerate(observed))
                            checks = syndrome(
                                cache, stage, 1, 1, view, kind, endian, reverse, 16
                            )
                            assert checks and compatible(checks, value)
                            affected = [mask & ~((1 << 128) - 1)
                                        for mask, _ in checks]
                            affected = [x for x in affected if x]
                            assert affected
                            victim = (affected[0] & -affected[0]).bit_length() - 1
                            assert victim >= 128
                            assert not compatible(checks, value ^ (1 << victim))
                            trials += 1
    assert trials == 96
    print("96/96 original-source-compatible seeded-state future-CRC positives PASS; "
          "96/96 heldout mutations detected")


def scan(cache, original):
    counts = {
        "layouts": 0, "strong_layouts": 0, "weak_layouts": 0,
        "source_qualified_original_assignments": 0, "training_hits": 0,
        "heldout_qualified_hits": 0, "complete_original_hits": 0,
    }
    matches = []
    for stage in sorted(set(anchor + delta for anchor in ANCHORS
                            for delta in range(-8, 9))):
        for lag in range(1, 17):
            for stride in range(1, 9):
                if stage + 15*stride + lag > STAGE_MAX:
                    continue
                for view in ("native", "tempered"):
                    for kind in ("ccitt", "arc"):
                        for endian in (False, True):
                            originals = {
                                init: normalized_originals(original, kind, endian, init)
                                for init in (0, 65535)
                            }
                            for reverse in (False, True):
                                counts["layouts"] += 1
                                first = syndrome(cache, stage, lag, stride, view,
                                                 kind, endian, reverse, 8)
                                if len(first) < 16:
                                    counts["weak_layouts"] += 1
                                    continue
                                counts["strong_layouts"] += 1
                                for init, groups in originals.items():
                                    counts["source_qualified_original_assignments"] += len(groups)
                                    for (name, orientation), values in groups.items():
                                        if not compatible(first, values):
                                            continue
                                        counts["training_hits"] += 1
                                        full = syndrome(cache, stage, lag, stride,
                                                        view, kind, endian, reverse, 16)
                                        qualified = len(full) - len(first) >= 24
                                        complete = compatible(full, values)
                                        counts["heldout_qualified_hits"] += int(qualified)
                                        counts["complete_original_hits"] += int(
                                            qualified and complete
                                        )
                                        matches.append({
                                            "stage":stage, "lag":lag, "stride":stride,
                                            "view":view, "crc":kind, "big_endian":endian,
                                            "reverse_words":reverse, "initial":init,
                                            "original_transfer":name,
                                            "checkpoint_endian":orientation,
                                            "first8_constraints":len(first),
                                            "heldout_additional_constraints":
                                                len(full)-len(first),
                                            "heldout_qualified":qualified,
                                            "complete_match":complete,
                                        })
    assert counts == {
        "layouts": 104448, "strong_layouts": 56640, "weak_layouts": 47808,
        "source_qualified_original_assignments": 906240,
        "training_hits": 3, "heldout_qualified_hits": 2,
        "complete_original_hits": 0,
    }, counts
    assert [m["stage"] for m in matches] == [1340,1344,1348], matches
    assert not any(m["complete_match"] for m in matches)
    print(json.dumps({"original_source_results":counts,
                      "first8_survivors":matches,
                      "new_authentic_selected_K04_bits":0},
                     indent=2, sort_keys=True))


def main():
    original = source_transfer()
    mt.LAST = MT_LAST
    source_basis, symbolic = mt.source(ROOT)
    assert source_basis.rank == 15365 and len(symbolic) == 2961
    cache = prepared_expressions(source_basis, symbolic)
    genuine_source_positives(cache, symbolic, source_basis)
    scan(cache, original)


if __name__ == "__main__":
    main()
