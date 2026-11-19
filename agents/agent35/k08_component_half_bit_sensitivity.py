#!/usr/bin/env python3
"""Enumerate K08 component low-bit outputs across half and bit-order choices."""
import itertools
import json
from collections import Counter
from pathlib import Path

ACCEPTED = ("K01", "K02", "K03", "K05", "K06", "K07")
OBSERVED_ORDER = ("K01", "K06", "K02")


def pack_lsb_plane(block, bit_order):
    if len(block) != 8:
        raise ValueError("each half must contain exactly eight bytes")
    bits = [byte & 1 for byte in block]
    if bit_order == "LSB":
        value = sum(bit << i for i, bit in enumerate(bits))
    elif bit_order == "MSB":
        value = sum(bit << (7 - i) for i, bit in enumerate(bits))
    else:
        raise ValueError(bit_order)
    return value


def selector(text):
    return sum((ord(ch) & 1) << i for i, ch in enumerate(text))


def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--candidate", type=Path, default=Path("candidate.json"))
    args = ap.parse_args()
    candidate = json.loads(args.candidate.read_text(encoding="utf-8"))
    values = {}
    for key in ACCEPTED:
        value = bytes.fromhex(candidate["components"][key]["component_hex"])
        if len(value) != 16:
            raise SystemExit(f"{key} is not a 16-byte accepted component")
        values[key] = value

    output = {}
    for half, start in (("upper", 0), ("lower", 8)):
        for bit_order in ("LSB", "MSB"):
            counts = Counter()
            literal_yea = 0
            for order in itertools.permutations(ACCEPTED, 3):
                raw = bytes(pack_lsb_plane(values[key][start:start + 8], bit_order) for key in order)
                text = "".join(chr(byte) for byte in raw)
                counts[selector(text)] += 1
                if text.upper() == "YEA":
                    literal_yea += 1
            observed = bytes(pack_lsb_plane(values[key][start:start + 8], bit_order) for key in OBSERVED_ORDER)
            observed_text = "".join(chr(byte) for byte in observed)
            output[f"{half}_{bit_order}"] = {
                "selector7_count_of_120": counts[7],
                "literal_YEA_casefold_count_of_120": literal_yea,
                "observed_K01_K06_K02_raw_hex": observed.hex().upper(),
                "observed_text_repr": repr(observed_text),
                "observed_selector": selector(observed_text),
            }

    print(json.dumps({
        "accepted_components": list(ACCEPTED),
        "ordered_triples": 120,
        "observed_order": list(OBSERVED_ORDER),
        "variants": output,
        "scope": "Half/bit-order sensitivity only; this is not the full K08 joint null."
    }, indent=2))


if __name__ == "__main__":
    main()
