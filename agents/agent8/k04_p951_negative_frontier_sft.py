"""K04: p951 negative-time causal frontier, read-only SFT.

An explicit 128-dimensional MT19937 target perturbation basis is
propagated backwards. The selected printer ACK, K04/K08 commitment,
route mask and verifier are never opened.

Run: python agents/agent8/k04_p951_negative_frontier_sft.py resources

Historical caveat: p951 and common MT producer are hypothetical.
"""
import importlib.util
import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DEP = ROOT / "agents/agent2/20261102_k04_multicarrier_p951_sft.py"
spec = importlib.util.spec_from_file_location("h17_p951_source", DEP)
source = importlib.util.module_from_spec(spec)
spec.loader.exec_module(source)
U = 0xffffffff
MAG = 0x9908b0df
NEGATIVE_FOOTPRINT = [
    -1089, -1088, -1087, -1086, -1085, -1084,
    -919, -918, -917, -916, -915,
    -861, -860, -859, -858, -857, -692, -523,
    -465, -464, -463, -462, -461,
    -296, -295, -294, -293, -292,
    -69, -68, -67, -66, -65,
]
EXTRA = {-809, -774, -768, -682, -676, -566, -398}


def rank(vectors):
    pivots = {}
    for vector in vectors:
        while vector:
            high = vector.bit_length() - 1
            if high not in pivots:
                pivots[high] = vector
                break
            vector ^= pivots[high]
    return len(pivots)


def trajectory(index, bit, lower=-1100, upper=1000):
    """Zero-baseline linear perturbation, forward and backward."""
    state = {i: (1 << bit if i == index else 0) for i in range(624)}
    known = {i: U for i in range(624)}
    for t in range(upper - 623):
        mix = (state[t] & 0x80000000) | (state[t+1] & 0x7fffffff)
        twist = (mix >> 1) ^ (MAG if mix & 1 else 0)
        state[t+624] = state[t+397] ^ twist
        known[t+624] = U
    for t in range(-1, lower-1, -1):
        reverse = source.inverse_twist(state[t+397] ^ state[t+624])
        for pos, mask in ((t, 0x80000000), (t+1, 0x7fffffff)):
            old = state.get(pos, 0)
            existing = known.get(pos, 0)
            assert not ((old ^ reverse) & existing & mask), (t, pos)
            state[pos] = (old & ~mask) | (reverse & mask)
            known[pos] = existing | mask
    assert all(known[t] == U for t in range(lower+1, upper+1))
    return state


def synthetic_reverse_control():
    rng = random.Random(9087612)
    actual = [source.untemper(rng.getrandbits(32)) for _ in range(3500)]
    state = {i: x for i, x in enumerate(actual[1200:1824])}
    known = {i: U for i in range(624)}
    for t in range(-1, -1101, -1):
        reverse = source.inverse_twist(state[t+397] ^ state[t+624])
        for pos, mask in ((t, 0x80000000), (t+1, 0x7fffffff)):
            old = state.get(pos, 0)
            existing = known.get(pos, 0)
            assert not ((old ^ reverse) & existing & mask)
            state[pos] = (old & ~mask) | (reverse & mask)
            known[pos] = existing | mask
    for t in (-1099, -964, -810, -568, -1, 0):
        assert known[t] == U and state[t] == actual[t+1200]
    print("Synthetic native MT reverse-state control: PASS")


def main(root):
    synthetic_reverse_control()
    words, known, offset = source.source_closure(root)
    assert (sum(mask == U for mask in known),
            sum(0 < mask < U for mask in known)) == (968, 306)
    carrier = []
    for label, raw in source.source_controls(root):
        x = source.untemper(int.from_bytes(raw, "little"))
        for pos, mask in enumerate(known):
            if mask.bit_count() >= 30 and (words[pos] ^ x) & mask == 0:
                carrier.append((label, pos-offset, mask.bit_count()))
    assert len(carrier) == 20
    matches = {item[1] for item in carrier}
    assert len(matches) == 20

    starts = source.STARTS
    p = starts[129]
    assert p == 951
    early, q, middle = p-851, p-623, p-227
    assert (early, q, middle) == (100, 328, 724)
    observed = {s+j for row, s in enumerate(starts)
                if row != 129 for j in range(4)}
    assert len(observed) == 528
    assert not observed.intersection({early, middle, q, q+1, q+2, q+3})
    assert max(observed) < p+227

    perturbations = ([(q+j, b) for j in range(4) for b in range(31)]
                     + [(q+j, 31) for j in range(3)]
                     + [(early, 31)])
    assert len(perturbations) == 128
    directions = [trajectory(*item) for item in perturbations]
    assert all(not any(state[i] for i in observed) for state in directions)
    output = [sum(source.temper(state[p+j]) << (32*j) for j in range(4))
              for state in directions]
    assert rank(output) == 128
    print("Printer-only causal target rank:", rank(output), "/128")

    for index in matches | EXTRA:
        assert all(state[index] == 0 for state in directions), index
    print("All 20 indexed 31/32-bit carrier positions and",
          len(EXTRA), "AUX/LATCH inference positions unchanged: PASS")

    for t in range(-1100, 0):
        mask = known[offset+t]
        assert all(not (state[t] & mask) for state in directions)
    footprint = sorted(t for t in range(-1100, 0)
                       if any(state[t] for state in directions))
    assert footprint == NEGATIVE_FOOTPRINT
    print("New negative-index target-sensitive positions:", footprint)
    print("Sensitive index count:", len(footprint), "/1100")
    print("CONCLUSION: 128 source-compatible target variations survive",
          "the present indexed control/AUX observations.")
    print("This is a conditional non-identifiability witness,",
          "not historical K04 authentication or a recovered coupon.")


if __name__ == "__main__":
    main(Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "resources")
