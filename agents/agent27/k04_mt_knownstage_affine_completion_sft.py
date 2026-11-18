"""Complete an MT packet from sparse packets under oracle-known native positions.

Synthetic positive only. The historical PS-0417 physical-coupon position is unknown.
Run: python agents/agent27/k04_mt_knownstage_affine_completion_sft.py
"""
import hashlib
import random
from k04_mt_knownstage_holdout_rank_sft import (
    linear_mt_vectors, source_packet_count, starts_from_gaps, untemper,
)

MASK = bytes.fromhex("8556C8CB6140A7F9A5123AC7571BEE1C")


def temper(value):
    value ^= value >> 11
    value ^= (value << 7) & 0x9D2C5680
    value ^= (value << 15) & 0xEFC60000
    value ^= value >> 18
    return value & 0xFFFFFFFF


def pack_tempered(native_128):
    return b"".join(
        temper((native_128 >> (32 * k)) & 0xFFFFFFFF).to_bytes(4, "little")
        for k in range(4)
    )


def xor(a, b):
    return bytes(x ^ y for x, y in zip(a, b))


class LinearModel:
    def __init__(self):
        self.basis = {}
        self.dependent_rows = 0

    def add(self, vector, result):
        while vector:
            bit = vector.bit_length()
            old = self.basis.get(bit)
            if old is None:
                self.basis[bit] = (vector, result)
                return True
            vector ^= old[0]
            result ^= old[1]
        self.dependent_rows += 1
        if result:
            raise ValueError("stage equations inconsistent with packet values")
        return False

    def reduce(self, vector):
        result = 0
        while vector:
            bit = vector.bit_length()
            old = self.basis.get(bit)
            if old is None:
                return vector, result
            vector ^= old[0]
            result ^= old[1]
        return 0, result


def model_observations(symbolic, positions, native, withheld, mutation=None, true_starts=None):
    model = LinearModel()
    first_dependency = None
    row_index = 0
    for packet, start in enumerate(positions):
        if packet == withheld:
            continue
        for offset in range(4):
            word = native[(true_starts or positions)[packet] + offset]
            for bit, equation in enumerate(symbolic[start + offset]):
                observed = (word >> bit) & 1
                if mutation == row_index:
                    observed ^= 1
                newly_independent = model.add(equation, observed)
                if first_dependency is None and not newly_independent:
                    first_dependency = row_index
                row_index += 1
    return model, first_dependency


def target_affine(model, symbolic, position):
    """Return a native 128-bit affine base and independent unknown XOR masks."""
    remainder_basis = {}
    masks = []
    base = 0
    for target_bit, equation in enumerate(
        item for word in symbolic[position:position + 4] for item in word
    ):
        remainder, known = model.reduce(equation)
        coeff = 0
        while remainder:
            lead = remainder.bit_length()
            existing = remainder_basis.get(lead)
            if existing is not None:
                remainder ^= existing[0]
                coeff ^= existing[1]
            else:
                index = len(masks)
                remainder_basis[lead] = (remainder, 1 << index)
                masks.append(0)
                coeff ^= 1 << index
                break
        if known:
            base |= 1 << target_bit
        for j in range(len(masks)):
            if coeff & (1 << j):
                masks[j] |= 1 << target_bit
    return base, masks


def native_at(native, start):
    return sum(native[start + k] << (32 * k) for k in range(4))


def run_fixture(schedule_mode, max_rank, max_fixtures=256):
    rng = random.Random(20261118)
    symbolic = linear_mt_vectors(133 * 9)
    for fixture in range(max_fixtures):
        positions = starts_from_gaps(rng, 133, schedule_mode)
        stage = positions[129]
        generated = random.Random(20261118000 + fixture)
        native = [untemper(generated.getrandbits(32)) for _ in range(positions[-1] + 4)]
        model, dep = model_observations(symbolic, positions, native, 129)
        base, masks = target_affine(model, symbolic, stage)
        if len(masks) > max_rank:
            continue
        actual_native = native_at(native, stage)
        diff = actual_native ^ base
        coef_basis = {}
        for j, mask in enumerate(masks):
            vector, coefs = mask, 1 << j
            while vector:
                lead = vector.bit_length()
                old = coef_basis.get(lead)
                if old is None:
                    coef_basis[lead] = (vector, coefs)
                    break
                vector ^= old[0]
                coefs ^= old[1]
            assert vector != 0
        real_nonce = 0
        while diff:
            lead = diff.bit_length()
            vec, cof = coef_basis[lead]
            diff ^= vec
            real_nonce ^= cof
        candidate_native = base
        for j, mask in enumerate(masks):
            if real_nonce & (1 << j):
                candidate_native ^= mask
        assert candidate_native == actual_native
        true_key = xor(pack_tempered(actual_native), MASK)
        commitment = hashlib.sha256(true_key).digest()
        hits = []
        if len(masks) <= 12:
            for bits in range(1 << len(masks)):
                coupon_native = base
                for j, mask in enumerate(masks):
                    if bits & (1 << j):
                        coupon_native ^= mask
                key = xor(pack_tempered(coupon_native), MASK)
                if hashlib.sha256(key).digest() == commitment:
                    hits.append((bits, coupon_native, key))
            assert len(hits) == 1
            assert hits[0] == (real_nonce, actual_native, true_key)
        else:
            assert hashlib.sha256(xor(pack_tempered(candidate_native), MASK)).digest() == commitment
        assert model.dependent_rows > 0 and dep is not None
        try:
            model_observations(symbolic, positions, native, 129, mutation=dep)
        except ValueError:
            altered_contradicted = True
        else:
            altered_contradicted = False
        assert altered_contradicted
        wrong_stages = starts_from_gaps(random.Random(51209), 133, schedule_mode)
        try:
            model_observations(symbolic, wrong_stages, native, 129, true_starts=positions)
        except ValueError:
            wrong_stage_contradicted = True
        else:
            wrong_stage_contradicted = False
        print("SYNTHETIC_PASS", "schedule", schedule_mode, "fixture", fixture,
              "observations", len(model.basis), "dependent", model.dependent_rows,
              "rank_bits", len(masks), "candidate_space", 1 << len(masks),
              "known_planted_freebits", real_nonce, "full_commitment_enumerated", bool(hits),
              "negative_control_inconsistency", altered_contradicted,
              "wrong_stage_contradicted", wrong_stage_contradicted)
        print("planted_coupon_hex", pack_tempered(actual_native).hex().upper())
        print("planted_key_hex", true_key.hex().upper())
        return
    raise AssertionError("No suitable planted rank fixture in search window")


if __name__ == "__main__":
    assert source_packet_count() == 132
    for family in ("3-or-4", "2-or-5"):
        run_fixture(family, max_rank=1 if family == "3-or-4" else 32,
                    max_fixtures=256)
    print("REAL_K04: no historical stage map, no recovered coupon")
