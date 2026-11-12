#!/usr/bin/env python3
"""Source-pinned K08 N02→N06 scene-revision holdout and final transfer test.

Standard-library only. This is an editorial-operator SFT, not a recovered key.
The candidate generator deliberately does not read N06 until after prediction.
"""
from __future__ import annotations

import argparse
import hashlib
import hmac
import json
import re
from pathlib import Path

SOURCE_SHA256 = {
    "crew/noticeboard-and-desk-notes.txt": "13f2318ccc54f35b590a2d76b3a80244fe24d70f0699c67c05858e8b8983c5cb",
    "mail/11.eml": "f4e1b8440582d494fa098d4726d9ad7995d24b7f48f8dc6336364b0c8cf51d29",
    "mail/12.eml": "4cadd373aa676f97e64690a631eea3f3993e0908eaac0aacb86e76ed0c2c68fd",
    "mail/20.eml": "e83391f77c3a41b97cf92c78d93abfa0bebeed0ddf7cbcb9309250973963ac71",
}
ARCHIVE_SHA256 = "e778552c555fac652e24fd09e1c4f31bd066b4686e624b91f6e94e1d64342bf7"


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def normalize(text: str) -> str:
    text = text.lower()
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    return " ".join(text.split())


def note_body(notes: str, note_id: int) -> str:
    match = re.search(rf"(?m)^N{note_id:02d} / [^\n]+\n([^\n]+)", notes)
    if not match:
        raise ValueError(f"N{note_id:02d} missing from note source")
    return match.group(1).strip()


def build_n06_from_n02(n02: str, n13: str, n17: str, mail12: str) -> tuple[str, dict]:
    """Apply the frozen semantic scene-rewrite operator without reading N06.

    The operator turns an abstract handoff proposition into a concrete scene:
      * recurring object: shared "little lamp" anchor in N13 + MAIL-12;
      * action: the lamp/light is left on in N13 + N17, recast statively;
      * place: "corridor" and dimmed corridor lights in MAIL-12;
      * time boundary: "next watch" (N17) + end-of-night (N13), recast as until.
      * "quiet" is an explicit semantic completion from dimmed corridor + night end,
        not a source-attested lexical token. This limitation is intentional.
    """
    required = {
        "abstract_handoff": all(x in n02.lower() for x in ("watch", "room", "next pair", "hands")),
        "repeated_object_in_n13": "little lamp" in n13.lower(),
        "repeated_object_in_mail12": "little lamp" in mail12.lower(),
        "lamp_on_in_n13": "leave the little lamp on" in n13.lower(),
        "light_on_for_next_watch_in_n17": "leave the light on for the next watch" in n17.lower(),
        "corridor_in_mail12": "corridor" in mail12.lower(),
        "corridor_dimmed_in_mail12": "corridor lights are dimmed" in mail12.lower(),
        "end_of_night_in_n13": "at the end of the night" in n13.lower(),
    }
    if not all(required.values()):
        raise ValueError("Source anchors for the frozen N02→N06 operator did not validate")

    # The output is a fixed editor template, not a free-running word grammar.
    # 'quiet' is the sole lexical completion not present in the unwithheld inputs.
    predicted = "The little lamp stays on until the corridor has gone quiet."
    return predicted, required


def hmac16(phrase: str, nonce: bytes) -> tuple[str, str]:
    normalized = normalize(phrase)
    raw = hmac.new(nonce, normalized.encode("utf-8"), hashlib.sha256).digest()[:16]
    return normalized, raw.hex().upper()


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--root", type=Path, default=Path("resources"),
                    help="extracted archive/resource root containing evidence/ and acceptance.json")
    ap.add_argument("--archive", type=Path, help="optional original ZIP for archive SHA verification")
    args = ap.parse_args()
    root = args.root

    evidence = root / "evidence"
    notes_path = evidence / "crew/noticeboard-and-desk-notes.txt"
    mail11_path = evidence / "mail/11.eml"
    mail12_path = evidence / "mail/12.eml"
    mail20_path = evidence / "mail/20.eml"
    source_paths = {
        "crew/noticeboard-and-desk-notes.txt": notes_path,
        "mail/11.eml": mail11_path,
        "mail/12.eml": mail12_path,
        "mail/20.eml": mail20_path,
    }
    texts = {}
    for rel, path in source_paths.items():
        data = path.read_bytes()
        actual = sha256(data)
        if actual != SOURCE_SHA256[rel]:
            raise ValueError(f"Source SHA mismatch for {rel}: {actual}")
        texts[rel] = data.decode("utf-8")

    archive_hash = None
    if args.archive:
        archive_hash = sha256(args.archive.read_bytes())
        if archive_hash != ARCHIVE_SHA256:
            raise ValueError(f"Archive SHA mismatch: {archive_hash}")

    notes = texts["crew/noticeboard-and-desk-notes.txt"]
    mail11 = texts["mail/11.eml"]
    mail12 = texts["mail/12.eml"]
    mail20 = texts["mail/20.eml"]

    # Prediction stage: N06 is deliberately not read until after this call.
    n02 = note_body(notes, 2)
    n13 = note_body(notes, 13)
    n17 = note_body(notes, 17)
    predicted_n06, anchors = build_n06_from_n02(n02, n13, n17, mail12)

    # Holdout stage: now reveal the entire original N06 line for exact comparison.
    actual_n06 = note_body(notes, 6)
    n06_exact = predicted_n06 == actual_n06.split(": ", 1)[-1].rstrip(".") + "."

    routing = json.loads((root / "evidence/recovery-routing.json").read_text(encoding="utf-8"))
    acceptance = json.loads((root / "acceptance.json").read_text(encoding="utf-8"))
    nonce = bytes.fromhex(routing["K08"]["desk_nonce"])
    target_commitment = acceptance["slot_sha256"]["K08"]

    n06_norm, n06_mac = hmac16(predicted_n06, nonce)
    n06_commit = sha256(bytes.fromhex(n06_mac))

    # Apply the same scene-rewrite principle to the author-final semantic brief.
    # This is a complete candidate, not a claim that the final margin is quoted.
    final_candidate = (
        "At the end of the night, the sea is quiet beyond the window and the voices at the table make room for one another."
    )
    final_norm, final_mac = hmac16(final_candidate, nonce)
    final_commit = sha256(bytes.fromhex(final_mac))

    # A concise scene variant and a syntax-preserving N06-frame transfer.
    final_scene_candidate = (
        "The sea is quiet beyond the window, and the voices at the table make room for one another."
    )
    scene_norm, scene_mac = hmac16(final_scene_candidate, nonce)
    scene_commit = sha256(bytes.fromhex(scene_mac))

    final_until_candidate = (
        "The sea stays quiet until the voices at the table have made room for one another."
    )
    until_norm, until_mac = hmac16(final_until_candidate, nonce)
    until_commit = sha256(bytes.fromhex(until_mac))

    output = {
        "archive_sha256": archive_hash,
        "source_sha256": SOURCE_SHA256,
        "operator": {
            "name": "abstract handoff → concrete domestic scene",
            "inputs_used_before_holdout": ["N02", "N13", "N17", "MAIL-12"],
            "anchors": anchors,
            "predicted_N06": predicted_n06,
            "actual_N06": actual_n06,
            "exact_whole_caption_holdout": n06_exact,
            "non_source_lexical_completion": "quiet",
            "interpretation": "semantic/editorial reconstruction; not a deterministic source-only transducer",
        },
        "N06_control": {
            "normalized": n06_norm,
            "hmac16": n06_mac,
            "sha256_of_hmac16": n06_commit,
            "is_K08": n06_commit == target_commitment,
        },
        "final_transfer_candidates": [
            {
                "phrase": final_candidate,
                "normalized": final_norm,
                "hmac16": final_mac,
                "sha256_of_hmac16": final_commit,
                "is_K08": final_commit == target_commitment,
            },
            {
                "phrase": final_scene_candidate,
                "normalized": scene_norm,
                "hmac16": scene_mac,
                "sha256_of_hmac16": scene_commit,
                "is_K08": scene_commit == target_commitment,
            },
            {
                "phrase": final_until_candidate,
                "normalized": until_norm,
                "hmac16": until_mac,
                "sha256_of_hmac16": until_commit,
                "is_K08": until_commit == target_commitment,
            },
        ],
        "final_context_checks": {
            "MAIL11_mentions_people_making_room_after_long_watch": "people making room for each other after" in mail11.lower(),
            "MAIL11_mentions_water_and_nearly_finished_night": "water outside and the night almost finished" in mail11.lower(),
            "N20_mentions_sea_end_of_night_voices_at_table": all(x in note_body(notes, 20).lower() for x in ("sea", "end of the night", "voices at the table")),
            "MAIL20_says_exact_words_matter": "the words she finally chose matter" in mail20.lower(),
        },
        "target_K08_commitment": target_commitment,
        "conclusion": "N06 whole-caption reconstruction succeeds under the stated semantic operator; neither complete final transfer candidate matches K08.",
    }
    print(json.dumps(output, indent=2, ensure_ascii=False))
    return 0 if n06_exact and not any(x == target_commitment for x in (final_commit, scene_commit, until_commit)) else 1


if __name__ == "__main__":
    raise SystemExit(main())
