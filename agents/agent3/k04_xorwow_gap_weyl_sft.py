"""H17 K04, exact 32-bit Weyl lifting and fourword XORWOW retry gap.

Hypothesis: 18:01 REQUESTED, missing 18:02 ACK and 18:03 REQUESTED
are consecutive 4x32-bit output frames of canonical five-word XORWOW.
Original sources, route, acceptance and canonical key are all read-only.
Run: python agents/agent3/k04_xorwow_gap_weyl_sft.py
"""
from pathlib import Path
import hashlib
import itertools
import json

ROOT = Path(__file__).resolve().parents[2] / "resources"
SPOOL = ROOT / "evidence" / "print" / "spool-reconstruction.log"
MASK32 = (1 << 32) - 1
WEYL = 362437
STAGES = (0, 1, 2, 3, 8, 9, 10, 11)
LAYOUTS = list(itertools.product((0, 1), repeat=3))
REVERSE = bytes(int(f"{i:08b}"[::-1], 2) for i in range(256))


def xorwow_step(state):
    x, y, z, w, v = state
    t = x ^ (x >> 2)
    out = ((v ^ (v << 4)) ^ (t ^ (t << 1))) & MASK32
    return (y, z, w, v, out), out


def relations():
    """Derive 96 GF2 parity checks and recover all 128 missing output bits."""
    output_rows = [0] * (12 * 32)
    for original_bit in range(160):
        state = tuple((1 << (original_bit % 32)) if i == original_bit // 32 else 0 for i in range(5))
        for stage in range(12):
            state, native = xorwow_step(state)
            for bit in range(32):
                if (native >> bit) & 1:
                    output_rows[stage * 32 + bit] |= 1 << original_bit
    pivots = {}
    redundant = []
    for j, stage in enumerate(STAGES):
        for bit in range(32):
            vector = output_rows[stage * 32 + bit]
            combination = 1 << (j * 32 + bit)
            while vector:
                p = vector.bit_length() - 1
                if p not in pivots:
                    pivots[p] = (vector, combination)
                    break
                a, b = pivots[p]
                vector ^= a
                combination ^= b
            if vector == 0:
                redundant.append(combination)
    assert len(pivots) == 160 and len(redundant) == 96

    def project(vector):
        witness = 0
        while vector:
            p = vector.bit_length() - 1
            assert p in pivots, "Underconstrained missing native output"
            a, b = pivots[p]
            vector ^= a
            witness ^= b
        return witness

    projections = [
        project(output_rows[stage * 32 + bit])
        for stage in range(4, 8)
        for bit in range(32)
    ]
    return redundant, projections


def parity(trace, native_words):
    return sum(
        (((trace >> (32 * j)) & MASK32) & word).bit_count()
        for j, word in enumerate(native_words)
    ) & 1


def encode(words, endian, reverse_words, reverse_bits):
    ordered = words[::-1] if reverse_words else words
    raw = b"".join(word.to_bytes(4, "big" if endian else "little") for word in ordered)
    return raw.translate(REVERSE) if reverse_bits else raw


def decode(raw, endian, reverse_words, reverse_bits):
    if reverse_bits:
        raw = raw.translate(REVERSE)
    words = [
        int.from_bytes(raw[i:i + 4], "big" if endian else "little")
        for i in range(0, 16, 4)
    ]
    return words[::-1] if reverse_words else words


def original_inputs():
    raw = SPOOL.read_bytes()
    assert hashlib.sha256(raw).hexdigest() == "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"
    lines = raw.decode("ascii").splitlines()

    def get(clock, attempt, state):
        prefix = (
            f"2026-10-03T{clock}:00Z JOB=PS-261003-0417 "
            f"ATTEMPT={attempt} STATE={state} CLASS=RECOVER PAYLOAD="
        )
        selected = [line for line in lines if line.startswith(prefix)]
        assert len(selected) == 1
        payload = bytes.fromhex(selected[0].split("PAYLOAD=")[1].split()[0])
        assert len(payload) == 16
        return payload

    first = get("18:01", 1, "REQUESTED")
    excluded = get("18:02", 2, "ACK")
    last = get("18:03", 3, "REQUESTED")
    assert first.hex().upper() == "CD3E4F216ADB2FB180DA2AA90B33F7A4"
    assert excluded.hex().upper() == "A9A9DC5731A5E2AE879C47215C2559D5"
    assert last.hex().upper() == "44D53DFC29D7943A95D89371DA58EC64"
    route = json.loads((ROOT / "evidence" / "recovery-routing.json").read_text())
    acceptance = json.loads((ROOT / "acceptance.json").read_text())
    mask = bytes.fromhex(route["K04"]["masked_component"])
    target = bytes.fromhex(acceptance["slot_sha256"]["K04"])
    assert mask.hex().upper() == "8556C8CB6140A7F9A5123AC7571BEE1C"
    assert target.hex() == "930a52a1bab97ca2966332137c99e99298ea6182fb32ab63a3421dfb4fd8c9e0"
    assert hashlib.sha256(bytes(a ^ b for a, b in zip(excluded, mask))).digest() != target
    return first, last, mask, target


def native_output(observed, d0):
    return [
        (value - d0 - WEYL * stage) & MASK32
        for value, stage in zip(observed, STAGES)
    ]


def solve_weyl(observed, checks):
    """Exact 2-adic lifting; all checked parity bits depend on <= current bit."""
    by_high_bit = [[] for _ in range(32)]
    for equation in checks:
        largest_bit = max(i % 32 for i in range(256) if equation >> i & 1)
        by_high_bit[largest_bit].append(equation)
    assert [len(group) for group in by_high_bit] == [0, 0, 0, 0] + [3] * 26 + [6, 12]
    survivors = [0]
    counts = []
    for bit in range(32):
        next_survivors = []
        for low in survivors:
            for guess in (low, low | (1 << bit)):
                native = native_output(observed, guess)
                if all(parity(eq, native) == 0 for eq in by_high_bit[bit]):
                    next_survivors.append(guess)
        survivors = next_survivors
        counts.append(len(survivors))
        if not survivors:
            break
    return survivors, counts


def reconstruct(observed, d0, projections):
    native = native_output(observed, d0)
    words = []
    for i in range(4):
        state_word = sum(
            parity(projections[i * 32 + bit], native) << bit
            for bit in range(32)
        )
        words.append((state_word + d0 + WEYL * (4 + i)) & MASK32)
    return words


def component(physical, mask):
    return bytes(a ^ b for a, b in zip(physical, mask))


def main():
    checks, projections = relations()
    first, last, mask, target = original_inputs()
    planted_state = (0x12345678, 0xABCDEF19, 0xDEADBEEF, 0xCAFEBABE, 0x875B29D4)
    planted_d0 = 0x00ABCDEF
    sequence = []
    for stage in range(12):
        planted_state, native = xorwow_step(planted_state)
        sequence.append((native + planted_d0 + WEYL * stage) & MASK32)
    for layout in LAYOUTS:
        left = encode(sequence[:4], *layout)
        right = encode(sequence[8:], *layout)
        observed = decode(left, *layout) + decode(right, *layout)
        guesses, _ = solve_weyl(observed, checks)
        assert guesses == [planted_d0], (layout, guesses)
        selected = reconstruct(observed, planted_d0, projections)
        assert selected == sequence[4:8]
        actual = component(encode(selected, *layout), mask)
        planted_target = hashlib.sha256(component(encode(sequence[4:8], *layout), mask)).digest()
        assert hashlib.sha256(actual).digest() == planted_target
    print("PASS eight genuine complete 4-word XORWOW synthetic coupon recovery controls")

    matches = []
    for layout in LAYOUTS:
        observed = decode(first, *layout) + decode(last, *layout)
        guesses, prefix_counts = solve_weyl(observed, checks)
        print("ORIGINAL_VIEW", layout, "FULL_WEYL_ROOTS", len(guesses), "LOWBIT_BRANCH_COUNTS", prefix_counts)
        for d0 in guesses:
            coupon = encode(reconstruct(observed, d0, projections), *layout)
            reduced = component(coupon, mask)
            if hashlib.sha256(reduced).digest() == target:
                matches.append((layout, d0, coupon.hex().upper(), reduced.hex().upper()))
        assert not guesses, (layout, guesses)
    assert not matches
    print("ORIGINAL SOURCE NO MATCH: all 8 layouts exclude every 32-bit Weyl state; K04 still missing")


if __name__ == "__main__":
    main()
