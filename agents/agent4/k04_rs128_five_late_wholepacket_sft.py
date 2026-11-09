"""H-17 K04 source-first 128+5 systematic/evaluation RS candidate reconstruction.

Read-only SFT. Standard-library Python, Windows-compatible; invokes no external tools.
The selected 18:02 ACK2 payload is excluded from all candidate construction.
"""
import hashlib
import itertools
import json
import random
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SPOOL = ROOT / "resources" / "evidence" / "print" / "spool-reconstruction.log"
SPOOL_SHA = "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"
MASK = bytes.fromhex("8556C8CB6140A7F9A5123AC7571BEE1C")
TARGET = "930a52a1bab97ca2966332137c99e99298ea6182fb32ab63a3421dfb4fd8c9e0"
PATTERN = re.compile(
    r"JOB=(\S+) ATTEMPT=(\d+) STATE=(\S+) CLASS=(\S+) "
    r"PAYLOAD=([0-9A-F]{32}) DEST=(\S+)"
)


def mul(a: int, b: int, poly: int) -> int:
    result = 0
    for _ in range(8):
        if b & 1:
            result ^= a
        a <<= 1
        if a & 256:
            a ^= poly
        b >>= 1
    return result


def power(a: int, n: int, poly: int) -> int:
    result = 1
    while n:
        if n & 1:
            result = mul(result, a, poly)
        a = mul(a, a, poly)
        n >>= 1
    return result


def lagrange_coefficients(xs: list[int], xt: int, poly: int) -> list[int]:
    assert len(xs) == len(set(xs)) and xt not in xs
    answer = []
    for i, x in enumerate(xs):
        numerator = denominator = 1
        for j, y in enumerate(xs):
            if i != j:
                numerator = mul(numerator, xt ^ y, poly)
                denominator = mul(denominator, x ^ y, poly)
        answer.append(mul(numerator, power(denominator, 254, poly), poly))
    return answer


def combine(coefficients: list[int], packets: list[bytes], poly: int) -> bytes:
    out = bytearray(16)
    for c, packet in zip(coefficients, packets):
        for j, b in enumerate(packet):
            out[j] ^= mul(c, b, poly)
    return bytes(out)


def parity(data: list[int], poly: int, alpha: int, root: int) -> list[int]:
    generator = [1]
    for i in range(root, root + 5):
        element = power(alpha, i, poly)
        nxt = [0] * (len(generator) + 1)
        for j, c in enumerate(generator):
            nxt[j] ^= c
            nxt[j + 1] ^= mul(c, element, poly)
        generator = nxt
    work = data.copy() + [0] * 5
    for j, c in enumerate(data):
        # The division dividend is mutable: later iterations use updated bytes.
        q = work[j]
        for k in range(1, 6):
            work[j + k] ^= mul(q, generator[k], poly)
    return work[-5:]


def evaluate_high(coefficients: list[int], x: int, poly: int) -> int:
    out = 0
    for c in coefficients:
        out = mul(out, x, poly) ^ c
    return out


def test_synthetic() -> None:
    rand = random.Random(991007)
    for poly in (0x11D, 0x11B):
        assert all(mul(i, power(i, 254, poly), poly) == 1 for i in range(1, 256))
        xs = list(range(133))
        coeff = [rand.randrange(256) for _ in range(128)]
        actual = [evaluate_high(coeff[::-1], x, poly) for x in xs]
        for t in range(128, 133):
            weights = lagrange_coefficients(xs[:128], xs[t], poly)
            predicted = 0
            for weight, value in zip(weights, actual[:128]):
                predicted ^= mul(weight, value, poly)
            assert predicted == actual[t]

        columns = [[rand.randrange(256) for _ in range(128)] for _ in range(16)]
        decoded = [parity(col, poly, 3, 1) for col in columns]
        for col, checks in zip(columns, decoded):
            for root in range(1, 6):
                assert evaluate_high(
                    col + checks, power(3, root, poly), poly
                ) == 0
        coupon = bytes(check[1] for check in decoded)
        component = bytes(x ^ y for x, y in zip(coupon, MASK))
        planted = hashlib.sha256(component).hexdigest()
        assert planted == hashlib.sha256(
            bytes(x ^ y for x, y in zip(coupon, MASK))
        ).hexdigest()


def main() -> None:
    original = SPOOL.read_bytes()
    assert hashlib.sha256(original).hexdigest() == SPOOL_SHA
    rows = []
    for line in original.decode("ascii").splitlines():
        if not line or line.startswith("#"):
            continue
        match = PATTERN.search(line)
        assert match, line
        job, attempt, state, kind, payload, dest = match.groups()
        rows.append((job, int(attempt), state, kind, bytes.fromhex(payload), dest))
    assert len(rows) == 133
    assert all(
        row[0] == f"PS-261003-{300 + i:04d}" and row[1] == 1 and row[2] == "ACK"
        for i, row in enumerate(rows[:128])
    )
    assert [(r[0], r[1], r[2]) for r in rows[128:]] == [
        ("PS-261003-0417", 1, "REQUESTED"),
        ("PS-261003-0417", 2, "ACK"),
        ("PS-261003-0417", 3, "REQUESTED"),
        ("PS-261003-0448", 1, "ACK"),
        ("PS-261003-0420", 2, "ACK"),
    ]
    test_synthetic()

    evaluations = []
    for poly in (0x11D, 0x11B):
        for coordinate in ("integer", "pow2", "pow3", "pow5"):
            xs = (
                list(range(133)) if coordinate == "integer" else
                [power(int(coordinate[3:]), i, poly) for i in range(133)]
            )
            if len(xs) != len(set(xs)):
                continue
            for reverse in (False, True):
                source = [r[4] for r in (rows[:128][::-1] if reverse else rows[:128])]
                predicted = [
                    combine(lagrange_coefficients(xs[:128], x, poly), source, poly)
                    for x in xs[128:]
                ]
                evaluations.append((f"eval:{poly:03x}:{coordinate}:{int(reverse)}", predicted))

    systematic = []
    for poly, alpha, root, reverse, reverse_checks in itertools.product(
        (0x11D, 0x11B), (2, 3, 5), (0, 1), (False, True), (False, True)
    ):
        source = [r[4] for r in (rows[:128][::-1] if reverse else rows[:128])]
        column_checks = [
            parity([packet[j] for packet in source], poly, alpha, root)
            for j in range(16)
        ]
        predicted = [bytes(check[j] for check in column_checks) for j in range(5)]
        if reverse_checks:
            predicted.reverse()
        name = f"sys:{poly:03x}:{alpha}:{root}:{int(reverse)}:{int(reverse_checks)}"
        systematic.append((name, predicted))

    all_models = evaluations + systematic
    original_hits = []
    source_full_hits = 0
    best_source_byte_score = 0
    best_source_model = None
    for model, predicted in all_models:
        # Only other ACK rows 3 and 4 serve as complete source holdouts.
        control_score = sum(
            sum(x == y for x, y in zip(predicted[i], rows[128 + i][4]))
            for i in (3, 4)
        )
        source_full_hits += sum(predicted[i] == rows[128 + i][4] for i in (3, 4))
        if control_score > best_source_byte_score:
            best_source_byte_score, best_source_model = control_score, model
        component = bytes(a ^ b for a, b in zip(predicted[1], MASK))
        if hashlib.sha256(component).hexdigest() == TARGET:
            original_hits.append({"model": model, "coupon": predicted[1].hex().upper(),
                                  "component": component.hex().upper()})
    print(json.dumps({
        "original_spool_sha256": SPOOL_SHA,
        "ordinary_packets": 128,
        "later_rows": 5,
        "complete_source_ack_holdouts_per_model": 2,
        "evaluation_models": len(evaluations),
        "systematic_models": len(systematic),
        "total_complete_K04_comparisons": len(all_models),
        "source_full_ack_hits": source_full_hits,
        "best_total_matching_bytes_across_two_ack_controls": best_source_byte_score,
        "best_model": best_source_model,
        "original_K04_hits": original_hits,
        "planted_interpolation_and_systematic_controls": "PASS"
    }, indent=2))



# Whole 128-bit symbol extension. Unlike the byte-lane RS code above, each
# printer PAYLOAD is one GF(2^128) symbol in x^128+x^7+x^2+x+1.
def _mul128(a: int, b: int) -> int:
    out = 0
    while b:
        if b & 1:
            out ^= a
        b >>= 1
        a <<= 1
        if a >> 128:
            a ^= (1 << 128) | 0x87
    return out


def _pow128(a: int, n: int) -> int:
    out = 1
    while n:
        if n & 1:
            out = _mul128(out, a)
        a = _mul128(a, a)
        n >>= 1
    return out


def _batch_inverse128(values: list[int]) -> list[int]:
    prefixes = [1]
    for value in values:
        assert value
        prefixes.append(_mul128(prefixes[-1], value))
    inverse = _pow128(prefixes[-1], (1 << 128) - 2)
    out = [0] * len(values)
    for i in range(len(values) - 1, -1, -1):
        out[i] = _mul128(inverse, prefixes[i])
        inverse = _mul128(inverse, values[i])
    return out


def _gf128_weights(xs: list[int], target_x: int) -> list[int]:
    assert len(xs) == 128 and len(set(xs)) == 128 and target_x not in xs
    # Lagrange basis: P(t) / ((t+x_i) P'(x_i)), addition is XOR.
    denominators = [1] * 128
    for i in range(128):
        for j in range(i):
            term = xs[i] ^ xs[j]
            denominators[i] = _mul128(denominators[i], term)
            denominators[j] = _mul128(denominators[j], term)
    inverse_denom = _batch_inverse128(denominators)
    deltas = [target_x ^ x for x in xs]
    inverse_deltas = _batch_inverse128(deltas)
    product = 1
    for term in deltas:
        product = _mul128(product, term)
    return [
        _mul128(product, _mul128(a, b))
        for a, b in zip(inverse_denom, inverse_deltas)
    ]


def run_gf128_extension() -> None:
    import datetime

    raw = SPOOL.read_bytes()
    assert hashlib.sha256(raw).hexdigest() == SPOOL_SHA
    lines = [
        line for line in raw.decode("ascii").splitlines()
        if PATTERN.search(line)
    ]
    assert len(lines) == 133
    rows = [PATTERN.search(line) for line in lines]
    assert all(m is not None for m in rows)
    assert rows[129].group(1) == "PS-261003-0417"
    assert rows[129].group(2) == "2"
    assert rows[129].group(3) == "ACK"
    assert rows[129].group(4) == "RECOVER"

    # Selected row 129's copied payload is never decoded or consulted.
    ordinary = [bytes.fromhex(m.group(5)) for m in rows[:128]]
    ack_controls = {
        3: bytes.fromhex(rows[131].group(5)),
        4: bytes.fromhex(rows[132].group(5)),
    }
    times = [
        datetime.datetime.fromisoformat(
            line.split(" ", 1)[0].replace("Z", "+00:00")
        )
        for line in lines
    ]
    clock_mins = [
        int((stamp - times[0]).total_seconds() // 60)
        for stamp in times
    ]
    assert clock_mins[:128] == [i * 5 for i in range(128)]
    assert clock_mins[128:] == [661, 662, 663, 684, 685]

    families = [
        ("sequential", list(range(128)), list(range(128, 133))),
        ("clock_minutes", clock_mins[:128], clock_mins[128:]),
    ]
    original_matches = []
    synthetic_checks = 0
    complete_source_holdout_hits = 0
    max_joint_holdout_bytes = 0
    cases = 0
    rng = random.Random(20261109)
    synthetic_coeff = [rng.getrandbits(128) for _ in range(12)]

    def eval_synthetic(t: int) -> int:
        accum = 0
        for coefficient in reversed(synthetic_coeff):
            accum = _mul128(accum, t) ^ coefficient
        return accum

    for label, xs, targets in families:
        projections = [_gf128_weights(xs, t) for t in targets]
        planted_source = [eval_synthetic(x) for x in xs]
        for target_x, coeff in zip(targets, projections):
            planted_target = 0
            for weight, datum in zip(coeff, planted_source):
                planted_target ^= _mul128(weight, datum)
            assert planted_target == eval_synthetic(target_x)
            synthetic_checks += 1

        for backward in (False, True):
            inputs = ordinary[::-1] if backward else ordinary
            for endian in ("big", "little"):
                packed = [int.from_bytes(p, endian) for p in inputs]
                predicted = []
                for coefficients in projections:
                    value = 0
                    for weight, datum in zip(coefficients, packed):
                        value ^= _mul128(weight, datum)
                    predicted.append(value.to_bytes(16, endian))
                source_byte_score = 0
                for idx, control in ack_controls.items():
                    source_byte_score += sum(
                        a == b for a, b in zip(predicted[idx], control)
                    )
                    complete_source_holdout_hits += predicted[idx] == control
                max_joint_holdout_bytes = max(
                    max_joint_holdout_bytes, source_byte_score
                )
                coupon = predicted[1]
                component = bytes(a ^ b for a, b in zip(coupon, MASK))
                if hashlib.sha256(component).hexdigest() == TARGET:
                    original_matches.append({
                        "family": label,
                        "reverse_source": backward,
                        "endian": endian,
                        "coupon": coupon.hex().upper(),
                        "component": component.hex().upper(),
                    })
                cases += 1

    assert synthetic_checks == 10 and cases == 8
    print(json.dumps({
        "extension": "whole128_GF2_power128_original_clock_or_sequential",
        "full_original_K04_comparisons": cases,
        "source_ACK_comparisons": 2 * cases,
        "source_full_ACK_hits": complete_source_holdout_hits,
        "max_matching_bytes_combined_two_ACK_controls": max_joint_holdout_bytes,
        "original_K04_hits": original_matches,
        "synthetic_polynomial_extrapolation_controls": synthetic_checks,
    }, indent=2))

if __name__ == "__main__":
    main()
    run_gf128_extension()
