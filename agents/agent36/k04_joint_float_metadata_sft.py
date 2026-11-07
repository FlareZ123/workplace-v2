"""H17 printer: single CPython random() joint CLASS/DEST issuer source-only test.

This speculative model differs from two-call randbelow(3) and one-call randbelow(9):
one random() float consumes exactly TWO consecutive native MT words and maps
the resulting 53-bit uniform draw to one of nine joint category labels.
Other hidden words in each gap are unrestricted filler. The historical selected
coupon is withheld completely.

Run: python agents/agent36/k04_joint_float_metadata_sft.py resources

Uses existing Agent49 immutable hypothetical p951 source fixture, without
assuming the printer really ran CPython.
"""
from __future__ import annotations

from collections import defaultdict
from pathlib import Path
import hashlib
import re
import sys
from random import Random

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "agent49"))
import k04_p951_symbolic_basis as mt


def possible_codes(known_first: tuple[int | None, ...], known_second: tuple[int | None, ...]) -> set[int]:
    """Over-approximate all 9-way outcomes of a single 53-bit random() draw.

    Correlations between missing bits are ignored, making a failure rigorous
    under the hypothetical fixture while allowing spurious possible codes.
    """
    lo = hi = 0
    for index, fixed in [(j, known_first[j]) for j in range(31, 4, -1)] + [
        (j, known_second[j]) for j in range(31, 5, -1)
    ]:
        lo = (lo << 1) | (fixed or 0)
        hi = (hi << 1) | (int(fixed is None or fixed == 1))
    assert 0 <= lo <= hi < (1 << 53)
    # Python multiplies a binary64 float by 9, with a final rounding. At
    # boundaries k=2,4,6,8 a 53-bit value can round *up* to the next integer.
    # The endpoint map below matches CPython's actual int(random()*9).
    return set(range(int((lo / (1 << 53)) * 9),
                     int((hi / (1 << 53)) * 9) + 1))


def packet_codes(w: list[tuple[int | None, ...]], selector: str) -> set[int]:
    assert len(w) >= 2
    if selector == "first":
        positions = (0,)
    elif selector == "last":
        positions = (len(w) - 2,)
    else:
        assert selector == "any_adjacent"
        positions = range(len(w) - 1)
    return set().union(*(possible_codes(w[i], w[i + 1]) for i in positions))


def find_matching(domains: dict[tuple[bytes, bytes], set[int]]) -> dict[tuple[bytes, bytes], int] | None:
    """All nine labels must be mapped injectively to nine native random bins."""
    assigned: dict[int, tuple[bytes, bytes]] = {}

    def augment(label: tuple[bytes, bytes], seen: set[int]) -> bool:
        for code in sorted(domains[label]):
            if code in seen:
                continue
            seen.add(code)
            if code not in assigned or augment(assigned[code], seen):
                assigned[code] = label
                return True
        return False

    if not all(augment(label, set()) for label in sorted(domains, key=lambda x: len(domains[x]))):
        return None
    return {label: code for code, label in assigned.items()}


def reduce_domains(
    labels: list[tuple[bytes, bytes]],
    domain_by_gap: list[set[int]],
    class_offset: int,
    destination_offset: int,
    limit: int = 127,
) -> tuple[dict[tuple[bytes, bytes], set[int]], list[tuple[int, tuple[bytes, bytes]]]]:
    domains: dict[tuple[bytes, bytes], set[int]] = defaultdict(lambda: set(range(9)))
    witnesses = []
    for row in range(limit):
        label = (labels[row + class_offset][0], labels[row + destination_offset][1])
        before = domains[label]
        after = before & domain_by_gap[row]
        if before and not after:
            witnesses.append((row, label))
        domains[label] = after
    return dict(domains), witnesses


def main(root: Path) -> None:
    raw = (root / "evidence/print/spool-reconstruction.log").read_bytes()
    assert hashlib.sha256(raw).hexdigest() == "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"
    labels = re.findall(rb"CLASS=(\w+) PAYLOAD=[0-9A-F]{32} DEST=(\w+)", raw)
    assert len(labels) == 133
    assert labels[129] == (b"RECOVER", b"bench")

    # Real standard-library random() positive: first two native getrandbits(32)
    # from a second identical seed must reproduce the same 53-bit float/bin.
    r_float = Random(1357911)
    r_native = Random(1357911)
    for _ in range(2000):
        actual = int(r_float.random() * 9)
        a, b = r_native.getrandbits(32), r_native.getrandbits(32)
        expected = ((a >> 5) << 26) | (b >> 6)
        assert actual == (9 * expected) >> 53
        known_a, known_b = (tuple((x >> j) & 1 for j in range(32)) for x in (a,b))
        assert possible_codes(known_a, known_b) == {actual}

    for k in (2, 4, 6, 8):
        around = (k * (1 << 53)) // 9
        for r in range(around - 4, around + 5):
            a = (r >> 26) << 5
            b = (r & ((1 << 26) - 1)) << 6
            native_a, native_b = (tuple((x >> j) & 1 for j in range(32))
                                  for x in (a, b))
            assert possible_codes(native_a, native_b) == {
                int((r / (1 << 53)) * 9)
            }

    source, bank = mt.source(root)
    assert source.rank == 15365
    gap_domains: dict[str, list[set[int]]] = {
        "first": [], "last": [], "any_adjacent": []
    }
    for row in range(127):
        start = mt.STARTS[row] + 4
        end = mt.STARTS[row + 1]
        assert end - start >= 2
        window = []
        for stage in range(start, end):
            output = mt.temper(mt.get(bank, stage))
            window.append(tuple(source.predict(x) for x in output))
        for selector in gap_domains:
            gap_domains[selector].append(packet_codes(window, selector))

    # A two-gap stage source witness has a single adjacent pair, so no
    # source-index ambiguity. It should be included in ALL three selectors.
    two_word_gaps = [i for i in range(127) if mt.STARTS[i+1]-mt.STARTS[i] == 6]
    assert len(two_word_gaps) == 53 and {22, 23, 77} <= set(two_word_gaps)
    for i in range(127):
        if mt.STARTS[i + 1] - mt.STARTS[i] == 6:
            assert gap_domains["first"][i] == gap_domains["last"][i] == gap_domains["any_adjacent"][i]

    results = []
    for selector, code_sets in gap_domains.items():
        for c_offset in (0, 1):
            for d_offset in (0, 1):
                train, train_witnesses = reduce_domains(labels, code_sets, c_offset, d_offset, 64)
                whole, witnesses = reduce_domains(labels, code_sets, c_offset, d_offset)
                mapping = find_matching(whole)
                out = {
                    "selector": selector,
                    "label_bind": [c_offset, d_offset],
                    "training_nonempty_domains": sum(bool(x) for x in train.values()),
                    "whole_nonempty_domains": sum(bool(x) for x in whole.values()),
                    "full_codebook_exists": mapping is not None,
                    "gap_domain_empty": sum(not s for s in code_sets),
                    "first_two_empty_domain_witnesses": [
                        {"row": row, "class": label[0].decode(), "dest": label[1].decode()}
                        for row, label in witnesses[:2]
                    ],
                    "train_first_two_witnesses": [
                        {"row": row, "class": label[0].decode(), "dest": label[1].decode()}
                        for row, label in train_witnesses[:2]
                    ],
                }
                results.append(out)
                print("MODEL", out)
    assert len(results) == 12
    assert not any(row["full_codebook_exists"] for row in results), (
        "Model survived: examine exact source and predict selected coupon!", results
    )
    print("SYNTHETIC_PYTHON_FLOAT_2000 PASS")
    print("SOURCE_RANK", source.rank, "hypothetical_selected_bits_authenticated", 0)
    print("FROZEN_METADATA_MODEL_COUNT", len(results))
    print("ORIGINAL_K04_K08_UNCHANGED")


if __name__ == "__main__":
    main(Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parents[2] / "resources")
