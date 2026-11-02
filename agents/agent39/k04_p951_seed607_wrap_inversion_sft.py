"""Original p951 printer source falsifies CPython integer seed length607.

Full first-cycle wrap-key inversion, selected row129 withheld from source fit.
Eight genuine seeded CPython length607 positive controls.
Run: python agents/agent39/k04_p951_seed607_wrap_inversion_sft.py
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
A, B = 1664525, 1566083941
INV_B = pow(B, -1, 1 << 32)


def mix(x: int, m: int) -> int:
    return ((x ^ (x >> 30)) * m) & U


def invert_g(y: int) -> int:
    x = (y * INV_B) & U
    return x ^ (x >> 30)


def predicted_s1_n607(s: list[int] | tuple[int, ...]) -> tuple[int, int, int]:
    """Length607 reused keys: j607 uses key[0]+0, j608 uses key[1]+1."""
    init = gf.prior.BASE
    a607 = ((s[607] + 607) & U) ^ mix(s[606], B)
    a608 = ((s[608] + 608) & U) ^ mix(s[607], B)
    a609 = ((s[609] + 609) & U) ^ mix(s[608], B)
    key0 = (a608 - (init[608] ^ mix(a607, A))) & U
    p1 = ((init[1] ^ mix(init[0], A)) + key0) & U
    key1 = (a609 - (init[609] ^ mix(a608, A)) - 1) & U
    a2 = (key1 + (init[2] ^ mix(p1, A)) + 1) & U
    a1 = invert_g(a2 ^ ((s[2] + 2) & U))
    s1 = ((a1 ^ mix(s[623], B)) - 1) & U
    return s1, key0, key1


def seeded_controls() -> None:
    rng = random.Random(0x607A617)
    for variant in range(8):
        words = [rng.getrandbits(32) for _ in range(607)]
        words[-1] |= 0x80000000
        seed = sum(x << (32*j) for j, x in enumerate(words))
        register = random.Random(seed).getstate()[1][:624]
        predicted = predicted_s1_n607(register)
        assert predicted == (register[1], words[0], words[1]), variant
    print("Eight true CPython n607 integer-seed inverse controls: PASS")


def main() -> None:
    seeded_controls()
    raw = (ROOT / "resources/evidence/print/spool-reconstruction.log").read_bytes()
    assert hashlib.sha256(raw).hexdigest() == gf.SHA
    fields = re.findall(rb"PAYLOAD=([0-9A-F]{32})", raw)
    assert len(fields) == len(gf.prior.STARTS) == 133
    assert gf.prior.STARTS[129] == 951
    packets = [b"" if i == 129 else bytes.fromhex(x.decode()) for i,x in enumerate(fields)]
    expressions = gf.symbolic_states()
    basis = gf.seed_base(packets, expressions)
    vals, masks = gf.individually_fixed(basis, expressions)
    assert all(masks[i] == U for i in (2, 606, 607, 608))
    assert masks[609] == masks[623] == 0x7fffffff
    assert masks[1] == 0x80000001 and vals[1] == 1
    for top609 in (0, 0x80000000):
        for top623 in (0, 0x80000000):
            trial = vals.copy()
            trial[609] |= top609
            trial[623] |= top623
            predicted, key0, key1 = predicted_s1_n607(trial)
            mismatch = (predicted ^ vals[1]) & masks[1]
            assert mismatch & 1, (top609, top623, hex(predicted))
            print("top609/top623", top609 >> 31, top623 >> 31,
                  "required S1", hex(predicted), "source-mask contradiction", hex(mismatch))
    print("Original source p951/CPython 607-word key array: EXCLUDED")
    print("Original selected K04 bits and K08 final words remain unknown")


if __name__ == "__main__":
    main()
