"""H17 original-source K08 wide-character literal recovery, zero external dependencies.

Read the source's original evidence bytes without changes. Search UTF-16/32
ASCII-printable wide-character runs and all contiguous normalized word windows.
A complete genuine final inscription, if encoded in this exact form, passes
original desk-nonce HMAC16 and acceptance SHA256. No guessed text or web data.
"""
import hashlib
import hmac
import re
import sys
from pathlib import Path

SOURCE_NOTE_SHA = "13f2318ccc54f35b590a2d76b3a80244fe24d70f0699c67c05858e8b8983c5cb"
NONCE = bytes.fromhex("5F933DA6A1BD03C32DA5CBC25344F497")
TARGET = bytes.fromhex("285eb6b4196d21eaf47e251449e61e0bce28749881ccc5a065ca733b0c3fd747")
N02_HMAC16 = bytes.fromhex("BF889359B0303F2B2B2FD96AE841210B")
# Match complete printable ASCII runs at any offset; avoid stray random encodings.
CHAR = rb"[\x09\x0a\x0d\x20-\x7e]"
REGEXES = {
    "utf-16-le": re.compile(rb"(?:" + CHAR + rb"\x00){16,}"),
    "utf-16-be": re.compile(rb"(?:\x00" + CHAR + rb"){16,}"),
    "utf-32-le": re.compile(rb"(?:" + CHAR + rb"\x00\x00\x00){16,}"),
    "utf-32-be": re.compile(rb"(?:\x00\x00\x00" + CHAR + rb"){16,}"),
}


def normalized(text: str) -> str:
    return " ".join("".join(c.lower() if c.isascii() and c.isalnum() else (" " if not c.isspace() else c) for c in text).split())


def component(text: str) -> bytes:
    return hmac.new(NONCE, normalized(text).encode("utf-8"), hashlib.sha256).digest()[:16]


def accepted(text: str, target: bytes) -> bool:
    return hashlib.sha256(component(text)).digest() == target


def candidates(text: str):
    words = normalized(text).split()
    if len(words) >= 2:
        for i in range(len(words) - 1):
            for j in range(i + 2, min(i + 33, len(words) + 1)):
                yield " ".join(words[i:j])


def scan(data: bytes, target: bytes, details=False):
    hits = []
    runs = []
    tested = 0
    seen = set()
    for codec, pat in REGEXES.items():
        for match in pat.finditer(data):
            text = match.group().decode(codec)
            runs.append((codec, match.start(), len(text), text[:120]))
            for cand in candidates(text):
                if cand in seen:
                    continue
                seen.add(cand)
                tested += 1
                if accepted(cand, target):
                    hits.append((codec, match.start(), cand))
    if details:
        return runs, tested, hits
    return hits


def main(path: Path):
    notes = path / "crew" / "noticeboard-and-desk-notes.txt"
    assert hashlib.sha256(notes.read_bytes()).hexdigest() == SOURCE_NOTE_SHA
    assert component("A good watch leaves the room ready for the next pair of hands.") == N02_HMAC16
    # All four codecs prove genuine in-family extraction and full HMAC+SHA.
    synth = "At the end of the night there is still room for another cup at the table"
    planted = hashlib.sha256(component(synth)).digest()
    for codec in REGEXES:
        data = b"\xff\x01\x9a" + synth.encode(codec) + b"\xaa\x06\xff"
        found = scan(data, planted)
        assert len(found) == 1 and found[0][0] == codec and found[0][2] == normalized(synth), (codec, found)
    total_runs = 0
    total_tested = 0
    true_hits = []
    nontrivial_runs = []
    source_files = sorted(p for p in path.rglob("*") if p.is_file())
    for file in source_files:
        runs, tested, hits = scan(file.read_bytes(), TARGET, details=True)
        total_runs += len(runs)
        total_tested += tested
        for codec, offset, length, text in runs:
            nontrivial_runs.append((file.relative_to(path).as_posix(), codec, offset, length, text))
        true_hits.extend((file.relative_to(path).as_posix(),) + h for h in hits)
    print("SOURCE_FILES", len(source_files), "ORIGINAL_WIDE_RUNS", total_runs, "COMPLETE_CANDIDATES", total_tested,
          "ORIGINAL_K08_MATCHES", len(true_hits), "SYNTHETIC_POSITIVES", len(REGEXES))
    for item in nontrivial_runs:
        print("WIDE_LITERAL", repr(item))
    for hit in true_hits:
        print("ORIGINAL_K08_MATCH", repr(hit))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(Path(sys.argv[1]) if len(sys.argv) > 1 else Path("resources/evidence")))
