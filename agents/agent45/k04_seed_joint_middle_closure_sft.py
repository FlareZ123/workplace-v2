"""Iterated K04 CPython seed-array middle/outer/MT source closure.

This test is conditional on the unproved p951 first-output CPython integer
seed model. It never reads the disputed selected ACK2 bytes or a target digest.
Original evidence and verifier stay untouched.

Run in the repository with Python 3:
    python agents/agent45/k04_seed_joint_middle_closure_sft.py 0 1
Optional shard arguments (index, total), with index in [0,total).
"""
import hashlib
import importlib.util
import random
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MIDDLE = ROOT / "agents/agent9/k04_cpython_middle_seed_sft.py"
spec = importlib.util.spec_from_file_location("h17_joint_middle", MIDDLE)
assert spec and spec.loader
q = importlib.util.module_from_spec(spec)
spec.loader.exec_module(q)
m = q.m
STEPS = 8


def residue_possible(length, terms):
    by_residue = {}
    for index, candidates in terms.items():
        j = index % length
        by_residue[j] = by_residue[j] & candidates if j in by_residue else candidates
        if not by_residue[j]:
            return False
    return True


def extend(length, payloads, initial, initial_masks):
    """Conservative fixed-bit consensus, followed by native MT closure."""
    values, masks = initial.copy(), initial_masks.copy()
    previous_bits = sum(x.bit_count() for x in masks)
    for iteration in range(STEPS):
        ok, values, masks, reason = m.infer_near(length, values, masks)
        if not ok:
            return False, reason, None, iteration + 1, 0
        ok, failure, findings = q.middle_constraints(
            length, values, masks, m.source_terms(values, masks))
        if not ok:
            return False, f"middle at i={failure}", None, iteration + 1, 0
        middle_gained = 0
        for i, size, added, pivot in findings:
            if added:
                index = i - 1
                values[index] = (values[index] & ~added) | (pivot & added)
                masks[index] |= added
                middle_gained += added.bit_count()
        extras = [(i, values[i], masks[i] & ~initial_masks[i])
                  for i in range(624) if masks[i] & ~initial_masks[i]]
        try:
            state, known, offset = m.close(payloads, extras)
        except ValueError as error:
            return False, f"MT: {error}", None, iteration + 1, middle_gained
        values, masks = state[offset - 624:offset], known[offset - 624:offset]
        bit_count = sum(x.bit_count() for x in masks)
        selected = [(state[offset + 951 + i], known[offset + 951 + i])
                    for i in range(4)]
        if bit_count == previous_bits:
            return True, "stable", selected, iteration + 1, middle_gained
        assert bit_count > previous_bits
        previous_bits = bit_count
    return True, "iteration-cap", selected, STEPS, middle_gained


def load_original():
    data = (ROOT / "resources/evidence/print/spool-reconstruction.log").read_bytes()
    assert hashlib.sha256(data).hexdigest() == m.SPOOL_SHA
    payloads = [bytes.fromhex(v.decode()) for v in
                re.findall(rb"PAYLOAD=([0-9A-F]{32})", data)]
    assert len(payloads) == len(m.STARTS) == 133
    # m.close deliberately omits row129: no use of its copied bytes.
    native, known, offset = m.close(payloads)
    return payloads, native[offset - 624:offset], known[offset - 624:offset]


def real_seed_controls():
    for length in (374, 394, 623):
        for variant in (0, 1):
            seed = sum((((0x621902dd + variant * 0x4646 + j * 0x12417)
                         & m.MASK) << (j * 32)) for j in range(length))
            generator = random.Random(seed)
            initialized = list(generator.getstate()[1][:624])
            draws = [generator.getrandbits(32) for _ in range(967)]
            packets = [b"".join(x.to_bytes(4, "little")
                                for x in draws[at:at + 4]) for at in m.STARTS]
            native, known, offset = m.close(packets)
            original, initial_masks = native[offset - 624:offset], known[offset - 624:offset]
            ok, reason, selected, rounds, gained = extend(
                length, packets, original, initial_masks)
            assert ok, (length, variant, reason)
            # A second source-independent reconstruction pins the true seeded
            # initialization and all four withheld packet words.
            values, masks = original.copy(), initial_masks.copy()
            for index, (expected, mask) in enumerate(zip(initialized, initial_masks)):
                assert not ((expected ^ values[index]) & mask), (length, index)
            for j, (value, mask) in enumerate(selected):
                assert not ((m.untemper(draws[951 + j]) ^ value) & mask), (length, j)
    print("SYNTHETIC_GENUINE_CPYPTHON_SEED_CONTROLS=6 PASS", flush=True)


def main(shard=0, shards=1):
    assert 0 <= shard < shards
    payloads, original, original_masks = load_original()
    terms = m.source_terms(original, original_masks)
    counts = dict(residue=0, prior=0, middle=0, further=0, final=0,
                  max_fixed=0, total_fixed=0, rounds=0)
    rejected = []
    retained = []
    for length in range(1, 624):
        if length % shards != shard or not residue_possible(length, terms):
            continue
        counts["residue"] += 1
        ok, values, masks, reason = m.infer_near(length, original, original_masks)
        if not ok:
            continue
        extras = [(i, values[i], masks[i] & ~original_masks[i])
                  for i in range(624) if masks[i] & ~original_masks[i]]
        try:
            m.close(payloads, extras)
        except ValueError:
            continue
        counts["prior"] += 1
        ok, failure, _ = q.middle_constraints(length, original, original_masks, terms)
        if not ok:
            continue
        counts["middle"] += 1
        ok, reason, selected, rounds, gained = extend(
            length, payloads, original, original_masks)
        counts["rounds"] += rounds
        if not ok:
            rejected.append((length, reason))
            continue
        counts["final"] += 1
        fixed = sum(mask.bit_count() for value, mask in selected)
        counts["max_fixed"] = max(counts["max_fixed"], fixed)
        counts["total_fixed"] += fixed
        retained.append((length, fixed, reason))
        if fixed:
            print("SOURCE_CONDITIONAL_SELECTED_FIXED", length, fixed,
                  [(f"{v:08X}", f"{mask:08X}") for v, mask in selected], flush=True)
    counts["further"] = len(rejected)
    print("ORIGINAL_SHARD", shard, "/", shards, "COUNTS", counts, flush=True)
    print("ADDITIONAL_EXCLUSIONS", rejected, flush=True)
    print("RETAINED_LENGTHS_AND_FIXED_BITS", retained, flush=True)
    if shard == 0:
        real_seed_controls()
    print("SELECTED_ACK2_EXCLUDED_FROM_SOURCE; K04_COMMITMENT_NOT_ACCESSED", flush=True)


if __name__ == "__main__":
    shard = int(sys.argv[1]) if len(sys.argv) > 1 else 0
    shards = int(sys.argv[2]) if len(sys.argv) > 2 else 1
    main(shard, shards)
