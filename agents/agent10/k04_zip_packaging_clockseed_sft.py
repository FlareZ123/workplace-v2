"""K04 ZIP-packaging-clock-seed source gate; 172,801 complete integer seeds.

Original copied selected K04 ACK row and acceptance hash are never read.
Run from repo root with standard Python; optionally pass original ZIP path as
--zip to independently pin and extract its UTC extended timestamp.
"""
from argparse import ArgumentParser
from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path
from zipfile import ZipFile
import json
import random
import re

ROOT = Path(__file__).resolve().parents[2] / "resources"
SPOOL = ROOT / "evidence/print/spool-reconstruction.log"
SPOOL_SHA = "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"
ZIP_SHA = "e778552c555fac652e24fd09e1c4f31bd066b4686e624b91f6e94e1d64342bf7"
ZIP_UTC_MIN = 1792469534 # 2026-10-20T04:12:14Z
assert sha256(SPOOL.read_bytes()).hexdigest() == SPOOL_SHA
rows = re.findall(rb"PAYLOAD=([0-9A-F]{32})", SPOOL.read_bytes())
assert len(rows) == 133
first = bytes.fromhex(rows[0].decode())
assert first.hex().upper() == "FBBBC54356483F5864BB3F06794518A5"

def orientations(value):
    variants = {}
    for i in range(4):
        word = value[4*i:4*i+4]
        for direction in (word,word[::-1]):
            variants[direction] = variants.get(direction,0)|(1<<i)
    return variants

def is_fourword_match(data, mapping):
    # All 24 word permutations and every one of 16 per-word reversal masks.
    masks = [mapping.get(data[4*i:4*i+4],0) for i in range(4)]
    if not all(masks):
        return False
    used = {0}
    for m in masks:
        used = {old|(1<<j) for old in used for j in range(4)
                if m&(1<<j) and not old&(1<<j)}
        if not used:
            return False
    return 15 in used

parser = ArgumentParser(description=__doc__)
parser.add_argument("--zip", type=Path, help="Original 46-file ZIP to authenticate packaging clock")
args = parser.parse_args()
if args.zip:
    assert sha256(args.zip.read_bytes()).hexdigest() == ZIP_SHA
    with ZipFile(args.zip) as z:
        stamps = []
        for info in z.infolist():
            at = info.extra.find(b"UT\x05\x00\x01")
            if at>=0:
                stamps.append(int.from_bytes(info.extra[at+5:at+9],"little"))
        assert len(stamps)>=46 and min(stamps)==ZIP_UTC_MIN
start=ZIP_UTC_MIN

# Planted future-phase positive, complete 16B packet with scrambled words.
g = random.Random(start+57).randbytes(4*8192)
unit = [g[(183+i)*4:(184+i)*4] for i in range(4)]
planted = b"".join(unit[i][::-1] if rev else unit[i]
                   for i,rev in ((1,True),(3,False),(0,False),(2,True)))
assert is_fourword_match(g[183*4:187*4],orientations(planted))
modified=planted[:10]+bytes([planted[10]^1])+planted[11:]
assert not is_fourword_match(g[183*4:187*4],orientations(modified))

mapping=orientations(first)
prefixes=set(mapping)
firstword_hits=0
matches=[]
for seed in range(start-86400,start+86401):
    stream = random.Random(seed).randbytes(4*8192)
    for p in prefixes:
        offset = stream.find(p)
        while offset>=0:
            if offset%4 == 0 and offset+16<=len(stream):
                firstword_hits+=1
                if is_fourword_match(stream[offset:offset+16],mapping):
                    matches.append((seed,offset//4))
            offset=stream.find(p,offset+1)

assert not matches
print(json.dumps({
  "packaging_clock_utc":datetime.fromtimestamp(start,timezone.utc).isoformat(),
  "original_source_sha256":SPOOL_SHA,
  "zip_sha256":ZIP_SHA,
  "integer_second_seed_count":172801,
  "complete_4word_start_candidates":172801*8189,
  "word_permutations_and_perword_endian_views":384,
  "original_firstword_prefix_collisions":firstword_hits,
  "original_complete_source_packet_matches":matches,
  "synthetic_fourword_positive":"PASS",
  "selected_ACK_and_K04_target_ignored":True,
},indent=2))
