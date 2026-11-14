#!/usr/bin/env python3
"""Read-only exact K08 phrase search for the original AX-7782 object.

This complements work/h17_ax7782_object_intake.py (transfer/object validation)
and work/h17_k04_binary_window_intake.py (K04 raw/encoded coupon scan). It
searches only text actually present in the supplied AX-7782 object or decoded
members. Every candidate is normalized by the original REC8/1 rule, HMACed
with the original desk nonce, truncated to 16 bytes, and checked against the
unchanged K08 SHA-256 commitment. It does not invent or paraphrase wording.

ZIP/TAR/GZIP, PDF text/content/annotations/attachments, image metadata, and
optional OCR are read in memory. No source is modified or extracted to disk.
Encrypted PDFs are not password-guessed.
"""
from __future__ import annotations

import argparse
import base64
import email.policy
from email.parser import BytesParser
import binascii
import gzip
import hashlib
import hmac
import html
import io
import json
import quopri
import re
import stat
import tarfile
import urllib.parse
import zipfile
from html.parser import HTMLParser
from pathlib import Path, PurePosixPath
from typing import Iterator

import h17_ax7782_object_intake as intake

HEX_RE = re.compile(r"(?<![A-Fa-f0-9])[A-Fa-f0-9]{16,4096}(?![A-Fa-f0-9])")
B64_RE = re.compile(r"(?<![A-Za-z0-9+/])[A-Za-z0-9+/]{24,4096}={0,2}(?![A-Za-z0-9+/])")


class VisibleText(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.parts: list[str] = []

    def handle_data(self, data: str) -> None:
        if data.strip():
            self.parts.append(data)

    def text(self) -> str:
        return "\n".join(self.parts)


def normalize(text: str) -> str:
    text = re.sub(r"[^a-z0-9\s]", " ", text.lower())
    return " ".join(text.split())


def k08_component(nonce: bytes, normalized_phrase: str) -> bytes:
    return hmac.new(nonce, normalized_phrase.encode("utf-8"), hashlib.sha256).digest()[:16]


def load_k08_rules(resources: Path):
    route = json.loads((resources / "evidence" / "recovery-routing.json").read_text(encoding="utf-8"))
    acceptance = json.loads((resources / "acceptance.json").read_text(encoding="utf-8"))
    nonce = bytes.fromhex(route["K08"]["desk_nonce"])
    target = bytes.fromhex(acceptance["slot_sha256"]["K08"])
    if len(nonce) != 16 or len(target) != 32:
        raise ValueError("invalid original K08 nonce/commitment width")
    control = k08_component(nonce, normalize("a good watch leaves the room ready for the next pair of hands"))
    if control.hex().upper() != "BF889359B0303F2B2B2FD96AE841210B":
        raise ValueError("original K08 normalization/HMAC known-answer check failed")
    return nonce, target


def decode_text_variants(data: bytes, name: str) -> list[tuple[str, str]]:
    variants: list[tuple[str, str]] = []
    seen: set[str] = set()

    def add(label: str, text: str) -> None:
        if text and text not in seen:
            ratio = sum(ch.isprintable() or ch.isspace() for ch in text) / max(1, len(text))
            if ratio >= 0.90 and len(text.strip()) >= 4:
                seen.add(text)
                variants.append((label, text))

    for encoding in ("utf-8-sig", "utf-16le", "utf-16be"):
        if encoding.startswith("utf-16") and not (
            data.startswith((b"\xff\xfe", b"\xfe\xff"))
            or data[:8192].count(b"\x00") > max(8, len(data[:8192]) // 10)
        ):
            continue
        try:
            text = data.decode(encoding)
        except (UnicodeDecodeError, UnicodeError):
            continue
        add(encoding, text)
        if encoding == "utf-8-sig":
            add("html-unescape", html.unescape(text))
            add("url-unquote", urllib.parse.unquote(text))
            try:
        add("quoted-printable", quopri.decodestring(text.encode("utf-8")).decode("utf-8", "replace"))
    except (ValueError, UnicodeEncodeError):
        pass
            if name.lower().endswith((".html", ".htm", ".xml")) or "<html" in text[:1000].lower():
                parser = VisibleText()
                try:
                    parser.feed(text)
                    add("html-visible-text", parser.text())
                except Exception:
                    pass
            if name.lower().endswith(".json"):
                try:
                    obj = json.loads(text)
                    strings = []
                    def walk(value):
                        if isinstance(value, str):
                            strings.append(value)
                        elif isinstance(value, dict):
                            for key, item in value.items():
                                strings.append(str(key))
                                walk(item)
                        elif isinstance(value, list):
                            for item in value:
                                walk(item)
                    walk(obj)
                    add("json-string-values", "\n".join(strings))
                except (json.JSONDecodeError, TypeError):
                    pass

    # Recover printable runs embedded in binary streams (for example, raw
    # spool/compound members with text interleaved with control bytes).
    candidates: list[tuple[str, str]] = []
    try:
        candidates.append(("utf8-whole-stream", data.decode("utf-8")))
    except UnicodeDecodeError:
        pass
    run_count = 0
    for match in re.finditer(rb"[\\x09\\x0a\\x0d\\x20-\\x7e]{4,}", data):
        candidates.append((f"embedded-ascii@{match.start()}", match.group().decode("ascii", "replace")))
        run_count += 1
        if run_count >= 10000:
            break
    if run_count < 10000:
        for pattern, encoding in (
            (rb"(?:[\\x09\\x0a\\x0d\\x20-\\x7e]\\x00){4,}", "utf-16le"),
            (rb"(?:\\x00[\\x09\\x0a\\x0d\\x20-\\x7e]){4,}", "utf-16be"),
        ):
            for match in re.finditer(pattern, data):
                candidates.append((f"embedded-{encoding}@{match.start()}", match.group().decode(encoding, "replace")))
                run_count += 1
                if run_count >= 10000:
                    break
            if run_count >= 10000:
                break

    # Decode only conventional Base64/hex carriers whose decoded bytes are
    # themselves printable text; this is not a general cipher search.
    for source_label, raw_text in candidates:
        add(source_label, raw_text)
        for token in HEX_RE.findall(raw_text):
            try:
                decoded = bytes.fromhex(token)
                text = decoded.decode("utf-8")
                add(f"hex-decoded-text-{source_label}", text)
            except (ValueError, UnicodeDecodeError):
                pass
        for token in B64_RE.findall(raw_text):
            try:
                padded = token if len(token) % 4 == 0 else token + ("=" * (4 - len(token) % 4))
                decoded = base64.b64decode(padded, validate=True)
                text = decoded.decode("utf-8")
                add(f"base64-decoded-text-{source_label}", text)
            except (binascii.Error, ValueError, UnicodeDecodeError):
                pass
    return variants


def iter_text_streams(name: str, data: bytes, depth: int, budget: list[int],
                      errors: list[dict], ocr: bool = False) -> Iterator[tuple[str, bytes]]:
    """Yield text-bearing leaf streams and decoded document text in memory."""
    if budget[0] + len(data) > intake.MAX_TOTAL or len(data) > intake.MAX_MEMBER:
        return
    budget[0] += len(data)
    if depth > intake.MAX_DEPTH:
        yield name, data
        return
    kind = intake.magic(data)
    if kind == "zip":
        content_yielded = False
        unreadable_member = False
        try:
            with zipfile.ZipFile(io.BytesIO(data)) as archive:
                if archive.comment:
                    yield f"{name}!/<zip-comment>", archive.comment
                for item in archive.infolist():
                    path = PurePosixPath(item.filename)
                    if item.filename:
                        yield f"{name}!/<member-name>", item.filename.encode("utf-8", "replace")
                    if item.comment:
                        yield f"{name}!/{item.filename}<comment>", item.comment
                    mode = (item.external_attr >> 16) & 0xFFFF
                    if (item.is_dir() or item.file_size > intake.MAX_MEMBER
                            or budget[0] + item.file_size > intake.MAX_TOTAL
                            or path.is_absolute() or ".." in path.parts or stat.S_ISLNK(mode)):
                        continue
                    try:
                        child = archive.read(item)
                    except (RuntimeError, OSError, zipfile.BadZipFile) as exc:
                        unreadable_member = True
                        errors.append({"source": f"{name}!/{item.filename}", "error": str(exc)})
                        continue
                    content_yielded = True
                    yield from iter_text_streams(f"{name}!/{item.filename}", child, depth + 1, budget, errors, ocr)
        except (zipfile.BadZipFile, OSError, RuntimeError) as exc:
            errors.append({"source": name, "error": str(exc)})
            unreadable_member = True
        if not content_yielded or unreadable_member:
            yield name, data
    elif kind == "tar":
        yielded = False
        try:
            with tarfile.open(fileobj=io.BytesIO(data), mode="r:*") as archive:
                for item in archive.getmembers():
                    path = PurePosixPath(item.name)
                    if (not item.isfile() or item.size > intake.MAX_MEMBER
                            or budget[0] + item.size > intake.MAX_TOTAL
                            or path.is_absolute() or ".." in path.parts):
                        continue
                    stream = archive.extractfile(item)
                    if stream is not None:
                        yielded = True
                        if item.name:
                            yield f"{name}!/<member-name>", item.name.encode("utf-8", "replace")
                        if item.pax_headers:
                            yield f"{name}!/{item.name}<pax-headers>", json.dumps(item.pax_headers).encode("utf-8", "replace")
                        yield from iter_text_streams(f"{name}!/{item.name}", stream.read(intake.MAX_MEMBER + 1), depth + 1, budget, errors, ocr)
        except (tarfile.TarError, OSError, EOFError) as exc:
            errors.append({"source": name, "error": str(exc)})
        if not yielded:
            yield name, data
    elif kind == "gzip":
        # The gzip header can carry an original filename/comment. The first
        # 512 bytes are bounded and are not treated as a decoded payload.
        yield f"{name}!/<gzip-header>", data[:512]
        try:
            with gzip.GzipFile(fileobj=io.BytesIO(data)) as stream:
                child = stream.read(intake.MAX_MEMBER + 1)
            if len(child) <= intake.MAX_MEMBER:
                yield from iter_text_streams(f"{name}!/<gzip-payload>", child, depth + 1, budget, errors, ocr)
            else:
                errors.append({"source": name, "error": "gzip member exceeds size cap"})
        except (OSError, EOFError) as exc:
            errors.append({"source": name, "error": str(exc)})
            yield name, data
    elif name.lower().endswith(".eml"):
        yielded = False
        try:
            message = BytesParser(policy=email.policy.default).parsebytes(data)
            headers = "\n".join(f"{key}: {value}" for key, value in message.items())
            if headers:
                yielded = True
                yield f"{name}!/<headers>", headers.encode("utf-8", "replace")
            for index, part in enumerate(message.walk()):
                if part.is_multipart():
                    continue
                payload = part.get_payload(decode=True)
                if not payload:
                    continue
                filename = part.get_filename() or f"part-{index}"
                content_type = part.get_content_type()
                if content_type.startswith("text/"):
                    charset = part.get_content_charset() or "utf-8"
                    try:
                        body = payload.decode(charset, "replace")
                    except LookupError:
                        body = payload.decode("utf-8", "replace")
                    yielded = True
                    yield f"{name}!/{filename}", body.encode("utf-8", "replace")
                else:
                    yielded = True
                    yield from iter_text_streams(f"{name}!/{filename}", payload, depth + 1, budget, errors, ocr)
        except Exception as exc:
            errors.append({"source": name, "error": f"MIME extraction failed: {exc}"})
        if not yielded:
            yield name, data
    elif kind == "ole-compound":
        yielded = False
        try:
            import olefile
            with olefile.OleFileIO(io.BytesIO(data)) as compound:
                for stream_path in compound.listdir(streams=True, storages=False):
                    stream_name = "/".join(stream_path)
                    payload = compound.openstream(stream_path).read()
                    yielded = True
                    yield from iter_text_streams(f"{name}!/{stream_name}", payload, depth + 1, budget, errors, ocr)
        except ImportError:
            errors.append({"source": name, "error": "olefile unavailable; compound document internals not decoded"})
        except Exception as exc:
            errors.append({"source": name, "error": f"OLE extraction failed: {exc}"})
        if not yielded:
            yield name, data
    elif kind == "pdf":
        content_yielded = False
        try:
            from pypdf import PdfReader
            reader = PdfReader(io.BytesIO(data), strict=False)
            metadata = "\n".join(f"{key}: {value}" for key, value in (reader.metadata or {}).items())
            if metadata:
                yield f"{name}!/<metadata>", metadata.encode("utf-8", "replace")
            for index, page in enumerate(reader.pages):
                page_text = page.extract_text() or ""
                if page_text:
                    content_yielded = True
                    yield f"{name}!/<page-{index + 1}-text>", page_text.encode("utf-8")
                annotations = []
                try:
                    for annotation_ref in page.get("/Annots", []):
                        annotation = annotation_ref.get_object()
                        for field in ("/Contents", "/T", "/Subj", "/NM", "/URI"):
                            value = annotation.get(field)
                            if value is not None:
                                annotations.append(f"{field}: {value}")
                except Exception:
                    pass
                if annotations:
                    content_yielded = True
                    yield f"{name}!/<page-{index + 1}-annotations>", "\n".join(annotations).encode("utf-8", "replace")
                try:
                    contents = page.get_contents()
                    if contents is not None:
                        stream_data = contents.get_data()
                        if stream_data:
                            content_yielded = True
                            yield f"{name}!/<page-{index + 1}-content-stream>", stream_data
                except Exception:
                    pass
                try:
                    for image_index, image in enumerate(page.images):
                        if image.data:
                            content_yielded = True
                            yield from iter_text_streams(f"{name}!/<page-{index + 1}-image-{image_index}>", image.data, depth + 1, budget, errors, ocr)
                except Exception:
                    pass
                if ocr and index < 20:
                    try:
                        import fitz
                        import pytesseract
                        from PIL import Image
                        document = fitz.open(stream=data, filetype="pdf")
                        pix = document[index].get_pixmap(matrix=fitz.Matrix(2, 2), alpha=False)
                        image = Image.open(io.BytesIO(pix.tobytes("png")))
                        ocr_text = pytesseract.image_to_string(image)
                        if ocr_text.strip():
                            content_yielded = True
                            yield f"{name}!/<page-{index + 1}-ocr>", ocr_text.encode("utf-8")
                    except Exception as exc:
                        errors.append({"source": f"{name}!/<page-{index + 1}-ocr>", "error": str(exc)})
            for filename, payloads in getattr(reader, "attachments", {}).items():
                if not isinstance(payloads, (list, tuple)):
                    payloads = [payloads]
                for index, payload in enumerate(payloads):
                    if isinstance(payload, bytes):
                        content_yielded = True
                        yield from iter_text_streams(f"{name}!/{filename}[{index}]", payload, depth + 1, budget, errors, ocr)
        except Exception as exc:
            errors.append({"source": name, "error": f"PDF extraction unavailable (no password guessing): {exc}"})
        if not content_yielded:
            yield name, data
    elif kind in {"jpeg", "png", "tiff"}:
        yield name, data
        try:
            from PIL import Image, ExifTags
            with Image.open(io.BytesIO(data)) as image:
                metadata = []
                for tag, value in image.getexif().items():
                    label = ExifTags.TAGS.get(tag, str(tag))
                    if isinstance(value, bytes):
                        value = value.decode("utf-8", "replace")
                    metadata.append(f"{label}: {value}")
                metadata.extend(f"{key}: {value}" for key, value in image.info.items())
                if metadata:
                    yield f"{name}!/<image-metadata>", "\n".join(metadata).encode("utf-8", "replace")
                if ocr:
                    import pytesseract
                    ocr_text = pytesseract.image_to_string(image)
                    if ocr_text.strip():
                        yield f"{name}!/<ocr-text>", ocr_text.encode("utf-8")
                else:
                    errors.append({"source": name, "error": "image present; OCR disabled"})
        except Exception as exc:
            errors.append({"source": name, "error": f"image metadata/OCR unavailable: {exc}"})
        # Image bytes themselves are not useful phrase text unless metadata/OCR is present.
    else:
        yield name, data


def scan_phrase_spans(text: str, nonce: bytes, target: bytes, source: str,
                      max_words: int, hits: list[dict]) -> int:
    words = normalize(text).split()
    tested = 0
    for start in range(len(words)):
        phrase_words: list[str] = []
        for end in range(start, min(len(words), start + max_words)):
            phrase_words.append(words[end])
            phrase = " ".join(phrase_words)
            tested += 1
            component = k08_component(nonce, phrase)
            if hashlib.sha256(component).digest() == target:
                hits.append({"source": source, "word_start": start,
                             "word_end_exclusive": end + 1,
                             "word_count": len(phrase_words),
                             "normalized_phrase": phrase,
                             "component_hex": component.hex().upper()})
    return tested


def inspect_object(path: Path, resources: Path, transfer_id: str = "AX-7782",
                   ocr: bool = False, max_phrase_words: int = 32) -> dict:
    selected, transfer_meta = intake.select_chain(resources, transfer_id)
    if not transfer_meta.get("handoff_email_confirms_retained_object"):
        raise ValueError("MAIL-13 does not confirm the retained AX-7782 object")
    if not path.is_file() or path.is_symlink():
        raise ValueError("object must be a regular, non-symlink file")
    size = path.stat().st_size
    if size != intake.EXPECTED_SIZE:
        raise ValueError(f"object is {size} bytes; expected exactly {intake.EXPECTED_SIZE}")
    data = path.read_bytes()
    acceptance = json.loads((resources / "acceptance.json").read_text(encoding="utf-8"))
    chain = b"".join(bytes.fromhex(row["checkpoint"]) for row in selected)
    k07_component = hashlib.sha256(chain).digest()[:16]
    k07_pass = hashlib.sha256(k07_component).hexdigest() == acceptance["slot_sha256"]["K07"]
    if not k07_pass:
        raise ValueError("selected AX-7782 chain does not pass original K07 commitment")
    if [int(row["attempt"]) for row in selected] != [2] * 8:
        raise ValueError("selected AX-7782 transfer attempts differ from the retained second-attempt chain")
    nonce, target = load_k08_rules(resources)
    hits: list[dict] = []
    errors: list[dict] = []
    budget = [0]
    streams = 0
    spans_tested = 0
    for source, stream_data in iter_text_streams(path.name, data, 0, budget, errors, ocr):
        streams += 1
        seen_normalized: set[str] = set()
        for label, text in decode_text_variants(stream_data, source):
            normalized = normalize(text)
            if not normalized or normalized in seen_normalized:
                continue
            seen_normalized.add(normalized)
            spans_tested += scan_phrase_spans(text, nonce, target,
                                              f"{source} [{label}]", max_phrase_words, hits)
    return {
        "object": {"path": str(path), "size": size,
                   "sha256": hashlib.sha256(data).hexdigest(),
                   "magic": intake.magic(data)},
        "transfer": {"id": transfer_id, "object": "IR-261003-H17",
                     "selected_attempts": [int(row["attempt"]) for row in selected],
                     "checkpoint_chain_hex": chain.hex().upper(),
                     "K07_component_hex": k07_component.hex().upper(),
                     "K07_commitment_pass": k07_pass,
                     "handoff_email_confirms_retained_object": transfer_meta["handoff_email_confirms_retained_object"]},
        "K08_search": {"text_streams_scanned": streams,
                       "normalized_contiguous_spans_tested": spans_tested,
                       "max_phrase_words": max_phrase_words,
                       "original_commitment_hits": hits,
                       "ocr_enabled": ocr},
        "errors_or_unavailable_decoders": errors,
        "limits": [
            "Only exact contiguous normalized phrase spans are tested; no paraphrase or word-edit search is performed.",
            "Encrypted PDFs are not password-guessed; their raw bytes are retained only as an unparsed stream.",
            "OCR is optional and may not reliably transcribe handwritten marginalia; visually inspect original images when needed.",
            "7z, RAR and SQLite internals are not decoded by this path; use authorized format-specific extraction if present. OLE streams are decoded only when olefile is installed.",
            "The K04 payload is handled by work/h17_k04_binary_window_intake.py, not by this phrase scanner.",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--object", required=True, type=Path, help="authorized local AX-7782 8 MiB object")
    parser.add_argument("--resources", type=Path, default=Path("resources"))
    parser.add_argument("--transfer", default="AX-7782")
    parser.add_argument("--ocr", action="store_true", help="optional OCR for images/scanned PDFs")
    parser.add_argument("--max-phrase-words", type=int, default=32)
    parser.add_argument("--json-out", type=Path)
    args = parser.parse_args()
    if not 1 <= args.max_phrase_words <= 256:
        parser.error("--max-phrase-words must be between 1 and 256")
    if not args.object.is_file() or args.object.is_symlink():
        parser.error("--object must be a regular, non-symlink file")
    if args.json_out:
        output_path = args.json_out.resolve()
        resources_path = args.resources.resolve()
        if output_path == args.object.resolve() or output_path == resources_path or resources_path in output_path.parents:
            parser.error("--json-out must be outside the source object and resources tree")
    try:
        result = inspect_object(args.object, args.resources, args.transfer,
                                args.ocr, args.max_phrase_words)
    except Exception as exc:
        parser.error(str(exc))
    output = json.dumps(result, indent=2, sort_keys=True)
    if args.json_out:
        args.json_out.write_text(output + "\n", encoding="utf-8")
    print(output)


if __name__ == "__main__":
    main()
