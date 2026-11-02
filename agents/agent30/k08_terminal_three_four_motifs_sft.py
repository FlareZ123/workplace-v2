"""K08 N13 terminal edit: independently insert/substitute three source motifs,
optionally a fourth MAIL11 motif. All unaffected N13 words remain ordered.
"""
from hashlib import sha256
from hmac import new as hmac_sha
from itertools import combinations, permutations
from pathlib import Path
import json
import re
import time

root = Path(__file__).resolve().parents[2] / "resources"
source = (root / "evidence/crew/noticeboard-and-desk-notes.txt").read_bytes()
assert sha256(source).hexdigest() == (
    "13f2318ccc54f35b590a2d76b3a80244fe24d70f0699c67c05858e8b8983c5cb"
)
n13 = re.search(r"^N13 / Emily \[censored\]\n([^\n]+)", source.decode(), re.M)
assert n13
base = re.findall(r"[a-z0-9]+", n13.group(1).lower())
assert len(base) == 22
route = json.loads((root / "evidence/recovery-routing.json").read_text())
key = bytes.fromhex(route["K08"]["desk_nonce"])
target = bytes.fromhex(json.loads((root / "acceptance.json").read_text())
                       ["slot_sha256"]["K08"])


def digest(words):
    component = hmac_sha(key, " ".join(words).encode(), "sha256").digest()[:16]
    return sha256(component).digest()


def render(replacements, insertions):
    result = []
    for i in range(23):
        if i in insertions:
            result.append(insertions[i])
        if i < 22:
            result.append(replacements.get(i, base[i]))
    return result


planted = render({0: "sea", 1: "voices", 2: "table"}, {5: "room"})
synthetic_target = digest(planted)
assert synthetic_target == digest(
    ["sea", "voices", "table", base[3], base[4], "room"] + base[5:]
)

for motifs in (("sea", "voices", "table"),
               ("sea", "voices", "table", "room")):
    count = matches = controls = 0
    started = time.perf_counter()
    for k in range(len(motifs) + 1):
        for positions in combinations(range(22), k):
            for gaps in combinations(range(23), len(motifs) - k):
                for arrangement in permutations(motifs):
                    words = render(dict(zip(positions, arrangement[:k])),
                                   dict(zip(gaps, arrangement[k:])))
                    actual = digest(words)
                    if actual == target:
                        matches += 1
                        print("ORIGINAL K08 MATCH:", " ".join(words), flush=True)
                    controls += actual == synthetic_target
                    count += 1
    assert count == (85140 if len(motifs) == 3 else 3575880)
    assert controls == (0 if len(motifs) == 3 else 1)
    print(f"motifs={motifs} complete={count} original_matches={matches} "
          f"synthetic_hits={controls} seconds={time.perf_counter()-started:.2f}")
