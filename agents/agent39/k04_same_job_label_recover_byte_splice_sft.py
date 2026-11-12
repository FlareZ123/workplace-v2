"""Bounded K04 same-job cross-version byte/word/XOR assembly test.

The two same-job ACK versions both target DEST=bench. Test per-byte splices
between them, 32-bit word assembly/permutations, and XOR subsets across all four
same-job records. These are exploratory models; the source does not attest that
a splice or combination occurred.
Run from repository root: python agents/agent39/k04_same_job_label_recover_byte_splice_sft.py
"""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RES = ROOT / "resources"
SPOOL = RES / "evidence/print/spool-reconstruction.log"
ROUTE = RES / "evidence/recovery-routing.json"
ACCEPT = RES / "acceptance.json"
EXPECTED_SHA256 = {
    SPOOL: "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083",
    ROUTE: "f8fcbca73d23bf1066edb88c088f89cd24cf22e7c78a4a412166254a4764d8a5",
    ACCEPT: "681739241b757b471acca4c0fef9d9d97e9493883887736d5db3b92bfb0c137f",
}


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def source_job_rows():
    rows = []
    for line in SPOOL.read_text(encoding="utf-8").splitlines():
        if "JOB=PS-261003-0417" not in line:
            continue
        fields = dict(token.split("=", 1) for token in line.split() if "=" in token)
        rows.append((
            int(fields["ATTEMPT"]), fields["STATE"], fields["CLASS"], fields["DEST"],
            bytes.fromhex(fields["PAYLOAD"]),
        ))
    expected = [
        (1, "ACK", "LABEL", "bench"),
        (1, "REQUESTED", "RECOVER", "bench"),
        (2, "ACK", "RECOVER", "bench"),
        (3, "REQUESTED", "RECOVER", "bench"),
    ]
    assert [(a, s, c, d) for a, s, c, d, _ in rows] == expected, rows
    assert all(len(payload) == 16 for *_, payload in rows)
    return rows


def wordwise_candidates(versions):
    assert len(versions) == 4 and all(len(p) == 16 for p in versions)
    # Each 32-bit word position is selected from one of the four same-job records.
    import itertools
    for choice in itertools.product(range(4), repeat=4):
        yield choice, b"".join(
            versions[choice[i]][4 * i:4 * i + 4] for i in range(4)
        )


def permuted_wordwise_candidates(versions):
    assert len(versions) == 4 and all(len(p) == 16 for p in versions)
    import itertools
    for choice in itertools.product(range(4), repeat=4):
        for order in itertools.permutations(range(4)):
            yield choice, order, b"".join(
                versions[choice[i]][4 * order[i]:4 * order[i] + 4]
                for i in range(4)
            )


def xor_subset_candidates(versions):
    assert len(versions) == 4 and all(len(p) == 16 for p in versions)
    from functools import reduce
    for subset in range(1, 1 << 4):
        yield subset, bytes(
            reduce(int.__xor__, (version[i] for j, version in enumerate(versions) if (subset >> j) & 1), 0)
            for i in range(16)
        )


def candidates(label: bytes, recover: bytes):
    assert len(label) == len(recover) == 16
    for selector in range(1 << 16):
        # Bit i selects LABEL[i]; zero selects RECOVER[i].
        yield selector, bytes(
            label[i] if (selector >> i) & 1 else recover[i]
            for i in range(16)
        )


def pairwise_bytewise_candidates(versions):
    assert len(versions) == 4 and all(len(p) == 16 for p in versions)
    import itertools
    for left, right in itertools.combinations(range(4), 2):
        for selector in range(1 << 16):
            yield left, right, selector, bytes(
                versions[left][i] if (selector >> i) & 1 else versions[right][i]
                for i in range(16)
            )


def matches(label: bytes, recover: bytes, mask: bytes, commitment: str):
    hits = []
    unique = set()
    for selector, payload in candidates(label, recover):
        if payload in unique:
            continue
        unique.add(payload)
        component = bytes(a ^ b for a, b in zip(payload, mask))
        if sha256(component) == commitment:
            hits.append((selector, payload.hex().upper(), component.hex().upper()))
    return len(unique), hits


def main() -> None:
    for path, expected in EXPECTED_SHA256.items():
        actual = sha256(path.read_bytes())
        assert actual == expected, (str(path), actual, expected)

    route = json.loads(ROUTE.read_text(encoding="utf-8"))["K04"]
    acceptance = json.loads(ACCEPT.read_text(encoding="utf-8"))
    mask = bytes.fromhex(route["masked_component"])
    commitment = acceptance["slot_sha256"]["K04"]
    assert len(mask) == 16

    rows = source_job_rows()
    versions = [row[4] for row in rows]
    label, recover = versions[0], versions[2]
    unique, original_hits = matches(label, recover, mask, commitment)

    pairwise_seen = set()
    pairwise_hits = []
    for left, right, selector, payload in pairwise_bytewise_candidates(versions):
        pairwise_seen.add(payload)
        component = bytes(a ^ b for a, b in zip(payload, mask))
        if sha256(component) == commitment:
            pairwise_hits.append((left, right, selector, payload.hex().upper(), component.hex().upper()))

    contiguous = set()
    for start in range(17):
        for end in range(start, 17):
            contiguous.add(bytes(
                label[i] if start <= i < end else recover[i]
                for i in range(16)
            ))
    contiguous_hits = []
    for payload in contiguous:
        component = bytes(a ^ b for a, b in zip(payload, mask))
        if sha256(component) == commitment:
            contiguous_hits.append((payload.hex().upper(), component.hex().upper()))

    wordwise_seen = set()
    wordwise_hits = []
    for choice, payload in wordwise_candidates(versions):
        wordwise_seen.add(payload)
        component = bytes(a ^ b for a, b in zip(payload, mask))
        if sha256(component) == commitment:
            wordwise_hits.append((choice, payload.hex().upper(), component.hex().upper()))

    permuted_seen = set()
    permuted_hits = []
    for choice, order, payload in permuted_wordwise_candidates(versions):
        permuted_seen.add(payload)
        component = bytes(a ^ b for a, b in zip(payload, mask))
        if sha256(component) == commitment:
            permuted_hits.append((choice, order, payload.hex().upper(), component.hex().upper()))

    xor_seen = set()
    xor_hits = []
    for subset, payload in xor_subset_candidates(versions):
        xor_seen.add(payload)
        component = bytes(a ^ b for a, b in zip(payload, mask))
        if sha256(component) == commitment:
            xor_hits.append((subset, payload.hex().upper(), component.hex().upper()))

    planted_pair = (1, 3)
    planted_pair_selector = 0xA53C
    planted_pair_payload = next(
        payload for left, right, selector, payload in pairwise_bytewise_candidates(versions)
        if (left, right, selector) == (planted_pair[0], planted_pair[1], planted_pair_selector)
    )
    planted_pair_commitment = sha256(bytes(a ^ b for a, b in zip(planted_pair_payload, mask)))
    planted_pair_hits = [
        (left, right, selector) for left, right, selector, payload in pairwise_bytewise_candidates(versions)
        if sha256(bytes(a ^ b for a, b in zip(payload, mask))) == planted_pair_commitment
    ]
    assert planted_pair_hits == [(planted_pair[0], planted_pair[1], planted_pair_selector)], planted_pair_hits
    print("PAIRWISE_BYTEWISE_SYNTHETIC_POSITIVE", planted_pair, hex(planted_pair_selector), planted_pair_hits)

    # Verify the exhaustive selector logic against a planted complete target.
    planted_selector = 0xA53C
    planted_payload = next(
        payload for selector, payload in candidates(label, recover)
        if selector == planted_selector
    )
    planted_component = bytes(a ^ b for a, b in zip(planted_payload, mask))
    planted_commitment = sha256(planted_component)
    planted_unique, planted_hits = matches(label, recover, mask, planted_commitment)
    assert planted_unique == 1 << 16
    assert planted_hits == [(
        planted_selector, planted_payload.hex().upper(), planted_component.hex().upper()
    )], planted_hits

    print("SOURCE_LABEL_ACK", label.hex().upper())
    print("SOURCE_RECOVER_ACK", recover.hex().upper())
    print("SOURCE_REQUESTED1", versions[1].hex().upper())
    print("SOURCE_REQUESTED3", versions[3].hex().upper())
    print("DESTINATION_PAIR", "bench -> bench")
    print("BYTEWISE_SPLICE_ASSIGNMENTS", 1 << 16)
    print("BYTEWISE_UNIQUE_PAYLOADS", unique)
    print("ORIGINAL_K04_COMMITMENT_HITS", original_hits)
    print("PAIRWISE_BYTEWISE_ASSIGNMENTS", 6 * (1 << 16))
    print("PAIRWISE_BYTEWISE_UNIQUE_PAYLOADS", len(pairwise_seen))
    print("PAIRWISE_BYTEWISE_K04_HITS", pairwise_hits)
    print("CONTIGUOUS_INTERVAL_UNIQUE_PAYLOADS", len(contiguous))
    print("CONTIGUOUS_INTERVAL_K04_HITS", contiguous_hits)
    print("WORDWISE_ASSIGNMENTS", 4 ** 4)
    print("WORDWISE_UNIQUE_PAYLOADS", len(wordwise_seen))
    print("WORDWISE_K04_HITS", wordwise_hits)
    print("PERMUTED_WORDWISE_ASSIGNMENTS", 4 ** 4 * 24)
    print("PERMUTED_WORDWISE_UNIQUE_PAYLOADS", len(permuted_seen))
    print("PERMUTED_WORDWISE_K04_HITS", permuted_hits)
    print("NONEMPTY_XOR_SUBSETS", (1 << 4) - 1)
    print("XOR_SUBSET_UNIQUE_PAYLOADS", len(xor_seen))
    print("XOR_SUBSET_K04_HITS", xor_hits)
    planted_choice = (3, 1, 2, 0)
    planted_wordwise = next(
        payload for choice, payload in wordwise_candidates(versions)
        if choice == planted_choice
    )
    planted_wordwise_commitment = sha256(bytes(a ^ b for a, b in zip(planted_wordwise, mask)))
    planted_wordwise_hits = [
        choice for choice, payload in wordwise_candidates(versions)
        if sha256(bytes(a ^ b for a, b in zip(payload, mask))) == planted_wordwise_commitment
    ]
    assert planted_wordwise_hits == [planted_choice], planted_wordwise_hits
    print("WORDWISE_SYNTHETIC_POSITIVE", planted_choice, planted_wordwise_hits)
    planted_permuted_choice = (3, 1, 2, 0)
    planted_permuted_order = (2, 0, 3, 1)
    planted_permuted = next(
        payload for choice, order, payload in permuted_wordwise_candidates(versions)
        if choice == planted_permuted_choice and order == planted_permuted_order
    )
    planted_permuted_commitment = sha256(bytes(a ^ b for a, b in zip(planted_permuted, mask)))
    planted_permuted_hits = [
        (choice, order) for choice, order, payload in permuted_wordwise_candidates(versions)
        if sha256(bytes(a ^ b for a, b in zip(payload, mask))) == planted_permuted_commitment
    ]
    assert planted_permuted_hits == [(planted_permuted_choice, planted_permuted_order)], planted_permuted_hits
    print("PERMUTED_WORDWISE_SYNTHETIC_POSITIVE", planted_permuted_choice, planted_permuted_order, planted_permuted_hits)

    planted_subset = 0b1011
    planted_xor = next(payload for subset, payload in xor_subset_candidates(versions) if subset == planted_subset)
    planted_xor_commitment = sha256(bytes(a ^ b for a, b in zip(planted_xor, mask)))
    planted_xor_hits = [
        subset for subset, payload in xor_subset_candidates(versions)
        if sha256(bytes(a ^ b for a, b in zip(payload, mask))) == planted_xor_commitment
    ]
    assert planted_xor_hits == [planted_subset], planted_xor_hits
    print("XOR_SUBSET_SYNTHETIC_POSITIVE", planted_subset, planted_xor_hits)
    print("SYNTHETIC_POSITIVE_SELECTOR", hex(planted_selector))
    print("SYNTHETIC_POSITIVE_HITS", len(planted_hits))
    print("RESULT", "NO_SAME_JOB_PAIRWISE_BYTE_WORD_OR_XOR_CANDIDATE")


if __name__ == "__main__":
    main()
