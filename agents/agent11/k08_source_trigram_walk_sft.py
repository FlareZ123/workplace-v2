"""H-17 K08 full-text trigram reconstruction (Agent11, 5 November 2026).

Single-file original-source SFT. The intact records supply every consecutive
three-word transition; walks can recombine at overlapping two-word boundaries.
Source content, commitments and canonical candidate remain read-only.

Run with H17_RESOURCE_ROOT pointing to the extracted official archive, or with
a checked-out workplace-v2 repository containing resources/.
"""
from collections import defaultdict
from hashlib import sha256
from hmac import digest
from pathlib import Path
import json
import os
import re

ROOT = Path(os.environ.get("H17_RESOURCE_ROOT", Path(__file__).resolve().parents[2] / "resources"))
NOTES_PATH = ROOT / "evidence/crew/noticeboard-and-desk-notes.txt"
SOURCE_SHA = "13f2318ccc54f35b590a2d76b3a80244fe24d70f0699c67c05858e8b8983c5cb"
assert sha256(NOTES_PATH.read_bytes()).hexdigest() == SOURCE_SHA
route = json.loads((ROOT / "evidence/recovery-routing.json").read_text())
acceptance = json.loads((ROOT / "acceptance.json").read_text())
key = bytes.fromhex(route["K08"]["desk_nonce"])
target = bytes.fromhex(acceptance["slot_sha256"]["K08"])


def normalize(s: str) -> str:
    return " ".join(re.findall(r"[a-z0-9]+", s.lower()))


def check(s: str) -> bytes:
    component = digest(key, normalize(s).encode("ascii"), "sha256")[:16]
    return sha256(component).digest()


draft = "A good watch leaves the room ready for the next pair of hands."
assert digest(key, normalize(draft).encode("ascii"), "sha256")[:16].hex().upper() == "BF889359B0303F2B2B2FD96AE841210B"

notes = NOTES_PATH.read_text()
records = []
for ident, body in re.findall(r"N(\d+) /[^\n]+\n([^\n]+)", notes):
    if ":" in body:
        body = body.split(":", 1)[1]
    records.append((f"N{ident}", body))

for n in (11, 20):
    mail = (ROOT / f"evidence/mail/{n:02}.eml").read_text()
    body = mail.split("\n\n", 1)[1]
    body = body.replace("Back before the first boat", "").replace("Leave the light on for the next watch", "")
    body = body.rsplit("\nEmily", 1)[0] if n == 11 else body.rsplit("\nGabriel", 1)[0]
    records.append((f"MAIL{n}", body))

# Each graph edge records an original, verbatim normalized three-word shingle.
# The original normalization erases sentence punctuation, so body-wide
# cross-sentence triples are also included. Older envelope labels remain
# available in N17/N18: a superset of the core six Emily-note constructions.
graph = defaultdict(set)
for name, body in records:
    w = normalize(body).split()
    for a, b, c in zip(w, w[1:], w[2:]):
        graph[(a, b)].add(c)

depth = 42
counts = defaultdict(int)
attempts = 0
matches = []
synthetic = "at the end of the night and the voices at the table"
synthetic_hash = check(synthetic)
synthetic_matches = 0

# Every full path has a unique start bigram and sequence of next-word edges.
for start in sorted(graph):
    stack = [(start, start)]
    while stack:
        pair, words = stack.pop()
        if len(words) >= 4:
            text = " ".join(words)
            attempts += 1
            counts[len(words)] += 1
            value = check(text)
            if value == target:
                matches.append((text, digest(key, text.encode("ascii"), "sha256")[:16].hex().upper()))
            if value == synthetic_hash:
                assert text == synthetic
                synthetic_matches += 1
        if len(words) < depth:
            for w in sorted(graph.get(pair, ()), reverse=True):
                stack.append(((pair[1], w), words + (w,)))

result = {
    "source_notes_sha256": SOURCE_SHA,
    "source_records": len(records),
    "graph_bigram_states": len(graph),
    "graph_trigram_edges": sum(map(len, graph.values())),
    "min_caption_words": 4,
    "max_caption_words": depth,
    "distinct_complete_captions": attempts,
    "by_length": dict(counts),
    "original_target_matches": matches,
    "planted_full_path_positive": synthetic_matches,
}
print(json.dumps(result, sort_keys=True))
assert synthetic_matches == 1
assert not matches
