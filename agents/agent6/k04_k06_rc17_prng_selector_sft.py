"""K06 approved-vs-withdrawn source-stage contrast, using original printer-only p951 basis.

Run from repository root: python agents/agent6/k04_k06_rc17_prng_selector_sft.py
One read-only SFT; original K04 selected printer packet is explicitly withheld.
"""
import hashlib
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "agents/agent49"))
from k04_p951_symbolic_basis import Basis, get, source, temper, untemper

RC17_SHA = "a4b649fdbb6909115fb9505133012b5c1dda42141aafc1c6ec756199ddf1fc6d"
EXPECTED_HITS = [
    ("B", "PURGE", "759E0027", "little", -185, 26),
    ("B", "VERIFY", "C130C9BB", "little", -186, 32),
]


def main():
    raw = (ROOT / "resources/evidence/procedures/RC-17-scans.txt").read_bytes()
    assert hashlib.sha256(raw).hexdigest() == RC17_SHA
    records = {}
    for revision, section, strip in re.findall(
        rb"DOCUMENT RC-17 / REV ([^ /]+) / SECTION ([A-Z]+).*?"
        rb"Footer control strip: ([0-9A-F]{8})", raw, re.S
    ):
        key = (revision.decode(), section.decode())
        assert key not in records
        records[key] = strip.decode()
    assert len(records) == 12

    base, symbolic = source(ROOT / "resources")
    assert base.rank == 15365
    known = {}
    for stage in range(-1100, 1041):
        mask = value = 0
        for bit, equation in enumerate(temper(get(symbolic, stage))):
            answer = base.predict(equation)
            if answer is not None:
                mask |= 1 << bit
                value |= answer << bit
        known[stage] = (mask, value)

    hits = []
    for (revision, section), strip in sorted(records.items()):
        for endian in ("little", "big"):
            value = int.from_bytes(bytes.fromhex(strip), endian)
            for stage, (mask, expected) in known.items():
                if mask.bit_count() >= 13 and (value ^ expected) & mask == 0:
                    hits.append((revision, section, strip, endian, stage, mask.bit_count()))
    assert hits == EXPECTED_HITS, hits
    official = "".join(records[("C", section)] for section in (
        "DRAIN", "ISOLATE", "PURGE", "VERIFY"
    ))
    assert official == "5DBF40EE52FAAED9A536D3326CF0D95A"

    extension = Basis()
    extension.rows = dict(base.rows)
    extension.rank = base.rank
    for revision, section, strip, endian, stage, _ in hits:
        native = untemper(int.from_bytes(bytes.fromhex(strip), endian))
        for bit, equation in enumerate(get(symbolic, stage)):
            extension.insert(equation, (native >> bit) & 1)
    assert extension.rank == 15366

    slot = Basis()
    slot.rows = {pivot: (equation, 0) for pivot, (equation, _) in extension.rows.items()}
    slot.rank = extension.rank
    for stage in range(951, 955):
        for equation in get(symbolic, stage):
            slot.insert(equation, 0)
    assert slot.rank - extension.rank == 128

    print("Original printer-only model and original RC17 source hashes verified")
    print("Only source-matching strips:", hits)
    print("Withdrawn B matches at adjacent stages -186,-185")
    print("Approved C controls:", official, "none match source-fixed original stages")
    print("GF(2) rank:", base.rank, "to", extension.rank)
    print("Selected K04 stage remains 128/128 free; actual key not recovered")


if __name__ == "__main__":
    main()
