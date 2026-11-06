"""Read-only original H17 BX25 PDF decoded-content K04 carrier sieve.

Run with python k04_bx25_decrypted_pdf_carrier_sft.py /path/to/h17-archive-dump.zip.
Requires PyMuPDF>=1.26; without an argument uses the repository resources tree.
"""
from __future__ import annotations
import argparse
import hashlib
from pathlib import Path
import re
import zipfile
import fitz

ZIP_SHA = "e778552c555fac652e24fd09e1c4f31bd066b4686e624b91f6e94e1d64342bf7"
PDF_SHA = "b6a6156f596575b988126c6d3e5cbb88d5794cc927a5564c37b6ddb8cecc3425"
PDF_PATH = "evidence/h17-supplemental-office-files/BX25-08.pdf"
TARGET = "930a52a1bab97ca2966332137c99e99298ea6182fb32ab63a3421dfb4fd8c9e0"
MASK = bytes.fromhex("8556C8CB6140A7F9A5123AC7571BEE1C")
COPIED = bytes.fromhex("A9A9DC5731A5E2AE879C47215C2559D5")

def carriers(payload: bytes) -> set[bytes]:
    result = {payload[i:i + 16] for i in range(len(payload) - 15)}
    for run in re.finditer(rb"[0-9a-fA-F]{32,}", payload):
        digits = run.group()
        for i in range(len(digits) - 31):
            result.add(bytes.fromhex(digits[i:i + 32].decode("ascii")))
    return result

def source_files(source: Path) -> dict[str, bytes]:
    if source.is_file():
        assert hashlib.sha256(source.read_bytes()).hexdigest() == ZIP_SHA
        with zipfile.ZipFile(source) as archive:
            return {name: archive.read(name) for name in archive.namelist() if not name.endswith("/")}
    return {p.relative_to(source).as_posix(): p.read_bytes()
            for p in source.rglob("*") if p.is_file() and p.name != ".gitkeep"}

def combine(a: bytes, b: bytes) -> bytes:
    return bytes(x ^ y for x, y in zip(a, b))

def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", nargs="?", type=Path,
                        default=Path(__file__).resolve().parents[2] / "resources")
    args = parser.parse_args()
    original = source_files(args.source)
    assert len(original) == 46, f"Original file count drifted: {len(original)}"
    pdf = original[PDF_PATH]
    assert hashlib.sha256(pdf).hexdigest() == PDF_SHA
    doc = fitz.open(stream=pdf, filetype="pdf")
    assert doc.needs_pass
    assert doc.authenticate("8131") > 0
    assert len(doc) == 1
    # Decrypted PDF streams were unavailable to scans of original ZIP member bytes.
    derived = [doc.tobytes(garbage=4, deflate=False, encryption=fitz.PDF_ENCRYPT_NONE),
               doc[0].get_text().encode("utf-8")]
    derived.extend(stream for x in range(1, doc.xref_length())
                   if (stream := doc.xref_stream(x)) is not None)
    assert len(derived) == 12
    original_carriers = set().union(*(carriers(data) for data in original.values()))
    decoded_carriers = set().union(*(carriers(data) for data in derived))
    assert len(original_carriers) == 67470
    assert len(decoded_carriers) == 6585
    assert len(decoded_carriers & original_carriers) == 1175
    novel = decoded_carriers - original_carriers
    assert len(novel) == 5410
    hit = {role: [] for role in ("paper", "alternate_mask", "component")}
    for value in decoded_carriers:
        proposals = (combine(value, MASK), combine(COPIED, value), value)
        for role, component in zip(hit, proposals):
            if hashlib.sha256(component).hexdigest() == TARGET:
                hit[role].append((value.hex(), component.hex()))
    planted = min(novel)
    planted_sha = hashlib.sha256(combine(planted, MASK)).digest()
    assert sum(hashlib.sha256(combine(x, MASK)).digest() == planted_sha
               for x in decoded_carriers) == 1
    print("BX25_DECRYPTED source_files=46 PDF_SHA_PASS streams=12"
          f" source_carriers={len(original_carriers)} decoded_carriers={len(decoded_carriers)}"
          f" overlap={len(original_carriers & decoded_carriers)} novel={len(novel)}"
          f" genuine_hits={sum(map(len, hit.values()))} planted_positive=1")
    for role, found in hit.items():
        print("ROLE", role, "original_matches", len(found), found)
    assert all(not values for values in hit.values())

if __name__ == "__main__":
    main()
