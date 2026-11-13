#!/usr/bin/env python3
"""Read-only intake for the AX-7782 retained H-17 archive object.

Expected input: eight consecutive 1 MiB chunks. The tool verifies the selected
transfer chain and K07 commitment, reports common CRC-16 interpretations
without assuming one, and safely inventories nested ZIP/TAR/PDF/image content.
It never modifies or extracts the source object to disk.
"""
from __future__ import annotations

import argparse
import hashlib
import io
import json
import re
import stat
import tarfile
import zipfile
import zlib
from pathlib import Path, PurePosixPath

ROOT = Path(__file__).resolve().parents[1]
CHUNK_SIZE = 1_048_576
CHUNK_COUNT = 8
EXPECTED_SIZE = CHUNK_SIZE * CHUNK_COUNT
MAX_MEMBER = 32 * 1024 * 1024
MAX_TOTAL = 128 * 1024 * 1024
MAX_DEPTH = 2
TERMS = (
    b"IR-261003-H17", b"IR-261003-H17.txt", b"AX-7782",
    b"PS-261003-0417", b"ESC-N", b"H17-POL-17/A3",
    b"Emily", b"N23", b"final envelope", b"envelope",
    b"caption", b"coupon", b"handoff", b"margin", b"wording",
    b"words I finally put on it", b"final wording",
    b"mug-stock", b"mug-stock.xls", b"transfer-index",
    b"transfer-index.htm", b"scanrelease.txt",
    b"desktop-move-2026.html", b"SEP26",
)
CRC16S = {
    "ARC": dict(poly=0x8005, init=0x0000, refin=True, xorout=0x0000),
    "MODBUS": dict(poly=0x8005, init=0xFFFF, refin=True, xorout=0x0000),
    "CCITT_FALSE": dict(poly=0x1021, init=0xFFFF, refin=False, xorout=0x0000),
    "CCITT_XMODEM": dict(poly=0x1021, init=0x0000, refin=False, xorout=0x0000),
    "CCITT_AUG": dict(poly=0x1021, init=0x1D0F, refin=False, xorout=0x0000),
    "X25": dict(poly=0x1021, init=0xFFFF, refin=True, xorout=0xFFFF),
    "KERMIT": dict(poly=0x1021, init=0x0000, refin=True, xorout=0x0000),
    "DNP": dict(poly=0x3D65, init=0x0000, refin=True, xorout=0xFFFF),
}


def crc16(data: bytes, *, poly: int, init: int, refin: bool, xorout: int) -> int:
    crc = init & 0xFFFF
    if refin:
        reflected = sum(((poly >> bit) & 1) << (15 - bit) for bit in range(16))
        for byte in data:
            crc ^= byte
            for _ in range(8):
                crc = (crc >> 1) ^ reflected if crc & 1 else crc >> 1
    else:
        for byte in data:
            crc ^= byte << 8
            for _ in range(8):
                crc = ((crc << 1) ^ poly) & 0xFFFF if crc & 0x8000 else (crc << 1) & 0xFFFF
    return (crc ^ xorout) & 0xFFFF


def select_chain(resources: Path, transfer_id: str):
    evidence = resources / "evidence"
    audit = evidence / "transfers" / "transfer-audit.jsonl"
    if not audit.is_file():
        raise FileNotFoundError(f"transfer audit not found: {audit}")
    rows = [json.loads(x) for x in audit.read_text(encoding="utf-8").splitlines() if x.strip()]
    commits = [r for r in rows if r.get("kind") == "COMMIT"
               and r.get("transfer") == transfer_id and r.get("dry_run") is False]
    if not commits:
        raise ValueError(f"no non-dry-run COMMIT for {transfer_id}")
    by_seq = {}
    for row in rows:
        if row.get("kind") == "CHUNK" and row.get("transfer") == transfer_id:
            by_seq.setdefault(int(row["seq"]), []).append(row)
    if set(by_seq) != set(range(CHUNK_COUNT)):
        raise ValueError(f"{transfer_id} chunk sequence is {sorted(by_seq)}, expected 0..7")
    selected = [max(by_seq[i], key=lambda r: int(r["attempt"])) for i in range(CHUNK_COUNT)]
    for seq, row in enumerate(selected):
        if int(row.get("bytes", -1)) != CHUNK_SIZE:
            raise ValueError(f"chunk {seq} is not {CHUNK_SIZE} bytes")
        if not re.fullmatch(r"[0-9A-Fa-f]{4}", str(row.get("checkpoint", ""))):
            raise ValueError(f"chunk {seq} has malformed checkpoint")
    objects = {r.get("object") for r in selected}
    if len(objects) != 1 or next(iter(objects)) != "IR-261003-H17":
        raise ValueError(f"unexpected or inconsistent object IDs: {objects}")
    queue = evidence / "transfers" / "queue-note.txt"
    mail13 = evidence / "mail" / "13.eml"
    queue_text = queue.read_text(encoding="utf-8", errors="replace") if queue.is_file() else ""
    mail_text = mail13.read_text(encoding="utf-8", errors="replace") if mail13.is_file() else ""
    mail_flat = " ".join(mail_text.casefold().split())
    meta = {
        "transfer": transfer_id,
        "object": "IR-261003-H17",
        "commit_records": len(commits),
        "selected_attempts": [int(r["attempt"]) for r in selected],
        "queue_note_excludes_drill_dryrun_and_stopped_transfers":
            all(x in queue_text for x in ("AX-7778", "AX-7781", "AX-7783")),
        "handoff_email_confirms_retained_object":
            all(x.casefold() in mail_flat for x in (transfer_id, "IR-261003-H17", "actual retained copy")),
        "handoff_email_locates_print":
            "handoff print" in mail_flat and "ordinary records folder" in mail_flat,
    }
    return selected, meta


def magic(data: bytes) -> str:
    if data.startswith((b"PK\x03\x04", b"PK\x05\x06", b"PK\x07\x08")):
        return "zip"
    if data.startswith(b"%PDF-"):
        return "pdf"
    if data.startswith(b"\x1f\x8b"):
        return "gzip"
    if data.startswith(b"7z\xbc\xaf\x27\x1c"):
        return "7z"
    if data.startswith(b"Rar!\x1a\x07"):
        return "rar"
    if data.startswith(b"SQLite format 3\x00"):
        return "sqlite"
    if data.startswith(b"\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1"):
        return "ole-compound"
    if data.startswith(b"\x89PNG\r\n\x1a\n"):
        return "png"
    if data.startswith(b"\xff\xd8\xff"):
        return "jpeg"
    if data.startswith((b"II*\x00", b"MM\x00*")):
        return "tiff"
    if len(data) >= 262 and data[257:262] == b"ustar":
        return "tar"
    return "text" if data and all(x in (9, 10, 13) or 32 <= x < 127 for x in data[:4096]) else "unknown"


def raw_hits(data: bytes):
    lower = data.lower()
    hits = []
    for term in TERMS:
        pos = lower.find(term.lower())
        if pos >= 0:
            hits.append({"term": term.decode("ascii"), "offset": pos, "encoding": "bytes"})
        wide = b"".join(bytes((x, 0)) for x in term)
        pos = lower.find(wide.lower())
        if pos >= 0:
            hits.append({"term": term.decode("ascii"), "offset": pos, "encoding": "utf-16le"})
    return hits


def scan_member(name: str, data: bytes, depth: int, budget: list[int]):
    kind = magic(data)
    name_lower = name.casefold()
    name_hits = [term.decode("ascii") for term in TERMS if term.decode("ascii").casefold() in name_lower]
    result = {"name": name, "size": len(data), "sha256": hashlib.sha256(data).hexdigest(),
              "magic": kind, "name_hits": name_hits, "raw_hits": raw_hits(data)}
    budget[0] += len(data)
    if budget[0] > MAX_TOTAL or depth >= MAX_DEPTH or len(data) > MAX_MEMBER:
        result["scan_limit"] = "depth, member-size, or total-byte cap"
        return result
    children = []
    if kind == "zip":
        try:
            with zipfile.ZipFile(io.BytesIO(data)) as archive:
                for item in archive.infolist():
                    path = PurePosixPath(item.filename)
                    mode = (item.external_attr >> 16) & 0xFFFF
                    if item.is_dir() or item.file_size > MAX_MEMBER or path.is_absolute() or ".." in path.parts or stat.S_ISLNK(mode):
                        continue
                    children.append(scan_member(f"{name}!/{item.filename}", archive.read(item), depth + 1, budget))
        except (zipfile.BadZipFile, OSError, RuntimeError) as exc:
            result["container_error"] = str(exc)
    elif kind == "gzip":
        try:
            import gzip
            with gzip.GzipFile(fileobj=io.BytesIO(data)) as stream:
                child = stream.read(MAX_MEMBER + 1)
            if len(child) <= MAX_MEMBER:
                children.append(scan_member(f"{name}!/<gzip-payload>", child, depth + 1, budget))
            else:
                result["scan_limit"] = "gzip payload exceeds member-size cap"
        except (OSError, EOFError) as exc:
            result["container_error"] = str(exc)
    elif kind == "tar":
        try:
            with tarfile.open(fileobj=io.BytesIO(data), mode="r:*") as archive:
                for item in archive.getmembers():
                    path = PurePosixPath(item.name)
                    if not item.isfile() or item.size > MAX_MEMBER or path.is_absolute() or ".." in path.parts:
                        continue
                    stream = archive.extractfile(item)
                    if stream is not None:
                        children.append(scan_member(f"{name}!/{item.name}", stream.read(MAX_MEMBER + 1), depth + 1, budget))
        except (tarfile.TarError, OSError) as exc:
            result["container_error"] = str(exc)
    elif kind in {"jpeg", "png", "tiff"}:
        try:
            from PIL import Image, ExifTags
            with Image.open(io.BytesIO(data)) as image:
                exif = {}
                for tag, value in image.getexif().items():
                    label = ExifTags.TAGS.get(tag, str(tag))
                    if isinstance(value, bytes):
                        value = value.decode("utf-16le" if len(value) % 2 == 0 else "utf-8", "replace").rstrip("\x00")
                    exif[label] = str(value)[:4096]
                result["image"] = {"format": image.format, "width": image.width, "height": image.height,
                                   "exif": exif, "info": {str(k): str(v)[:4096] for k, v in image.info.items()}}
                meta = json.dumps(result["image"], ensure_ascii=False).casefold()
                result["image"]["metadata_hits"] = [t.decode("ascii") for t in TERMS if t.decode("ascii").casefold() in meta]
        except ImportError:
            result["image_note"] = "Pillow unavailable; raw string scan only"
        except Exception as exc:
            result["image_error"] = str(exc)
    elif kind == "pdf":
        try:
            from pypdf import PdfReader
            reader = PdfReader(io.BytesIO(data), strict=False)
            text = "\n".join(page.extract_text() or "" for page in reader.pages)
            result["pdf"] = {"pages": len(reader.pages),
                             "metadata": {str(k): str(v) for k, v in (reader.metadata or {}).items()},
                             "text_hits": [t.decode("ascii") for t in TERMS if t.decode("ascii").casefold() in text.casefold()],
                             "has_attachments": bool(getattr(reader, "attachments", {}))}
        except ImportError:
            result["pdf_note"] = "pypdf unavailable; raw string scan only"
        except Exception as exc:
            result["pdf_error"] = str(exc)
    if children:
        result["members"] = children
    return result


def inspect_object(path: Path, resources: Path, transfer_id: str, allow_size_mismatch: bool = False):
    selected, transfer_meta = select_chain(resources, transfer_id)
    size = path.stat().st_size
    if size != EXPECTED_SIZE and not allow_size_mismatch:
        raise ValueError(f"object is {size} bytes; expected exactly {EXPECTED_SIZE}")
    if size < EXPECTED_SIZE:
        raise ValueError("object is shorter than eight complete 1 MiB chunks")
    data = path.read_bytes()
    chain = b"".join(bytes.fromhex(r["checkpoint"]) for r in selected)
    component = hashlib.sha256(chain).digest()[:16]
    acceptance_paths = (resources / "acceptance.json", resources.parent / "acceptance.json")
    acceptance_path = next((p for p in acceptance_paths if p.is_file()), None)
    k07 = {"chain_hex": chain.hex().upper(), "component_hex": component.hex().upper(),
           "acceptance_file": str(acceptance_path) if acceptance_path else None}
    if acceptance_path:
        acceptance = json.loads(acceptance_path.read_text(encoding="utf-8"))
        expected = acceptance.get("slot_sha256", {}).get("K07")
        k07["expected_component_sha256"] = expected
        k07["matches_acceptance"] = bool(expected and hashlib.sha256(component).hexdigest().lower() == expected.lower())
    chunks, matches = [], {}
    for seq, row in enumerate(selected):
        block = data[seq * CHUNK_SIZE:(seq + 1) * CHUNK_SIZE]
        checkpoint = str(row["checkpoint"]).upper()
        raw = bytes.fromhex(checkpoint)
        big, little = int(checkpoint, 16), int.from_bytes(raw, "little")
        checks = {name: crc16(block, **params) for name, params in CRC16S.items()}
        matched = [name for name, value in checks.items() if value in (big, little)]
        for name in matched:
            matches.setdefault(name, []).append(seq)
        chunks.append({"seq": seq, "attempt": int(row["attempt"]), "offset": seq * CHUNK_SIZE,
                       "checkpoint": checkpoint, "crc16": {k: f"{v:04X}" for k, v in checks.items()},
                       "crc16_matches": matched, "crc32_ieee": f"{zlib.crc32(block) & 0xffffffff:08X}",
                       "adler32": f"{zlib.adler32(block) & 0xffffffff:08X}",
                       "md5": hashlib.md5(block).hexdigest(), "sha256": hashlib.sha256(block).hexdigest()})
    all8 = [name for name, seqs in matches.items() if seqs == list(range(CHUNK_COUNT))]
    return {"object": {"path": str(path), "size": size, "expected_size": EXPECTED_SIZE,
                       "sha256": hashlib.sha256(data).hexdigest(), "magic": magic(data)},
            "transfer_source": transfer_meta, "k07_chain_validation": k07,
            "checkpoint_interpretation": {"selected_checkpoints": [r["checkpoint"].upper() for r in selected],
                                          "common_crc16_algorithms_matching_all_8": all8,
                                          "note": "No checksum algorithm is assumed; an empty list only closes these common CRC-16 variants."},
            "chunks": chunks,
            "container_inventory": scan_member(path.name, data, 0, [0])}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--object", required=True, type=Path, help="local AX-7782 8 MiB object; read-only")
    parser.add_argument("--resources", type=Path, default=ROOT / "resources")
    parser.add_argument("--transfer", default="AX-7782")
    parser.add_argument("--allow-size-mismatch", action="store_true", help="diagnostic only; object must still contain eight full chunks")
    parser.add_argument("--json-out", type=Path)
    args = parser.parse_args()
    try:
        result = inspect_object(args.object, args.resources, args.transfer, args.allow_size_mismatch)
    except Exception as exc:
        parser.error(str(exc))
    output = json.dumps(result, indent=2, sort_keys=True)
    if args.json_out:
        args.json_out.write_text(output + "\n", encoding="utf-8")
    print(output)


if __name__ == "__main__":
    main()
