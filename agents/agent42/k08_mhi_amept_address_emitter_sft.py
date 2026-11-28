#!/usr/bin/env python3
"""Target-blind MHI + transfer path emits the complete AT/MT/ET/PT address set."""
from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path
import re

PINS = {
    "crew": "13f2318ccc54f35b590a2d76b3a80244fe24d70f0699c67c05858e8b8983c5cb",
    "audit": "32970ad4431a9d610cc12dcca2813f39dd8fd2e396f9e748dc94b5932cb69adf",
    "mail13": "80d7b086d77fe7036a596198825dd221fec82e34cbd5a5a43edae74569e171aa",
}
SPAN_SHA = {
    "AT": "556713372501bc1d2a113beaf1fe4fe921267d5cd0c9655b2386ec536a6bffa0",
    "MT": "a9bb20e02706cf2079ed0a11b3fededd1c9325edeea5925734f7592ca7c943c9",
    "ET": "44359e21492d788147966d8c0bc5beb2f4f4d0d05dd36f3ff36a0cd36a349907",
    "PT": "9ad80878ed715fd6a1b1bf2b353e344a3dda762a4f3f5c713ccb2dad3d01d88f",
}
PAYLOAD_SHA = "4b3350e5b34e40cc9dd1ba53d926ef0455888aa056aac4ba7da141569664e95c"


def pack(bits):
    return sum((b & 1) << i for i, b in enumerate(bits))


def lowbit(text: str) -> int:
    return sum((ord(c.lower()) & 1) << i for i, c in enumerate(text))


def longest(a: list[str], b: list[str]):
    best = 0
    runs = []
    for i in range(len(a)):
        for j in range(len(b)):
            k = 0
            while i + k < len(a) and j + k < len(b) and a[i + k] == b[j + k]:
                k += 1
            if k > best:
                best = k
                runs = [(i, j, tuple(a[i:i + k]))] if k else []
            elif k and k == best:
                runs.append((i, j, tuple(a[i:i + k])))
    return best, runs


def main() -> None:
    root = Path(__file__).resolve().parents[2] / "resources" / "evidence"
    raw_crew = (root / "crew/noticeboard-and-desk-notes.txt").read_bytes()
    raw_audit = (root / "transfers/transfer-audit.jsonl").read_bytes()
    raw_mail13 = (root / "mail/13.eml").read_bytes()
    assert sha256(raw_crew).hexdigest() == PINS["crew"]
    assert sha256(raw_audit).hexdigest() == PINS["audit"]
    assert sha256(raw_mail13).hexdigest() == PINS["mail13"]

    notes = {}
    raw_lines = {}
    for m in re.finditer(
        r"^N(\d{2}) / (\w+) \[censored\]\n([^\n]+)$",
        raw_crew.decode("utf-8"),
        re.M,
    ):
        n = int(m.group(1))
        line = m.group(3)
        body = line.split(": ", 1)[1] if ": " in line else line
        notes[n] = re.findall(r"[A-Za-z0-9]+", body.lower())
        raw_lines[n] = line
    assert set(notes) == set(range(1, 25))

    # N20 is T in the A1Z26 note namespace. Its raw first 24 post-label
    # characters independently emit MHI under the established LOW BIT pack.
    n20_body = raw_lines[20]
    n20_bits = [ord(c) & 1 for c in n20_body]
    mhi = bytes(pack(n20_bits[i:i + 8]) for i in (0, 8, 16)).decode("ascii")
    assert mhi == "MHI"
    fixed_coordinate = chr(ord("A") + 20 - 1)
    assert fixed_coordinate == "T"

    # MHI A1Z26 addresses N13/N08/N09. Their first body-word HEAD parities
    # generate A; HEAD(MHI) is M; whole-token LOW BIT(MHI) is E.
    ids = [ord(c) - ord("A") + 1 for c in mhi]
    assert ids == [13, 8, 9]
    head_bits = [
        (ord(notes[n][0][0].upper()) - ord("A") + 1) & 1
        for n in ids
    ]
    a_value = pack(head_bits)
    assert head_bits == [1, 0, 0] and a_value == 1

    a = chr(ord("A") + a_value - 1)
    m = mhi[0]
    e_value = lowbit(mhi)
    e = chr(ord("A") + e_value - 1)
    assert (a, m, e) == ("A", "M", "E")
    first_three = [a + fixed_coordinate, m + fixed_coordinate, e + fixed_coordinate]
    assert first_three == ["AT", "MT", "ET"]

    # Independently established transfer side: MAIL13 fixes AX-7782; the
    # source-emitted ATTEMPT/TAILBIT/LOW-IF-EVEN rule chooses alternating
    # attempt 1/2 by zero-based sequence parity. Its packed low bits decode
    # PT under 7-bit ASCII with even parity.
    mail13 = raw_mail13.decode("utf-8")
    assert "final custodian handoff is AX-7782" in mail13
    rows = [json.loads(x) for x in raw_audit.decode().splitlines() if x.strip()]
    d = {
        (r["seq"], r["attempt"]): bytes.fromhex(r["checkpoint"])
        for r in rows
        if r.get("kind") == "CHUNK" and r["transfer"] == "AX-7782"
    }
    mixed = b"".join(d[(seq, 1 if seq % 2 == 0 else 2)] for seq in range(8))
    bits = [b & 1 for b in mixed]
    packed = bytes(pack(bits[o:o + 8]) for o in (0, 8))
    assert mixed.hex().upper() == "6224CEDCF3B873BA18887BE63DB0C5C9"
    assert packed.hex().upper() == "50D4"
    assert all(b.bit_count() % 2 == 0 for b in packed)
    pt = "".join(chr(b & 0x7F) for b in packed)
    assert pt == "PT"

    addresses = first_three + [pt]
    assert addresses == ["AT", "MT", "ET", "PT"]

    # The now-generated addresses recover the independently pinned spans.
    spans = {}
    positions = {}
    for address in addresses:
        left, right = (ord(c) - ord("A") + 1 for c in address)
        length, runs = longest(notes[left], notes[right])
        assert len(runs) == 1
        i, j, run = runs[0]
        text = " ".join(run)
        assert sha256(text.encode()).hexdigest() == SPAN_SHA[address]
        spans[address] = length
        positions[address] = j

    assert spans == {"AT": 2, "MT": 5, "ET": 2, "PT": 2}
    assert positions == {"AT": 6, "MT": 8, "ET": 13, "PT": 19}

    # AT through the word before PT is the already-fixed 13-token payload.
    payload = notes[20][positions["AT"]:positions["PT"]]
    assert len(payload) == 13
    assert sha256(" ".join(payload).encode()).hexdigest() == PAYLOAD_SHA

    print({
        "source_pins": "PASS",
        "target_or_nonce_read": False,
        "n20_raw_lowbit_token": mhi,
        "mhi_address_ids": ids,
        "mhi_head_parity_bits": head_bits,
        "generated_varying_coordinates": a + m + e + pt[0],
        "fixed_coordinate": fixed_coordinate,
        "addresses": addresses,
        "span_lengths": spans,
        "n20_positions": positions,
        "payload_word_count": len(payload),
        "payload_sha256": PAYLOAD_SHA,
        "complete_author_final_wording_emitted": False,
    })


if __name__ == "__main__":
    main()
