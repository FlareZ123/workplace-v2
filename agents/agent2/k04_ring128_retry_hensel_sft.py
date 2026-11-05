"""H-17 K04: full-modulus 2-adic affine retry coupon inversion (original-source SFT).

Read-only, Python standard library; use original extracted archive root. The copied
selected 18:02 RECOVER ACK2 payload is excluded before byte decoding.
"""
import hashlib
import itertools
import json
import re
import sys
from pathlib import Path

BITS = 128
MOD = 1 << BITS
MASK = bytes.fromhex("8556C8CB6140A7F9A5123AC7571BEE1C")
TARGET = bytes.fromhex("930a52a1bab97ca2966332137c99e99298ea6182fb32ab63a3421dfb4fd8c9e0")
SPOOL_SHA = "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"
PATTERN = re.compile(r"JOB=(\S+) ATTEMPT=(\d+) STATE=(\S+) CLASS=(\S+) PAYLOAD=([0-9A-F]{32})")


def layout(raw, word_reverse, byte_reverse, bit_reverse):
    if bit_reverse:
        raw = bytes(int(f"{v:08b}"[::-1], 2) for v in raw)
    blocks = [raw[i:i + 4] for i in range(0, 16, 4)]
    if byte_reverse:
        blocks = [block[::-1] for block in blocks]
    if word_reverse:
        blocks.reverse()
    return b"".join(blocks)


def valuation(x, bits=BITS):
    x &= (1 << bits) - 1
    return bits if x == 0 else (x & -x).bit_length() - 1


def linear_roots(a, b, bits=BITS):
    """Solve a*x == b (mod 2**bits), preserving every possible high-bit lift."""
    v = valuation(a, bits)
    if b & ((1 << v) - 1):
        return []
    if v >= 16:
        raise ValueError("Unconstrained or excessive linear roots")
    width = 1 << (bits - v)
    x = ((b >> v) * pow(a >> v, -1, width)) % width
    return [x + j * width for j in range(1 << v)]


def quadratic_roots(c2, c1, c0, bits=BITS):
    """Complete Hensel lifting, including even leading coefficients."""
    v = min(valuation(c2, bits), valuation(c1, bits), valuation(c0, bits))
    if v >= 16:
        raise ValueError("Unconstrained or excessive quadratic roots")
    c2, c1, c0 = c2 >> v, c1 >> v, c0 >> v
    roots = [0]
    for step in range(1, bits - v + 1):
        offset, mask = 1 << (step - 1), (1 << step) - 1
        roots = [x for r in roots for x in (r, r + offset)
                 if ((c2 * x * x + c1 * x + c0) & mask) == 0]
        if not roots:
            return []
        if len(roots) > 65536:
            raise ValueError("Hensel roots exceeded bounded inversion")
    spacing = 1 << (bits - v)
    return [r + j * spacing for r in roots for j in range(1 << v)]


def solve(a, b, c, u, v):
    """Each result is an independently identified (multiplier, increment)."""
    return (
        # Two real transitions: A->B and U->V. Hold out B->X->C.
        [(h, (b - h * a) % MOD)
         for h in linear_roots((a - u) % MOD, (b - v) % MOD)],
        # A->B and B->X->C. Hold out U->V.
        [(h, (b - h * a) % MOD)
         for h in quadratic_roots((b - a) % MOD, (b - a) % MOD, (b - c) % MOD)],
        # U->V and B->X->C. Hold out A->B.
        [(h, (v - h * u) % MOD)
         for h in quadratic_roots((b - u) % MOD, (v - u) % MOD, (v - c) % MOD)],
    )


def positive_controls():
    multiplier = 0x102030405060708090A0B0C0D0E0F01
    increment = 0x8F4EA51DE4C3B2907ADBC9382016445
    a = 0x9A8B7C6D5E4F301928374655EABDCF17
    u = 0x000FEDCBA9876543210123456789ABCD
    t = lambda x: (multiplier * x + increment) % MOD
    b, x, c, v = t(a), t(t(a)), t(t(t(a))), t(u)
    planted = hashlib.sha256(bytes(i ^ j for i, j in zip(x.to_bytes(16, "big"), MASK))).digest()
    for group, solutions in enumerate(solve(a, b, c, u, v)):
        assert (multiplier, increment) in solutions, f"Missing true planted coefficients in {group}"
        assert any(hashlib.sha256(bytes(i ^ j for i, j in
                   zip(((h * b + p) % MOD).to_bytes(16, "big"), MASK))).digest() == planted
                   for h, p in solutions), f"Missing planted coupon in {group}"
    print("SYNTHETIC_RING128_ALL_THREE_FULL_COUPON_CONTROLS=PASS")


def main(root):
    spool = (root / "evidence/print/spool-reconstruction.log").read_bytes()
    assert hashlib.sha256(spool).hexdigest() == SPOOL_SHA
    accepted = json.loads((root / "acceptance.json").read_text())
    route = json.loads((root / "evidence/recovery-routing.json").read_text())
    assert bytes.fromhex(accepted["slot_sha256"]["K04"]) == TARGET
    assert bytes.fromhex(route["K04"]["masked_component"]) == MASK
    rows = {}
    selected_metadata = 0
    for line in spool.decode("ascii").splitlines():
        match = PATTERN.search(line)
        if not match:
            continue
        job, attempt, state, category, payload_text = match.groups()
        attempt = int(attempt)
        if (job, attempt, state, category) == ("PS-261003-0417", 2, "ACK", "RECOVER"):
            assert line.startswith("2026-10-03T18:02:00Z ")
            selected_metadata += 1
            continue  # Never decode the disputed original copied ACK2 hex bytes.
        key = (job, attempt, state, category)
        assert key not in rows
        rows[key] = bytes.fromhex(payload_text)
    assert selected_metadata == 1
    keys = (
        ("PS-261003-0417", 1, "ACK", "LABEL"),
        ("PS-261003-0417", 1, "REQUESTED", "RECOVER"),
        ("PS-261003-0417", 3, "REQUESTED", "RECOVER"),
        ("PS-261003-0420", 1, "ACK", "STORES"),
        ("PS-261003-0420", 2, "ACK", "RECOVER"),
    )
    originals = [rows[key] for key in keys]
    counts = [0, 0, 0]
    holdouts = [0, 0, 0]
    candidates = [set(), set(), set()]
    original_hits = []
    for flags in itertools.product((False, True), repeat=3):
        assert all(layout(layout(s, *flags), *flags) == s for s in originals)
        a, b, c, u, v = [int.from_bytes(layout(s, *flags), "big") for s in originals]
        families = solve(a, b, c, u, v)
        print("LAYOUT", "".join(str(int(x)) for x in flags),
              "full_parameter_roots", [len(f) for f in families])
        for group, solutions in enumerate(families):
            for h, p in solutions:
                t = lambda x: (h * x + p) % MOD
                middle = t(b)
                held = (t(middle) == c if group == 0 else
                        (t(u) == v if group == 1 else t(a) == b))
                counts[group] += 1
                holdouts[group] += int(held)
                paper = layout(middle.to_bytes(16, "big"), *flags)
                candidates[group].add(paper)
                candidate_component = bytes(i ^ j for i, j in zip(paper, MASK))
                if hashlib.sha256(candidate_component).digest() == TARGET:
                    original_hits.append((group, flags, paper.hex()))
    assert counts == [6, 4, 7], counts
    assert holdouts == [0, 0, 0], holdouts
    assert list(map(len, candidates)) == [5, 2, 7]
    assert len(set.union(*candidates)) == 14
    assert original_hits == [], original_hits
    print("ORIGINAL_K04_RING128 full_candidates", counts,
          "independent_original_holdout_matches", holdouts,
          "distinct_full_coupons", len(set.union(*candidates)),
          "original_slot_sha256_matches", len(original_hits))


if __name__ == "__main__":
    positive_controls()
    main(Path(sys.argv[1] if len(sys.argv) > 1 else "resources"))
