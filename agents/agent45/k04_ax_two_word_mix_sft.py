"""K04 two-word AX checkpoint producer: complete source-stage heldout probe.

Read-only standard NumPy SFT. Run from repository root:
    python agents/agent45/k04_ax_two_word_mix_sft.py resources

Assumes the *hypothetical*, not authenticated p951 MT19937 printer source
model. The disputed selected printer ACK2 payload is omitted by the imported
source closure. No K04 or K08 acceptance/hash/route data enter this study.

New emitter family: a 16-bit checkpoint is the XOR, sum or directed
difference modulo 65536 of one 16-bit projection from each of two MT words.
Both words are separated by a constant 1..32 native stage lag; checkpoints
are emitted with constant stride 1..8 over 16 ordered original values.
"""
import hashlib
import json
import random
import re
import sys
from pathlib import Path

import numpy as np

from k04_p951_seed_residue_inverse_sft import STARTS, close

ROOT = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("resources")
SPOOL_SHA = "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"
TRANSFER_SHA = "32970ad4431a9d610cc12dcca2813f39dd8fd2e396f9e748dc94b5932cb69adf"
OPS = ("xor", "add", "subtract", "reverse_subtract")
OFFSET = 2000
START_MIN, START_MAX = -1100, 3000
WORD_MASK = 0xffffffff
POPCOUNT = np.array([i.bit_count() for i in range(65536)], dtype=np.uint8)


def temper(x):
    x ^= x >> 11
    x ^= (x << 7) & 0x9d2c5680
    x ^= (x << 15) & 0xefc60000
    x ^= x >> 18
    return x & WORD_MASK


DEPENDENCIES = tuple(
    sum((1 << j) for j in range(32) if temper(1 << j) & (1 << bit))
    for bit in range(32)
)


def temper_known_mask(mask):
    return sum(1 << bit for bit, dependencies in enumerate(DEPENDENCIES)
               if dependencies & (WORD_MASK ^ mask) == 0)


def projected_views(state, state_masks):
    assert len(state) == len(state_masks) == 6000
    native = np.array(state, dtype=np.uint32)
    nmask = np.array(state_masks, dtype=np.uint32)
    tempered = np.array([temper(int(x)) for x in state], dtype=np.uint32)
    tmask = np.array([temper_known_mask(int(m)) for m in state_masks],
                     dtype=np.uint32)
    return {
        f"{name}_{half}": (
            np.array((words >> shift) & 65535, dtype=np.uint16),
            np.array((known >> shift) & 65535, dtype=np.uint16))
        for name, words, known in (("native", native, nmask),
                                  ("tempered", tempered, tmask))
        for half, shift in (("low", 0), ("high", 16))
    }


def pair_prefix_known_mask(intersection):
    """Low-bit mask before first unknown bit; safe for modular carry."""
    missing = np.bitwise_xor(intersection, np.uint16(65535)).astype(np.uint32)
    lowest_unknown = missing & (-missing)
    return ((lowest_unknown - 1) & 65535).astype(np.uint16)


def paired(words, masks, lag, op):
    a, b = words[:-lag], words[lag:]
    known = masks[:-lag] & masks[lag:]
    if op == "xor":
        return a ^ b, known
    if op == "add":
        return np.add(a, b, dtype=np.uint16), pair_prefix_known_mask(known)
    if op == "subtract":
        return np.subtract(a, b, dtype=np.uint16), pair_prefix_known_mask(known)
    if op == "reverse_subtract":
        return np.subtract(b, a, dtype=np.uint16), pair_prefix_known_mask(known)
    raise ValueError(op)


def signed_controls():
    source = (ROOT / "evidence/print/spool-reconstruction.log").read_bytes()
    audit = (ROOT / "evidence/transfers/transfer-audit.jsonl").read_bytes()
    assert hashlib.sha256(source).hexdigest() == SPOOL_SHA
    assert hashlib.sha256(audit).hexdigest() == TRANSFER_SHA
    payloads = [bytes.fromhex(x.decode("ascii"))
                for x in re.findall(rb"PAYLOAD=([0-9A-F]{32})", source)]
    assert len(payloads) == len(STARTS) == 133 and STARTS[129] == 951
    rows = [json.loads(s) for s in audit.decode("utf-8").splitlines()]
    observations = {}
    for transfer in ("AX-7778", "AX-7781", "AX-7782", "AX-7783"):
        chosen = sorted((r for r in rows if r["kind"] == "CHUNK"
                         and r["transfer"] == transfer),
                        key=lambda r: (r["seq"], r["attempt"]))
        assert len(chosen) == 16
        assert [(r["seq"], r["attempt"]) for r in chosen] == [
            (sequence, attempt) for sequence in range(8) for attempt in (1, 2)
        ]
        observations[transfer] = np.array([
            [int.from_bytes(bytes.fromhex(r["checkpoint"]), byteorder)
             for r in chosen]
            for byteorder in ("big", "little")
        ], dtype=np.uint16)
    return payloads, observations


def real_direct_control(views, observations):
    """Independent already known AX-7778 actual positive at stage -157."""
    value, known = views["tempered_high"]
    positions = OFFSET - 157 + np.arange(16)
    predicted = value[positions]
    mask = known[positions]
    fixed = int(POPCOUNT[mask].astype(np.int32).sum())
    mismatch = int(POPCOUNT[(predicted ^ observations["AX-7778"][1]) & mask]
                   .astype(np.int32).sum())
    reverse = int(POPCOUNT[(predicted ^ observations["AX-7778"][0]) & mask]
                  .astype(np.int32).sum())
    assert fixed >= 100 and mismatch == 0 and reverse > 0
    print(f"Authentic AX-7778 direct-stage control: {fixed} fixed bits, "
          f"{mismatch} correct-view errors, {reverse} wrong-view errors",
          flush=True)


def known_bit_score(observed, value, known, start, lag, op, stride=1):
    result, mask = paired(value, known, lag, op)
    indices = OFFSET + start + stride*np.arange(16)
    bits = int(POPCOUNT[mask[indices]].astype(np.int32).sum())
    mismatch = int(POPCOUNT[(result[indices] ^ observed) & mask[indices]]
                   .astype(np.int32).sum())
    return bits, mismatch, mask[indices]


def seeded_positive_controls():
    """Genuine generator seeds, intact printer states and heldout checkpoint."""
    checks = 0
    for seed in (20261103, 1947, 8675309):
        rng = random.Random(seed)
        actual_draws = [rng.getrandbits(32) for _ in range(967)]
        payloads = [
            b"".join(actual_draws[k].to_bytes(4, "little")
                     for k in range(start, start+4))
            for start in STARTS
        ]
        state, masks, offset = close(payloads)
        assert offset == OFFSET
        views = projected_views(state, masks)
        for view in ("native_low", "tempered_high"):
            value, known = views[view]
            actual_words = [actual_draws[i] if view.startswith("tempered")
                            else untemper_local(actual_draws[i])
                            for i in range(35)]
            half = [((w >> 16) if view.endswith("high") else w) & 65535
                    for w in actual_words]
            for op in OPS:
                start, lag, stride = 16, 2, 1
                expected = np.array([
                    pair_values(half[start+j], half[start+j+lag], op)
                    for j in range(16)
                ], dtype=np.uint16)
                trainbits, errors, _ = known_bit_score(
                    expected, value, known, start, lag, op, stride)
                assert errors == 0 and trainbits >= 100
                _, pairmask = paired(value, known, lag, op)
                index = OFFSET + start + 9
                changed = expected.copy()
                one_known_bit = int(pairmask[index]) & -int(pairmask[index])
                assert one_known_bit
                changed[9] ^= one_known_bit
                _, corrupt_errors, _ = known_bit_score(
                    changed, value, known, start, lag, op, stride)
                assert corrupt_errors >= 1
                checks += 1
    assert checks == 24
    print("24/24 genuine full-printer seeded model controls PASS; "
          "24/24 heldout one-bit corruptions detected", flush=True)


def untemper_local(x):
    for shift, left, mask in ((18, False, WORD_MASK),
                              (15, True, 0xefc60000),
                              (7, True, 0x9d2c5680),
                              (11, False, WORD_MASK)):
        y = x
        for _ in range(6):
            y = x ^ (((y << shift) & mask) if left else (y >> shift))
        x = y & WORD_MASK
    return x


def pair_values(a, b, op):
    if op == "xor":
        return a ^ b
    if op == "add":
        return (a + b) & 65535
    if op == "subtract":
        return (a - b) & 65535
    return (b - a) & 65535


def scan(views, observations):
    counts = {op: [0, 0, 0] for op in OPS}
    for view, (words, known) in views.items():
        for lag in range(1, 33):
            for op in OPS:
                encoded, fixed = paired(words, known, lag, op)
                for stride in range(1, 9):
                    end = min(len(encoded) - 15*stride,
                              OFFSET + START_MAX + 1)
                    starts = np.arange(OFFSET + START_MIN, end,
                                       dtype=np.int32)
                    indices = starts[:, None] + stride*np.arange(16)[None, :]
                    predictions = encoded[indices]
                    masks = fixed[indices]
                    trained_bits = POPCOUNT[masks[:, :8]].astype(np.int16).sum(axis=1)
                    testable = np.flatnonzero(trained_bits >= 32)
                    counts[op][0] += len(testable) * len(observations) * 2
                    for transfer, original in observations.items():
                        for endian in (0, 1):
                            actual = original[endian]
                            matches = testable[np.all(
                                ((predictions[testable, :8] ^ actual[:8])
                                 & masks[testable, :8]) == 0,
                                axis=1)]
                            counts[op][1] += len(matches)
                            if len(matches):
                                heldout_bits = POPCOUNT[masks[matches, 8:]].astype(
                                    np.int16).sum(axis=1)
                                heldout_err = POPCOUNT[
                                    ((predictions[matches, 8:] ^ actual[8:])
                                     & masks[matches, 8:])
                                ].astype(np.int16).sum(axis=1)
                                counts[op][2] += int(np.sum(
                                    (heldout_bits >= 24) & (heldout_err == 0)))
        print(f"Completed {view}; "
              f"training stage assignments: {dict((o,c[0]) for o,c in counts.items())}",
              flush=True)
    expected = {"xor": 8891944, "add": 8586880,
                "subtract": 8586880, "reverse_subtract": 8586880}
    assert {op: counts[op][0] for op in OPS} == expected
    assert all(counts[op][1:] == [0, 0] for op in OPS)
    print(json.dumps({"original_source_qualified_assignments": counts,
                      "source_only_result": "NO_TRAINING_MATCH",
                      "selected_K04_bits_recovered": 0},
                     indent=2, sort_keys=True))


def main():
    payloads, observations = signed_controls()
    state, masks, offset = close(payloads)
    assert offset == OFFSET
    assert len(state) == len(masks) == 6000
    views = projected_views(state, masks)
    real_direct_control(views, observations)
    seeded_positive_controls()
    scan(views, observations)


if __name__ == "__main__":
    main()
