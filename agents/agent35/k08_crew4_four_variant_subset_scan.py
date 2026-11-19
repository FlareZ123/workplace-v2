#!/usr/bin/env python3
"""Fixed-codebook 4-variant subset scan for the K08 CREW4 -> ATEALBIT bridge.

This is an upstream sensitivity component, NOT the full-chain null and NOT a
calibrated global p-value. It enumerates every 8-of-24 author-position subset
under A0/A1 x LSB/MSB, holding the observed first-appearance codebook fixed.
"""
import hashlib
import itertools
import json
import re
from pathlib import Path

EXPECTED = "13f2318ccc54f35b590a2d76b3a80244fe24d70f0699c67c05858e8b8983c5cb"


def parse_notes(text):
    chunks = re.split(r"(?m)(?=^N\d{2} /)", text)
    notes = {}
    for chunk in chunks:
        m = re.match(r"N(\d{2}) / ([^\n]+)\n", chunk)
        if not m:
            continue
        n = int(m.group(1))
        body = chunk[m.end():].strip()
        if ":" in body:
            body = body.split(":", 1)[1].strip()
        notes[n] = body
    return notes


def tokens(text):
    return re.findall(r"[A-Za-z0-9]+(?:-[A-Za-z0-9]+)?", text)


def decode_mask(mask, base, order):
    letters = []
    for start in range(0, 20, 5):
        val = 0
        for j in range(5):
            bit = (mask >> (start + j)) & 1
            val |= bit << (j if order == "LSB" else 4 - j)
        if base == 0:
            letters.append(chr(65 + val) if val < 26 else "?")
        else:
            letters.append(chr(64 + val) if 1 <= val <= 26 else "?")
    tail = 0
    for j in range(4):
        bit = (mask >> (20 + j)) & 1
        tail |= bit << (j if order == "LSB" else 3 - j)
    return "".join(letters) + str(tail)


def bridge_for_subset(ids, notes):
    valid = []
    for pos, original in enumerate(ids):
        shifted = ids.copy()
        shifted[pos] = original + 1
        if shifted != sorted(shifted) or len(set(shifted)) != 8 or any(n not in notes for n in shifted):
            continue
        heads = "".join(tokens(notes[n])[0][0].upper() for n in shifted)
        counts = [len(tokens(notes[n])) for n in shifted]
        count_letters = "".join(chr(65 + c) if c < 26 else "?" for c in counts)
        a_teal_bit = heads
        a_low_bit = heads[0] + count_letters[1:4] + heads[5:8]
        valid.append({
            "edit": f"N{original:02d}->N{original+1:02d}",
            "selected_ids": shifted,
            "heads": heads,
            "word_counts": counts,
            "count_letters": count_letters,
            "ATEALBIT_exact": a_teal_bit == "ATEALBIT",
            "ALOWBIT_exact": a_low_bit == "ALOWBIT",
            "ALOWBIT": a_low_bit,
        })
    return valid


def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--notes", type=Path, default=Path("resources/evidence/crew/noticeboard-and-desk-notes.txt"))
    args = ap.parse_args()
    raw = args.notes.read_bytes()
    digest = hashlib.sha256(raw).hexdigest()
    if digest != EXPECTED:
        raise SystemExit(f"source pin mismatch: {digest}")
    notes = parse_notes(raw.decode("utf-8"))
    if sorted(notes) != list(range(1, 25)):
        raise SystemExit(f"unexpected note inventory: {sorted(notes)}")

    author_lines = [line for line in raw.decode("utf-8").splitlines() if re.match(r"^N\d{2} /", line)]
    authors = [line.split("/", 1)[1].strip().split()[0] for line in author_lines]
    first_appearance_order = list(dict.fromkeys(authors))
    if len(first_appearance_order) != 6:
        raise SystemExit(f"unexpected author codebook: {first_appearance_order}")

    counts = {f"A{base}_{order}": 0 for base in (0, 1) for order in ("LSB", "MSB")}
    hits = {key: [] for key in counts}
    total = 0
    for comb in itertools.combinations(range(24), 8):
        total += 1
        mask = sum(1 << i for i in comb)
        ids = [i + 1 for i in comb]
        for base in (0, 1):
            for order in ("LSB", "MSB"):
                key = f"A{base}_{order}"
                if decode_mask(mask, base, order) == "CREW4":
                    counts[key] += 1
                    hits[key].append(ids)

    detail = []
    full_bridge_hits = []
    for key, subsets in hits.items():
        for ids in subsets:
            edits = bridge_for_subset(ids, notes)
            exact = [e for e in edits if e["ATEALBIT_exact"] and e["ALOWBIT_exact"]]
            detail.append({"variant": key, "CREW4_subset": ids, "valid_plus_one_edits": edits})
            for e in exact:
                full_bridge_hits.append({"variant": key, "CREW4_subset": ids, **e})

    print(json.dumps({
        "source_sha256": digest,
        "note_count": len(notes),
        "first_appearance_author_order": first_appearance_order,
        "subsets_per_variant": total,
        "CREW4_hits_by_variant": counts,
        "CREW4_total_variant_subset_hits": sum(counts.values()),
        "CREW4_hit_details": detail,
        "exact_ATEALBIT_and_ALOWBIT_after_one_plus_one_edit": full_bridge_hits,
        "exact_full_bridge_hit_count": len(full_bridge_hits),
        "scope_warning": "Fixed observed codebook; only A0/A1 x LSB/MSB and +1 one-row edits enumerated. Not the full author-label permutation or end-to-end null.",
    }, indent=2))


if __name__ == "__main__":
    main()
