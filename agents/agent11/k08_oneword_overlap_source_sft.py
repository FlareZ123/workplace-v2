"""H17 K08: one novel 3-gram at a one-word overlap of original source walks.

Read-only source-pinned SFT, 5 November 2026. Set H17_RESOURCE_ROOT to
the extracted official archive, or run in workplace-v2 with resources/.
"""
from collections import defaultdict
from hashlib import sha256
from hmac import digest
from pathlib import Path
import json
import os
import re

root = Path(os.environ.get("H17_RESOURCE_ROOT", Path(__file__).resolve().parents[2] / "resources"))
notes = root / "evidence/crew/noticeboard-and-desk-notes.txt"
assert sha256(notes.read_bytes()).hexdigest() == "13f2318ccc54f35b590a2d76b3a80244fe24d70f0699c67c05858e8b8983c5cb"
route = json.loads((root / "evidence/recovery-routing.json").read_text())
acceptance = json.loads((root / "acceptance.json").read_text())
key = bytes.fromhex(route["K08"]["desk_nonce"])
target = bytes.fromhex(acceptance["slot_sha256"]["K08"])


def normalize(s: str) -> str:
    return " ".join(re.findall(r"[a-z0-9]+", s.lower()))


def k08(s: str) -> bytes:
    return sha256(digest(key, normalize(s).encode(), "sha256")[:16]).digest()


original_draft = "A good watch leaves the room ready for the next pair of hands."
assert digest(key, normalize(original_draft).encode(), "sha256")[:16].hex().upper() == "BF889359B0303F2B2B2FD96AE841210B"
records = []
for identifier, body in re.findall(r"N(\d+) /[^\n]+\n([^\n]+)", notes.read_text()):
    if ":" in body:
        body = body.split(":", 1)[1]
    records.append(body)
for n in (11, 20):
    body = (root / f"evidence/mail/{n:02}.eml").read_text().split("\n\n", 1)[1]
    body = body.replace("Back before the first boat", "").replace("Leave the light on for the next watch", "")
    body = body.rsplit("\nEmily", 1)[0] if n == 11 else body.rsplit("\nGabriel", 1)[0]
    records.append(body)

graph = defaultdict(set)
for body in records:
    words = normalize(body).split()
    for a, b, c in zip(words, words[1:], words[2:]):
        graph[(a, b)].add(c)
assert len(graph) == 545 and sum(map(len, graph.values())) == 585

paths = []
for start in sorted(graph):
    stack = [(start, start)]
    while stack:
        pair, words = stack.pop()
        if len(words) >= 3:
            paths.append(words)
        if len(words) < 12:
            for word in sorted(graph.get(pair, ()), reverse=True):
                stack.append(((pair[1], word), words + (word,)))
by_first = defaultdict(list)
by_last = defaultdict(list)
for path in paths:
    by_first[path[0]].append(path)
    by_last[path[-1]].append(path)

# Every transition inside the halves was already attested as a source 3-gram.
# The *only* newly invented 3-gram is [left last two, right second word].
# Requiring that new 3-gram distinguishes this class from the prior SFT.
synthetic = "mugs stood beside the window and the voices at the table"
synthetic_hash = k08(synthetic)
seen = set()
assignments = 0
original_hits = []
planted_hits = 0
for join in sorted(set(by_first) & set(by_last)):
    for left in by_last[join]:
        for right in by_first[join]:
            assignments += 1
            if right[1] in graph.get((left[-2], join), ()):
                continue
            words = left + right[1:]
            if not (5 <= len(words) <= 22):
                continue
            candidate = " ".join(words)
            if candidate in seen:
                continue
            seen.add(candidate)
            reduced = k08(candidate)
            if reduced == target:
                original_hits.append(candidate)
            if reduced == synthetic_hash:
                assert candidate == synthetic
                planted_hits += 1

result = {
    "source_records": len(records),
    "graph_states": len(graph),
    "graph_edges": sum(map(len, graph.values())),
    "source_walks_up_to_12_words": len(paths),
    "one_word_join_assignments": assignments,
    "distinct_one_new_trigram_captions": len(seen),
    "original_K08_hits": original_hits,
    "planted_full_caption_hits": planted_hits,
}
print(json.dumps(result, sort_keys=True))
assert len(paths) == 10444
assert assignments == 2077927
assert len(seen) == 1722779
assert planted_hits == 1 and not original_hits
