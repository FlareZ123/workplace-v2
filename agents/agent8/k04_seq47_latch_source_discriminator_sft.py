"""K04 seq47 conditional target-parity stage discriminator.

Original 132 printer rows and 56 recorder CONTROL words only are fitted.
The historical selected ACK payload, original K04 target hash and route mask are
not read. The 3-bit original recorder latch is an independent holdout.
Run: python agents/agent8/k04_seq47_latch_source_discriminator_sft.py
"""
import hashlib
import random
import struct
import sys
import zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "agents" / "agent49"))
sys.path.insert(0, str(ROOT / "agents" / "agent2"))
from k04_p951_symbolic_basis import source, get, temper
from k04_node50_full_syndrome_gap_sft import recorder_controls
from k04_conditional_onebit_parity_sft import PATH, joint_basis, target_relations

ANCHORS = {7, 9, 12, 13, 14, 24, 25, 41, 43, 44, 45, 61, 63, 64, 70}
REC_HASH = "5ebc6204ed773102237dd287772de96d19740e163b49b4075537d937888657ba"


def original_latches():
    raw = (ROOT / "resources/evidence/recorder/trip-recorder.raw").read_bytes()
    assert hashlib.sha256(raw).hexdigest() == REC_HASH
    assert raw[:8] == b"TRP2DUMP" and len(raw) == 16 + 88 * 24
    result = {}
    for idx in range(88):
        row = raw[16 + idx * 24:16 + (idx + 1) * 24]
        _, node, _, latch, seq, _, _, crc = struct.unpack("<IHBBIIII", row)
        if node == 50:
            assert zlib.crc32(row[:20]) == crc
            result[seq] = latch
    assert set(result) == set(range(72))
    return result


def predicted(joint, vectors, stage):
    """Predicted CPython getrandbits(3) bits, low-to-high, or None."""
    return tuple(joint.predict(v) for v in temper(get(vectors, stage))[29:32])


def counts(predictions, latches):
    fixed = correct = 0
    for bits, latch in zip(predictions, latches):
        for bit, value in enumerate(bits):
            if value is not None:
                fixed += 1
                correct += value == ((latch >> bit) & 1)
    return fixed, correct


def permutation_tail(predictions, observed, repetitions=20000):
    """Label-shuffle null; control stages and CONTROL words remain fixed."""
    rng = random.Random(20261103)
    true_correct = counts(predictions, observed)[1]
    extreme = 0
    for _ in range(repetitions):
        shuffled = observed[:]
        rng.shuffle(shuffled)
        extreme += counts(predictions, shuffled)[1] >= true_correct
    return extreme, repetitions, (extreme + 1) / (repetitions + 1)


def main():
    printer, vectors = source(ROOT / "resources")
    controls = recorder_controls()
    latches = original_latches()
    assert printer.rank == 15365

    other = tuple((seq, pos) for seq, pos in PATH if seq != 47)
    # Full 4..11-output/seq local chronology also permits -527..-524,
    # but each creates an exact original CONTROL inconsistency with the 55 rows.
    for pos in (-527, -526, -525, -524):
        try:
            joint_basis(printer, vectors, controls, other + ((47, pos),))
        except AssertionError:
            continue
        raise AssertionError(f"unexpected source-compatible seq47 stage {pos}")

    alternatives = []
    for pos in (-523, -522, -521, -520):
        joint = joint_basis(printer, vectors, controls, other + ((47, pos),))
        bits = predicted(joint, vectors, pos - 1)
        fixed, correct = counts([bits], [latches[47]])
        target_unknown = len(target_relations(joint, vectors)[0])
        alternatives.append((pos, joint.rank, fixed, correct, target_unknown, bits))
    assert [(pos, rank, fixed, correct, target_unknown)
            for pos, rank, fixed, correct, target_unknown, _ in alternatives] == [
                (-523, 16663, 2, 1, 127),
                (-522, 16664, 0, 0, 128),
                (-521, 16664, 0, 0, 128),
                (-520, 16664, 0, 0, 128)]
    print("seq47 stage / joint rank / fixed preceding-latch bits / correct / K04 free:")
    for row in alternatives:
        print(row)
    assert latches[47] == 1
    assert alternatives[0][-1] == (0, 0, None)  # preceding predicted ?00, true 001

    selected = joint_basis(printer, vectors, controls, PATH)
    assert selected.rank == 16663
    for name, subset, expected in (
        ("15 original source-indexed anchors", ANCHORS, (36, 35)),
        ("41 newly placed controls", set(seq for seq, _ in PATH) - ANCHORS, (53, 33)),
    ):
        sample = [(seq, pos) for seq, pos in PATH if seq in subset]
        pp = [predicted(selected, vectors, pos - 1) for seq, pos in sample]
        vv = [latches[seq] for seq, pos in sample]
        assert counts(pp, vv) == expected
        print(name, "source-fixed preceding-latch bits/correct:", expected,
              "label permutation >= observed:", permutation_tail(pp, vv))

    print("Offset controls (all 56, not fitted on latch):")
    for delta in (-7, -6, -5, -4, -3, -2, -1, 1, 2, 3, 4, 5, 6, 7):
        pp = [predicted(selected, vectors, pos + delta) for _, pos in PATH]
        fixed, correct = counts(pp, [latches[seq] for seq, _ in PATH])
        print(delta, fixed, correct)
    print("Conditional latch-1 model rejects stage -523; no verified K04 bit gained.")


if __name__ == "__main__":
    main()
