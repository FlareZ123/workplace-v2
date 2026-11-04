"""Test xoroshiro128++ as a generator spanning the 18:01 / 18:03
exceptional Z-formatted printer records. Read-only. The missing 18:02 ACK2
payload is withheld entirely. Uses standard xoroshiro128++ 1.0 transition.

Run from repo root: python agents/agent23/k04_xoroshiro128pp_two_request_sft.py --view 0
Requires pip install z3-solver. Model and holdout assumptions are conjectural.
"""
import argparse
import hashlib
import json
from pathlib import Path
from z3 import BitVec, BitVecVal, RotateLeft, RotateRight, Solver, sat, unsat

R = Path(__file__).resolve().parents[2] / "resources"
SHA = "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"
N = (1 << 64) - 1


def rot(v, shift):
    return ((v << shift) | (v >> (64 - shift))) & N


def step(a, b):
    out = (rot((a + b) & N, 17) + a) & N
    t = a ^ b
    return out, (rot(a, 49) ^ t ^ ((t << 21) & N)) & N, rot(t, 28)


def smtstep(a, b):
    out = RotateLeft(a + b, 17) + a
    t = a ^ b
    return out, RotateLeft(a, 49) ^ t ^ (t << 21), RotateLeft(t, 28)


def encode(words, view):
    endian = "little" if view & 1 else "big"
    if view & 2:
        words = words[::-1]
    return b"".join(w.to_bytes(8, endian) for w in words)


def decode(block, view):
    endian = "little" if view & 1 else "big"
    words = [int.from_bytes(block[i:i+8], endian) for i in (0, 8)]
    return words[::-1] if view & 2 else words


def solve(words0, words3, timeout_ms=180000, return_target=False):
    # First output directly expresses b in terms of a and observed word0:
    # y0 = rotl(a+b,17) + a (mod 2^64).
    a = BitVec("initial_s0", 64)
    b = RotateRight(BitVecVal(words0[0], 64) - a, 17) - a
    s = Solver()
    s.set(timeout=timeout_ms)
    out, a1, b1 = smtstep(a, b)
    s.add(out == BitVecVal(words0[0], 64))
    out, a2, b2 = smtstep(a1, b1)
    s.add(out == BitVecVal(words0[1], 64))
    out2, a3, b3 = smtstep(a2, b2)
    out3, a4, b4 = smtstep(a3, b3)
    out, a5, b5 = smtstep(a4, b4)
    s.add(out == BitVecVal(words3[0], 64))
    out, _, _ = smtstep(a5, b5)
    s.add(out == BitVecVal(words3[1], 64))

    status = s.check()
    if status == unsat:
        return {"status": "UNSAT"}
    if status != sat:
        return {"status": "UNKNOWN", "reason": s.reason_unknown()}

    model = s.model()
    initial = (model.eval(a).as_long(), model.eval(b).as_long())
    values = []
    a0, b0 = initial
    for _ in range(6):
        out, a0, b0 = step(a0, b0)
        values.append(out)
    assert values[:2] == list(words0)
    assert values[4:] == list(words3)
    return {"status": "SAT", "state": [f"{w:016X}" for w in initial],
            "missing_words": [f"{w:016X}" for w in values[2:4]],
            "missing_values": values[2:4] if return_target else None}


def load():
    spool = (R / "evidence/print/spool-reconstruction.log").read_bytes()
    assert hashlib.sha256(spool).hexdigest() == SHA
    rows = {}
    for line in spool.decode("ascii").splitlines():
        if not line.startswith("2026"):
            continue
        timestamp, *tokens = line.split()
        fields = dict(x.split("=", 1) for x in tokens)
        rows[timestamp] = fields
    assert len(rows) == 133
    req1, selected, req3 = (rows["2026-10-03T18:01:00Z"],
                            rows["2026-10-03T18:02:00Z"],
                            rows["2026-10-03T18:03:00Z"])
    assert all(r["JOB"] == "PS-261003-0417" for r in (req1, selected, req3))
    assert [(r["STATE"], r["ATTEMPT"]) for r in (req1, selected, req3)] == [
        ("REQUESTED", "1"), ("ACK", "2"), ("REQUESTED", "3")]
    # Deliberately do not decode selected["PAYLOAD"].
    return bytes.fromhex(req1["PAYLOAD"]), bytes.fromhex(req3["PAYLOAD"])


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--view", type=int, choices=range(4), required=True)
    p.add_argument("--timeout-ms", type=int, default=180000)
    args = p.parse_args()
    view = args.view
    assert encode(decode(bytes(range(16)), view), view) == bytes(range(16))
    before, after = load()

    # Real-seeded six-consecutive-output positive with 2 middle outputs hidden.
    synthetic = []
    s0, s1 = 0x5D1DE1A5CAFEBEEF, 0x17A5B3CB69A1CBCA
    for _ in range(6):
        o, s0, s1 = step(s0, s1)
        synthetic.append(o)
    planted = solve(synthetic[:2], synthetic[4:], args.timeout_ms, True)
    assert planted["status"] == "SAT", planted
    assert planted["missing_values"] == synthetic[2:4], planted
    print("GENUINE_SEEDED_COMPLETE_TWO_REQUEST_BRIDGE_PASS", flush=True)

    words0 = decode(before, view)
    words3 = decode(after, view)
    outcome = solve(words0, words3, args.timeout_ms, True)
    result = {"view": view, "original_source": outcome["status"],
              "original_synthetic_control": "PASS"}
    if outcome["status"] == "SAT":
        payload = encode(outcome["missing_values"], view)
        mask = bytes.fromhex(json.loads((R / "evidence/recovery-routing.json").read_text())
                             ["K04"]["masked_component"])
        component = bytes(a ^ b for a, b in zip(payload, mask))
        expected = json.loads((R / "acceptance.json").read_text())["slot_sha256"]["K04"]
        result["conditional_coupon"] = payload.hex().upper()
        result["K04_original_commitment_PASS"] = hashlib.sha256(component).hexdigest() == expected
        result["K04_component_if_pass"] = component.hex().upper() if result["K04_original_commitment_PASS"] else None
    if outcome["status"] == "UNKNOWN":
        result["reason"] = outcome["reason"]
    print(json.dumps(result, sort_keys=True), flush=True)


if __name__ == "__main__":
    main()
