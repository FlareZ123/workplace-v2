"""Source-only test for any unknown period-16 XOR obscuring a K08 literal.

A UTF-16/32 ASCII text encoded under an arbitrary unknown 16-byte XOR key
must leave the high zero-byte lane periodic in the ciphertext. The constraint
is key-independent and robust to any alignment or XOR key value. Similarly,
an encoded 64-character ordinary ASCII span must have periodic cipher MSBs.
Read-only: no original commitments or candidate values are modified.
"""
from hashlib import sha256
from pathlib import Path
from random import Random

ROOT = Path(__file__).resolve().parents[2]
EVIDENCE = ROOT / "resources" / "evidence"
NOTE_SHA = "13f2318ccc54f35b590a2d76b3a80244fe24d70f0699c67c05858e8b8983c5cb"


def masked(source: bytes, key: bytes) -> bytes:
    return bytes(value ^ key[i % 16] for i, value in enumerate(source))


def wide_witness(data: bytes, width: int, little: bool, chars: int = 16):
    zero_lanes = range(1, width) if little else range(width - 1)
    for start in range(len(data) - width * chars + 1):
        seen = {}
        ok = True
        for i in range(chars):
            for lane in zero_lanes:
                pos = start + i * width + lane
                r = pos % 16
                value = data[pos]
                if r in seen and seen[r] != value:
                    ok = False
                    break
                seen[r] = value
            if not ok:
                break
        if ok:
            yield start


def ascii_bit_witnesses(data: bytes, chars: int = 64):
    # Maximal segments satisfying bit7(cipher[i]) = bit7(cipher[i-16]).
    if len(data) < chars:
        return
    high = [value >> 7 for value in data]
    start = 0
    for stop in range(16, len(high)):
        if high[stop] != high[stop - 16]:
            if stop - start >= chars:
                yield start, stop
            start = stop - 15
    if len(data) - start >= chars:
        yield start, len(data)


def main():
    original = (EVIDENCE / "crew" / "noticeboard-and-desk-notes.txt").read_bytes()
    assert sha256(original).hexdigest() == NOTE_SHA
    files = sorted(p for p in EVIDENCE.rglob("*") if p.is_file())
    assert len(files) == 42
    phrase = "A good watch leaves the room ready for the next pair of hands"
    rng = Random(72105)
    for width in (2, 4):
        for little in (True, False):
            encoding = ("utf-16-" if width == 2 else "utf-32-") + (
                "le" if little else "be"
            )
            prefix = bytes(rng.randrange(256) for _ in range(rng.randrange(10, 43)))
            key = bytes(rng.randrange(256) for _ in range(16))
            source = masked(prefix + phrase.encode(encoding), key)
            assert len(prefix) in wide_witness(source, width, little), (width, little)

    # A text-only XOR capture also has a necessary repeating high-bit parity.
    prefix = bytes(rng.randrange(256) for _ in range(23))
    key = bytes(rng.randrange(256) for _ in range(16))
    source = masked(prefix + phrase.encode() + b" a little more space at the table", key)
    assert any(a <= 23 < b and b - a >= 64 for a, b in ascii_bit_witnesses(source))

    wide_hits = []
    opaque_ascii_hits = []
    files_seen = []
    for path in files:
        raw = path.read_bytes()
        files_seen.append(path.name)
        for width in (2, 4):
            for little in (True, False):
                for at in wide_witness(raw, width, little):
                    wide_hits.append((str(path.relative_to(EVIDENCE)), at, width, little))
        for start, stop in ascii_bit_witnesses(raw):
            # Ordinary unmasked ASCII files/PDF syntax are already literal-search
            # controls. A hidden text carrier in binary would need source bytes
            # whose high bits vary or that include NULs.
            segment = raw[start:stop]
            if any(byte >= 128 or byte == 0 for byte in segment):
                opaque_ascii_hits.append((str(path.relative_to(EVIDENCE)), start, stop))

    print("source_files", len(files_seen))
    print("unknown-key UTF16/32 ASCII span >=16chars:", len(wide_hits), wide_hits[:12])
    print("unknown-key ASCII opaque span >=64chars:", len(opaque_ascii_hits), opaque_ascii_hits[:12])
    assert len(wide_hits) == 0, wide_hits[:20]
    assert len(opaque_ascii_hits) == 0, opaque_ascii_hits[:20]


if __name__ == "__main__":
    main()
