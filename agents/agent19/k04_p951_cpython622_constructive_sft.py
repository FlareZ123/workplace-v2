"""Conditional K04: genuine CPython 622-word integer seeds can attain ANY coupon.

Import the source-pinned Agent19 624-word GF2 model. Never decode selected
source row129; never use acceptance or route mask. The 622-word key repeats
key0 as word622 and key1 as word623, with cyclic injections j=0/1.
"""
import importlib.util
import random
from pathlib import Path

ME = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location(
    "agent19_base", ME / "k04_p951_cpython624_623_constructive_sft.py"
)
base = importlib.util.module_from_spec(spec)
spec.loader.exec_module(base)
U = base.U


def impose_word(basis, index, value):
    for bit in range(32):
        equation = (1 << (32 * index + bit + 1)) | ((value >> bit) & 1)
        rem = base.reduce(equation, basis)
        if rem == 1:
            return False
        if rem > 1:
            basis[rem.bit_length() - 1] = rem
    return True


def invert_q(c, target):
    """Exact 32-bit bit-lifting of (c XOR mix(q,M2)) - q = target."""
    options = []
    for bit31 in (0, 1):
        for bit30 in (0, 1):
            high = (bit31 << 31) | (bit30 << 30)
            prefixes = [0]
            for width in range(1, 31):
                mask = (1 << width) - 1
                new = []
                for prefix in prefixes:
                    for candidate in (prefix, prefix | (1 << (width - 1))):
                        q = candidate | high
                        predicted = ((c ^ base.mix(q, base.M2)) - q) & mask
                        if predicted == (target & mask):
                            new.append(candidate)
                prefixes = new
                if not prefixes:
                    break
                assert len(prefixes) <= 20000
            for prefix in prefixes:
                q = prefix | high
                if ((c ^ base.mix(q, base.M2)) - q) & U == target:
                    options.append(q)
    return options


def seeded622(register):
    """Invert 622 words, exact repeated-key equalities externally frozen."""
    x = base.pre_second_register(register)
    a = base.BASE[1] ^ base.mix(base.BASE[0], base.M1)
    # At j=622 and 623, cyclic key positions are 0 and 1.
    key0 = (x[623] - (base.BASE[623] ^ base.mix(x[622], base.M1))) & U
    y = (key0 + a) & U
    key1 = (x[2] - (base.BASE[2] ^ base.mix(y, base.M1)) - 1) & U
    assert key1 == ((x[1] - (y ^ base.mix(x[623], base.M1)) - 1) & U)
    keys = [0] * 622
    keys[0], keys[1] = key0, key1
    for i in range(3, 624):
        j = i - 1
        if j >= 622:
            continue
        keys[j] = (x[i] - (base.BASE[i] ^ base.mix(x[i-1], base.M1)) - j) & U
    assert keys[-1] != 0
    seed = int.from_bytes(b"".join(k.to_bytes(4, "little") for k in keys), "little")
    assert base.actual_register(seed) == tuple(register)
    return seed


def find_source_622():
    rng = random.Random(20261103)
    source = base.initialized_register(base.initial_solution(base.basis))
    assert source[2] == 0xE32E1557 and source[622] == 0xBBD5A4AB
    for trial in range(1000):
        s621 = rng.getrandbits(31)
        s623 = 0x04710790 | (rng.getrandbits(1) << 31)
        b = base.basis.copy()
        assert impose_word(b, 621, s621) and impose_word(b, 623, s623)
        x623 = (((s623 + 623) & U) ^ base.mix(source[622], base.M2)) & U
        x622 = (((source[622] + 622) & U) ^ base.mix(s621, base.M2)) & U
        key0 = (x623 - (base.BASE[623] ^ base.mix(x622, base.M1))) & U
        a = base.BASE[1] ^ base.mix(base.BASE[0], base.M1)
        y = (key0 + a) & U
        c = (source[2] + 2) & U
        required = ((base.BASE[2] ^ base.mix(y, base.M1))
                    - (y ^ base.mix(x623, base.M1))) & U
        d = base.mix(s623, base.M2)
        for q in invert_q(c, required):
            s1 = ((q ^ d) - 1) & U
            extended = b.copy()
            if not impose_word(extended, 1, s1):
                continue
            reg = base.initialized_register(base.initial_solution(extended))
            assert reg[1] == s1 and reg[621] == s621 and reg[623] == s623
            seed = seeded622(reg)
            assert base.selected_from_actual_seed(seed) is not None
            print("PASS source-consistent exact 622-word initializer, trial", trial)
            return extended
    raise AssertionError("No 622-word source-consistent witness in 1000 trials")


def complete_target(source_basis, target):
    enlarged = source_basis.copy()
    for lane in range(4):
        stateword = base.untemper(
            int.from_bytes(target[lane * 4:lane * 4 + 4], "little")
        )
        for bit, expr in enumerate(base.expressions[624 + 951 + lane]):
            rem = base.reduce((expr << 1) | ((stateword >> bit) & 1), enlarged)
            assert rem != 1
            if rem > 1:
                enlarged[rem.bit_length() - 1] = rem
    assert len(enlarged) - len(source_basis) == 128
    reg = base.initialized_register(base.initial_solution(enlarged))
    seed = seeded622(reg)
    assert base.selected_from_actual_seed(seed) == target
    return True


def main():
    source_basis = find_source_622()
    for selected in (bytes(16), bytes([0xFF]) * 16, bytes([0xAA]) * 16):
        assert complete_target(source_basis, selected)
        print("PASS original intact 132/132 and prescribed K04 128/128",
              selected.hex().upper())
    print("RESULT: under unverified p951/CPython622 architecture the selected"
          " 128-bit target remains arbitrary; no true K04 bytes recovered")


if __name__ == "__main__":
    main()
