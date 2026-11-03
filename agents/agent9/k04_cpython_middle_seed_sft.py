"""Source-pinned CPython MT seed-array middle-word inversion, extending Agent45.

The 2-adic inverse retains all solutions for the middle state word given
its outer neighbors and a repeated CPython integer-seed key residue.
Selected row129 is withheld by the predecessor's source-state reducer.
"""
import hashlib
import importlib.util
import random
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2] / "resources"
SOURCE = ROOT / "evidence/print/spool-reconstruction.log"
PREDECESSOR = Path(__file__).resolve().parents[1] / "agent45/k04_p951_seed_residue_inverse_sft.py"
spec = importlib.util.spec_from_file_location("h17_agent45_state", PREDECESSOR)
assert spec and spec.loader
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


def completions(value, mask):
    missing = m.MASK ^ mask
    if missing.bit_count() > 1:
        return ()
    return (value, value | missing) if missing else (value,)


def middle_solutions(i, key, first, third):
    """Enumerate every middle 32-bit word via exact lower-bit constraints.

    The right-shift-by-30 inside CPython's mix couples the unknown high two
    bits into low terms. Enumerate those two first. The low k output bits
    then depend only on the low k unknown middle bits.
    """
    solutions = set()
    for high in range(4):
        states = [high << 30]
        for depth in range(1, 31):
            bit = 1 << (depth - 1)
            mask = (bit << 1) - 1
            target = key & mask
            next_states = []
            for value in states:
                if m.key_term(i, first, value, third) & mask == target:
                    next_states.append(value)
                with_bit = value | bit
                if m.key_term(i, first, with_bit, third) & mask == target:
                    next_states.append(with_bit)
            states = next_states
            if not states:
                break
        solutions.update(x for x in states if m.key_term(i, first, x, third) == key)
    return solutions


def middle_constraints(length, values, masks, terms):
    """Reject a repeated-seed residue if every middle-word completion fails."""
    residues = {}
    for index, candidates in terms.items():
        residue = index % length
        residues[residue] = residues[residue] & candidates if residue in residues else candidates
        if not residues[residue]:
            return False, index, []
    findings = []
    for i in range(4, 624):
        keys = residues.get((i - 1) % length)
        if not keys or masks[i - 1] == m.MASK:
            continue
        first = completions(values[i - 2], masks[i - 2])
        third = completions(values[i], masks[i])
        if not first or not third:
            continue
        possibilities = set()
        for key in keys:
            for a in first:
                for c in third:
                    possibilities.update(
                        b for b in middle_solutions(i, key, a, c)
                        if not ((b ^ values[i - 1]) & masks[i - 1])
                    )
        if not possibilities:
            return False, i, findings
        pivot = next(iter(possibilities))
        consensus = m.MASK
        for value in possibilities:
            consensus &= ~(value ^ pivot) & m.MASK
        added = consensus & ~masks[i - 1]
        findings.append((i, len(possibilities), added, pivot))
    return True, None, findings


def original_source():
    data = SOURCE.read_bytes()
    assert hashlib.sha256(data).hexdigest() == m.SPOOL_SHA
    payloads = [bytes.fromhex(x.decode()) for x in re.findall(rb"PAYLOAD=([0-9A-F]{32})", data)]
    assert len(payloads) == len(m.STARTS) == 133
    assert m.STARTS[129] == 951
    source, masks, offset = m.close(payloads)
    original = source[offset - 624:offset]
    known = masks[offset - 624:offset]
    terms = m.source_terms(original, known)
    baseline, prior_survivors, middle_fail = [], [], []
    for length in range(1, 624):
        residues = {}
        for j, choices in terms.items():
            residue = j % length
            residues[residue] = residues[residue] & choices if residue in residues else choices
            if not residues[residue]:
                break
        else:
            baseline.append(length)
            valid, index, _ = middle_constraints(length, original, known, terms)
            if not valid:
                middle_fail.append((length, index))
    assert len(baseline) == 144

    for length in baseline:
        valid, values, new_masks, reason = m.infer_near(length, original, known)
        if not valid:
            continue
        extras = [
            (i, values[i], new_masks[i] & ~known[i])
            for i in range(624) if new_masks[i] & ~known[i]
        ]
        try:
            m.close(payloads, extras)
        except ValueError:
            continue
        prior_survivors.append(length)
    assert len(prior_survivors) == 71, prior_survivors
    new = sorted(set(length for length, _ in middle_fail) & set(prior_survivors))
    assert new == [364, 394, 512, 522, 573], new
    remaining = sorted(set(prior_survivors) - set(new))
    assert len(remaining) == 66 and min(remaining) == 374
    print("original source: 144 base candidates; 71 prior survivors")
    print("new exclusions", [(n, i) for n, i in middle_fail if n in new])
    print("new conditional survivors", len(remaining), "first", min(remaining))


def mathematical_controls():
    rng = random.Random(4776)
    for trial in range(50):
        i = rng.randrange(4, 624)
        a, b, c = [rng.getrandbits(32) for _ in range(3)]
        target = m.key_term(i, a, b, c)
        options = middle_solutions(i, target, a, c)
        assert b in options, (trial, i, b)
        assert all(m.key_term(i, a, v, c) == target for v in options)
    print("50/50 random exact mathematical inversion controls PASS")


def seeded_controls():
    for length in (249, 307, 345, 364, 368, 392, 394, 406, 414,
                   421, 474, 509, 512, 522, 538, 573, 623):
        for variant in (0, 1):
            seed = sum(
                (((0x621902dd + variant * 0x4646 + j * 0x12417) & m.MASK) << (j * 32))
                for j in range(length)
            )
            generator = random.Random(seed)
            initialized = list(generator.getstate()[1][:624])
            draws = [generator.getrandbits(32) for _ in range(967)]
            packets = [b"".join(x.to_bytes(4, "little") for x in draws[at:at + 4])
                       for at in m.STARTS]
            state, masks, offset = m.close(packets)
            values = state[offset - 624:offset]
            known = masks[offset - 624:offset]
            assert all(not ((a ^ b) & mask) for a, b, mask in
                       zip(initialized, values, known))
            valid, fail, findings = middle_constraints(
                length, values, known, m.source_terms(values, known))
            assert valid, (length, variant, fail)
            for i, size, consensus_mask, consensus_value in findings:
                assert not ((initialized[i - 1] ^ consensus_value) & consensus_mask)
    print("34/34 CPython truly seeded withheld-row control streams PASS")


def main():
    mathematical_controls()
    seeded_controls()
    original_source()
    print("K04 selected coupon and K08 final caption remain unresolved")


if __name__ == "__main__":
    main()
