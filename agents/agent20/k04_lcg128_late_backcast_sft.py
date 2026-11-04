"""Source-only modular-128 affine backcast of the selected K04 coupon."""
from pathlib import Path
import hashlib
import json
import os
import re

root = Path(os.environ.get("H17_RESOURCE_ROOT", Path(__file__).resolve().parents[2] / "resources"))
spool = (root / "evidence/print/spool-reconstruction.log").read_bytes()
route_bytes = (root / "evidence/recovery-routing.json").read_bytes()
accept_bytes = (root / "acceptance.json").read_bytes()
assert hashlib.sha256(spool).hexdigest() == "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"
assert hashlib.sha256(route_bytes).hexdigest() == "f8fcbca73d23bf1066edb88c088f89cd24cf22e7c78a4a412166254a4764d8a5"
assert hashlib.sha256(accept_bytes).hexdigest() == "681739241b757b471acca4c0fef9d9d97e9493883887736d5db3b92bfb0c137f"
route, acceptance = json.loads(route_bytes), json.loads(accept_bytes)
mask = bytes.fromhex(route["K04"]["masked_component"])
target = acceptance["slot_sha256"]["K04"]

regular, late = [], []
for line in spool.decode("utf-8").splitlines():
    found = re.search(r"PAYLOAD=([0-9A-F]{32})", line)
    if found is None:
        continue
    if "+00:00 " in line:
        regular.append(bytes.fromhex(found[1]))
    else:
        # Do not even decode the unverified selected copied payload.
        late.append((line, None if "2026-10-03T18:02:00Z" in line else bytes.fromhex(found[1])))
assert len(regular) == 128 and len(late) == 5
assert "PS-261003-0417" in late[1][0] and late[1][1] is None
assert "PS-261003-0417" in late[0][0] and "PS-261003-0417" in late[2][0]
assert "PS-261003-0448" in late[3][0] and "PS-261003-0420" in late[4][0]

modulus = 1 << 128
bitmask = modulus - 1

def view(b, shape):
    if shape == 0:
        return b
    if shape == 1:
        return b[::-1]
    if shape == 2:
        return b[12:] + b[8:12] + b[4:8] + b[:4]
    if shape == 3:
        return b[0:4][::-1] + b[4:8][::-1] + b[8:12][::-1] + b[12:16][::-1]
    if shape == 4:
        return bytes(b[4*j+i] for i in range(4) for j in range(4))
    if shape == 5:
        return bytes(int(f"{x:08b}"[::-1], 2) for x in b)
    if shape == 6:
        return bytes(int(f"{x:08b}"[::-1], 2) for x in b[::-1])
    raise ValueError(shape)

def backcast(y0, y1, y2):
    """Fit x[next]=a*x+b mod 2^128, then predict two prior whole states."""
    d0 = (y1 - y0) & bitmask
    d1 = (y2 - y1) & bitmask
    if d0 == 0:
        return []
    t = (d0 & -d0).bit_length() - 1
    if d1 & ((1 << t) - 1) or t > 12:
        return []
    modulus_reduced = 1 << (128 - t)
    first_a = ((d1 >> t) * pow(d0 >> t, -1, modulus_reduced)) % modulus_reduced
    output = []
    for k in range(1 << t):
        a = first_a + k * modulus_reduced
        if not (a & 1):
            continue
        b = (y1 - a * y0) & bitmask
        inv = pow(a, -1, modulus)
        prior1 = ((y0 - b) * inv) & bitmask
        prior2 = ((prior1 - b) * inv) & bitmask
        assert (a * prior2 + b) & bitmask == prior1
        assert (a * prior1 + b) & bitmask == y0
        output.append((prior2, prior1))
    return output

# A generated stream must exactly recover two hidden original states.
for a, b, x0 in ((0x4435, 0xDEADBEEF, 0xBADABADA),
                 (0xB135, 0xFFFF, 0x123456789ABCDEF)):
    xs = [x0]
    for _ in range(5):
        xs.append((a * xs[-1] + b) & bitmask)
    assert (xs[1], xs[2]) in backcast(xs[3], xs[4], xs[5])

normal_checks = 0
normal_hits = []
for shape in range(7):
    values = [int.from_bytes(view(v, shape), "big") for v in regular]
    for i in range(len(values) - 4):
        guesses = backcast(*values[i+2:i+5])
        normal_checks += len(guesses)
        if (values[i], values[i+1]) in guesses:
            normal_hits.append((shape, i))

original_tests = []
for shape in range(7):
    values = [int.from_bytes(view(raw, shape), "big") if raw is not None else None
              for _, raw in late]
    for previous, selected in backcast(*values[2:5]):
        coupon = view(selected.to_bytes(16, "big"), shape)  # All seven views are involutions.
        component = bytes(a ^ b for a, b in zip(coupon, mask))
        original_tests.append({
            "view": shape,
            "prior_1801_exact": previous == values[0],
            "candidate_K04": component.hex().upper(),
            "original_sha256_match": hashlib.sha256(component).hexdigest() == target,
        })

assert normal_checks == 424 and not normal_hits
assert len(original_tests) == 7
assert not any(x["prior_1801_exact"] or x["original_sha256_match"] for x in original_tests)
print(json.dumps({
    "regular_original_heldout_packet_predictions": normal_checks,
    "regular_two_prior_packet_exact_matches": normal_hits,
    "original_late_K04_complete_checks": len(original_tests),
    "distinct_late_K04_candidates": len({x["candidate_K04"] for x in original_tests}),
    "late_candidate_results": original_tests
}, indent=2))
