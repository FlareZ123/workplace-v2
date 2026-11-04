"""K04 hypothetical binary B seed: exact 8-byte two-source donor sieve.
No disputed ACK2 payload, its XOR mask, acceptance target or verifier is read.
Run: python agents/agent29/k04_binary_seed_twostream_donor_sft.py
"""
from __future__ import annotations
import hashlib
import re
from pathlib import Path
from zipfile import ZipFile
ROOT = Path(__file__).resolve().parents[2]
ZIP_SHA = "e778552c555fac652e24fd09e1c4f31bd066b4686e624b91f6e94e1d64342bf7"
TARGET = bytes.fromhex("06EDCDADFD6A4CF7")
LIMIT = (1 << 64) - 1

def carriers() -> tuple[dict[bytes, tuple[str, str, int]], int, int]:
    original = [(p.relative_to(ROOT / "resources").as_posix(), p.read_bytes())
                for p in (ROOT / "resources").rglob("*") if p.is_file()]
    archive = ROOT / "h17-archive-dump.zip"
    if archive.exists():
        raw = archive.read_bytes()
        assert hashlib.sha256(raw).hexdigest() == ZIP_SHA
        with ZipFile(archive) as z:
            original = [(entry.filename, z.read(entry)) for entry in z.infolist()
                        if not entry.is_dir()]
        assert len(original) == 46
        original.append(("[original ZIP container]", raw))
    spool = dict(original)["evidence/print/spool-reconstruction.log"]
    assert hashlib.sha256(spool).hexdigest() == "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"
    seen = {}
    raw_count = hex_count = 0
    for name, data in original:
        if name == "evidence/print/spool-reconstruction.log":
            data = b"\n".join(line for line in data.splitlines() if not
                             (b"JOB=PS-261003-0417" in line and b"ATTEMPT=2 STATE=ACK" in line))
        for i in range(len(data) - 7):
            seen.setdefault(data[i:i+8], (name, "raw", i))
            raw_count += 1
        for m in re.finditer(rb"[A-Fa-f0-9]{16,}", data):
            token = m.group()
            for i in range(len(token) - 15):
                word = bytes.fromhex(token[i:i+16].decode("ascii"))
                seen.setdefault(word, (name, "hex", m.start() + i))
                hex_count += 1
    return seen, raw_count, hex_count

def sieve(words: set[bytes], target: bytes) -> dict[str, set[tuple[bytes, bytes]]]:
    assert len(target) == 8
    result = {key: set() for key in ("xor", "sum_be", "sum_le", "sub_be", "sub_le")}
    for a in words:
        partner = bytes(x ^ y for x, y in zip(target, a))
        if partner in words:
            result["xor"].add(tuple(sorted((a, partner))))
        for endian in ("big", "little"):
            suffix = "be" if endian == "big" else "le"
            value = int.from_bytes(a, endian)
            desired = int.from_bytes(target, endian)
            partner_sum = ((desired - value) & LIMIT).to_bytes(8, endian)
            if partner_sum in words:
                result["sum_" + suffix].add(tuple(sorted((a, partner_sum))))
            partner_sub = ((value - desired) & LIMIT).to_bytes(8, endian)
            if partner_sub in words:
                result["sub_" + suffix].add((a, partner_sub))
    return result

def positive_controls() -> None:
    a = bytes.fromhex("0102030405060708")
    b = bytes.fromhex("1020304050607080")
    pool = {a, b}
    pairs = {
        "xor": bytes(x ^ y for x, y in zip(a, b)),
        "sum_be": ((int.from_bytes(a, "big") + int.from_bytes(b, "big")) & LIMIT).to_bytes(8, "big"),
        "sum_le": ((int.from_bytes(a, "little") + int.from_bytes(b, "little")) & LIMIT).to_bytes(8, "little"),
        "sub_be": ((int.from_bytes(a, "big") - int.from_bytes(b, "big")) & LIMIT).to_bytes(8, "big"),
        "sub_le": ((int.from_bytes(a, "little") - int.from_bytes(b, "little")) & LIMIT).to_bytes(8, "little"),
    }
    for operation, target in pairs.items():
        actual = sieve(pool, target)
        expected = (a, b) if operation.startswith("sub") else tuple(sorted((a, b)))
        assert expected in actual[operation], (operation, actual)

def main() -> None:
    positive_controls()
    observed, n_raw, n_hex = carriers()
    result = sieve(set(observed), TARGET)
    print(f"source_unique_8byte_values={len(observed)} raw_windows={n_raw} hex_windows={n_hex}")
    for operation, values in result.items():
        print(f"{operation} complete_8byte_donor_pairs={len(values)}")
        assert not values
    print("PASS: five planted source-pair positives; all five original-source NO_MATCH")

if __name__ == "__main__":
    main()
