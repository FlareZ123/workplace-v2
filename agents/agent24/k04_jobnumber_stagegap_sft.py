"""H-17 K04: source-only job-ID counter versus native MT stage gap.
Run from repo root: python agents/agent24/k04_jobnumber_stagegap_sft.py
Selected ACK2 payload, K04 mask, acceptance, candidate and verifier are withheld.
Requires only the Python standard library and existing original-source helpers.
"""
from pathlib import Path
import hashlib
import re
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from agents.agent13 import k04_stagefree_31bit_hidden_predecessor_graph_sft as first
from agents.agent1 import k04_mt_secondorder_4sum_sft as second

raw = (ROOT / "resources/evidence/print/spool-reconstruction.log").read_bytes()
assert hashlib.sha256(raw).hexdigest() == "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"
rows = [line for line in raw.decode("ascii").splitlines() if "PAYLOAD=" in line]
assert len(rows) == 133
assert "JOB=PS-261003-0417 ATTEMPT=2 STATE=ACK CLASS=RECOVER" in rows[129]
assert "JOB=PS-261003-0427" in rows[127]
assert "JOB=PS-261003-0448" in rows[131]
flat = []
for row, line in enumerate(rows):
    if row == 129:
        continue
    match = re.search(r"PAYLOAD=([0-9A-F]{32})", line)
    assert match is not None
    packet = bytes.fromhex(match.group(1))
    for lane in range(4):
        word = int.from_bytes(packet[lane*4:lane*4+4], "little")
        flat.append((row, lane, first.untemper(word)))
assert len(flat) == 528

# Re-discover all numerical relations without providing assumed stage indices.
triples = first.discover(flat)
assert len(triples) == 42
quad_matches = second.secondorder_quads(flat)
quad_groups = second.grouped_quads(quad_matches)
trusted = {key: group for key, group in quad_groups.items() if len(group) >= 2}
assert (len(quad_matches), len(trusted), sum(map(len, trusted.values()))) == (15, 4, 9)

# Difference constraints: each exact source relation fixes two or three
# packet-stage differences. Monotone output order consumes >=4 words/packet.
edges = []
for r, lane, sr, sl, tr, tl, _ in triples:
    for other, gap in ((sr, 396+lane-sl), (tr, 623+lane-tl)):
        edges.extend(((r,other,gap), (other,r,-gap)))
for ar, br, cr, dr, ab, ac, ad in trusted:
    for other, gap in ((br, ab), (cr, ac), (dr, ad)):
        edges.extend(((ar,other,gap), (other,ar,-gap)))
for r in range(132):
    edges.append((r+1,r,-4))

def shortest(start):
    distances = [float("inf")] * 133
    distances[start] = 0
    for iteration in range(133):
        changed = False
        for a,b,w in edges:
            if distances[a] != float("inf") and distances[b] > distances[a]+w:
                distances[b] = distances[a]+w
                changed = True
        if not changed:
            return distances
    raise AssertionError("negative cycle in source chronology")

lo = -shortest(131)[127]
hi = shortest(127)[131]
assert (lo,hi) == (16,71)
# Suffix difference 0448-0427=21 means 20 intervening distinct numbers
# 0428..0447. If all 20 yielded an extra independent 16-byte job within
# these source times, each would need four draws. Three observed 0417
# attempt rows also lie between 127 and 131.
minimum_if_all_20_emitted = (1 + 3 + 20) * 4
assert minimum_if_all_20_emitted == 96 > hi
max_extra = (hi-lo)//4
assert max_extra == 13
assert 20-max_extra == 7

# Genuine native producer consistency: the independent p951 synthetic
# reference is a CONTROL only; it is never an input to source relation search.
starts = first.STAGES
assert starts[131] - starts[127] == 17
for r, lane, sr, sl, tr, tl, _ in triples:
    assert starts[sr]+sl-starts[r]-lane == 396
    assert starts[tr]+tl-starts[r]-lane == 623
for (a,b,c,d,ab,ac,ad) in trusted:
    assert tuple(starts[q]-starts[a] for q in (b,c,d)) == (ab,ac,ad)
print("ORIGINAL_SHA256_PASS")
print("SOURCE_31BIT_RELATIONS",len(triples),"REINFORCED_4SUM_GROUPS",len(trusted))
print("ROW127_131_NATIVE_STAGE_GAP_MIN_MAX",lo,hi)
print("IF_ALL_20_INTERMEDIATE_JOB_IDS_EMITTED_MIN_NATIVE_GAP",minimum_if_all_20_emitted)
print("MAX_ADDITIONAL_FOUR_WORD_JOBS",max_extra)
print("SOURCE_CONTRADICTS_ALL_20_EMITTED_IN_THIS_INTERVAL",hi<minimum_if_all_20_emitted)
print("P951_RELATION_CONTROL_PASS; HISTORICAL_GENERATOR_UNPROVEN")
print("K04_PHYSICAL_BITS_RECOVERED=0; K08_FINAL_WORDS=0; REC8_INCOMPLETE")
