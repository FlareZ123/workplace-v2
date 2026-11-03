"""K04: minute-clock GF(2^128) affine packet emitter with original source holdouts.

Test a source-time hypothesis: x[t+1] = g*x[t] XOR c in GF(2^128).
Solve the exact quadratic from intact 18:01 and18:03 packets to infer
the missing 18:02 packet. Then predict intact 18:24->18:25 (1 minute)
and18:03->18:24 (21 minutes). Original selected copied coupon excluded.
"""
import hashlib
import itertools
import json
import random
import re
from pathlib import Path

from k04_gf128_secondorder_middle_sft import mul, roots, viewed, unviewed

ROOT = Path(__file__).resolve().parents[2] / "resources"
PIN = "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"


def source():
    raw = (ROOT / "evidence/print/spool-reconstruction.log").read_bytes()
    assert hashlib.sha256(raw).hexdigest() == PIN
    rows = [x for x in raw.decode("ascii").splitlines() if "PAYLOAD=" in x]
    assert len(rows) == 133
    assert rows[129].startswith(
        "2026-10-03T18:02:00Z JOB=PS-261003-0417 ATTEMPT=2 STATE=ACK CLASS=RECOVER "
    )
    result = {}
    for i, timestamp in (
        (128, "18:01:00Z"), (130, "18:03:00Z"),
        (131, "18:24:00Z"), (132, "18:25:00Z"),
    ):
        assert timestamp in rows[i]
        m = re.search(r"PAYLOAD=([0-9A-F]{32})(?:\s|$)", rows[i])
        assert m is not None
        result[i] = int(m.group(1), 16)
    return result


def infer(x01, x03, x24, x25, constant):
    # x03 = g^2*x01 XOR g*c XOR c, a quadratic in g.
    candidates = []
    for g in roots(x01, constant, x03 ^ constant) or []:
        selected = mul(g, x01) ^ constant
        assert mul(g, selected) ^ constant == x03
        predicted_25 = mul(g, x24) ^ constant
        predicted_24 = x03
        for _ in range(21):
            predicted_24 = mul(g, predicted_24) ^ constant
        candidates.append(
            (g, selected, predicted_25 == x25, predicted_24 == x24)
        )
    return candidates


def planted_controls(mask):
    rng = random.Random(0x20261103)
    count = 0
    for constant in (0, mask):
        for _ in range(12):
            g, initial = rng.getrandbits(128), rng.getrandbits(128)
            values = [initial]
            for _ in range(24):
                values.append(mul(g, values[-1]) ^ constant)
            options = infer(values[0], values[2], values[23],
                            values[24], constant)
            assert any(middle == values[1] and a and b
                       for _, middle, a, b in options)
            count += 1
    return count


def main():
    original = source()
    route = json.loads((ROOT / "evidence/recovery-routing.json").read_text())
    mask = int(route["K04"]["masked_component"], 16)
    acceptance = json.loads((ROOT / "acceptance.json").read_text())
    target = acceptance["slot_sha256"]["K04"]
    models = options = no_roots = one_minute = gap21 = hits = 0
    all_candidates = set()
    sample = None
    for flags in itertools.product((False, True), repeat=3):
        x01, x03, x24, x25 = (
            viewed(original[i], *flags) for i in (128, 130, 131, 132)
        )
        for offset_name, constant in (
            ("zero", 0), ("original_route_mask", viewed(mask, *flags))
        ):
            models += 1
            solutions = infer(x01, x03, x24, x25, constant)
            no_roots += not solutions
            for _, middle, held1, held21 in solutions:
                options += 1
                one_minute += held1
                gap21 += held21
                selected = unviewed(middle, *flags)
                key = selected ^ mask
                component = f"{key:032X}"
                all_candidates.add(component)
                yes = hashlib.sha256(
                    key.to_bytes(16, "big")
                ).hexdigest() == target
                hits += yes
                if sample is None:
                    sample = {
                        "serializer": list(flags),
                        "offset": offset_name,
                        "complete_predicted_K04": component,
                        "original_K04_commitment_match": yes,
                    }
    assert models == 16 and options == 14 and no_roots == 5
    assert one_minute == gap21 == hits == 0
    assert len(all_candidates) == 14
    assert sample["complete_predicted_K04"] == (
        "5C273E1D17F86CF8E89514FA4F14D0CB"
    )
    controls = planted_controls(mask)
    assert controls == 24
    print(json.dumps({
        "source_SHA256": PIN,
        "selected_ACK2_payload_decoded": False,
        "source_time_alignment": "18:01->18:03, 18:24->18:25",
        "field": "GF(2^128), x^128+x^7+x^2+x+1",
        "frozen_models": models,
        "models_with_no_quadratic_root": no_roots,
        "complete_candidate_assignments": options,
        "distinct_predicted_K04": len(all_candidates),
        "intact_18_24_to_18_25_predictions_correct": one_minute,
        "intact_18_03_to_18_24_predictions_correct": gap21,
        "original_K04_SHA_matches": hits,
        "genuinely_seeded_clock_positive": controls,
        "example": sample,
        "result": "NO_MATCH_TIMESTAMP_STEP_EMITTER",
    }, indent=2))


if __name__ == "__main__":
    main()
