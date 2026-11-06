"""H-17 K08: original printer CLASS/DEST trits as 27-symbol text, source-pinned SFT.

From repo root: python agents/agent44/k08_categorical_base27_sft.py
From local archive: python agents/agent44/k08_categorical_base27_sft.py --archive h17-archive-dump.zip
"""
from __future__ import annotations

import argparse
import hashlib
import hmac
import itertools
import json
from pathlib import Path
import re
import zipfile

SPOOL_SHA = "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"
ALPHABET = " abcdefghijklmnopqrstuvwxyz"
OLD_N02 = "a good watch leaves the room ready for the next pair of hands"
OLD_N02_HMAC16 = "BF889359B0303F2B2B2FD96AE841210B"
SYNTHETIC_N17 = "leave the light on for the next watch"


def load(name: str, archive: str | None) -> bytes:
    if archive:
        with zipfile.ZipFile(archive) as pack:
            return pack.read(name)
    return (Path(__file__).resolve().parents[2] / "resources" / name).read_bytes()


def encode_synthetic(phrase: str) -> list[tuple[int, int]]:
    trits = []
    for char in phrase:
        symbol = ALPHABET.index(char)
        trits.extend((symbol // 9, (symbol // 3) % 3, symbol % 3))
    if len(trits) % 2:
        trits.append(0)
    return list(zip(trits[0::2], trits[1::2]))


def decode(trits: list[int], offset: int, shift: int, sign: int) -> str:
    codes = [9 * trits[i] + 3 * trits[i + 1] + trits[i + 2]
             for i in range(offset, len(trits) - 2, 3)]
    return "".join(ALPHABET[(shift + sign * code) % 27] for code in codes)


def main(archive: str | None) -> None:
    source = load("evidence/print/spool-reconstruction.log", archive)
    assert hashlib.sha256(source).hexdigest() == SPOOL_SHA
    rows = [dict(re.findall(r"([A-Z]+)=([^ ]+)", line))
            for line in source.decode("utf-8").splitlines()
            if line.startswith("2026")]
    assert len(rows) == 133
    route = json.loads(load("evidence/recovery-routing.json", archive))
    acceptance = json.loads(load("acceptance.json", archive))
    nonce = bytes.fromhex(route["K08"]["desk_nonce"])
    commitment = bytes.fromhex(acceptance["slot_sha256"]["K08"])

    def digest(phrase: str) -> bytes:
        return hashlib.sha256(hmac.digest(nonce, phrase.encode("ascii"), "sha256")[:16]).digest()

    assert hmac.digest(nonce, OLD_N02.encode("ascii"), "sha256")[:16].hex().upper() == OLD_N02_HMAC16
    synthetic_rows = encode_synthetic(SYNTHETIC_N17)
    synthetic_trits = [part for pair in synthetic_rows for part in pair]
    reconstructed = decode(synthetic_trits, 0, 0, 1)
    assert reconstructed == SYNTHETIC_N17
    assert digest(reconstructed) == digest(SYNTHETIC_N17)
    print("ORIGINAL_SOURCE_PIN", SPOOL_SHA, "rows", len(rows))
    print("N02_REAL_HMAC16_POSITIVE", OLD_N02_HMAC16)
    print("INDEPENDENT_SYNTHETIC_N17_BASE27_POSITIVE", len(synthetic_rows), "rows")

    classes = sorted({row["CLASS"] for row in rows})
    destinations = sorted({row["DEST"] for row in rows})
    assert len(classes) == len(destinations) == 3
    views = {
        "regular128": rows[:128],
        "all133": rows,
        "without_selected": rows[:129] + rows[130:],
        "job_sorted": sorted(rows, key=lambda row: (row["JOB"], int(row["ATTEMPT"]))),
        "reversed": rows[::-1],
        "attempt_selected": rows[:128] + [rows[129]] + rows[131:],
    }
    tried = set()
    decodes = 0
    hits = []
    for view_name, ordered in views.items():
        for codes_class in itertools.permutations(range(3)):
            class_map = dict(zip(classes, codes_class))
            for codes_dest in itertools.permutations(range(3)):
                dest_map = dict(zip(destinations, codes_dest))
                for order in ("cd", "dc"):
                    trits = [digit for row in ordered for digit in
                             ((class_map[row["CLASS"]], dest_map[row["DEST"]]) if order == "cd"
                              else (dest_map[row["DEST"]], class_map[row["CLASS"]]))]
                    for reverse in (False, True):
                        stream = trits[::-1] if reverse else trits
                        for phase in (0, 1, 2):
                            for shift in range(27):
                                for sign in (-1, 1):
                                    text = decode(stream, phase, shift, sign)
                                    decodes += 1
                                    words = text.split()
                                    if len(words) < 2:
                                        continue
                                    for first in range(len(words)):
                                        for stop in range(first + 1, min(len(words), first + 26) + 1):
                                            candidate = " ".join(words[first:stop])
                                            if candidate in tried:
                                                continue
                                            tried.add(candidate)
                                            if digest(candidate) == commitment:
                                                hits.append((view_name, codes_class, codes_dest,
                                                             order, reverse, phase, shift, sign, candidate))
    assert decodes == 139968, ("decodes", decodes)
    assert len(tried) == 323060, ("unique", len(tried))
    assert hits == [], ("unexpected original K08 recovery", hits)
    print("ORIGINAL_K08_DECODED_STREAMS", decodes)
    print("ORIGINAL_K08_UNIQUE_NORMALIZED_ONE_TO_26_WORD_SPANS", len(tried))
    print("ORIGINAL_K08_COMMITMENT_HITS", len(hits))
    print("STATUS", "NO_MATCH, K04/K08 remain unresolved")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--archive", help="Original 46-file ZIP; defaults to repository resources")
    main(parser.parse_args().archive)
