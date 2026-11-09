"""H-17 K08 source-calibrated 128-bit permuted wire transport.

Hypothesis: the complete HMAC16 of a known Nxx caption was sent as a
printer packet PS-(0300+xx), with a fixed arbitrary 128-bit permutation
and arbitrary per-wire XOR pad. The N23 final-margin text is withheld:
invert the physical PS-0323 packet to predict an entire K08 component.

Needs numpy and scipy; both are used for exact minimum-cost bipartite
assignment (Hungarian algorithm), not heuristic optimization.
"""
from hashlib import sha256
from pathlib import Path
from scipy.optimize import linear_sum_assignment
import hmac
import json
import numpy as np
import re

ROOT = Path(__file__).resolve().parents[2] / "resources"
NOTE = ROOT / "evidence/crew/noticeboard-and-desk-notes.txt"
SPOOL = ROOT / "evidence/print/spool-reconstruction.log"
assert sha256(NOTE.read_bytes()).hexdigest() == (
    "13f2318ccc54f35b590a2d76b3a80244fe24d70f0699c67c05858e8b8983c5cb"
)
assert sha256(SPOOL.read_bytes()).hexdigest() == (
    "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"
)
route = json.loads((ROOT / "evidence/recovery-routing.json").read_text())
nonce = bytes.fromhex(route["K08"]["desk_nonce"])
original_target = json.loads((ROOT / "acceptance.json").read_text())["slot_sha256"]["K08"]

chunks = re.findall(
    r"(?ms)^N(\d\d) / [^\n]+\n(.*?)(?=^N\d\d / |\Z)", NOTE.read_text()
)
assert len(chunks) == 24
notes = {int(k): v.strip() for k, v in chunks}

spool = {}
for line in SPOOL.read_text().splitlines():
    match = re.search(
        r"JOB=PS-261003-(\d+) ATTEMPT=1 STATE=ACK .*?"
        r"PAYLOAD=([0-9A-F]{32})", line
    )
    if match and 301 <= int(match[1]) <= 324:
        spool[int(match[1]) - 300] = bytes.fromhex(match[2])
assert len(spool) == 24

def normalize(text):
    return " ".join(re.sub(r"[^a-z0-9\s]", " ", text.lower()).split())

def reduced_note(text, view):
    if view == "after_colon" and ":" in text:
        text = text.split(":", 1)[1]
    return hmac.new(nonce, normalize(text).encode("utf-8"), sha256).digest()[:16]

def bits(block):
    return np.unpackbits(np.frombuffer(block, dtype=np.uint8))

def pack(bit_vector):
    return np.packbits(bit_vector.astype(np.uint8)).tobytes()

def fit_wiring(inputs, outputs):
    """Minimum Hamming error bit permutation with one XOR bit per output wire."""
    xs = inputs.T.astype(np.int16)
    ys = outputs.T.astype(np.int16)
    errors = np.count_nonzero(ys[:, None, :] != xs[None, :, :], axis=2)
    cost = np.minimum(errors, inputs.shape[0] - errors)
    output_lanes, source_lanes = linear_sum_assignment(cost)
    pad = (errors[output_lanes, source_lanes] > inputs.shape[0] / 2).astype(np.uint8)
    return output_lanes, source_lanes, pad, int(cost[output_lanes, source_lanes].sum()), cost

def invert(observed, output_lanes, source_lanes, pad):
    recovered = np.zeros(128, dtype=np.uint8)
    recovered[source_lanes] = observed[output_lanes] ^ pad
    return recovered

# N23 is the target locator, never a training or historical control text.
known = [i for i in range(1, 25) if i != 23]
train, heldout = known[:20], known[20:]
assert len(train) == 20 and len(heldout) == 3
rng = np.random.default_rng(20261109)
planted_permutation = rng.permutation(128)
planted_pad = rng.integers(0, 2, 128, dtype=np.uint8)

for view in ("full_body", "after_colon"):
    source = np.array([bits(reduced_note(notes[i], view)) for i in train], dtype=np.uint8)
    actual = np.array([bits(spool[i]) for i in train], dtype=np.uint8)
    observed_n02 = reduced_note(notes[2], "after_colon").hex().upper()
    assert observed_n02 == "BF889359B0303F2B2B2FD96AE841210B"
    rows, cols, pad, training_errors, cost = fit_wiring(source, actual)
    possible_exact_edges = int((cost == 0).sum())
    heldout_errors = sum(
        np.count_nonzero(
            bits(spool[i])[rows] != (bits(reduced_note(notes[i], view))[cols] ^ pad)
        )
        for i in heldout
    )
    predicted = pack(invert(bits(spool[23]), rows, cols, pad))
    accepted = sha256(predicted).hexdigest() == original_target

    # Plant an exact arbitrary 128-bit bit-permutation+pad issuer using the
    # actual source texts, and require real role-named holdouts and full target
    # inversion to succeed without source-shaped synthetic easy data.
    synthetic_printer = source[:, planted_permutation] ^ planted_pad
    r, c, p, residual, planted_cost = fit_wiring(source, synthetic_printer)
    assert residual == 0
    assert all(
        np.array_equal(
            bits(reduced_note(notes[i], view))[planted_permutation] ^ planted_pad,
            bits(reduced_note(notes[i], view))[c] ^ p
        )
        for i in heldout
    )
    blinded = bits(reduced_note(notes[23], view))[planted_permutation] ^ planted_pad
    recovered_planted = pack(invert(blinded, r, c, p))
    assert recovered_planted == reduced_note(notes[23], view)

    print("VIEW", view, "20-source training bit errors", training_errors,
          "exact candidate wire edges", possible_exact_edges,
          "3-whole-source heldout bit errors", heldout_errors,
          "of", 384,
          "full K08 component candidate", predicted.hex().upper(),
          "original acceptance PASS", accepted,
          "synthetic 3-whole-source + full-target positive PASS")
    if accepted:
        print("RECOVERED_K08", predicted.hex().upper())
        raise SystemExit(0)
