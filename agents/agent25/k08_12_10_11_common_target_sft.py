#!/usr/bin/env python3
"""Test one finite K08 text-extraction hypothesis from selectors 12/10/11.

Run from the workplace-v2 repository root:
    python agents/agent25/k08_12_10_11_common_target_sft.py

The MAIL-12 body is deliberately treated as a text node under the existing
K08 HMAC-low-bit note router. That extension is a hypothesis, not an
authenticated historical rule. The script freezes the resulting paths and
checks the single common-note candidate against the unchanged K08 commitment.
"""
from __future__ import annotations

import collections
import email
import hashlib
import hmac
import json
import re
from email import policy
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
EVIDENCE = ROOT / "resources" / "evidence"
ROUTING = ROOT / "resources" / "evidence" / "recovery-routing.json"
ACCEPTANCE = ROOT / "resources" / "acceptance.json"

EXPECTED_SHA256 = {
    "notes": "13f2318ccc54f35b590a2d76b3a80244fe24d70f0699c67c05858e8b8983c5cb",
    "mail12": "4cadd373aa676f97e64690a631eea3f3993e0908eaac0aacb86e76ed0c2c68fd",
    "routing": "f8fcbca73d23bf1066edb88c088f89cd24cf22e7c78a4a412166254a4764d8a5",
    "acceptance": "681739241b757b471acca4c0fef9d9d97e9493883887736d5db3b92bfb0c137f",
}
EXPECTED_EMAIL_REACH = {0: 2, 1: 3, 2: 6, 3: 5, 4: 2, 5: 1}
EXPECTED_CANDIDATE = (
    "at the end of the night the mugs stood beside the window and "
    "somebody had remembered to leave the little lamp on"
)
EXPECTED_HMAC16 = "26076C5426016BDB768A2B83E9F36857"
EXPECTED_CANDIDATE_SHA256 = (
    "33e430295cb8ba51e8432fdab4a4da518c89ea8ee71dd2d3dc9fe09ee74f3d20"
)


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def normalize(text: str) -> str:
    return " ".join(re.sub(r"[^a-z0-9\s]", " ", text.lower()).split())


def low_value(text: str) -> int:
    return sum((ord(ch) & 1) << i for i, ch in enumerate(text))


def low_pack(raw: bytes) -> bytes:
    assert len(raw) == 16
    return bytes(
        sum((raw[i + j] & 1) << j for j in range(8))
        for i in (0, 8)
    )


def parse_notes(text: str) -> dict[int, tuple[str, str]]:
    pattern = re.compile(
        r"^N(\d{2}) / ([^\n]+?)\n(.*?)(?=\n\nN\d{2} /|\Z)",
        re.MULTILINE | re.DOTALL,
    )
    parsed = {
        int(match.group(1)): (
            match.group(2).split()[0],
            match.group(3).strip(),
        )
        for match in pattern.finditer(text)
    }
    assert sorted(parsed) == list(range(1, 25))
    return parsed


def note_body(raw: str) -> str:
    return raw.split(":", 1)[1].strip() if ":" in raw else raw


def k08_hmac16(text: str, key: bytes) -> bytes:
    return hmac.new(
        key, normalize(text).encode("utf-8"), hashlib.sha256
    ).digest()[:16]


def selector(text: str, key: bytes) -> tuple[str, int]:
    digest = k08_hmac16(text, key)
    packed_hex = low_pack(digest).hex().upper()
    return digest.hex().upper(), low_value(packed_hex)


def trace_to_target(
    start: int, edges: dict[int, int], target: int = 13
) -> list[int] | None:
    if not 1 <= start <= 24:
        return None
    path = [start]
    seen = {start}
    while path[-1] != target:
        nxt = edges[path[-1]]
        if not 1 <= nxt <= 24 or nxt in seen:
            return path
        path.append(nxt)
        seen.add(nxt)
    return path


def read_mail_body(number: int) -> str:
    raw = (EVIDENCE / "mail" / f"{number:02d}.eml").read_bytes()
    message = email.message_from_bytes(raw, policy=policy.default)
    content = message.get_content()
    assert isinstance(content, str)
    return content


def main() -> None:
    notes_path = EVIDENCE / "crew" / "noticeboard-and-desk-notes.txt"
    notes_bytes = notes_path.read_bytes()
    mail12_bytes = (EVIDENCE / "mail" / "12.eml").read_bytes()
    routing_bytes = ROUTING.read_bytes()
    acceptance_bytes = ACCEPTANCE.read_bytes()

    assert sha256(notes_bytes) == EXPECTED_SHA256["notes"]
    assert sha256(mail12_bytes) == EXPECTED_SHA256["mail12"]
    assert sha256(routing_bytes) == EXPECTED_SHA256["routing"]
    assert sha256(acceptance_bytes) == EXPECTED_SHA256["acceptance"]

    routing = json.loads(routing_bytes)
    acceptance = json.loads(acceptance_bytes)
    key = bytes.fromhex(routing["K08"]["desk_nonce"])
    notes = parse_notes(notes_bytes.decode("utf-8"))

    # Pre-registered source order is MAIL-12, N10, N11: selector 12/10/11.
    mail12_text = read_mail_body(12)
    assert "small card by the shelf" in normalize(mail12_text)
    assert notes[10][0] == "Emily"
    assert notes[11][0] == "David"
    assert notes[13][0] == "Emily"
    assert notes[11][1].startswith("Mug shelf:")

    mail12_hmac, mail12_start = selector(mail12_text, key)
    n10_hmac, n10_start = selector(note_body(notes[10][1]), key)
    n11_hmac, n11_start = selector(note_body(notes[11][1]), key)

    edges = {
        number: selector(note_body(raw), key)[1]
        for number, (_, raw) in notes.items()
    }

    paths = {
        "MAIL12": trace_to_target(mail12_start, edges),
        "N10": trace_to_target(n10_start, edges),
        "N11": trace_to_target(n11_start, edges),
    }
    assert mail12_start == 6
    assert n10_start == 13
    assert n11_start == 13
    assert paths == {
        "MAIL12": [6, 10, 13],
        "N10": [13],
        "N11": [13],
    }

    common = set(paths["MAIL12"] or [])
    for path in (paths["N10"], paths["N11"]):
        common.intersection_update(path or [])
    common_in_source_order = [
        node for node in (paths["MAIL12"] or []) if node in common
    ]
    assert common_in_source_order == [13]
    candidate = normalize(note_body(notes[13][1]))
    assert candidate == EXPECTED_CANDIDATE

    # Check all 20 email bodies as matched controls. This shows whether the
    # extension to email bodies is actually selective.
    distance_counts: collections.Counter[int] = collections.Counter()
    for number in range(1, 21):
        start = selector(read_mail_body(number), key)[1]
        path = trace_to_target(start, edges)
        if path is not None and path[-1] == 13:
            distance_counts[len(path) - 1] += 1

    assert dict(sorted(distance_counts.items())) == EXPECTED_EMAIL_REACH
    assert sum(distance_counts.values()) == 19

    candidate_hmac = k08_hmac16(candidate, key)
    candidate_commit = sha256(candidate_hmac)
    expected_commit = acceptance["slot_sha256"]["K08"]
    assert candidate_hmac.hex().upper() == EXPECTED_HMAC16
    assert candidate_commit == EXPECTED_CANDIDATE_SHA256
    assert candidate_commit != expected_commit

    print("SOURCE_ORDER=MAIL12,N10,N11")
    print(f"MAIL12_HMAC16={mail12_hmac}; SELECTOR={mail12_start}")
    print(f"N10_HMAC16={n10_hmac}; SELECTOR={n10_start}")
    print(f"N11_HMAC16={n11_hmac}; SELECTOR={n11_start}")
    print("NOTE_PATHS=MAIL12:6->10->13;N10:13;N11:13")
    print("FIRST_COMMON_NOTE=N13")
    print("NORMALIZED_CANDIDATE=" + candidate)
    print("CANDIDATE_HMAC16=" + candidate_hmac.hex().upper())
    print("CANDIDATE_SHA256=" + candidate_commit)
    print("EXPECTED_K08_SHA256=" + expected_commit)
    print("K08_MATCH=NO")
    print("EMAIL_CONTROL_REACH_N13=19/20")
    print("EMAIL_CONTROL_EDGE_DISTANCES=" + json.dumps(
        dict(sorted(distance_counts.items())), sort_keys=True
    ))
    print("LIMIT=the HMAC router's extension to email bodies is a hypothesis")
    print("PASS: deterministic candidate and negative commitment reproduced")


if __name__ == "__main__":
    main()
