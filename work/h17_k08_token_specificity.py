#!/usr/bin/env python3
"""Source-blind specificity benchmark for the frozen H-17 A1/low-bit parser.

Reads the canonical candidate.json, reports raw-byte A1 pairs and the fixed
first-bit-as-LSB low-bit pack, then compares those rules with a deterministic
uniform 16-byte null panel. It does not search phrase candidates or choose a
parser orientation separately for any slot.
"""
import argparse
import json
import random
from collections import Counter

ACCEPTED_SLOTS = {"K01", "K02", "K03", "K05", "K06", "K07"}
TARGET_TOKENS = {
    bytes((3, 67)), bytes((67, 3)),       # C3
    bytes((10, 77)), bytes((77, 10)),    # M10
    bytes((80, 212)), bytes((212, 80)),  # P212
}


def colname(n: int) -> str:
    if not 1 <= n <= 255:
        raise ValueError(n)
    out = ""
    while n:
        n, r = divmod(n - 1, 26)
        out = chr(65 + r) + out
    return out


def raw_cells(raw: bytes):
    row_col, col_row = [], []
    for i in range(0, 16, 2):
        a, b = raw[i], raw[i + 1]
        if 1 <= a <= 255 and 1 <= b <= 255:
            row_col.append(f"{colname(b)}{a}")
            col_row.append(f"{colname(a)}{b}")
        else:
            row_col.append(None)
            col_row.append(None)
    return row_col, col_row


def lowbit_pack(raw: bytes) -> bytes:
    bits = [byte & 1 for byte in raw]
    return bytes(sum(bits[i + j] << j for j in range(8)) for i in (0, 8))


def lowbit_a1_tokens(raw: bytes):
    a, b = lowbit_pack(raw)
    tokens = []
    # Fixed A1 parser, both orientations, applied identically to every slot.
    if 65 <= a <= 90 and 1 <= b <= 255:
        tokens.append(("letter-row", f"{chr(a)}{b}"))
    if 65 <= b <= 90 and 1 <= a <= 255:
        tokens.append(("row-letter", f"{chr(b)}{a}"))
    return bytes((a, b)), tokens


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("candidate", help="canonical candidate.json")
    ap.add_argument("--samples", type=int, default=1_000_000)
    ap.add_argument("--seed", type=int, default=20261119)
    args = ap.parse_args()

    with open(args.candidate, encoding="utf-8") as f:
        data = json.load(f)
    accepted = {k: bytes.fromhex(v) for k, v in data.items()
                if k in ACCEPTED_SLOTS and isinstance(v, str)}
    if set(accepted) != ACCEPTED_SLOTS or any(len(v) != 16 for v in accepted.values()):
        raise SystemExit("candidate.json does not contain the six expected accepted 16-byte components")

    print("ACCEPTED_COMPONENTS")
    for slot, raw in accepted.items():
        rc, cr = raw_cells(raw)
        packed, tokens = lowbit_a1_tokens(raw)
        print(json.dumps({
            "slot": slot,
            "hex": raw.hex().upper(),
            "raw_row_col": rc,
            "raw_col_row": cr,
            "raw_valid_pairs": sum(x is not None for x in rc),
            "lowbit_hex": packed.hex().upper(),
            "lowbit_a1_tokens": tokens,
        }, separators=(",", ":")))

    rng = random.Random(args.seed)
    all8 = a1_any = a1_mail = exact_targets = 0
    raw_valid_sum = 0
    token_counts = Counter()
    for _ in range(args.samples):
        raw = rng.randbytes(16)
        rc, _ = raw_cells(raw)
        valid = sum(x is not None for x in rc)
        raw_valid_sum += valid
        all8 += (valid == 8)
        packed, tokens = lowbit_a1_tokens(raw)
        a1_any += bool(tokens)
        a1_mail += any(1 <= int(token[1:]) <= 24 for _, token in tokens)
        exact_targets += packed in TARGET_TOKENS
        for kind, token in tokens:
            token_counts[(kind, token)] += 1

    p_all8 = (255 / 256) ** 16
    p_a1 = 2 * (26 / 256) * (255 / 256) - (26 / 256) ** 2
    p_a1_mail = 2 * (26 / 256) * (24 / 256)
    p_exact = len(TARGET_TOKENS) / 65536
    print("NULL_PANEL")
    print(json.dumps({
        "samples": args.samples,
        "seed": args.seed,
        "raw_all_8_A1_count": all8,
        "raw_all_8_A1_rate": all8 / args.samples,
        "raw_all_8_A1_exact_probability": p_all8,
        "mean_valid_raw_pairs": raw_valid_sum / (args.samples * 8),
        "lowbit_A1_either_orientation_count": a1_any,
        "lowbit_A1_either_orientation_rate": a1_any / args.samples,
        "lowbit_A1_exact_probability": p_a1,
        "lowbit_A1_mail_note_row_count": a1_mail,
        "lowbit_A1_mail_note_row_rate": a1_mail / args.samples,
        "lowbit_A1_mail_note_row_exact_probability": p_a1_mail,
        "exact_C3_M10_P212_either_orientation_count": exact_targets,
        "exact_C3_M10_P212_rate": exact_targets / args.samples,
        "exact_C3_M10_P212_exact_probability": p_exact,
        "top_lowbit_A1_tokens": token_counts.most_common(10),
    }, separators=(",", ":")))


if __name__ == "__main__":
    main()
