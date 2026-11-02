"""Exact CPython n612 p951 source-only falsifier from one wrapped key term.

Selected original spool row 129 withheld. Original commitments/verifier untouched.
Run: python agents/agent39/k04_p951_seed612_singlewrap_sft.py
"""
from __future__ import annotations

import hashlib
import importlib.util
import random
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location(
    "p951_source", ROOT/"agents/agent39/k04_p951_gf2_seed_cross_sft.py"
)
gf = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gf)
U = 0xffffffff
A, B = 1664525, 1566083941
INV_A = pow(A, -1, 1 << 32)
INV_B = pow(B, -1, 1 << 32)


def mix(x: int, m: int) -> int:
    return ((x ^ (x >> 30)) * m) & U


def invert(y: int, inv_m: int) -> int:
    t = (y * inv_m) & U
    return t ^ (t >> 30)


def recover_s621(s: tuple[int, ...] | list[int]) -> tuple[int, int]:
    """Under n612, repeated absolute step622 == seed key[10] with +10."""
    init = gf.prior.BASE
    a10 = ((s[10] + 10) & U) ^ mix(s[9], B)
    a11 = ((s[11] + 11) & U) ^ mix(s[10], B)
    key10 = (a11 - (init[11] ^ mix(a10, A)) - 10) & U
    a623 = ((s[623] + 623) & U) ^ mix(s[622], B)
    a622 = invert(init[623] ^ ((a623 - key10 - 10) & U), INV_A)
    s621 = invert(a622 ^ ((s[622] + 622) & U), INV_B)
    return s621, key10


def controls() -> None:
    rng = random.Random(0x612621)
    for i in range(8):
        key = [rng.getrandbits(32) for _ in range(612)]
        key[-1] |= 0x80000000
        seed = sum(word << (32*j) for j, word in enumerate(key))
        state = random.Random(seed).getstate()[1][:624]
        got_s621, got_key10 = recover_s621(state)
        assert (got_s621, got_key10) == (state[621], key[10]), i
    print("8 actual CPython seeded n612 single-wrap inversions PASS")


def main() -> None:
    controls()
    raw = (ROOT/"resources/evidence/print/spool-reconstruction.log").read_bytes()
    assert hashlib.sha256(raw).hexdigest() == gf.SHA
    fields = re.findall(rb"PAYLOAD=([0-9A-F]{32})", raw)
    assert len(fields) == len(gf.prior.STARTS) == 133
    assert gf.prior.STARTS[129] == 951
    packets = [b"" if i == 129 else bytes.fromhex(v.decode()) for i, v in enumerate(fields)]
    symbolic = gf.symbolic_states()
    source = gf.seed_base(packets, symbolic)
    values, masks = gf.individually_fixed(source, symbolic)
    for i in (9,10,11,622):
        assert masks[i] == U, i
    assert masks[621] == 0x80000000 and values[621] == 0
    assert masks[623] == 0x7fffffff and values[623] == 0x04710790
    for top in (0, 0x80000000):
        original = values.copy()
        original[623] |= top
        predicted, key = recover_s621(original)
        assert predicted & 0x80000000, (hex(predicted), hex(key))
        print("S623 highest bit", top >> 31, "predicted S621",
              hex(predicted), "original S621 top bit=0: CONTRADICTION")
    print("Conditional p951 CPython integer seed-array length612 EXCLUDED")
    print("No authentic K04 bit or K08 wording recovered")


if __name__ == "__main__":
    main()
