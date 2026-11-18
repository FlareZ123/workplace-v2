"""Known-stage MT19937 holdout rank under two synthetic sparse packet schedulers.

This tests *possibility of prediction with known packet positions*, not whether
historical printer positions or the missing physical coupon follow either model.
Run in the repository: python agents/agent27/k04_mt_knownstage_holdout_rank_sft.py
"""

import hashlib
import random
from collections import Counter
from pathlib import Path

SOURCE_SHA256 = "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"
MATRIX_A = 0x9908B0DF


def untemper(y):
    y ^= y >> 18
    y ^= (y << 15) & 0xEFC60000
    for _ in range(7):
        y ^= (y << 7) & 0x9D2C5680
    for _ in range(3):
        y ^= y >> 11
    return y & 0xFFFFFFFF


def twist(a, b):
    x = (a & 0x80000000) | (b & 0x7FFFFFFF)
    return ((x >> 1) ^ (MATRIX_A if b & 1 else 0)) & 0xFFFFFFFF


def linear_mt_vectors(length):
    """Bit-level linear MT native-output vectors against 624 symbolic words."""
    words = [[1 << (32 * t + b) for b in range(32)] for t in range(624)]
    for t in range(length - 624):
        a, b, c = words[t], words[t + 1], words[t + 397]
        half = [b[k + 1] for k in range(30)] + [a[31], 0]
        words.append([
            c[k] ^ half[k] ^ (b[0] if MATRIX_A & (1 << k) else 0)
            for k in range(32)
        ])
    return words


def starts_from_gaps(rng, n, mode):
    starts = [0]
    for _ in range(n - 1):
        if mode == "3-or-4":
            gap = 4 if rng.randrange(100) < 37 else 3
        else:
            gap = 5 if rng.randrange(100) < 47 else 2
        starts.append(starts[-1] + 4 + gap)
    return starts


def knownstage_rank(vectors, starts, heldout):
    """Exact dimension left free in the held-out 128-bit packet after all others."""
    basis = {}

    def add(vector):
        while vector:
            pivot = vector.bit_length()
            existing = basis.get(pivot)
            if existing is None:
                basis[pivot] = vector
                return 1
            vector ^= existing
        return 0

    for r, s in enumerate(starts):
        if r != heldout:
            for word in vectors[s:s + 4]:
                for bit in word:
                    add(bit)
    before = len(basis)
    rank_increase = 0
    for word in vectors[starts[heldout]:starts[heldout] + 4]:
        for bit in word:
            rank_increase += add(bit)
    assert len(basis) == before + rank_increase
    return rank_increase


def forward_recovery(starts, heldout):
    """Count whole native words exposed by one-pass forward MT recurrence peeling."""
    end = starts[-1] + 4
    have = bytearray(end)
    for r, s in enumerate(starts):
        if r != heldout:
            have[s:s + 4] = b"\x01" * 4
    for t in range(end - 624):
        if have[t] and have[t + 1] and have[t + 397]:
            have[t + 624] = 1
    return sum(have[starts[heldout]:starts[heldout] + 4])


def source_packet_count():
    source = Path(__file__).resolve().parents[2] / "resources/evidence/print/spool-reconstruction.log"
    content = source.read_bytes()
    assert hashlib.sha256(content).hexdigest() == SOURCE_SHA256
    rows = [line for line in content.decode().splitlines() if " PAYLOAD=" in line]
    selected = [r for r in rows if "JOB=PS-261003-0417 " in r and
                "ATTEMPT=2 " in r and "STATE=ACK " in r]
    assert len(rows) == 133 and len(selected) == 1
    return len(rows) - len(selected)


def main():
    observed_n = source_packet_count()
    assert observed_n == 132
    print("SOURCE_SHA256", SOURCE_SHA256, "observed_nonselected_packets", observed_n)

    generated = random.Random(13579)
    native = [untemper(generated.getrandbits(32)) for _ in range(1000)]
    symbolic = linear_mt_vectors(1000)
    for pos in (624, 625, 850, 999):
        assert native[pos] == native[pos - 227] ^ twist(native[pos - 624], native[pos - 623])
    first_state_bits = sum(word << (i * 32) for i, word in enumerate(native[:624]))
    for pos in (0, 397, 623, 624, 625, 850, 999):
        projected = sum(
            (((first_state_bits & vec).bit_count() & 1) << bit)
            for bit, vec in enumerate(symbolic[pos])
        )
        assert projected == native[pos]
    dense = list(range(0, 880, 4))
    assert knownstage_rank(symbolic, dense, 200) == 0
    assert forward_recovery(dense, 200) == 4
    print("PLANTED_POSITIVES genuine_mt_recurrence=PASS symbolic_projection=PASS dense_16byte_holdout=PASS")

    linear = linear_mt_vectors(133 * 9)
    for mode in ("3-or-4", "2-or-5"):
        rng = random.Random(20261118)
        residuals = Counter()
        forward_words = Counter()
        for _ in range(256):
            positions = starts_from_gaps(rng, 133, mode)
            residuals[knownstage_rank(linear, positions, 129)] += 1
            forward_words[forward_recovery(positions, 129)] += 1
        print("SYNTHETIC", mode, "fixtures=256 heldout_row=129")
        print("  residual_GF2_bits", dict(sorted(residuals.items())))
        print("  forward_native_words", dict(sorted(forward_words.items())))
        print("  residual_le32", sum(count for dim, count in residuals.items() if dim <= 32))
        print("  complete_linear_predictions", residuals[0])
    print("BOUNDARY: exact known synthetic stages; no source stage inference, physical-coupon authentication or K04 candidate")


if __name__ == "__main__":
    main()
