"""H-17 K08: N02/N06 two-interior crossover with N20 motif bridge.

Source-derived normalized complete-candidate class; originals are read-only.
Run: python agents/agent40/k08_draft_crossover_n20_sft.py
"""
import hashlib
import hmac
import json
import re
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2] / "resources"
notes = (ROOT / "evidence/crew/noticeboard-and-desk-notes.txt").read_bytes()
assert hashlib.sha256(notes).hexdigest() == (
    "13f2318ccc54f35b590a2d76b3a80244fe24d70f0699c67c05858e8b8983c5cb"
)
nonce = bytes.fromhex(json.loads(
    (ROOT / "evidence/recovery-routing.json").read_text()
)["K08"]["desk_nonce"])
want = bytes.fromhex(json.loads(
    (ROOT / "acceptance.json").read_text()
)["slot_sha256"]["K08"])
base = {}
for number in ("02", "06"):
    match = re.search(
        rb"^N" + number.encode() + rb" / [^\n]+\n[^:\n]+: ([^\n]+)", notes, re.M
    )
    assert match
    base[number] = tuple(re.findall(rb"[a-z0-9]+", match[1].lower()))
assert [len(base[x]) for x in ("02", "06")] == [13, 11]

def fragments(words):
    return tuple(
        words[i:i+k]
        for k in range(1, 6)
        for i in range(len(words)-k+1)
    )

n20 = next(line for line in notes.splitlines()
           if line.startswith(b"I wanted the line"))
motifs = [
    tuple(x.split()) for x in (
        b"the sea", b"the end of the night", b"the voices at the table"
    )
]
assert all(b" ".join(m) in n20.lower() for m in motifs)

def checksum(words):
    return hashlib.sha256(
        hmac.digest(nonce, b" ".join(words), "sha256")[:16]
    ).digest()

known = bytes.fromhex("BF889359B0303F2B2B2FD96AE841210B")
assert checksum(base["02"]) == hashlib.sha256(known).digest()
planted = (
    base["02"][:2] + base["06"][:2] + base["02"][3:8]
    + base["06"][4:6] + base["02"][9:] + (b"and",) + motifs[0]
)
control_digest = checksum(planted)
direct = bridged = control = 0
matches = []
start = time.perf_counter()
for nA, nB in (("02", "06"), ("06", "02")):
    A, B = base[nA], base[nB]
    frag = fragments(B)
    n = len(A)
    for c1 in range(2, n-5):
        for c2 in range(c1+1, n-4):
            for c3 in range(c2+3, n-1):
                for c4 in range(c3+1, n-1):
                    if n-c4 < 2:
                        continue
                    pieces0 = (A[:c1], A[c2:c3], A[c4:])
                    for x in frag:
                        for y in frag:
                            pieces = (
                                pieces0[0], x, pieces0[1], y, pieces0[2]
                            )
                            candidate = tuple(
                                w for piece in pieces for w in piece
                            )
                            direct += 1
                            if checksum(candidate) == want:
                                matches.append(("direct", nA, nB, candidate))
                            for motif in motifs:
                                for joiner in ((), (b"and",)):
                                    for position in (1, 3, 5):
                                        words = []
                                        for i, piece in enumerate(pieces):
                                            if i == position:
                                                words.extend(joiner + motif)
                                            words.extend(piece)
                                        if position == 5:
                                            words.extend(joiner + motif)
                                        verdict = checksum(tuple(words))
                                        bridged += 1
                                        control += verdict == control_digest
                                        if verdict == want:
                                            matches.append((
                                                "motif", nA, nB, tuple(words)
                                            ))
assert direct == 187125 and bridged == 3368250 and control == 1
assert not matches, matches
print("N02/N06 two-interior replacements:", direct)
print("Plus N20 motif and optional conjunction:", bridged)
print("Planted exact two-draft/motif control hits:", control)
print("Original K08 commitment matches:", len(matches))
print("Elapsed seconds:", round(time.perf_counter()-start, 2))
print("Original evidence, acceptance, verifier and candidate unchanged.")
