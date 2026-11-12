"""Bounded K04 same-job cross-version byte/word-splice construction test.

The two same-job ACK versions both target DEST=bench. Test per-byte splices
between them and 32-bit word assembly across all four same-job records. These
are exploratory models; the source does not attest that a splice occurred.
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


def candidates(label: bytes, recover: bytes):
    assert len(label) == len(recover) == 16
    for selector in range(1 << 16):
        # Bit i selects LABEL[i]; zero selects RECOVER[i].
        yield selector, bytes(
            label[i] if (selector >> i) & 1 else recover[i]
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
    print("CONTIGUOUS_INTERVAL_UNIQUE_PAYLOADS", len(contiguous))
    print("CONTIGUOUS_INTERVAL_K04_HITS", contiguous_hits)
    print("WORDWISE_ASSIGNMENTS", 4 ** 4)
    print("WORDWISE_UNIQUE_PAYLOADS", len(wordwise_seen))
    print("WORDWISE_K04_HITS", wordwise_hits)
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
    print("SYNTHETIC_POSITIVE_SELECTOR", hex(planted_selector))
    print("SYNTHETIC_POSITIVE_HITS", len(planted_hits))
    print("RESULT", "NO_SAME_JOB_BYTE_OR_WORD_SPLICE_CANDIDATE")


if __name__ == "__main__":
    main()
