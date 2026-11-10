"""Source-pinned K08 reduction-variant pilot.

This deliberately tests alternate *complete* 16-byte reducers of normalized
source passages, rather than further subjective caption paraphrases.
The official HMAC-SHA256 rule remains authoritative; none of the alternate
reducers is claimed historically. Pure stdlib; does not modify evidence.
"""
import hashlib
import hmac
import json
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parents[2] / "resources"

for relative, digest in {
    "acceptance.json": "681739241b757b471acca4c0fef9d9d97e9493883887736d5db3b92bfb0c137f",
    "evidence/recovery-routing.json": "f8fcbca73d23bf1066edb88c088f89cd24cf22e7c78a4a412166254a4764d8a5",
    "evidence/crew/noticeboard-and-desk-notes.txt": "13f2318ccc54f35b590a2d76b3a80244fe24d70f0699c67c05858e8b8983c5cb",
}.items():
    assert hashlib.sha256((ROOT / relative).read_bytes()).hexdigest() == digest, relative

acceptance = json.loads((ROOT / "acceptance.json").read_text())
target = acceptance["slot_sha256"]["K08"]
nonce = bytes.fromhex(json.loads(
    (ROOT / "evidence/recovery-routing.json").read_text()
)["K08"]["desk_nonce"])


def norm(s):
    return " ".join(re.sub(r"[^a-z0-9\s]", " ", s.lower()).split())


files = [
    ROOT / "evidence/crew/noticeboard-and-desk-notes.txt",
    *sorted((ROOT / "evidence/mail").glob("*.eml")),
]
assert len(files) == 21
phrases = set()
for file in files:
    original = file.read_text()
    if file.suffix == ".eml":
        original = original.split("\n\n", 1)[-1]
    for paragraph in re.split(r"\n\s*\n", original):
        p = norm(paragraph)
        if 3 <= len(p.split()) <= 100:
            phrases.add(p)
        for sentence in re.split(r"[.!?;:\n]", paragraph):
            words = norm(sentence).split()
            if 3 <= len(words) <= 70:
                phrases.add(" ".join(words))
            for n in range(2, min(len(words), 22) + 1):
                for i in range(len(words) - n + 1):
                    phrases.add(" ".join(words[i:i+n]))

variants = {
    "SHA256(key||caption)": lambda x: hashlib.sha256(nonce+x).digest()[:16],
    "SHA256(caption||key)": lambda x: hashlib.sha256(x+nonce).digest()[:16],
    "HMAC-SHA1/first16": lambda x: hmac.digest(nonce, x, "sha1")[:16],
    "HMAC-SHA224/first16": lambda x: hmac.digest(nonce, x, "sha224")[:16],
    "HMAC-SHA384/first16": lambda x: hmac.digest(nonce, x, "sha384")[:16],
    "HMAC-SHA512/first16": lambda x: hmac.digest(nonce, x, "sha512")[:16],
    "HMAC-SHA256/last16": lambda x: hmac.digest(nonce, x, "sha256")[-16:],
    "HMAC-SHA256/reverse-key": lambda x: hmac.digest(nonce[::-1], x, "sha256")[:16],
    "HMAC-SHA256/ascii-key": lambda x: hmac.digest(nonce.hex().upper().encode(), x, "sha256")[:16],
    "HMAC-SHA256/caption-key": lambda x: hmac.digest(x, nonce, "sha256")[:16],
    "BLAKE2s-keyed-16": lambda x: hashlib.blake2s(x, key=nonce, digest_size=16).digest(),
    "BLAKE2b-keyed-16": lambda x: hashlib.blake2b(x, key=nonce, digest_size=16).digest(),
    "SHA3-256(key||caption)": lambda x: hashlib.sha3_256(nonce+x).digest()[:16],
    "MD5(key||caption)": lambda x: hashlib.md5(nonce+x).digest(),
    "SHAKE128(key||caption)": lambda x: hashlib.shake_128(nonce+x).digest(16),
}

control = norm("A good watch leaves the room ready for the next pair of hands.")
assert hmac.digest(nonce, control.encode(), "sha256")[:16].hex().upper() == (
    "BF889359B0303F2B2B2FD96AE841210B"
)
assert target == "285eb6b4196d21eaf47e251449e61e0bce28749881ccc5a065ca733b0c3fd747"
assert len(phrases) == 12078
assert len(variants) == 15

for label, derive in variants.items():
    hits = [
        (phrase, component.hex().upper())
        for phrase in phrases
        if hashlib.sha256(component := derive(phrase.encode())).hexdigest() == target
    ]
    assert hits == [], (label, hits)
    print(label, len(phrases), "tested", "0 authentic hits")
print("PASS 181170 complete original acceptance checks, 0 authentic hits")
