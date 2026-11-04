"""Read-only CPython hypothetical binary seed source-window periodic pad SFT.

Use Agent15's exact original-source 86-word inverse key constraints as imported
from the companion agent3 seed-periodicity SFT. Search 9 original source files
at all 54,692 endpoints and pad periods 1..512 in 4 byte/word transforms.
Original 0417 ACK2 copy, K04 acceptance and official verifier never entered.
"""
from pathlib import Path
import numpy as np
import k04_cpython_binary_seed_periodicity_sft as seed

ROOT = Path(__file__).resolve().parents[2]
original = seed.fragments(seed.original_seed_words())
full = [(offset, value) for offset, value, mask in original if mask == 255]
assert len(full) == 320


def offset_view(offset, reverse):
    return (offset // 4) * 4 + 3 - offset % 4 if reverse else offset


def pairs(period):
    groups = {}
    for offset, value in full:
        groups.setdefault(offset % period, []).append((offset, value))
    return [
        (group[0], value)
        for group in groups.values() if len(group) > 1
        for value in group[1:]
    ]


def matching_endpoints(blob, period, reverse, add):
    data = np.frombuffer(blob, dtype=np.uint8)
    ends = np.arange(2357, len(data) + 1, dtype=np.int32)
    for (off_a, val_a), (off_b, val_b) in pairs(period):
        if not len(ends):
            break
        a = data[ends + offset_view(off_a, reverse)]
        b = data[ends + offset_view(off_b, reverse)]
        if add:
            left = (np.uint16(val_a) - a.astype(np.uint16)) & 255
            right = (np.uint16(val_b) - b.astype(np.uint16)) & 255
            keep = left == right
        else:
            keep = (a ^ val_a) == (b ^ val_b)
        ends = ends[keep]
    return ends


def main():
    source_root = ROOT / "resources/evidence"
    originals = [
        (p.relative_to(source_root).as_posix(), p.read_bytes())
        for p in source_root.rglob("*")
        if p.is_file() and p.stat().st_size >= 2357
    ]
    total_endpoints = sum(len(blob) - 2356 for _, blob in originals)
    assert len(originals) == 9 and total_endpoints == 54692
    for reverse in (False, True):
        for add in (False, True):
            matches = []
            for period in range(1, 513):
                for name, blob in originals:
                    found = matching_endpoints(blob, period, reverse, add)
                    if len(found):
                        matches.append((name, period, len(found)))
            assert matches == [], matches
            # Plant every source-derived full-byte constraint as a genuine
            # complete periodic-pad copy of a synthetic source window.
            blob = bytearray(bytes((i*37 + 7) % 256 for i in range(3200)))
            pad = bytes((i*7 + 13) % 256 for i in range(32))
            end = 3000
            for offset, value in full:
                location = end + offset_view(offset, reverse)
                blob[location] = (
                    (value - pad[offset % 32]) % 256 if add
                    else value ^ pad[offset % 32]
                )
            assert end in matching_endpoints(bytes(blob), 32, reverse, add)
            print("REVERSE", reverse, "ADDITIVE_PAD", add,
                  "SOURCE_MODELS", total_endpoints * 512,
                  "SOURCE_MATCHES", len(matches),
                  "PLANTED_FULL_SOURCE_POSITIVE", "PASS")
    print("ALL_FOUR_MODES", total_endpoints*512*4, "ORIGINAL_MATCHES", 0)
    print("K04_AUTHENTICATED_BITS", 0)


if __name__ == "__main__":
    main()
