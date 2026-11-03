"""H-17 K04: arbitrary 128-bit GF(2) packet-transition reconstruction.

This tests a homogeneous Y=A*X or affine Y=A*X XOR b common
producer for entire printed 16-byte packets. The selected source buffer
is never decoded. Intact later-packet transitions are full-packet
holdouts. A generic random source with a planted missing packet is the
positive control. Original acceptance and route are read-only.
Run: python agents/agent48/k04_packet_gf2_affine_sft.py
"""
import hashlib
import json
import random
import re
from pathlib import Path

SOURCE_SHA = "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"
ROOT = Path(__file__).resolve().parents[2] / "resources"
N = 128
SELECTED = 129


class StateMap:
    def __init__(self, affine):
        self.affine = affine
        self.basis = {}
        self.conflicts = []

    def row(self, x):
        assert 0 <= x < (1 << N)
        return x | (1 << N if self.affine else 0)

    def add(self, x, y, label):
        assert 0 <= y < (1 << N)
        v, out = self.row(x), y
        while v:
            p = v.bit_length() - 1
            if p in self.basis:
                previous_v, previous_out = self.basis[p]
                v ^= previous_v
                out ^= previous_out
            else:
                self.basis[p] = (v, out)
                return
        if out:
            self.conflicts.append(label)

    def predict(self, x):
        v, out = self.row(x), 0
        while v:
            p = v.bit_length() - 1
            if p not in self.basis:
                return None
            previous_v, previous_out = self.basis[p]
            v ^= previous_v
            out ^= previous_out
        return out


def original_packets():
    raw = (ROOT / "evidence/print/spool-reconstruction.log").read_bytes()
    assert hashlib.sha256(raw).hexdigest() == SOURCE_SHA
    rows = [s for s in raw.decode("ascii").splitlines() if "PAYLOAD=" in s]
    assert len(rows) == 133
    assert rows[SELECTED].startswith(
        "2026-10-03T18:02:00Z JOB=PS-261003-0417 ATTEMPT=2 STATE=ACK CLASS=RECOVER ")
    out = []
    for i, row in enumerate(rows):
        if i == SELECTED:
            out.append(None)
        else:
            m = re.search(r"PAYLOAD=([0-9A-F]{32})(?:\s|$)", row)
            assert m is not None
            out.append(int(m.group(1), 16))
    return out


def source_pairs(values):
    return [(i, values[i], values[i + 1]) for i in range(132)
            if i not in (128, 129)]


def planted_states(affine):
    rng = random.Random(0x20261103 + int(affine))
    columns = [rng.getrandbits(N) for _ in range(N)]
    bias = rng.getrandbits(N) if affine else 0
    assert (not affine) or bias != 0

    def advance(x):
        output = bias
        while x:
            bit = x & -x
            output ^= columns[bit.bit_length() - 1]
            x ^= bit
        return output

    values = [rng.getrandbits(N)]
    for _ in range(132):
        values.append(advance(values[-1]))
    return values


def test(values, affine):
    pairs = source_pairs(values)
    assert len(pairs) == 130
    model = StateMap(affine)
    for i, x, y in pairs[:128]:
        model.add(x, y, i)
    assert not model.conflicts and len(model.basis) == 128
    holdouts = [(i, model.predict(x) == y) for i, x, y in pairs[128:]]
    joint = StateMap(affine)
    for i, x, y in pairs:
        joint.add(x, y, i)
    result = {
        "affine": affine, "training_rank": len(model.basis),
        "all_source_conflicts": joint.conflicts,
        "heldout_packet_predictions": holdouts,
        "selected_packet_predictable": model.predict(values[128]) is not None,
    }
    if not affine and values[SELECTED] is None:
        packet = model.predict(values[128])
        assert packet is not None
        route = json.loads((ROOT / "evidence/recovery-routing.json").read_text())
        acceptance = json.loads((ROOT / "acceptance.json").read_text())
        candidate = packet ^ int(route["K04"]["masked_component"], 16)
        digest = hashlib.sha256(candidate.to_bytes(16, "big")).hexdigest()
        result["predicted_packet"] = f"{packet:032X}"
        result["complete_K04_component"] = f"{candidate:032X}"
        result["untouched_K04_commitment_match"] = (
            digest == acceptance["slot_sha256"]["K04"])
        result["two_step_original_row130_match"] = (
            model.predict(packet) == values[130])
    return result


def main():
    original = original_packets()
    outcomes = [test(original, affine) for affine in (False, True)]
    assert all(x["all_source_conflicts"] == [130, 131] for x in outcomes)
    assert all(x["heldout_packet_predictions"] == [(130, False), (131, False)]
               for x in outcomes)
    assert outcomes[0]["complete_K04_component"] == (
        "4FBA87F353CD6DDECC4217E3A9866EFB")
    assert outcomes[0]["untouched_K04_commitment_match"] is False
    assert outcomes[0]["two_step_original_row130_match"] is False
    assert outcomes[1]["selected_packet_predictable"] is False

    synthetic = []
    for affine in (False, True):
        state = planted_states(affine)
        model = StateMap(affine)
        for i, x, y in source_pairs(state)[:128]:
            model.add(x, y, i)
        assert not model.conflicts
        assert model.predict(state[128]) == state[129]
        assert model.predict(state[130]) == state[131]
        assert model.predict(state[131]) == state[132]
        assert model.predict(state[131]) != (state[132] ^ 1)
        synthetic.append({"affine": affine, "selected_reconstruction": "PASS",
                          "heldout_predictions": "PASS",
                          "tampered_last_packet": "REJECTED"})
    print(json.dumps({
        "original_spool_sha256": SOURCE_SHA,
        "selected_payload_decoded": False,
        "original_tests": outcomes,
        "synthetic_controls": synthetic,
        "result": "NO_K04_ACCEPTANCE_COMMON_PACKET_STAGE_FALSIFIED",
    }, indent=2))


if __name__ == "__main__":
    main()
