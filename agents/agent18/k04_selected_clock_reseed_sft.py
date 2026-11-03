"""Read-only selected-only K04 producer probe: UTC clock-seeded CPython MT.

Source record selects ESC-N PS-261003-0417 attempt2 ACK at 18:02Z.
Test per-attempt reset with integer UTC seconds across the whole original
printer day and millisecond integer epochs near selected attempt2.
Original company material does not assert a clock-seeded producer.
Run: python agents/agent18/k04_selected_clock_reseed_sft.py
"""
import hashlib
import json
import random
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2] / "resources"
spool = (ROOT / "evidence/print/spool-reconstruction.log").read_bytes()
assert hashlib.sha256(spool).hexdigest() == (
    "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"
)
selected = [line for line in spool.decode().splitlines()
            if "JOB=PS-261003-0417 ATTEMPT=2 STATE=ACK CLASS=RECOVER" in line]
assert len(selected) == 1 and selected[0].startswith("2026-10-03T18:02:00Z")
route = json.loads((ROOT / "evidence/recovery-routing.json").read_text())
mask = bytes.fromhex(route["K04"]["masked_component"])
accept = json.loads((ROOT / "acceptance.json").read_text())
target = bytes.fromhex(accept["slot_sha256"]["K04"])

def epoch(iso):
    return int(datetime.fromisoformat(iso.replace("Z", "+00:00")).timestamp())

start_seconds = epoch("2026-10-03T07:00:00Z")
end_seconds = epoch("2026-10-03T18:26:00Z")
start_ms = epoch("2026-10-03T18:00:00Z") * 1000
end_ms = epoch("2026-10-03T18:04:00Z") * 1000
assert end_seconds-start_seconds==41160 and end_ms-start_ms==240000

def views(words):
    chunks = [w.to_bytes(4, "little") for w in words]
    return (b"".join(chunks),
            b"".join(c[::-1] for c in chunks),
            b"".join(reversed(chunks)),
            b"".join(c[::-1] for c in reversed(chunks)))

def digest(payload):
    component = bytes(a ^ b for a,b in zip(payload, mask))
    return hashlib.sha256(component).digest()

seed_for_control = start_ms + 1000
offset_for_control = 9
rng = random.Random(seed_for_control)
drawn = [rng.getrandbits(32) for _ in range(offset_for_control+4)]
control = digest(views(drawn[-4:])[2])
assert control != target

original_hits = []
control_hits = []
def test_seed(seed, positions):
    rng = random.Random(seed)
    words = [rng.getrandbits(32) for _ in range(positions+3)]
    for offset in range(positions):
        for orientation,payload in enumerate(views(words[offset:offset+4])):
            candidate_hash = digest(payload)
            if candidate_hash == target:
                original_hits.append((seed,offset,orientation,payload.hex().upper()))
            if candidate_hash == control:
                control_hits.append((seed,offset,orientation))

for seed in range(start_seconds,end_seconds+1):
    test_seed(seed,16)
for seed in range(start_ms,end_ms+1):
    test_seed(seed,12)
assert control_hits == [(seed_for_control,offset_for_control,2)]
assert not original_hits
print(json.dumps({
    "seconds_seeds":end_seconds-start_seconds+1,
    "millisecond_seeds":end_ms-start_ms+1,
    "seeded_draw_start_offsets_seconds":16,
    "seeded_draw_start_offsets_milliseconds":12,
    "word_and_byte_orientations":4,
    "original_component_SHA256_checks":14154352,
    "planted_control":control_hits,
    "authentic_K04_matches":original_hits
},indent=2))
