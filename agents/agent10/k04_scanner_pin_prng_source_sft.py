"""H-17: test the independently recovered BX25 PDF release PIN as a seed
for a shared CPython MT19937 native 32-bit printer-payload stream.

Uses the unmodified original printer export. The historical document does not
claim a common scanner/printer seed or CPython firmware. The selected copied
ACK2 bytes are never used in source fitting.
"""
from pathlib import Path
import hashlib
import random
import re
import struct
from collections import defaultdict

ROOT = Path(__file__).resolve().parents[2] / "resources"
raw = (ROOT / "evidence/print/spool-reconstruction.log").read_bytes()
assert hashlib.sha256(raw).hexdigest() == "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"
source = [bytes.fromhex(s.decode()) for s in re.findall(rb"PAYLOAD=([0-9A-F]{32})", raw)]
assert len(source) == 133

index = defaultdict(list)
source_words = set()
for i, packet in enumerate(source):
    if i == 129:
        continue
    words = [packet[j:j+4] for j in range(0, 16, 4)]
    for reverse in (False, True):
        arranged = words[::-1] if reverse else words
        for endian in ("little", "big"):
            index[tuple(int.from_bytes(w, endian) for w in arranged)].append((i, reverse, endian))
            source_words.update(int.from_bytes(w, endian) for w in words)

assert sum(map(len, index.values())) == 528
seeds = [
    ("pin_int", 8131),
    ("pin_ascii", "8131"),
    ("pin_le", b"\xc3\x1f"),
    ("pin_be", b"\x1f\xc3"),
    ("pin_sha_int", int.from_bytes(hashlib.sha256(b"8131").digest(), "big")),
    ("pin_plusfolio", "8131:BX25/08"),
    ("folio_pluspin", "BX25/08:8131"),
]
N = 100_000
hits = []
for name, seed in seeds:
    rng = random.Random(seed)
    words = [rng.getrandbits(32) for _ in range(N + 3)]
    matches = [(j, m) for j in range(N) if (m := index.get(tuple(words[j:j+4])))]
    word_matches = sum(w in source_words for w in words)
    print(
        f"SEED {name} tested_windows={N} source_single_word_hits={word_matches} "
        f"source_complete_packet_hits={len(matches)}"
    )
    hits.extend((name, j, m) for j, m in matches)
assert not hits
# Full generated positive coupon: a seeded genuine 4-word consecutive window
# is recovered in its exact deterministic stream at its unique planted index.
control_rng = random.Random(8131)
control = [control_rng.getrandbits(32) for _ in range(135)]
planted = tuple(control[67:71])
assert [j for j in range(120) if tuple(control[j:j+4]) == planted] == [67]
print("ORIGINAL_SOURCE_NO_MATCH positive_control=PASS")
