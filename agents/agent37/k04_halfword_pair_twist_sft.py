"""K04 source-only halfword-pair MT donor probe (Agent37, 2026-11-03).

Checks adjacent u16 DIAG_WORD and AX checkpoint pairs against p951 printer
twist-derived 31-bit source signatures. Selected ACK row129 and K04 commitment
are excluded. The printer chronology is hypothetical, not proven hardware fact.
Run on Windows 11: python agents/agent37/k04_halfword_pair_twist_sft.py
"""
import hashlib
import itertools
import json
import re
import struct
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2] / "resources/evidence"
PINS = {
    "print/spool-reconstruction.log": "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083",
    "telemetry/freeze-export.jsonl": "3787dbd6bab3930ea5293c25a995175161a1c0d7683daad29f498026e057639f",
    "transfers/transfer-audit.jsonl": "32970ad4431a9d610cc12dcca2813f39dd8fd2e396f9e748dc94b5932cb69adf",
}
for name, sha in PINS.items():
    assert hashlib.sha256((ROOT / name).read_bytes()).hexdigest() == sha

# Published v1 agent5 conditional printer chronology p951. Whole selected
# record129 occupies 951..954; never add its observed words to known.
STARTS = [
    0,7,16,22,30,37,45,54,64,72,80,88,95,108,116,122,130,136,142,148,
    154,164,170,176,182,188,194,203,209,218,224,230,237,244,250,257,
    265,272,284,294,301,307,314,324,335,342,348,354,360,366,372,378,
    384,394,401,408,416,423,429,435,446,454,460,470,477,485,491,503,
    511,518,524,531,539,556,562,568,576,582,588,595,602,608,617,624,
    632,638,644,650,658,666,672,678,686,693,701,710,717,729,736,743,
    755,762,770,776,782,788,795,801,813,819,825,831,837,846,853,861,
    870,876,884,891,899,905,912,918,924,930,936,942,947,951,955,959,963,
]
assert len(STARTS) == 133 and STARTS[129] == 951

def untemper(x: int) -> int:
    y = x ^ (x >> 18)
    y ^= (y << 15) & 0xEFC60000
    base = y
    for _ in range(5):
        y = base ^ ((y << 7) & 0x9D2C5680)
    base = y
    for _ in range(3):
        y = base ^ (y >> 11)
    return y & 0xFFFFFFFF

rows = []
for line in (ROOT / "print/spool-reconstruction.log").read_text().splitlines():
    if line and not line.startswith("#"):
        rows.append(dict(re.findall(r"([A-Z]+)=([^\s]+)", line)))
assert len(rows) == 133 and rows[129]["JOB"] == "PS-261003-0417"
assert rows[129]["ATTEMPT"] == "2" and rows[129]["STATE"] == "ACK"
known = {}
for i, r in enumerate(rows):
    if i == 129:
        continue
    for j, word in enumerate(struct.unpack("<4I", bytes.fromhex(r["PAYLOAD"]))):
        known[STARTS[i] + j] = untemper(word)
assert len(known) == 528
assert known[211] == 0xCF76E469 and known[438] == 0xF9997B00

# MT recurrence S[t+624]=S[t+397]^twist(S[t],S[t+1]). A known
# q=t+397 and q+227=t+624 constrain the low31 of S[t+1].
need = defaultdict(list)
for q, a in known.items():
    if q + 227 not in known:
        continue
    u = a ^ known[q + 227]
    for parity in (0, 1):
        low = (((u ^ (0x9908B0DF if parity else 0)) << 1) | parity) & 0x7FFFFFFF
        need[low].append(q - 396)
assert sum(map(len, need.values())) == 442
rc17_b_purge = untemper(int.from_bytes(bytes.fromhex("759E0027"), "little"))
assert rc17_b_purge == 0xEDDF3ED2 and -185 in need[rc17_b_purge & 0x7FFFFFFF]

def read_jsonl(name):
    return [json.loads(l) for l in (ROOT / name).read_text().splitlines()]

chunks = [x for x in read_jsonl("transfers/transfer-audit.jsonl") if x["kind"] == "CHUNK"]
streams = {}
for (transfer, attempt), group in itertools.groupby(
    sorted(chunks, key=lambda x: (x["transfer"], x["attempt"], x["seq"])),
    lambda x: (x["transfer"], x["attempt"])
):
    streams[f"AX:{transfer}:attempt{attempt}"] = {
        x["seq"]: bytes.fromhex(x["checkpoint"]) for x in group
    }
for transfer in sorted({x["transfer"] for x in chunks}):
    chosen = {}
    for x in chunks:
        if x["transfer"] == transfer and (
            x["seq"] not in chosen or x["attempt"] > chosen[x["seq"]]["attempt"]
        ):
            chosen[x["seq"]] = x
    streams[f"AX:{transfer}:best"] = {
        seq: bytes.fromhex(x["checkpoint"]) for seq, x in chosen.items()
    }
diag = [x for x in read_jsonl("telemetry/freeze-export.jsonl") if x["field"] == "DIAG_WORD"]
for (quality, state), group in itertools.groupby(
    sorted(diag, key=lambda x: (x["quality"], x["state"], x["seq"], x["revision"])),
    lambda x: (x["quality"], x["state"])
):
    chosen = {}
    for x in group:
        if x["seq"] not in chosen or x["revision"] > chosen[x["seq"]]["revision"]:
            chosen[x["seq"]] = x
    streams[f"LT204:{quality}:{state}:best"] = {
        seq: x["value"].to_bytes(2, "big") for seq, x in chosen.items()
    }

assignments = 0
fingerprint_hits = []
copy_hits = []
known_values = set(known.values())
for source, items in streams.items():
    for seq, a in items.items():
        if seq + 1 not in items:
            continue
        b = items[seq + 1]
        for halves in ((a, b), (b, a)):
            for flip in (False, True):
                data = b"".join(part[::-1] if flip else part for part in halves)
                for endian in ("little", "big"):
                    raw = int.from_bytes(data, endian)
                    for mode in ("native", "tempered"):
                        word = raw if mode == "native" else untemper(raw)
                        assignments += 1
                        tag = (source, seq, flip, endian, mode)
                        if word in known_values:
                            copy_hits.append(tag)
                        if (word & 0x7FFFFFFF) in need:
                            fingerprint_hits.append((tag, need[word & 0x7FFFFFFF]))
assert len(streams) == 15 and assignments == 1680
assert fingerprint_hits == [] and copy_hits == []
print(json.dumps({
    "original_source_positive": "PASS",
    "known_printer_words": len(known),
    "p951_twist_signatures": 442,
    "paired_streams": len(streams),
    "complete_pair_assignments": assignments,
    "exact_twist_fingerprint_hits": len(fingerprint_hits),
    "direct_word_copy_hits": len(copy_hits),
    "K04_selected_bytes_used": 0
}, indent=2))
