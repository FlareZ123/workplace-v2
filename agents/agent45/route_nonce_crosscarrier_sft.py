"""H-17: scan route-local mask/nonce and six accepted slots as possible MT donors.

A bounded exploratory original-source test. No K04 ACK, K04/K08 target digests,
K08 final phrase, or verifier is read. The p951 producer remains hypothetical.

Run: python agents/agent45/route_nonce_crosscarrier_sft.py
"""
import hashlib
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RESOURCES = ROOT / "resources"
MODULE_PATH = ROOT / "agents/agent2/20261102_k04_multicarrier_p951_sft.py"
spec = importlib.util.spec_from_file_location("p951_source", MODULE_PATH)
producer = importlib.util.module_from_spec(spec)
spec.loader.exec_module(producer)

word, known, offset = producer.source_closure(RESOURCES)
routing_path = RESOURCES / "evidence/recovery-routing.json"
routing_bytes = routing_path.read_bytes()
assert hashlib.sha256(routing_bytes).hexdigest() == (
    "f8fcbca73d23bf1066edb88c088f89cd24cf22e7c78a4a412166254a4764d8a5"
)
route = json.loads(routing_bytes)
accepted = json.loads((ROOT / "candidate.json").read_text(encoding="utf-8"))
carriers = {
    "K04-route-mask": route["K04"]["masked_component"],
    "K08-desk-nonce": route["K08"]["desk_nonce"],
}
carriers.update({name: accepted[name] for name in
                 ("K01", "K02", "K03", "K05", "K06", "K07")})

# The data path really finds a planted, fully known source word.
native = word[offset]
printed = producer.temper(native).to_bytes(4, "little")
assert producer.untemper(int.from_bytes(printed, "little")) == native
assert known[offset] == 0xffffffff
assert all(known[offset + 951 + lane] == 0 for lane in range(4))

def reverse_each_byte_bits(raw):
    return bytes(int(format(value, "08b")[::-1], 2) for value in raw)

total_interpretations = 0
for name, hex_value in carriers.items():
    raw = bytes.fromhex(hex_value)
    assert len(raw) == 16
    hits = []
    for start in range(13):
        window = raw[start:start + 4]
        for orientation, candidate_bytes in (
            ("native", window),
            ("reverse-bits-in-byte", reverse_each_byte_bits(window)),
        ):
            for endian in ("little", "big"):
                total_interpretations += 1
                candidate = producer.untemper(int.from_bytes(candidate_bytes, endian))
                for position, mask in enumerate(known):
                    if mask.bit_count() >= 24 and ((word[position] ^ candidate) & mask) == 0:
                        hits.append((start, orientation, endian, position - offset,
                                     mask.bit_count()))
    print(name, "matches at >=24 known source bits:", hits)
    assert not hits, (name, hits)

assert total_interpretations == 416
print("416 four-byte windows/orientations across eight preserved 16-byte carriers;")
print("zero p951 source-state matches with >=24 independent known MT bits.")
print("No historical producer proof and no K04/K08 component recovered.")
