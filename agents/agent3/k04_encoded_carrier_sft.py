"""H-17 accepted K04 alternate-encoding source-carrier sieve.

Searches 16-byte candidates recovered from base64 (standard/URL), base32,
base58, Python Base85 and Adobe ASCII85 text in all source bytes. The
previous all-file source audit already exhausted raw 16-byte/ASCII hex.
This script reads the original local export ZIP or the resources directory;
it never alters the evidence, route, acceptance or candidate.
Run: python agents/agent3/k04_encoded_carrier_sft.py <original-export.zip>
"""
from __future__ import annotations

import base64
import hashlib
import json
from collections import Counter
from pathlib import Path
import re
import sys
import zipfile

ALPHABET58 = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"
PATTERNS = (
    ("base64", r"[A-Za-z0-9+/_=-]{22,}"),
    ("base32", r"[A-Za-z2-7=]{26,}"),
    ("base58", r"[123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz]{21,}"),
    ("base85", r"[!-~]{20,}"),
)
WINDOWS = {
    "base64": (22, 23, 24, 28, 32),
    "base32": (26, 32),
    "base58": (21, 22, 23, 24),
    "base85": (20,),
}


def base58_decode(value):
    n = 0
    for digit in value:
        n = n * 58 + ALPHABET58.index(digit)
    zeroes = bytes([0]) * (len(value) - len(value.lstrip("1")))
    return zeroes + (n.to_bytes((n.bit_length()+7)//8, "big") if n else b"")


def candidates(raw):
    # Latin-1 maps each original byte to exactly one code point. ASCII regex
    # runs therefore stay valid even for binary members (such as raw recorder).
    text = raw.decode("latin1")
    for kind, pattern in PATTERNS:
        for token in re.finditer(pattern, text):
            string = token.group()
            for width in WINDOWS[kind]:
                for begin in range(len(string) - width + 1):
                    part = string[begin:begin + width]
                    if kind == "base64":
                        padding = "=" * (-len(part) % 4)
                        for label, decode in (
                            ("base64-standard", lambda s: base64.b64decode(s, validate=True)),
                            ("base64-url", base64.urlsafe_b64decode),
                        ):
                            try:
                                data = decode(part + padding)
                            except (ValueError, base64.binascii.Error):
                                continue
                            for at in range(len(data)-15):
                                yield label, data[at:at+16]
                    elif kind == "base32":
                        try:
                            data = base64.b32decode(part.upper() + "=" * (-len(part) % 8))
                        except (ValueError, base64.binascii.Error):
                            continue
                        for at in range(len(data)-15):
                            yield "base32", data[at:at+16]
                    elif kind == "base58":
                        data = base58_decode(part)
                        if len(data) == 16:
                            yield "base58", data
                    else:
                        for label, decode in (
                            ("base85", base64.b85decode),
                            ("ascii85", base64.a85decode),
                        ):
                            try:
                                data = decode(part)
                            except (ValueError, base64.binascii.Error, OverflowError):
                                continue
                            if len(data) == 16:
                                yield label, data


def files_at(path):
    if path.is_file() and path.suffix.lower() == ".zip":
        with zipfile.ZipFile(path) as archive:
            return [
                (i.filename, archive.read(i))
                for i in archive.infolist() if not i.is_dir()
            ]
    return [(str(p.relative_to(path)), p.read_bytes())
            for p in sorted(path.rglob("*")) if p.is_file()]


def main(path):
    files = files_at(path)
    data = dict(files)
    route_name = next(n for n in data if n.endswith("evidence/recovery-routing.json"))
    accept_name = next(n for n in data if n.endswith("acceptance.json"))
    spool_name = next(n for n in data
                      if n.endswith("evidence/print/spool-reconstruction.log"))
    assert hashlib.sha256(data[spool_name]).hexdigest() == (
        "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"
    )
    route = json.loads(data[route_name])
    accept = json.loads(data[accept_name])
    mask = bytes.fromhex(route["K04"]["masked_component"])
    target = accept["slot_sha256"]["K04"]
    assert mask.hex().upper() == "8556C8CB6140A7F9A5123AC7571BEE1C"
    assert target == "930a52a1bab97ca2966332137c99e99298ea6182fb32ab63a3421dfb4fd8c9e0"

    sample = bytes.fromhex("A9A9DC5731A5E2AE879C47215C2559D5")
    for name, encoded in (
        ("base64", base64.b64encode(sample)),
        ("base32", base64.b32encode(sample)),
        ("base85", base64.b85encode(sample)),
        ("ascii85", base64.a85encode(sample)),
    ):
        assert any(value == sample for _, value in
                   candidates(b"ENCODED=" + encoded + b"\n")), name
    assert base58_decode("22") == b"\x3b"
    assert base58_decode("1") == b"\x00"
    print("SYNTHETIC_CARRIER_CONTROLS PASS")

    counts, hits = Counter(), []
    for name, blob in files:
        for encoding, coupon in candidates(blob):
            counts[encoding] += 1
            component = bytes(x ^ y for x, y in zip(coupon, mask))
            if hashlib.sha256(component).hexdigest() == target:
                hits.append((name, encoding, coupon.hex().upper()))
    if path.is_file():
        print("INPUT_ZIP_SHA256", hashlib.sha256(path.read_bytes()).hexdigest())
    print("SOURCE_FILES", len(files), "ASSIGNMENTS", sum(counts.values()))
    print("MODEL_COUNTS", dict(counts), "ORIGINAL_K04_MATCHES", hits)


if __name__ == "__main__":
    main(Path(sys.argv[1]) if len(sys.argv) > 1
         else Path(__file__).resolve().parents[2] / "resources")
