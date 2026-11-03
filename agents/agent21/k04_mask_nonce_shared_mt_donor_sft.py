"""Original H17 K04 target-reaching mask/nonce MT donor hypothesis.

Read-only test of a speculative shared-generator relationship. The original
selected ESC-N row129 is withheld from Agent49's p951 source basis.
Run as Python 3 from any working directory; no dependencies outside stdlib.
"""
import hashlib
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MODEL = ROOT / "agents/agent49/k04_p951_symbolic_basis.py"
spec = importlib.util.spec_from_file_location("h17_p951_model", MODEL)
model = importlib.util.module_from_spec(spec)
spec.loader.exec_module(model)
source = ROOT / "resources"
basis, words = model.source(source)
assert basis.rank == 15365

def source_reduce(vector):
    residual = 0
    known = 0
    while vector:
        pivot = vector.bit_length() - 1
        if pivot in basis.rows:
            other, value = basis.rows[pivot]
            vector ^= other
            known ^= value
        else:
            vector ^= 1 << pivot
            residual |= 1 << pivot
    return residual, known

# Cache the source quotient before evaluating any proposed donor value.
quotient = [[source_reduce(v) for v in vector] for vector in words]
target = [quotient[model.STARTS[129] + j - model.ORIGIN] for j in range(4)]

def temper(x):
    x ^= x >> 11
    x ^= (x << 7) & 0x9D2C5680
    x ^= (x << 15) & 0xEFC60000
    x ^= x >> 18
    return x & 0xFFFFFFFF

def reconstruct(observed, stage):
    """Return ("CONTRADICTION"|"PARTIAL"|"FULL", payload or None, known bits)."""
    local = {}
    for lane in range(4):
        for bit, (residual0, srcbit) in enumerate(quotient[stage + lane - model.ORIGIN]):
            residual = residual0
            rhs = ((observed[lane] >> bit) & 1) ^ srcbit
            while residual:
                pivot = residual.bit_length() - 1
                if pivot not in local:
                    local[pivot] = (residual, rhs)
                    break
                other, value = local[pivot]
                residual ^= other
                rhs ^= value
            if not residual and rhs:
                return "CONTRADICTION", None, 0

    native_words = []
    known_count = 0
    for lane in range(4):
        native = 0
        for bit, (residual0, srcbit) in enumerate(target[lane]):
            residual = residual0
            rhs = srcbit
            while residual:
                pivot = residual.bit_length() - 1
                if pivot not in local:
                    break
                other, value = local[pivot]
                residual ^= other
                rhs ^= value
            if not residual:
                known_count += 1
                native |= rhs << bit
        native_words.append(native)
    if known_count != 128:
        return "PARTIAL", None, known_count
    payload = b"".join(temper(w).to_bytes(4, "little") for w in native_words)
    return "FULL", payload, known_count

routing = json.loads((source / "evidence/recovery-routing.json").read_text())
targets = json.loads((source / "acceptance.json").read_text())
mask = bytes.fromhex(routing["K04"]["masked_component"])
nonce = bytes.fromhex(routing["K08"]["desk_nonce"])
copied = bytes.fromhex("A9A9DC5731A5E2AE879C47215C2559D5")

# Planted controlled interpretation at original selected stage, which is
# unconstrained by the source. This must reconstruct the complete test value.
control = [model.untemper(int.from_bytes(copied[4*j:4*j+4], "little")) for j in range(4)]
status, predicted, known = reconstruct(control, model.STARTS[129])
assert (status, known, predicted) == ("FULL", 128, copied)
assert hashlib.sha256(bytes(a ^ b for a, b in zip(predicted, mask))).hexdigest() != targets["slot_sha256"]["K04"]
print("selected-stage 128-bit reconstruction control PASS; copied ACK original target NO_MATCH")

for label, field in (("route_mask", mask), ("desk_nonce", nonce)):
    for order in ("little", "big"):
        for representation in ("tempered", "native"):
            observed = [int.from_bytes(field[4*j:4*j+4], order) for j in range(4)]
            if representation == "tempered":
                observed = [model.untemper(v) for v in observed]
            counts = {"CONTRADICTION": 0, "PARTIAL": 0, "FULL": 0}
            full_stages = []
            originals = []
            for stage in range(model.ORIGIN, model.LAST - 2):
                status, payload, known = reconstruct(observed, stage)
                counts[status] += 1
                if status == "FULL":
                    full_stages.append(stage)
                    component = bytes(a ^ b for a, b in zip(payload, mask))
                    if hashlib.sha256(component).hexdigest() == targets["slot_sha256"]["K04"]:
                        originals.append((stage, component.hex().upper()))
            assert sum(counts.values()) == 2138
            assert full_stages == [951], (label, order, representation, full_stages)
            assert not originals, (label, order, representation, originals)
            print(label, order, representation, counts, "fully determined stages", full_stages,
                  "K04 target matches", len(originals))
print("PASS: no original K04 recovery under these eight frozen donor models")
