#!/usr/bin/env python3
"""Bounded K08 STOW14/N23 whole-text selection falsification.

Reads only the crew note sheet, reconstructed print log, routing sheet and
acceptance JSON. It never opens the hash-only BX25-08 PDF or private/.
"""
from __future__ import annotations
import argparse
import hashlib
import hmac
import json
import re
from pathlib import Path

NOTE_RE = re.compile(
    r"(?m)^N(\d{2}) / ([^\n]+)\n(.*?)(?=\n\nN\d{2} / |\Z)", re.S
)
WORD_RE = re.compile(r"[A-Za-z0-9]+(?:[-'][A-Za-z0-9]+)*")
SPOOL_RE = re.compile(
    r"JOB=PS-261003-(\d{4}) ATTEMPT=1 STATE=ACK CLASS=(\w+) "
    r"PAYLOAD=([0-9A-F]{32}) DEST=(\w+)"
)


def normalize(text: str) -> str:
    text = text.lower()
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    return " ".join(text.split())


def hmac_commit(text: str, nonce: bytes, target: str) -> tuple[str, str, bool]:
    normalized = normalize(text)
    mac16 = hmac.new(nonce, normalized.encode("utf-8"), hashlib.sha256).digest()[:16]
    digest = hashlib.sha256(mac16).hexdigest()
    return mac16.hex().upper(), digest, digest == target


def pack_lsb(bits: list[int]) -> bytes:
    return bytes(
        sum(bits[i + j] << j for j in range(8))
        for i in range(0, len(bits) - 7, 8)
    )


def spool_selector(payload: bytes) -> tuple[str, int]:
    low = pack_lsb([byte & 1 for byte in payload])
    hex_text = low.hex().upper()
    selector = sum((ord(ch) & 1) << i for i, ch in enumerate(hex_text))
    return hex_text, selector


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--evidence-root", type=Path, default=Path("resources/evidence"))
    ap.add_argument("--acceptance", type=Path, default=Path("resources/acceptance.json"))
    args = ap.parse_args()
    note_path = args.evidence_root / "crew/noticeboard-and-desk-notes.txt"
    spool_path = args.evidence_root / "print/spool-reconstruction.log"
    route_path = args.evidence_root / "recovery-routing.json"
    for path in (note_path, spool_path, route_path, args.acceptance):
        if not path.is_file():
            raise SystemExit(f"missing required source: {path}")

    note_raw = note_path.read_bytes()
    spool_raw = spool_path.read_bytes()
    route = json.loads(route_path.read_text(encoding="utf-8"))
    acceptance = json.loads(args.acceptance.read_text(encoding="utf-8"))
    nonce = bytes.fromhex(route["K08"]["desk_nonce"])
    target = acceptance["slot_sha256"]["K08"]

    notes: dict[int, dict] = {}
    for match in NOTE_RE.finditer(note_raw.decode("utf-8")):
        note_id = int(match.group(1))
        author = match.group(2).split()[0]
        body = re.sub(r"^[^:]+:\s*", "", match.group(3).strip())
        words = WORD_RE.findall(body)
        notes[note_id] = {"author": author, "body": body, "words": words}
    if sorted(notes) != list(range(1, 25)):
        raise SystemExit("expected exactly N01..N24")

    payloads: dict[int, bytes] = {}
    for line in spool_raw.decode("utf-8").splitlines():
        match = SPOOL_RE.search(line)
        if not match:
            continue
        job = int(match.group(1))
        note_id = job - 300
        if 1 <= note_id <= 24:
            payloads[note_id] = bytes.fromhex(match.group(3))
    if sorted(payloads) != list(range(1, 25)):
        raise SystemExit("expected one ordinal PS-0301..0324 ACK1 payload per N01..N24")

    stow = [
        n for n in range(1, 25)
        if notes[n]["author"] in {"Simon", "Emily", "Gabriel"}
    ]
    print("SOURCE_SHA256 notes", hashlib.sha256(note_raw).hexdigest())
    print("SOURCE_SHA256 spool", hashlib.sha256(spool_raw).hexdigest())
    print("SOURCE_SHA256 routing", hashlib.sha256(route_path.read_bytes()).hexdigest())
    print("STOW14", stow, "count", len(stow))
    print("N23-minus-14", 23 - len(stow), "(ordinal locator only)")

    # Conditional ordinal note/job map: apply the low-bit selector to each
    # 16-byte ACK1 payload, but do not promote it to a route/authentication.
    selector_rows = {}
    for n in range(1, 25):
        _, selector_rows[n] = spool_selector(payloads[n])
    print(
        "PS0323_LOWBIT",
        pack_lsb([b & 1 for b in payloads[23]]).hex().upper(),
        "selector",
        selector_rows[23],
    )
    print("ALL_24_ORDINAL_SELECTORS", [selector_rows[n] for n in range(1, 25)])

    # Test the simplest whole-text edit interpretation: payload LSBs select words.
    for source_id, mask_id in ((23, 23), (20, 23), (23, 20), (20, 20)):
        source_words = notes[source_id]["words"][:16]
        bits = [b & 1 for b in payloads[mask_id]][:len(source_words)]
        selected = [w for w, bit in zip(source_words, bits) if bit]
        complement = [w for w, bit in zip(source_words, bits) if not bit]
        for label, words in (("ones", selected), ("zeros", complement)):
            mac16, digest, hit = hmac_commit(" ".join(words), nonce, target)
            print(
                f"WORD_MASK source=N{source_id:02d} mask=PS{300+mask_id} "
                f"{label}={normalize(' '.join(words))!r} "
                f"HMAC16={mac16} digest={digest} hit={hit}"
            )

    # Test one 14-word selection from the 14 STOW notes.
    for label, indices in (
        ("low_nibble", [b & 0x0F for b in payloads[23][:14]]),
        ("high_nibble", [b >> 4 for b in payloads[23][:14]]),
    ):
        selected = [
            notes[n]["words"][k % len(notes[n]["words"])]
            for n, k in zip(stow, indices)
        ]
        mac16, digest, hit = hmac_commit(" ".join(selected), nonce, target)
        print(
            f"STOW14_WORD_PICK {label} indices={indices} "
            f"text={normalize(' '.join(selected))!r} "
            f"HMAC16={mac16} digest={digest} hit={hit}"
        )

    # Specificity control for interpreting STOW14 as a 14-position note shift.
    sets = [set(w.lower() for w in notes[n]["words"]) for n in range(1, 25)]
    authors = [notes[n]["author"] for n in range(1, 25)]
    offset_stats = []
    for offset in range(1, 24):
        same = sum(
            authors[i] == authors[(i + offset) % 24] for i in range(24)
        )
        jaccard = []
        for i in range(24):
            a, b = sets[i], sets[(i + offset) % 24]
            jaccard.append(len(a & b) / len(a | b) if a | b else 0.0)
        offset_stats.append((offset, same, sum(jaccard) / 24))
    print("SHIFT14", next(x for x in offset_stats if x[0] == 14))
    print(
        "SHIFT14_BACKWARD_PAIRS",
        [
            (
                n,
                ((n - 14 - 1) % 24) + 1,
                notes[n]["author"],
                notes[((n - 14 - 1) % 24) + 1]["author"],
            )
            for n in range(1, 25)
        ],
    )
    max_same = max(x[1] for x in offset_stats)
    max_jaccard = max(x[2] for x in offset_stats)
    print(
        "SHIFT_MAX_SAME_AUTHOR",
        max_same,
        "offsets",
        [x[0] for x in offset_stats if x[1] == max_same],
    )
    print(
        "SHIFT_MAX_AVG_JACCARD",
        max_jaccard,
        "offsets",
        [x[0] for x in offset_stats if x[2] == max_jaccard],
    )

    # Known label controls: the same per-job LSB word mask does not reconstruct
    # either explicit old label in N17/N18.
    for n in (17, 18):
        words = notes[n]["words"]
        bits = [b & 1 for b in payloads[n]][:min(16, len(words))]
        selected = [w for w, bit in zip(words, bits) if bit]
        print(
            f"LABEL_CONTROL N{n:02d} original={normalize(notes[n]['body'])!r} "
            f"selected={normalize(' '.join(selected))!r}"
        )

    print("DECISION: no source-authenticated complete K08 text-selection rule or HMAC hit")
    print("LIMIT: note/job suffix join and ACK1 payload integrity are not authenticated;")
    print("       K08 route names crew notes/noticeboard drafts, not spool payloads.")


if __name__ == "__main__":
    main()
