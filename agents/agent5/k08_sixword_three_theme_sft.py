"""Complete six-word Emily-lexicon caption search with N20 theme anchors.

Use a disjoint half-open first-token shard for a bounded read-only run.
This tests an exploratory authoring model, not a quoted final inscription.
"""
from __future__ import annotations

import argparse
import hashlib
import hmac
import json
import re
from pathlib import Path

NOTES_SHA = "13f2318ccc54f35b590a2d76b3a80244fe24d70f0699c67c05858e8b8983c5cb"
VOCAB_SHA = "a323bd487dce87a6023e813c2e9756e9103df4f2f771f3e5c0455e0f1e11e261"
EXPECTED_TOTAL = 241_258_500
SELECTED = {2, 6, 10, 13, 17, 18, 20, 23}
HUMAN = {"room", "table", "voices"}


def vocabulary(notes: bytes) -> list[str]:
    assert hashlib.sha256(notes).hexdigest() == NOTES_SHA
    text = notes.decode("utf-8")
    records = re.findall(r"(?ms)^N(\d\d) /[^\n]*\n(.*?)(?=^N\d\d /|\Z)", text)
    words = sorted({word for number, body in records if int(number) in SELECTED
                    for word in re.findall(r"[a-z0-9]+", body.lower())})
    assert len(words) == 90
    assert hashlib.sha256("\n".join(words).encode()).hexdigest() == VOCAB_SHA
    return words


def run(resources: Path, start: int, end: int) -> dict:
    notes = (resources / "evidence/crew/noticeboard-and-desk-notes.txt").read_bytes()
    words = vocabulary(notes)
    assert 0 <= start < end <= len(words)
    routing = json.loads((resources / "evidence/recovery-routing.json").read_text())
    acceptance = json.loads((resources / "acceptance.json").read_text())
    nonce = bytes.fromhex(routing["K08"]["desk_nonce"])
    target = bytes.fromhex(acceptance["slot_sha256"]["K08"])
    first_draft = "a good watch leaves the room ready for the next pair of hands"
    assert hmac.digest(nonce, first_draft.encode(), "sha256")[:16].hex().upper() == (
        "BF889359B0303F2B2B2FD96AE841210B"
    )

    def checksum(text: str) -> tuple[bytes, bytes]:
        raw = hmac.digest(nonce, text.encode("ascii"), "sha256")[:16]
        return hashlib.sha256(raw).digest(), raw

    plant = "sea night voices table room good"
    planted_target, _ = checksum(plant)
    kinds = [int(word == "sea") | (int(word == "night") << 1) |
             (int(word in HUMAN) << 2) for word in words]
    total = positive = 0
    hits: list[dict[str, str]] = []

    def walk(sentence: str, depth: int, mask: int) -> None:
        nonlocal total, positive
        if depth == 6:
            assert mask == 7
            digest, component = checksum(sentence)
            total += 1
            positive += digest == planted_target
            if digest == target:
                hits.append({"caption": sentence, "K08": component.hex().upper()})
            return
        remaining = 5 - depth
        for word, flag in zip(words, kinds):
            next_mask = mask | flag
            if (7 ^ next_mask).bit_count() <= remaining:
                walk(sentence + " " + word, depth + 1, next_mask)

    for index in range(start, end):
        walk(words[index], 1, kinds[index])
    assert positive == int(start <= words.index("sea") < end)
    if start == 0 and end == 90:
        assert total == EXPECTED_TOTAL
    return {"first_token_shard": f"{start}:{end}", "full_phrases_checked": total,
            "original_K08_matches": hits, "planted_positive_matches": positive}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--resources", type=Path, default=Path(__file__).resolve().parents[2] / "resources")
    parser.add_argument("--first-start", type=int, default=0)
    parser.add_argument("--first-end", type=int, default=90)
    args = parser.parse_args()
    print(json.dumps(run(args.resources, args.first_start, args.first_end), indent=2))


if __name__ == "__main__":
    main()
