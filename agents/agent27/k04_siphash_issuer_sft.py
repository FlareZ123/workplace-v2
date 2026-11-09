"""H-17: original source heldout test for keyed SipHash-2-4 128-bit printer issuer.

Exploratory hypothesis only. Requires libsodium >=1.0.12 and Python 3.10+.
Run against an original 46-file archive ZIP, or run without arguments from the
repository checkout to read resources/ (read-only).
"""
from __future__ import annotations

import ctypes
import ctypes.util
import hashlib
import json
import re
import sys
import zipfile
from pathlib import Path

ROOT = Path(sys.argv[1]) if len(sys.argv) == 2 else Path(__file__).resolve().parents[2] / "resources"
SPOOL_SHA = "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"
MASK = bytes.fromhex("8556C8CB6140A7F9A5123AC7571BEE1C")
K04_SHA = bytes.fromhex("930a52a1bab97ca2966332137c99e99298ea6182fb32ab63a3421dfb4fd8c9e0")
K08_SHA = bytes.fromhex("285eb6b4196d21eaf47e251449e61e0bce28749881ccc5a065ca733b0c3fd747")

lib = ctypes.CDLL(ctypes.util.find_library("sodium"))
lib.sodium_init.restype = ctypes.c_int
assert lib.sodium_init() >= 0
for fn_name in ("crypto_shorthash_siphashx24", "crypto_shorthash_siphash24"):
    fn = getattr(lib, fn_name)
    fn.argtypes = [ctypes.c_void_p, ctypes.c_void_p, ctypes.c_ulonglong, ctypes.c_void_p]
    fn.restype = ctypes.c_int


def siphash(key: bytes, message: bytes, wide: bool) -> bytes:
    assert len(key) == 16
    out = ctypes.create_string_buffer(16 if wide else 8)
    fn = lib.crypto_shorthash_siphashx24 if wide else lib.crypto_shorthash_siphash24
    assert fn(out, message, len(message), key) == 0
    return out.raw


def emit(key: bytes, message: bytes, scheme: int) -> bytes:
    if scheme == 0:
        return siphash(key, message, True)
    if scheme == 1:
        return siphash(key, message + b"\x00", False) + siphash(key, message + b"\x01", False)
    if scheme == 2:
        return siphash(key, b"\x00" + message, False) + siphash(key, b"\x01" + message, False)
    return siphash(key, message, False) + siphash(key, message + b"\x00", False)


def layouts(value: bytes) -> tuple[bytes, ...]:
    return (
        value,
        value[::-1],
        b"".join(value[i:i + 4][::-1] for i in range(0, 16, 4)),
        b"".join(value[i:i + 4] for i in (12, 8, 4, 0)),
    )


def messages(row: dict[str, str]) -> tuple[bytes, ...]:
    job, attempt, state, category, dest, time = (
        row[k] for k in ("JOB", "ATTEMPT", "STATE", "CLASS", "DEST", "time")
    )
    suffix = int(job[-4:])
    return tuple(
        s.encode("ascii") for s in (
            job, f"{job}|{attempt}", f"{job}|{attempt}|{state}|{category}|{dest}",
            f"{job}|{time}", time, f"{job}/{category}/{dest}",
            f"{job}|{category}|{dest}", f"{job}-{attempt}-{category}-{dest}"
        )
    ) + (
        suffix.to_bytes(2, "big"), suffix.to_bytes(2, "little"),
        suffix.to_bytes(4, "big"), suffix.to_bytes(4, "little")
    )


def read_source(name: str) -> bytes:
    if ROOT.is_file():
        with zipfile.ZipFile(ROOT) as archive:
            return archive.read(name)
    return (ROOT / name).read_bytes()


def run() -> None:
    assert siphash(bytes(range(16)), b"", False).hex() == "310e0edd47db6f72"
    spool = read_source("evidence/print/spool-reconstruction.log")
    assert hashlib.sha256(spool).hexdigest() == SPOOL_SHA
    route = json.loads(read_source("evidence/recovery-routing.json"))
    acceptance = json.loads(read_source("acceptance.json"))
    assert bytes.fromhex(route["K04"]["masked_component"]) == MASK
    assert bytes.fromhex(acceptance["slot_sha256"]["K04"]) == K04_SHA
    assert bytes.fromhex(acceptance["slot_sha256"]["K08"]) == K08_SHA
    rows = []
    for line in spool.decode("utf-8").splitlines():
        if "PAYLOAD=" in line:
            values = dict(re.findall(r"(\w+)=([\w-]+)", line))
            values["time"] = line.split()[0]
            rows.append(values)
    assert len(rows) == 133
    controls = rows[:128]
    assert controls[0]["JOB"] == "PS-261003-0300"
    assert controls[-1]["JOB"] == "PS-261003-0427"
    assert all(r["ATTEMPT"] == "1" and r["STATE"] == "ACK" for r in controls)
    selected = next(r for r in rows if r["JOB"] == "PS-261003-0417" and r["ATTEMPT"] == "2")
    assert selected["PAYLOAD"] == "A9A9DC5731A5E2AE879C47215C2559D5"
    keys = [
        bytes.fromhex(s) for s in (
            "049AAB2E1CDE7A82CD7C60234303C91A",
            "0D7E3AB56FB75DA3EB0E2E06786D239E",
            "1384AF96E25D6ADA666209CB55E062FA",
            "FF8B78200A56E8586DCDA00EF01E4572",
            "5DBF40EE52FAAED9A536D3326CF0D95A",
            "93495F5E425AB8E592123DABAEB68545",
            route["K04"]["masked_component"], route["K08"]["desk_nonce"]
        )
    ]
    source_hits = []
    k04_hits = []
    k08_hits = []
    selected_values = set()
    for key_index, key in enumerate(keys):
        for message_index in range(12):
            for scheme in range(4):
                for layout in range(4):
                    assignment = (key_index, message_index, scheme, layout)
                    for row in controls:
                        value = layouts(emit(key, messages(row)[message_index], scheme))[layout]
                        if value == bytes.fromhex(row["PAYLOAD"]):
                            source_hits.append((assignment, row["JOB"]))
                    value = layouts(emit(key, messages(selected)[message_index], scheme))[layout]
                    selected_values.add(value)
                    if hashlib.sha256(bytes(a ^ b for a, b in zip(value, MASK))).digest() == K04_SHA:
                        k04_hits.append(assignment)
                    if hashlib.sha256(value).digest() == K08_SHA:
                        k08_hits.append(assignment)
    planted = emit(keys[6], messages(controls[0])[0], 0)
    positive = [
        (ki, mi, scheme, layout)
        for ki, key in enumerate(keys)
        for mi in range(12)
        for scheme in range(4)
        for layout in range(4)
        if layouts(emit(key, messages(controls[0])[mi], scheme))[layout] == planted
    ]
    assert positive == [(6, 0, 0, 0)]
    assert not source_hits and not k04_hits and not k08_hits
    print(json.dumps({
        "model": "SipHash-2-4-128 plus three doubled-SipHash-2-4-64 layouts",
        "source_control_replays": source_hits,
        "source_comparisons": 196608,
        "complete_selected_assignments": 1536,
        "distinct_complete_selected_coupons": len(selected_values),
        "K04_commitment_hits": k04_hits,
        "K08_direct_component_hits": k08_hits,
        "synthetic_issuer_control": positive,
    }, indent=2))


if __name__ == "__main__":
    run()
