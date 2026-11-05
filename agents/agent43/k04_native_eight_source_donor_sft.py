"""Conditional K04 reconstruction from two complete native-MT donor quartets.

An exact source-only p951 model predicts the four missing printer words
from eight native MT words. This tests pairs of original 16-byte blocks
as hypothetical eight-word donors, with selected spool row129 excluded
as a fitting observation. No archive source authenticates this bridge.
"""
from pathlib import Path
from itertools import permutations, product
import hashlib
import json
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "agents" / "agent49"))
import k04_p951_symbolic_basis as mt

source, symbolic = mt.source(ROOT / "resources")
assert source.rank == 15365
stages = (328, 329, 330, 331, 724, 725, 726, 727)

# Each donor observation contributes a formal symbolic bit. All 256 donor
# bit equations are independent of the intact original printer observations.
for i, stage in enumerate(stages):
    for bit, expr in enumerate(mt.get(symbolic, stage)):
        source.insert(expr, 1 << (1 + 32 * i + bit))
assert source.rank == 15621

target_formulas = []
for stage in range(951, 955):
    projected = [source.predict(expr) for expr in mt.get(symbolic, stage)]
    assert all(value is not None for value in projected)
    target_formulas.append(projected)

route = json.loads((ROOT / "resources/evidence/recovery-routing.json").read_text())
mask = bytes.fromhex(route["K04"]["masked_component"])
acceptance = json.loads((ROOT / "resources/acceptance.json").read_text())
target_digest = bytes.fromhex(acceptance["slot_sha256"]["K04"])

# All source-derived block values are in evidence-derived selector order.
# Late sources are speculative statistical donors, not causal earlier keys.
donors = {
    "K01_ink": "049AAB2E1CDE7A82CD7C60234303C91A",
    "K02_raw": "E1A5E474BAD7E853A2E8C71D3317D507",
    "K03_serials": "D7DAD6BC9714519B7DAD0AD4BE8E87FD",
    "K05_latches": "FF8B78200A56E8586DCDA00EF01E4572",
    "K06_cabinet": "5DBF40EE52FAAED9A536D3326CF0D95A",
    "K07_raw": "8947CEDCB9CC73BAB7E87BE63302C5C9",
    "mask": mask.hex(),
    "nonce": "5F933DA6A1BD03C32DA5CBC25344F497",
    "samejob_LABEL117": "E1E60D5F6B6DD2225FA6D5A2A63AD932",
    "samejob_REQUEST128": "CD3E4F216ADB2FB180DA2AA90B33F7A4",
    "samejob_REQUEST130": "44D53DFC29D7943A95D89371DA58EC64",
}
donors = {name: bytes.fromhex(value) for name, value in donors.items()}
assert all(len(value) == 16 for value in donors.values())


def parse_donor(raw, endian, reverse_words, inverse_temper):
    words = [int.from_bytes(raw[i:i + 4], endian) for i in range(0, 16, 4)]
    if reverse_words:
        words.reverse()
    if inverse_temper:
        words = [mt.untemper(word) for word in words]
    return words


def complete_coupon(left, right):
    donor_bits = sum(word << (32 * i) for i, word in enumerate(left + right))
    selected = []
    for formula in target_formulas:
        native = sum(
            (((term & 1) ^ (((term >> 1) & donor_bits).bit_count() & 1)) << bit)
            for bit, term in enumerate(formula)
        )
        tempered = mt.temper([(native >> bit) & 1 for bit in range(32)])
        selected.append(sum(value << bit for bit, value in enumerate(tempered)))
    return b"".join(word.to_bytes(4, "little") for word in selected)


models = 0
distinct = set()
hits = []
planted = None
views = product(("little", "big"), (False, True), (False, True),
                ("little", "big"), (False, True), (False, True))
views = list(views)

for left_name, right_name in permutations(donors, 2):
    for left_endian, left_reverse, left_untemper, right_endian, right_reverse, right_untemper in views:
        left = parse_donor(donors[left_name], left_endian, left_reverse, left_untemper)
        right = parse_donor(donors[right_name], right_endian, right_reverse, right_untemper)
        coupon = complete_coupon(left, right)
        component = bytes(x ^ y for x, y in zip(coupon, mask))
        if planted is None:
            planted = component
        models += 1
        distinct.add(component)
        if hashlib.sha256(component).digest() == target_digest:
            hits.append((left_name, right_name, component.hex()))

assert models == len(donors) * (len(donors) - 1) * 64 == 7040
assert len(distinct) == models
assert not hits
# End-to-end synthetic planted original commitment must recover one whole value.
synthetic_digest = hashlib.sha256(planted).digest()
assert sum(hashlib.sha256(value).digest() == synthetic_digest for value in distinct) == 1

print(f"source_rank=15365, independent_native_donor_bits=256")
print(f"complete_k04_candidates={models}, distinct={len(distinct)}, original_hits={len(hits)}")
print("synthetic whole-component commitment: PASS")
print("K04 remains unresolved; every tested donor-to-native-stage bridge is hypothetical.")
