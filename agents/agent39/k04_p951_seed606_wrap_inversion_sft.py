"""Source-only CPython p951 integer seed length606 exact first-cycle wrap exclusion.

The authentic selected spool row129 is omitted before fitting. No K04/K08
commitments, original mask, or verifier are touched. Eight full real Python
606-word seeded inversion positive controls.
Run: python agents/agent39/k04_p951_seed606_wrap_inversion_sft.py
"""
from __future__ import annotations

import hashlib
import importlib.util
import random
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location(
    "p951_source", ROOT / "agents/agent39/k04_p951_gf2_seed_cross_sft.py"
)
gf = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gf)
U = 0xffffffff
A = 1664525
B = 1566083941
INV_A = pow(A, -1, 1 << 32)
INV_B = pow(B, -1, 1 << 32)


def mix(x: int, multiplier: int) -> int:
    return ((x ^ (x >> 30)) * multiplier) & U


def unmix(y: int, inverse_multiplier: int) -> int:
    x = (y * inverse_multiplier) & U
    return x ^ (x >> 30)


def invert_repeated_seed(s: list[int] | tuple[int, ...]) -> tuple[int, int, int, int, int]:
    """Length606: key[606]=key[0], key[607]=key[1], key[608]=key[2].

    Given S2,S3,S606,S607,S608,S609,S623, infer required S1,S605
    and all three repeated key words without other unknown native words.
    The +j term uses *wrapped* seed key index j%606, not absolute step.
    """
    init = gf.prior.BASE
    a3 = ((s[3] + 3) & U) ^ mix(s[2], B)
    a607 = ((s[607] + 607) & U) ^ mix(s[606], B)
    a608 = ((s[608] + 608) & U) ^ mix(s[607], B)
    a609 = ((s[609] + 609) & U) ^ mix(s[608], B)
    key1 = (a608 - (init[608] ^ mix(a607, A)) - 1) & U
    key2 = (a609 - (init[609] ^ mix(a608, A)) - 2) & U
    a2 = unmix(init[3] ^ ((a3 - key2 - 2) & U), INV_A)
    a1 = unmix(a2 ^ ((s[2] + 2) & U), INV_B)
    s1 = ((a1 ^ mix(s[623], B)) - 1) & U
    p1 = unmix(init[2] ^ ((a2 - key1 - 1) & U), INV_A)
    key0 = (p1 - (init[1] ^ mix(init[0], A))) & U
    a606 = unmix(init[607] ^ ((a607 - key0) & U), INV_A)
    s605 = unmix(a606 ^ ((s[606] + 606) & U), INV_B)
    return s1, s605, key0, key1, key2


def seeded_controls() -> None:
    rng = random.Random(0x606A713)
    for variant in range(8):
        key = [rng.getrandbits(32) for _ in range(606)]
        key[-1] |= 0x80000000
        integer_seed = sum(w << (32*i) for i, w in enumerate(key))
        register = random.Random(integer_seed).getstate()[1][:624]
        result = invert_repeated_seed(register)
        assert result == (register[1], register[605], key[0], key[1], key[2]), variant
    print("Eight full real CPython n606 seeded first-cycle inverse controls: PASS")


def main() -> None:
    seeded_controls()
    raw = (ROOT / "resources/evidence/print/spool-reconstruction.log").read_bytes()
    assert hashlib.sha256(raw).hexdigest() == gf.SHA
    fields = re.findall(rb"PAYLOAD=([0-9A-F]{32})", raw)
    assert len(fields) == len(gf.prior.STARTS) == 133
    assert gf.prior.STARTS[129] == 951
    # Drop selected before constructing original GF(2) constraints.
    packets = [b"" if i == 129 else bytes.fromhex(x.decode()) for i, x in enumerate(fields)]
    expressions = gf.symbolic_states()
    original = gf.seed_base(packets, expressions)
    vals, masks = gf.individually_fixed(original, expressions)
    for i in (2, 3, 606, 607, 608):
        assert masks[i] == U, i
    assert masks[1] == 0x80000001
    assert masks[605] == 0x80000000
    assert masks[609] == masks[623] == 0x7fffffff
    results = []
    for top609 in (0, 0x80000000):
        for top623 in (0, 0x80000000):
            proposed = vals.copy()
            proposed[609] |= top609
            proposed[623] |= top623
            s1, s605, key0, key1, key2 = invert_repeated_seed(proposed)
            mismatch1 = (s1 ^ vals[1]) & masks[1]
            mismatch605 = (s605 ^ vals[605]) & masks[605]
            results.append((top609 >> 31, top623 >> 31, mismatch1, mismatch605))
            assert mismatch1 or mismatch605, "unexpected source-compatible n606 branch"
    print("Four exhaustive source-fixed top-bit possibilities (S609,S623):")
    for r in results:
        print("top609,top623,mismatch S1,S605:", r[:2], hex(r[2]), hex(r[3]))
    assert all(a or b for _, _, a, b in results)
    print("Original p951/CPython length606: EXCLUDED by exact seed-index wrap source contradiction")
    print("No historical generator, selected K04 bit or K08 final caption is authenticated")


if __name__ == "__main__":
    main()
