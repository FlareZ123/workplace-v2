"""SFT: monotone node50 auxiliary candidates from preserved p951 source masks.

Extends Agent3's source-only AUX 13-bit control-word bridge. Never use
selected row129 payload, route XOR mask, original REC8 acceptance or verifier.
The original control+aux record is physically retained; the index geometry
and shared generator remain hypothetical, and permutation controls are
retrospective significance diagnostics, not a historical-proof p-value.

Run: python agents/agent3/k04_aux13_monotone_index_sft.py resources
"""
import random
import sys
from collections import Counter
from pathlib import Path

from k04_aux_sampler_p951_sft import original_node50, propagate, source, U


def main(root):
    word, known, offset = source.source_closure(root)
    anchors = original_node50(root, word, known, offset)
    inferred = {-809: 0, -774: 1, -768: 1, -682: 0, -676: 1, -566: 1}
    learned = propagate(word, known, offset, inferred)
    assert learned == 70

    # Same original CRC-verified node50 controls, keyed by original seq.
    import hashlib
    import struct
    import zlib
    raw = (root / "evidence/recorder/trip-recorder.raw").read_bytes()
    assert hashlib.sha256(raw).hexdigest() == source.REC_SHA
    observations = {}
    for row in range(88):
        at = 16 + 24 * row
        ts, node, event, latch, seq, value, aux, crc = struct.unpack_from(
            "<IHBBI4sII", raw, at)
        if node == 50 and zlib.crc32(raw[at:at + 20]) == crc:
            observations[seq] = (source.untemper(
                int.from_bytes(value, "little")), aux)

    labels, allowed, observed = [], {}, {}
    for seq, (control, aux) in sorted(observations.items()):
        if seq in anchors:
            continue
        earlier = [(s, p) for s, (p, _) in anchors.items() if s < seq]
        later = [(s, p) for s, (p, _) in anchors.items() if s > seq]
        if not earlier or not later:
            continue
        left_seq, left_index = max(earlier)
        right_seq, right_index = min(later)
        # Six draws is the greatest simple floor consistent with seq12->13
        # and seq24->25. This floor is an explicit speculative hypothesis.
        lower = left_index + 6 * (seq - left_seq)
        upper = right_index - 6 * (right_seq - seq)
        options = []
        for pos in range(lower, upper + 1):
            i = offset + pos
            mask = known[i]
            next_mask = known[i + 1]
            if (mask == 0 or next_mask.bit_count() < 31 or
                    ((word[i] ^ control) & mask) != 0):
                continue
            bits = ((0, 1) if next_mask != U else ((word[i+1] >> 31),))
            for bit in bits:
                state = (word[i+1] & next_mask) | (bit << 31)
                code = source.temper(state) >> 19
                if code < 6000:
                    options.append((code, pos, bit, mask.bit_count()))
        labels.append(seq)
        observed[seq] = aux - 2000
        allowed[seq] = options

    assert len(labels) == 56
    assert sum(len(allowed[s]) for s in labels) == 109
    hits = [(seq, observed[seq], [(p, bit, nb)
            for code, p, bit, nb in allowed[seq] if code == observed[seq]])
            for seq in labels if any(
                code == observed[seq] for code, *_ in allowed[seq])]
    assert hits == [
        (54, 876, [(-459, 0, 1)]),
        (55, 4663, [(-452, 1, 1)]),
        (63, 3571, [(-397, 0, 1)])]
    print("three candidate source placements:", hits)
    print("seq54->55 spacing: 7 MT output indices, no control fullword witness")

    # Freeze positions, field controls, candidate set. Shuffle only AUX labels.
    rng = random.Random(20261102)
    values = list(observed.values())
    histogram = Counter()
    trials = 100000
    for _ in range(trials):
        rng.shuffle(values)
        score = sum(any(code == sample for code, *_ in allowed[seq])
                    for seq, sample in zip(labels, values))
        histogram[score] += 1
    at_least_three = sum(n for score, n in histogram.items() if score >= 3)
    assert at_least_three == 51, histogram
    print("AUX-only label-shuffle controls:", trials,
          "three or more coincidences:", at_least_three)
    print("Empirical shuffled-label exceedance:", at_least_three / trials)
    assert [known[offset+source.STARTS[129]+j] for j in range(4)] == [0]*4
    print("All new placements speculative; K04 selected output masks ZERO")


if __name__ == "__main__":
    main(Path(sys.argv[1]) if len(sys.argv) > 1 else
         Path(__file__).resolve().parents[2] / "resources")
