"""Source-pinned K04 stage-relocation and copier-serialization falsifier.

Tests complete coupons using only source-fixed or <=4-bit-free, relocated MT
windows. The selected damaged spool row is excluded during inference. This
is conditional on the unconfirmed p951 MT19937 history of Agent49.
"""
import hashlib
import importlib.util
import itertools
import json
import re
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2] / "resources"
DEP = Path(__file__).resolve().parents[1] / "agent49" / "k04_p951_symbolic_basis.py"
spec = importlib.util.spec_from_file_location("k04_basis", DEP)
mt = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mt)
basis, forms = mt.source(ROOT)
assert basis.rank == 15365

routing = json.loads((ROOT / "evidence/recovery-routing.json").read_text())
inventory = json.loads((ROOT / "acceptance.json").read_text())
mask = bytes.fromhex(routing["K04"]["masked_component"])
target = bytes.fromhex(inventory["slot_sha256"]["K04"])
raw = (ROOT / "evidence/print/spool-reconstruction.log").read_bytes()
assert hashlib.sha256(raw).hexdigest() == "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"
packets = [bytes.fromhex(x.decode("ascii")) for x in re.findall(rb"PAYLOAD=([0-9A-F]{32})", raw)]
assert len(packets) == len(mt.STARTS) == 133

def reduce_source(v):
    known = 0
    remaining = 0
    while v:
        index = v.bit_length() - 1
        if index in basis.rows:
            form, bit = basis.rows[index]
            v ^= form
            known ^= bit
        else:
            remaining |= 1 << index
            v ^= 1 << index
    return remaining, known

reduced = {
    pos: tuple(reduce_source(form) for form in mt.get(forms, pos))
    for pos in range(mt.ORIGIN, mt.LAST + 1)
}

def parameterize(start):
    free_basis = {}
    directions = []
    baseline = 0
    for lane in range(4):
        for bit, (residual, known) in enumerate(reduced[start + lane]):
            output_index = 32 * lane + bit
            if known:
                baseline ^= 1 << output_index
            while residual:
                pivot = residual.bit_length() - 1
                if pivot not in free_basis:
                    free_basis[pivot] = (residual, len(directions))
                    directions.append(0)
                    break
                form, direction = free_basis[pivot]
                residual ^= form
                directions[direction] ^= 1 << output_index
            if residual:
                direction = free_basis[residual.bit_length() - 1][1]
                directions[direction] ^= 1 << output_index
    return baseline, directions

def temper(v):
    v ^= v >> 11
    v ^= (v << 7) & 0x9d2c5680
    v ^= (v << 15) & 0xefc60000
    v ^= v >> 18
    return v & 0xffffffff

def packet(native128):
    return b"".join(
        temper((native128 >> (32 * lane)) & 0xffffffff).to_bytes(4, "little")
        for lane in range(4)
    )

counts = Counter()
tested = 0
matches = []
starts = []
positive = False
for start in range(mt.ORIGIN, mt.LAST - 2):
    baseline, directions = parameterize(start)
    rank = len(directions)
    if rank > 4:
        continue
    starts.append(start)
    counts[rank] += 1
    for free_assignment in range(1 << rank):
        native = baseline
        for bit, difference in enumerate(directions):
            if (free_assignment >> bit) & 1:
                native ^= difference
        source_packet = packet(native)
        words = [source_packet[i * 4 : i * 4 + 4] for i in range(4)]
        for order in itertools.permutations(range(4)):
            for endian_mask in range(16):
                serialized = b"".join(
                    words[word][::-1] if (endian_mask >> lane) & 1 else words[word]
                    for lane, word in enumerate(order)
                )
                component = bytes(a ^ b for a, b in zip(serialized, mask))
                tested += 1
                if start == mt.STARTS[3] and free_assignment == 0 and order == (0, 1, 2, 3) and endian_mask == 0:
                    assert serialized == packets[3]
                    positive = True
                if hashlib.sha256(component).digest() == target:
                    matches.append({
                        "start": start, "assignment": free_assignment,
                        "order": order, "endian_mask": endian_mask,
                        "K04": component.hex().upper()
                    })
assert positive
assert mt.STARTS[129] == 951 and len(parameterize(951)[1]) == 128
assert (counts[0], counts[1], counts[2], counts[3], counts[4]) == (284, 118, 43, 9, 4)
assert tested == 317952
print(json.dumps({
    "original_K04_matches": matches,
    "stage_windows": len(starts),
    "off_original_start_stages": sum(x not in mt.STARTS for x in starts),
    "original_selected_rank": 128,
    "rank_histogram": dict(sorted(counts.items())),
    "full_candidate_checks": tested,
    "synthetic_intact_packet_control": "PASS",
    "stage_starts_sha256": hashlib.sha256(",".join(map(str, starts)).encode()).hexdigest()
}, indent=2))
