"""PTW417 original full-word contiguous-MT carrier hypothesis, source-only.

Run at repository root: python agents/agent40/k04_ptw417_consecutive_sft.py
The published p951 MT model is conditional. No selected K04 ACK, mask or hash is used.
"""
import hashlib
import importlib.util
import itertools
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DEP = ROOT / "agents/agent35/k04_p951_minimal_future_donor_sft.py"
spec = importlib.util.spec_from_file_location("h17_mt_source", DEP)
g = importlib.util.module_from_spec(spec)
spec.loader.exec_module(g)
resources = ROOT / "resources"
spool = (resources / "evidence/print/spool-reconstruction.log").read_bytes()
receipts = (resources / "evidence/maintenance/seal-receipts.jsonl").read_bytes()
assert hashlib.sha256(spool).hexdigest() == "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"
assert hashlib.sha256(receipts).hexdigest() == "c00944558636fbcc7e91b81e8e838ffd13fcd5a30d121b41951888766a8a0e32"
payload = [bytes.fromhex(x.decode()) for x in re.findall(rb"PAYLOAD=([A-F0-9]{32})", spool)]
assert len(payload) == len(g.STARTS) == 133 and g.STARTS[129] == 951

# IMPORTANT: symbolic origin must PRECEDE all tested negative indices.
# Using the dependency's origin=-160 for indices around -900 would trigger
# negative Python list indexing and a false target-rank result.
ORIGIN = -1100
symbols = g.states(count=3000)
source = {}
source_affine = {}

def insert_affine(expr, value, system):
    eq = (expr << 1) | (value & 1)
    while eq:
        pivot = eq.bit_length() - 1
        if pivot == 0:
            return False
        if pivot not in system:
            system[pivot] = eq
            return True
        eq ^= system[pivot]
    return True

for row, (at, bytes16) in enumerate(zip(g.STARTS, payload)):
    if row == 129:
        continue
    for lane in range(4):
        native = g.untemper(int.from_bytes(bytes16[4*lane:4*lane+4], "little"))
        for bit, expr in enumerate(symbols[at+lane-ORIGIN]):
            g.add(expr, source)
            assert insert_affine(expr, (native >> bit) & 1, source_affine)
assert len(source) == len(source_affine) == 15365

def original_word_fits(at, serial, original=None):
    assert at >= ORIGIN
    system = (source_affine if original is None else original).copy()
    native = g.untemper(int.from_bytes(bytes.fromhex(serial[3:]), "little"))
    for bit, expr in enumerate(symbols[at-ORIGIN]):
        if not insert_affine(expr, (native >> bit) & 1, system):
            return None
    return system

seals = [json.loads(x) for x in receipts.splitlines()]
for permit, at in (("PTW-405", -964), ("PTW-412", -944), ("PTW-414", -937)):
    serial = next(r["serial"] for r in seals if r["permit"] == permit)
    assert original_word_fits(at, serial) is not None
# A deliberately flipped original printer bit must contradict source equations.
wrong = source_affine.copy()
known = g.untemper(int.from_bytes(payload[0][:4], "little"))
assert not insert_affine(symbols[0-ORIGIN][0], (known & 1) ^ 1, wrong)

late = [r for r in seals if r["permit"] == "PTW-417"]
assert len(late) == 17

def layouts():
    for variant in ("with_asset", "without_asset"):
        selected = [r for r in late if not (
            r["revision"] == 1 and r["bay"] == "A"
            and (("asset" in r) != (variant == "with_asset"))
        )]
        assert len(selected) == 16
        for grouping in ("revision", "bay"):
            for bay_order in itertools.permutations("ABCD"):
                if grouping == "revision":
                    key = lambda z: (z["revision"], bay_order.index(z["bay"]))
                else:
                    key = lambda z: (bay_order.index(z["bay"]), z["revision"])
                yield variant, grouping, "".join(bay_order), sorted(selected, key=key)

target = [b for at in range(951, 955) for b in symbols[at-ORIGIN]]
assert g.rank_overlap([], target, source) == (128, 0, 0)
full = []
checked = 0
max_prefix = 0
for first in range(-1020, -800):
    addresses = range(first, first+16)
    native_expr = [e for at in addresses for e in symbols[at-ORIGIN]]
    target_gain = g.rank_overlap(native_expr, target, source)[2]
    for variant, grouping, bay_order, records in layouts():
        checked += 1
        state = source_affine.copy()
        depth = 0
        for at, record in zip(addresses, records):
            state = original_word_fits(at, record["serial"], state)
            if state is None:
                break
            depth += 1
        max_prefix = max(max_prefix, depth)
        if depth == 16:
            full.append((first, target_gain, variant, grouping, bay_order))
assert checked == 21120 and len(full) == 46 and max_prefix == 16
assert {rec[1] for rec in full} == {0}
assert {rec[0] for rec in full} == {-870, -869, -868}
print("Original printer-only affine rank:", len(source_affine))
print("Contiguous 16-full-word PTW417 assignments checked:", checked)
print("Exactly source-compatible assignments:", len(full))
print("Survivors start indices:", sorted({r[0] for r in full}))
print("All surviving source-compatible layouts selected quotient gain: 0/128")
print("No independently established PTW417 start index or historical producer.")
print("No authenticated K04 byte or accepted complete candidate.")
