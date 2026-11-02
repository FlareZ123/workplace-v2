"""K08 exact-order deletion reconstruction from Emily's dated, nonlabelled prose.
Source-only author hypothesis: final line is an ordered subsequence of ONE
quoted Emily sentence, without adding or reordering words.
Reads unchanged routing nonce/acceptance and crew notes; no source mutations.
Usage: python agents/agent48/k08_emily_ordered_deletion_sft.py resources
"""
import hashlib
import hmac
import json
import re
import sys
from pathlib import Path

ROOT = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("resources")
p = ROOT / "evidence/crew/noticeboard-and-desk-notes.txt"
source = p.read_bytes()
assert hashlib.sha256(source).hexdigest() == "13f2318ccc54f35b590a2d76b3a80244fe24d70f0699c67c05858e8b8983c5cb"
notes = source.decode("utf-8")
route = json.loads((ROOT / "evidence/recovery-routing.json").read_text())
accept = json.loads((ROOT / "acceptance.json").read_text())
key = bytes.fromhex(route["K08"]["desk_nonce"])
target = accept["slot_sha256"]["K08"]

# These six source-exact Emily clauses omit board labels and prose descriptors.
clauses = {
    "N02": "A good watch leaves the room ready for the next pair of hands",
    "N06": "The little lamp stays on until the corridor has gone quiet",
    "N10": "I kept going back to the photograph after the last cup",
    "N13": "At the end of the night the mugs stood beside the window and somebody had remembered to leave the little lamp on",
    "N20": "I wanted the line to hold the sea the end of the night and the voices at the table",
    "N23": "The envelope only remembers the words I finally put on it",
}
def normalize(s):
    return " ".join(re.sub(r"[^a-z0-9\s]", " ", s.lower()).split())
def slot_digest(words):
    component = hmac.digest(key, words.encode("utf-8"), "sha256")[:16]
    return hashlib.sha256(component).hexdigest(), component.hex().upper()
def ordered_deletions(words):
    n = len(words)
    for mask in range(1, 1 << n):
        if 4 <= mask.bit_count() <= 18:
            yield " ".join(w for i, w in enumerate(words) if mask & (1 << i))
def main():
    for note, clause in clauses.items():
        # Check the actual original note's normalized phrase as a single span.
        line = re.search(rf"(?m)^{note} / Emily \[censored\]\n([^\n]+)", notes).group(1)
        assert normalize(clause) in normalize(line), note
    # Genuine positive: the enumerator must find an independently planted
    # HMAC/SHA commitment for a known proper subsequence of original N13.
    planted = "at the end of the night beside the window"
    planted_digest, _ = slot_digest(planted)
    found = sum(slot_digest(s)[0] == planted_digest for s in ordered_deletions(clauses["N13"].lower().split()))
    assert found >= 1, "synthetic deletion recovery failed"
    total = 0
    for note, clause in clauses.items():
        hits = []
        count = 0
        for text in ordered_deletions(clause.lower().split()):
            digest, comp = slot_digest(text)
            count += 1
            if digest == target:
                hits.append((text, comp))
        total += count
        print(note, "candidates", count, "original K08 hits", hits, flush=True)
    print("total original candidates", total, "synthetic positive", found)
if __name__ == "__main__":
    main()
