"""K04 original-source-only alternative spool stage: four nonadjacent native MT words.

Run from repo root: python agents/agent3/k04_p951_noncontiguous_coupon_sft.py
Uses Agent2's SHA-pinned original-printer p951 closure; excludes selected row129
from generator reconstruction. Tests the untouched acceptance commitment.
"""
from hashlib import sha256
from itertools import combinations, product
from pathlib import Path
import importlib.util
import json

ROOT = Path(__file__).resolve().parents[2]
MODULE = ROOT / "agents/agent2/20261102_k04_multicarrier_p951_sft.py"
spec = importlib.util.spec_from_file_location("p951_orig", MODULE)
p951 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(p951)
word, known, offset = p951.source_closure(ROOT / "resources")
assert all(known[offset + 951 + i] == 0 for i in range(4))

route = json.loads((ROOT / "resources/evidence/recovery-routing.json").read_text())
commitments = json.loads((ROOT / "resources/acceptance.json").read_text())
mask = bytes.fromhex(route["K04"]["masked_component"])
target = bytes.fromhex(commitments["slot_sha256"]["K04"])
assert target.hex() == "930a52a1bab97ca2966332137c99e99298ea6182fb32ab63a3421dfb4fd8c9e0"

positions = [i for i in range(919, 981) if known[offset + i] == 0xffffffff]
assert len(positions) == 41
values = {i: word[offset + i] for i in positions}
views = {(s, e): {i: (p951.temper(v) if s == "tempered" else v).to_bytes(4, e)
                  for i, v in values.items()}
         for s in ("native", "tempered") for e in ("little", "big")}
plant = (919, 920, 921, 924)
planted_bytes = b"".join(views["tempered", "little"][i] for i in plant)
synthetic_digest = sha256(bytes(a ^ b for a, b in zip(planted_bytes, mask))).digest()

total = originals = positives = 0
for kind in ("native", "tempered"):
    lo, hi = views[kind, "little"], views[kind, "big"]
    for selection in combinations(positions, 4):
        for ordered in (selection, selection[::-1]):
            for endian_bits in product((0, 1), repeat=4):
                raw = b"".join((hi if flag else lo)[i]
                               for i, flag in zip(ordered, endian_bits))
                reduced = bytes(a ^ b for a, b in zip(raw, mask))
                digest = sha256(reduced).digest()
                total += 1
                if digest == synthetic_digest:
                    positives += 1
                if digest == target:
                    originals += 1
                    print("ORIGINAL_PASS", kind, selection, ordered, endian_bits,
                          reduced.hex().upper())
assert total == 6481280 and positives == 1
print("K04 source-known donor positions", len(positions),
      "complete candidates", total, "original matches", originals,
      "synthetic positive", positives)
assert originals == 0
