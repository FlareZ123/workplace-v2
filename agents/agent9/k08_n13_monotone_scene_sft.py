"""Source-conditioned K08 two-insertion, multi-deletion search.

Hypothesis: the N13 reminiscence was shortened by deleting up to four
individual words, then received two ordered scene fragments: sea before
voices/table. All surviving N13 words remain in order. This permits
noncontiguous omissions not represented by a two-interior-replacement edit.
Run: python agents/agent9/k08_n13_monotone_scene_sft.py
No facility or source modifications.
"""
from itertools import combinations
from pathlib import Path
import hashlib
import hmac
import json
import re
import time

root = Path(__file__).resolve().parents[2] / "resources"
notes = (root / "evidence/crew/noticeboard-and-desk-notes.txt").read_text()
mail = (root / "evidence/mail/11.eml").read_text()
route = json.loads((root / "evidence/recovery-routing.json").read_text())
target = bytes.fromhex(json.loads((root / "acceptance.json").read_text())["slot_sha256"]["K08"])
assert hashlib.sha256(notes.encode()).hexdigest() == "13f2318ccc54f35b590a2d76b3a80244fe24d70f0699c67c05858e8b8983c5cb"
n13 = re.search(r"^N13 / Emily \[censored\]\n(.*?)\n\n", notes, re.M | re.S).group(1)
n20 = re.search(r"^N20 / Emily \[censored\]\n(.*?)\n\n", notes, re.M | re.S).group(1)
assert "voices at the table" in n20 and "water outside" in mail
words = re.findall(r"[a-z0-9]+", n13.lower())
sea = ("the sea", "the water outside", "the sea at the end of the night")
voices = ("the voices at the table", "the voices", "people making room for each other")
key = bytes.fromhex(route["K08"]["desk_nonce"])

def key_for(phrase):
    return hmac.digest(key, phrase.encode(), "sha256")[:16]

n02 = re.search(r"^N02 / Emily \[censored\]\n(.*?)\n\n", notes, re.M | re.S).group(1)
clean_n02 = " ".join(re.findall(r"[a-z0-9]+", n02.lower()))
assert key_for(clean_n02) == hmac.new(key, clean_n02.encode(), hashlib.sha256).digest()[:16]

# Independent synthetic target constructed from a specific 2-deletion case.
keep = [w for i, w in enumerate(words) if i not in (0, 3)]
probe = " ".join(keep[:4] + sea[1].split() + keep[4:10] + voices[2].split() + keep[10:])
probe_hash = hashlib.sha256(key_for(probe)).digest()
assert probe_hash != target
found_synthetic = False
count = 0
start = time.monotonic()
for deleted in range(5):
    for drop in combinations(range(len(words)), deleted):
        removed = set(drop)
        keep = [w for i, w in enumerate(words) if i not in removed]
        for i in range(len(keep) + 1):
            a = " ".join(keep[:i])
            for j in range(i, len(keep) + 1):
                mid = " ".join(keep[i:j])
                tail = " ".join(keep[j:])
                for s in sea:
                    prefix = " ".join((a, s, mid)) + " "
                    for v in voices:
                        phrase = " ".join((prefix, v, tail)).strip()
                        digest = hashlib.sha256(key_for(phrase)).digest()
                        count += 1
                        if digest == probe_hash:
                            found_synthetic = True
                        if digest == target:
                            print("ORIGINAL_MATCH", repr(phrase), key_for(phrase).hex().upper(), "count", count)
                            raise SystemExit(0)
    print("deletions", deleted, "candidates", count, "seconds", round(time.monotonic() - start, 2), flush=True)
assert found_synthetic
assert count == 15952077, count
print("NO_MATCH", count, "synthetic_positive=PASS")
