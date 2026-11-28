#!/usr/bin/env python3
"""K04 source-pinned three CRC-good recorder cohorts -> seven future MT donor words.

Bounded 5,308,416 full-coupon original checks; requires the published
Agent39 seven-donor source-projection library. Selected ACK2 original
PAYLOAD is withheld before decoding, not used to choose a hypothesis.
No payloads, reconstructed coupon bytes, or commitment diagnostics printed.
"""
import hashlib
import importlib.util
import itertools
import json
import re
import struct
import zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
E = ROOT / "resources/evidence"
spec = importlib.util.spec_from_file_location(
    "affine", ROOT / "agents/agent39/k04_p951_seven_donor_affine_sft.py"
)
affine = importlib.util.module_from_spec(spec)
spec.loader.exec_module(affine)

spool = (E / "print/spool-reconstruction.log").read_bytes()
recorder = (E / "recorder/trip-recorder.raw").read_bytes()
assert hashlib.sha256(spool).hexdigest() == "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"
assert hashlib.sha256(recorder).hexdigest() == "5ebc6204ed773102237dd287772de96d19740e163b49b4075537d937888657ba"
fields = re.findall(rb"PAYLOAD=([0-9A-F]{32})", spool)
assert len(fields) == len(affine.prior.STARTS) == 133
assert affine.prior.STARTS[129] == 951

# Do not decode or use the selected row129 bytes.
packets = [b"" if i == 129 else bytes.fromhex(f.decode())
           for i, f in enumerate(fields)]
expressions = affine.express()
affine.positive_controls(expressions)  # 7 genuine CPython seed-length controls
coupon_map = affine.make_coupon_map(expressions, packets)

assert len(recorder) == 16 + 88*24
cohorts = {}
for j in range(88):
    b = recorder[16+24*j:16+24*(j+1)]
    timestamp, node, event, latch, seq = struct.unpack_from("<IHBBI", b)
    if node == 49 and event == 82 and (
        200 <= seq <= 203 or 300 <= seq <= 303 or 990 <= seq <= 993
    ):
        assert zlib.crc32(b[:20]) & 0xffffffff == int.from_bytes(b[20:24], "little")
        cohorts.setdefault(seq // 100, []).append((seq, b[12:16]))
assert set(cohorts) == {2, 3, 9}
assert all(len(v) == 4 for v in cohorts.values())
blocks = {k: [x for _, x in sorted(v)] for k, v in cohorts.items()}

routing = json.loads((E / "recovery-routing.json").read_text())
accept = json.loads((ROOT / "resources/acceptance.json").read_text())
mask = bytes.fromhex(routing["K04"]["masked_component"])
target = bytes.fromhex(accept["slot_sha256"]["K04"])

checked = 0
hits = 0
for order in itertools.permutations(sorted(blocks)):
    for modes in itertools.product(range(4), repeat=3):
        transformed = []
        for cohort, mode in zip(order, modes):
            byteorder = "big" if mode & 1 else "little"
            is_tempered = bool(mode & 2)
            vals = [int.from_bytes(x, byteorder) for x in blocks[cohort]]
            if is_tempered:
                vals = [affine.prior.untemper(x) for x in vals]
            transformed.append(vals)
        # First quartet supplies 3 future native words (1179..1181);
        # second and third supply 2 each (1347..1348; 1574..1575).
        for first in itertools.permutations(transformed[0], 3):
            for middle in itertools.permutations(transformed[1], 2):
                for last in itertools.permutations(transformed[2], 2):
                    selected = affine.select_native(coupon_map, first + middle + last)
                    for byteorder in ("little", "big"):
                        for reverse in (False, True):
                            words = selected[::-1] if reverse else selected
                            payload = b"".join(affine.temper(x).to_bytes(4, byteorder)
                                               for x in words)
                            component = bytes(x ^ y for x, y in zip(payload, mask))
                            checked += 1
                            if hashlib.sha256(component).digest() == target:
                                hits += 1
    print("COHORT_ORDER_COMPLETE", order, "cumulative_checks", checked,
          "accepted", hits, flush=True)

assert checked == 6 * (4 ** 3) * 24 * 12 * 12 * 4 == 5308416
assert hits == 0
print("FINAL", "genuine_MT_controls", 7, "complete_K04", checked,
      "original_commitment_matches", hits)
