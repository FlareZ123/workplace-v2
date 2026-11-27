#!/usr/bin/env python3
"""Local-only source-holdout AES feedback test for the selected K04 printer job.

This is a conditional producer F(B0)=B1, F(B1)=B2 screen. The source-derived
16-byte AES key is constructed from the N09/N13/N23/N20 cue path, never
embedded or printed. The selected attempt-2 ACK and original K04 commitment
are not read. No PDF, private material, live equipment or public CI.
"""
from collections import Counter
from hashlib import sha256
from pathlib import Path
import json
import re

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

ROOT = Path(__file__).resolve().parents[2] / "resources" / "evidence"
HASHES = {
    "crew/noticeboard-and-desk-notes.txt": "13f2318ccc54f35b590a2d76b3a80244fe24d70f0699c67c05858e8b8983c5cb",
    "print/spool-reconstruction.log": "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083",
    "recovery-routing.json": "f8fcbca73d23bf1066edb88c088f89cd24cf22e7c78a4a412166254a4764d8a5",
}


def sources():
    data = {}
    for path, digest in HASHES.items():
        buf = (ROOT / path).read_bytes()
        assert sha256(buf).hexdigest() == digest, f"source pin: {path}"
        data[path] = buf
    notes = {
        int(m.group(1)): m.group(2)
        for m in re.finditer(
            r"^N(\d{2}) /[^\n]+\n([^\n]+)",
            data["crew/noticeboard-and-desk-notes.txt"].decode("ascii"), re.M
        )
    }
    assert len(notes) == 24
    tokenize = lambda s: re.findall(r"[A-Za-z0-9]+", s)
    # Source-selected cue route: three first words, then N20 word19.
    words = (
        tokenize(notes[9].split(":", 1)[-1])[0],
        tokenize(notes[13])[0],
        tokenize(notes[23])[0],
        tokenize(notes[20])[18],
    )
    keys = (
        "".join(words).upper().encode("ascii"),
        "".join(words).lower().encode("ascii"),
        "".join(w.capitalize() for w in words).encode("ascii"),
    )
    assert all(len(k) == 16 for k in keys)
    route = json.loads(data["recovery-routing.json"])
    tweaks = (
        b"\x00" * 16,
        bytes.fromhex(route["K08"]["desk_nonce"]),
        bytes.fromhex(route["K04"]["masked_component"]),
    )
    source_packets = {}
    for line in data["print/spool-reconstruction.log"].decode("ascii").splitlines():
        if "JOB=PS-261003-0417" not in line:
            continue
        fields = dict(re.findall(r"([A-Z_]+)=([^\s]+)", line))
        attempt = fields.get("ATTEMPT")
        if fields.get("STATE") != "REQUESTED" or attempt not in ("1", "3"):
            continue
        source_packets[int(attempt)] = bytes.fromhex(fields["PAYLOAD"])
    assert set(source_packets) == {1, 3}
    assert all(len(x) == 16 for x in source_packets.values())
    return keys, tweaks, source_packets


def views():
    result = {}
    for chunk_width in (4, 8):
        for reverse_chunks in (False, True):
            for reverse_bytes in (False, True):
                chunks = [list(range(i, i + chunk_width)) for i in range(0, 16, chunk_width)]
                if reverse_chunks:
                    chunks.reverse()
                if reverse_bytes:
                    chunks = [c[::-1] for c in chunks]
                indices = tuple(i for c in chunks for i in c)
                result[indices] = (chunk_width, reverse_chunks, reverse_bytes)
    assert len(result) == 6
    return result


def xor16(a, b):
    return bytes(x ^ y for x, y in zip(a, b))


def emitter(key, tweak, inxor, outxor, direction):
    cipher = Cipher(algorithms.AES(key), modes.ECB())

    def emit(block):
        start = xor16(block, tweak) if inxor else block
        ctx = cipher.encryptor() if direction == "encrypt" else cipher.decryptor()
        output = ctx.update(start) + ctx.finalize()
        return xor16(output, tweak) if outxor else output

    return emit


def main():
    keys, tweaks, originals = sources()
    original_a, original_c = originals[1], originals[3]
    tested = controls = matches = 0
    for key in keys:
        for ti, tweak in enumerate(tweaks):
            for inxor, outxor in ((False, False), (False, True), (True, False), (True, True)):
                if ti == 0 and (inxor or outxor):
                    continue
                if ti != 0 and not (inxor or outxor):
                    continue
                for direction in ("encrypt", "decrypt"):
                    f = emitter(key, tweak, inxor, outxor, direction)
                    for positions in views():
                        a = bytes(original_a[i] for i in positions)
                        c = bytes(original_c[i] for i in positions)
                        # A -> missing B -> heldout C; test C first.
                        tested += 1
                        if f(f(a)) == c:
                            matches += 1
                        # End-to-end planted whole-block positive, independent
                        # of original packets, for the same exact mapping.
                        planted_a = bytes(range(16))
                        planted_b = f(planted_a)
                        planted_c = f(planted_b)
                        assert f(planted_a) == planted_b and f(f(planted_a)) == planted_c
                        controls += 1
    assert tested == 252 and controls == 252
    print(json.dumps({
        "source_flank_presentations": tested,
        "whole_flank_source_matches": matches,
        "planted_positive_controls": controls,
        "selected_ack2_read": False, "acceptance_read": False,
        "source_sha_pins_verified": True,
    }, sort_keys=True))


if __name__ == "__main__":
    main()
