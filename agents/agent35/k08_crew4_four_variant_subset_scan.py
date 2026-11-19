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
from fractions import Fraction
from math import comb, factorial, prod
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


def ways_david_fourth(k, other_counts):
    total = 0
    for i in range(4):
        for j in range(i + 1, 4):
            for count_i in range(1, min(other_counts[i], k) + 1):
                count_j = k - count_i
                if count_j < 1 or count_j > other_counts[j]:
                    continue
                remaining = other_counts.copy()
                remaining[i] -= count_i
                remaining[j] -= count_j
                total += comb(k, count_i) * factorial(13 - k) // prod(factorial(x) for x in remaining)
    return total


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
    valid_edit_total = 0
    for combi in itertools.combinations(range(24), 8):
        total += 1
        mask = sum(1 << i for i in combi)
        ids = [i + 1 for i in combi]
        id_set = set(ids)
        valid_edit_total += sum(1 for n in ids if n < 24 and n + 1 not in id_set)
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

    # Joint upstream null: choose uniformly from all (8-position subset,
    # encoding variant, valid +1 edit) triples, then choose David's 3 positions
    # and the remaining author-label assignment uniformly. This is still not
    # the full K08 chain; it stops at the ATEALBIT/ALOWBIT source bridge.
    author_counts = {author: authors.count(author) for author in first_appearance_order}
    emily_positions = [n for n in range(1, 25) if authors[n - 1] == "Emily"]
    david_positions = [n for n in range(1, 25) if authors[n - 1] == "David"]
    non_emily = [n for n in range(1, 25) if n not in emily_positions]
    other_authors = [a for a in first_appearance_order if a not in ("Emily", "David")]
    other_counts = [author_counts[a] for a in other_authors]
    low_triples = [
        triple for triple in itertools.combinations(non_emily, 3)
        if tuple(len(tokens(notes[n])) for n in triple) == (11, 14, 22)
    ]
    summed_ways = 0
    low_triple_details = []
    for triple in low_triples:
        earliest = min(triple)
        k = sum(n < earliest for n in non_emily)
        ways = ways_david_fourth(k, other_counts)
        summed_ways += ways
        low_triple_details.append({"david_positions": list(triple), "earlier_non_emily_slots": k, "ways_david_fourth": ways})
    total_other_assignments = factorial(13) // prod(factorial(x) for x in other_counts)
    expected_valid_edit_total = 23 * comb(22, 7)
    if valid_edit_total != expected_valid_edit_total:
        raise SystemExit(f"valid-edit count mismatch: {valid_edit_total} != {expected_valid_edit_total}")
    if len(full_bridge_hits) != 1 or full_bridge_hits[0]["variant"] != "A0_LSB":
        raise SystemExit("expected exactly one full ATEALBIT/ALOWBIT bridge hit")
    joint_numerator = summed_ways
    joint_denominator = 4 * valid_edit_total * comb(16, 3) * total_other_assignments
    joint_p = Fraction(joint_numerator, joint_denominator)
    conditional_agent9_p = Fraction(1, comb(24, 8)) * Fraction(
        summed_ways, comb(16, 3) * total_other_assignments
    )

    def split_tokens(s):
        return re.findall(r"[A-Za-z0-9]+", s)
    split_low_triples = [
        triple for triple in itertools.combinations(non_emily, 3)
        if tuple(len(split_tokens(notes[n])) for n in triple) == (11, 14, 22)
    ]

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
        "author_counts": author_counts,
        "emily_positions": emily_positions,
        "david_positions": david_positions,
        "david_low_triples_11_14_22": low_triple_details,
        "david_low_triple_count": len(low_triples),
        "david_low_triples_same_under_hyphen_split": low_triples == split_low_triples,
        "valid_plus_one_edit_pairs_over_all_subsets": valid_edit_total,
        "valid_plus_one_edit_pairs_formula": "23 * C(22,7)",
        "other_author_counts": dict(zip(other_authors, other_counts)),
        "other_author_assignments_per_David_triple": total_other_assignments,
        "David_fourth_LOW_assignment_count": summed_ways,
        "joint_upstream_null": {
            "numerator": joint_numerator,
            "denominator": joint_denominator,
            "probability": str(joint_p),
            "reciprocal_approx": round(1 / float(joint_p), 3),
            "model": "uniform over pooled (8-subset, 4 encoding variant, valid +1 edit) triples; then uniform David 3-position choice and remaining author-label assignments"
        },
        "Agent9_fixed_A0_LSB_conditional_null": str(conditional_agent9_p),
        "scope_warning": "Joint upstream null only; codebook fixed to observed first-appearance order, no grouping/tail variants beyond A0/A1 x LSB/MSB, and no downstream component/half/bit-order/bookmark/transfer choices. Not the full K08 null.",
    }, indent=2))


if __name__ == "__main__":
    main()
