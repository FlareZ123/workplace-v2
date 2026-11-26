#!/usr/bin/env python3
"""Read-only exact K08 phrase search for the original AX-7782 object.

This complements work/h17_ax7782_object_intake.py (transfer/object validation)
and work/h17_k04_binary_window_intake.py (K04 raw/encoded coupon scan). It
searches only text actually present in the supplied AX-7782 object or decoded
members. Every candidate is normalized by the original REC8/1 rule, HMACed
with the original desk nonce, truncated to 16 bytes, and checked against the
unchanged K08 SHA-256 commitment. It does not invent or paraphrase wording.

ZIP/TAR/GZIP, PDF text/content/annotations/attachments, image metadata, and
optional OCR are read in memory. Legacy Excel .xls BIFF cells and legacy Word .doc content/comments are decoded with isolated temporary-copy LibreOffice fallbacks when xlrd is unavailable or a .doc is encountered; other OLE streams are scanned when olefile is installed. No source is modified; legacy Office fallbacks write only short-lived temporary copies outside the source tree.
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

from h17_redaction import redact_by_default, redact_sensitive
from typing import Iterator

import h17_ax7782_object_intake as intake
from h17_ooxml_text_intake import iter_ooxml_revision_units, iter_ooxml_text_units
from h17_photo_caption_metadata import iter_exif_caption_units, iter_iptc_caption_units, iter_xmp_caption_units

HEX_RE = re.compile(r"(?<![A-Fa-f0-9])[A-Fa-f0-9]{16,4096}(?![A-Fa-f0-9])")
EXPECTED_SYNTHETIC_HMAC16 = "D80E9E725D394C7F1B60CCDD801F7407"
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
    control = k08_component(bytes(range(16)), normalize("a good watch leaves the room ready for the next pair of hands"))
    if control.hex().upper() != EXPECTED_SYNTHETIC_HMAC16:
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
    for match in re.finditer(rb"[\x09\x0a\x0d\x20-\x7e]{4,}", data):
        candidates.append((f"embedded-ascii@{match.start()}", match.group().decode("ascii", "replace")))
        run_count += 1
        if run_count >= 10000:
            break
    if run_count < 10000:
        for pattern, encoding in (
            (rb"(?:[\x09\x0a\x0d\x20-\x7e]\x00){4,}", "utf-16le"),
            (rb"(?:\x00[\x09\x0a\x0d\x20-\x7e]){4,}", "utf-16be"),
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
    def add_decoded_bytes(kind: str, source_label: str, decoded: bytes) -> None:
        try:
            add(f"{kind}-decoded-text-{source_label}", decoded.decode("utf-8"))
        except UnicodeDecodeError:
            pass
        sample = decoded[:8192]
        if decoded.startswith((b"\xff\xfe", b"\xfe\xff")) or sample.count(b"\x00") >= max(2, len(sample) // 10):
            for encoding in ("utf-16le", "utf-16be"):
                try:
                    add(f"{kind}-decoded-{encoding}-{source_label}", decoded.decode(encoding))
                except UnicodeDecodeError:
                    pass

    for source_label, raw_text in candidates:
        add(source_label, raw_text)
        for token in HEX_RE.findall(raw_text):
            try:
                add_decoded_bytes("hex", source_label, bytes.fromhex(token))
            except ValueError:
                pass
        for token in B64_RE.findall(raw_text):
            try:
                padded = token if len(token) % 4 == 0 else token + ("=" * (4 - len(token) % 4))
                add_decoded_bytes("base64", source_label, base64.b64decode(padded, validate=True))
            except (binascii.Error, ValueError):
                pass
    return variants


def _looks_like_xps_package(data: bytes) -> bool:
    """Recognize an OPC XPS/OXPS package without treating every ZIP as XPS."""
    try:
        with zipfile.ZipFile(io.BytesIO(data)) as package:
            infos = package.infolist()
            if len(infos) > 20_000:
                return False
            names = {item.filename for item in infos}
            if "[Content_Types].xml" not in names:
                return False
            if any(name.casefold().endswith((".fpage", ".fdseq")) for name in names):
                return True
            with package.open("[Content_Types].xml") as stream:
                content_types = stream.read(256 * 1024).lower()
            return b"fixedpage" in content_types
    except (zipfile.BadZipFile, OSError, RuntimeError, EOFError, ValueError):
        return False


def _xps_has_glyph_indices(data: bytes) -> bool:
    """Check bounded FixedPage parts for Indices attributes before font decoding."""
    try:
        with zipfile.ZipFile(io.BytesIO(data)) as package:
            for item in package.infolist():
                if (item.is_dir() or not item.filename.casefold().endswith(".fpage")
                        or item.file_size > 4 * 1024 * 1024):
                    continue
                with package.open(item) as stream:
                    page = stream.read(4 * 1024 * 1024 + 1)
                if len(page) <= 4 * 1024 * 1024 and b"Indices" in page:
                    return True
    except (zipfile.BadZipFile, OSError, RuntimeError, EOFError, ValueError):
        return False
    return False


def iter_m10_teal_bit_text(name: str, image_data: bytes,
                           errors: list[dict]) -> Iterator[tuple[str, bytes]]:
    """Read the two source-literal TEAL BIT / LOW IF EVEN layouts from one M10 image.

    This is exploratory, exact-source-coordinate intake. A phrase commitment hit
    still needs independent original-workbook and Emily-version authentication.
    """
    try:
        from PIL import Image
        from h17_k08_teal_bit_image_scan import _bit_variants, _candidate_texts
        with Image.open(io.BytesIO(image_data)) as opened:
            if opened.width * opened.height > 16_000_000:
                errors.append({"source": name, "error": "M10 teal image exceeds 16M-pixel bound"})
                return
            for frame in range(getattr(opened, "n_frames", 1)):
                opened.seek(frame)
                for layout, bits in _bit_variants(opened.copy(), source_literal_only=True):
                    for run_index, run in enumerate(_candidate_texts(bits)):
                        if 8 <= len(run) <= 4096:
                            yield (
                                f"{name}!/<teal-bit:{layout}:frame={frame}:run={run_index}>",
                                run.encode("utf-8"),
                            )
    except Exception as exc:
        errors.append({
            "source": name,
            "error": f"M10 teal image decoding unavailable: {type(exc).__name__}: {exc}",
        })


def iter_msg_rtf_text(name: str, payload: bytes,
                      errors: list[dict]) -> Iterator[tuple[str, bytes]]:
    """Decode PidTagRtfCompressed 0x10090102 from an original Outlook MSG.

    The original message/RtfCompressed stream is read only. The declared
    uncompressed-size bound is checked before library decompression.
    """
    if (len(payload) < 16 or payload[8:12] not in (b"LZFu", b"MELA")):
        errors.append({"source": name, "error": "invalid Outlook compressed RTF header"})
        return
    expected_size = int.from_bytes(payload[4:8], "little")
    if expected_size > 8 * 1024 * 1024:
        errors.append({"source": name, "error": "Outlook RTF exceeds 8 MiB bound"})
        return
    try:
        from compressed_rtf import decompress
        from striprtf.striprtf import rtf_to_text
        rtf = decompress(payload)
        if isinstance(rtf, str):
            rtf = rtf.encode("latin-1", "replace")
        if len(rtf) != expected_size or len(rtf) > 8 * 1024 * 1024:
            raise ValueError("Outlook RTF decompressed-size mismatch")
        plain = rtf_to_text(rtf.decode("latin-1"), errors="ignore")
        if plain.strip():
            yield f"{name}!/<rtf-plain>", plain.encode("utf-8")
    except Exception as exc:
        errors.append({
            "source": name,
            "error": f"Outlook RTF decode failed: {type(exc).__name__}: {exc}",
        })


def iter_text_streams(name: str, data: bytes, depth: int, budget: list[int],
                      errors: list[dict], ocr: bool = False,
                      pdf_password: str | None = None,
                      style_metadata: list[dict] | None = None,
                      allow_pdf_source: bool = False) -> Iterator[tuple[str, bytes]]:
    """Yield text-bearing leaf streams and decoded document text in memory."""
    opaque_sha256 = hashlib.sha256(data).hexdigest()
    if opaque_sha256 == intake.OPAQUE_PDF_SHA256:
        budget[0] += len(data)
        errors.append({"source": name, "status": "skipped_opaque_pdf",
                       "size": len(data), "sha256": opaque_sha256})
        return
    if intake.is_opaque_pdf_name(name):
        budget[0] += len(data)
        errors.append({"source": name, "status": "skipped_opaque_pdf_by_name",
                       "size": len(data), "pinned_sha256": intake.OPAQUE_PDF_SHA256})
        return
    if intake.is_pdf_candidate(name, data) and not allow_pdf_source:
        budget[0] += len(data)
        errors.append({"source": name, "status": "skipped_pdf_pending_provenance",
                       "size": len(data)})
        return
    if style_metadata is None:
        style_metadata = []
    if budget[0] + len(data) > intake.MAX_TOTAL or len(data) > intake.MAX_MEMBER:
        return
    budget[0] += len(data)
    kind = "pdf" if intake.is_pdf_candidate(name, data) else intake.magic(data)
    is_container = kind in {"zip", "tar", "gzip", "ole-compound"} or name.casefold().endswith(".eml")
    if depth > intake.MAX_DEPTH:
        if is_container:
            errors.append({"source": name, "status": "container_depth_limit_raw_suppressed"})
        else:
            yield name, data
        return
    # Container bytes can include a quarantined nested PDF. Inspect only
    # their named members/structured text, never their raw compressed carrier.
    if not is_container:
        for label, text in iter_xmp_caption_units(name, data):
            yield f"{name}!/{label}", text.encode("utf-8", "replace")
        for label, text in iter_iptc_caption_units(name, data):
            yield f"{name}!/{label}", text.encode("utf-8", "replace")
        for label, text in iter_exif_caption_units(name, data):
            yield f"{name}!/{label}", text.encode("utf-8", "replace")
    if kind == "zip":
        for label, authored in iter_ooxml_text_units(data):
            yield f"{name}!/{label}", authored
        # Preserve the Word editor's revision semantics separately from the
        # visible final-view paragraphs: old/deleted text and attributed edits
        # are useful provenance, but are not automatically the accepted phrase.
        for label, authored in iter_ooxml_revision_units(data):
            yield f"{name}!/{label}", authored
        # XPS/OXPS is an OPC ZIP, but its visible strings are Glyphs attributes,
        # not XML text nodes. Run the bounded page readers before generic ZIP
        # recursion; the glyph-index reader fails closed on incomplete coverage.
        if _looks_like_xps_package(data):
            xps_stream_count = 0
            try:
                from h17_xps_text import extract_xps_text
                for label, payload in extract_xps_text(data):
                    if budget[0] + len(payload) > intake.MAX_TOTAL:
                        errors.append({"source": name, "error": "XPS UnicodeString output exceeds total scan budget"})
                        break
                    budget[0] += len(payload)
                    xps_stream_count += 1
                    yield f"{name}!/{label}", payload
            except Exception as exc:
                errors.append({"source": name, "error": f"xps-unicode-text:{type(exc).__name__}:{exc}"})
            if _xps_has_glyph_indices(data):
                try:
                    import h17_xps_glyph_indices as glyph_reader
                    if glyph_reader.TTFont is None:
                        errors.append({
                            "source": name,
                            "error": "xps-glyph-indices:fontTools-unavailable; glyph-index-only text remains undecoded",
                        })
                    else:
                        for label, payload in glyph_reader.extract_xps_glyph_streams(data):
                            if budget[0] + len(payload) > intake.MAX_TOTAL:
                                errors.append({"source": name, "error": "XPS glyph-index output exceeds total scan budget"})
                                break
                            budget[0] += len(payload)
                            xps_stream_count += 1
                            yield f"{name}!/{label}", payload
                except Exception as exc:
                    errors.append({"source": name, "error": f"xps-glyph-indices:{type(exc).__name__}:{exc}"})
            if xps_stream_count == 0 and not any(
                item.get("source") == name and str(item.get("error", "")).startswith("xps-")
                for item in errors
            ):
                errors.append({
                    "source": name,
                    "error": "XPS package contains no extractable UnicodeString or complete glyph-index text; bitmap/outline-only pages may remain",
                })
        content_yielded = False
        unreadable_member = False
        opaque_member_seen = False
        try:
            with zipfile.ZipFile(io.BytesIO(data)) as archive:
                if archive.comment:
                    yield f"{name}!/<zip-comment>", archive.comment
                for item in archive.infolist():
                    path = PurePosixPath(item.filename)
                    if intake.is_opaque_pdf_name(item.filename):
                        opaque_member_seen = True
                        content_yielded = True
                        errors.append({
                            "source": f"{name}!/{item.filename}",
                            "status": "skipped_opaque_pdf_by_name",
                            "size": item.file_size,
                            "pinned_sha256": intake.OPAQUE_PDF_SHA256,
                        })
                        continue
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
                    yield from iter_text_streams(f"{name}!/{item.filename}", child, depth + 1, budget, errors, ocr, pdf_password, style_metadata, allow_pdf_source)
        except (zipfile.BadZipFile, OSError, RuntimeError) as exc:
            errors.append({"source": name, "error": str(exc)})
            unreadable_member = True
        if (not content_yielded or unreadable_member) and not opaque_member_seen:
            yield name, data
    elif kind == "tar":
        yielded = False
        opaque_member_seen = False
        try:
            with tarfile.open(fileobj=io.BytesIO(data), mode="r:*") as archive:
                for item in archive.getmembers():
                    path = PurePosixPath(item.name)
                    if intake.is_opaque_pdf_name(item.name):
                        opaque_member_seen = True
                        yielded = True
                        errors.append({
                            "source": f"{name}!/{item.name}",
                            "status": "skipped_opaque_pdf_by_name",
                            "size": item.size,
                            "pinned_sha256": intake.OPAQUE_PDF_SHA256,
                        })
                        continue
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
                        yield from iter_text_streams(f"{name}!/{item.name}", stream.read(intake.MAX_MEMBER + 1), depth + 1, budget, errors, ocr, pdf_password, style_metadata, allow_pdf_source)
        except (tarfile.TarError, OSError, EOFError) as exc:
            errors.append({"source": name, "error": str(exc)})
        if not yielded and not opaque_member_seen:
            yield name, data
    elif kind == "gzip":
        # The gzip header can carry an original filename/comment. The first
        # 512 bytes are bounded and are not treated as a decoded payload.
        yield f"{name}!/<gzip-header>", data[:512]
        try:
            with gzip.GzipFile(fileobj=io.BytesIO(data)) as stream:
                child = stream.read(intake.MAX_MEMBER + 1)
            if len(child) <= intake.MAX_MEMBER:
                yield from iter_text_streams(f"{name}!/<gzip-payload>", child, depth + 1, budget, errors, ocr, pdf_password, style_metadata, allow_pdf_source)
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
                filename = part.get_filename() or f"part-{index}"
                if intake.is_opaque_pdf_name(filename):
                    yielded = True
                    errors.append({
                        "source": f"{name}!/{filename}",
                        "status": "skipped_opaque_pdf_by_name",
                        "pinned_sha256": intake.OPAQUE_PDF_SHA256,
                    })
                    continue
                payload = part.get_payload(decode=True)
                if not payload:
                    continue
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
                    yield from iter_text_streams(f"{name}!/{filename}", payload, depth + 1, budget, errors, ocr, pdf_password, style_metadata, allow_pdf_source)
        except Exception as exc:
            errors.append({"source": name, "error": f"MIME extraction failed: {exc}"})
        if not yielded:
            yield name, data
    elif kind == "ole-compound":
        yielded = False
        fallback_used = False
        xls_streams = None
        suffix = PurePosixPath(name.replace("\\", "/")).suffix.casefold()
        m10_image_workbook = (
            suffix == ".xls"
            and PurePosixPath(name.replace(chr(92), "/")).name.casefold() == "mug-stock.xls"
        )
        xls_image_records: list[dict] = []
        m10_seen_image_digests: set[str] = set()
        if m10_image_workbook:
            # Native BIFF8/OfficeArt shapes can preserve captions and original
            # image streams lost in a spreadsheet-conversion round trip.
            # Only the exact source-linked workbook and M10-anchored shapes
            # are eligible to emit text or images into the K08 phrase scanner.
            try:
                from h17_biff_officeart_blips import extract_xls_officeart_blips
                officeart = extract_xls_officeart_blips(data, include_image_data=True)
                for shape in officeart["shapes"]:
                    if shape.get("anchor_cell") != "M10":
                        continue
                    shape_source = f"{name}!/<native-officeart:{shape['sheet']}!M10>"
                    for field in ("wz_name", "wz_description"):
                        caption_text = shape.get(field)
                        if isinstance(caption_text, str) and caption_text.strip():
                            yielded = True
                            yield f"{shape_source}:{field}", caption_text.encode("utf-8")
                    if shape.get("blip_ref_status") != "resolved":
                        continue
                    pib = shape.get("pib")
                    blips = officeart["blip_store"]
                    if not isinstance(pib, int) or not 1 <= pib <= len(blips):
                        continue
                    blip = blips[pib - 1]
                    if not blip.get("data_base64"):
                        continue
                    image_data = base64.b64decode(blip["data_base64"], validate=True)
                    actual_digest = hashlib.sha256(image_data).hexdigest()
                    if actual_digest != str(blip["sha256"]).lower():
                        raise ValueError("native M10 OfficeArt image SHA-256 mismatch")
                    if actual_digest in m10_seen_image_digests:
                        continue
                    m10_seen_image_digests.add(actual_digest)
                    image_format = str(blip.get("format") or "png").lower()
                    yielded = True
                    # Run the source-literal M10 bit-plane reader independently;
                    # a generic image metadata/parser failure must not suppress it.
                    yield from iter_m10_teal_bit_text(shape_source, image_data, errors)
                    yield from iter_text_streams(
                        f"{shape_source}.{image_format}", image_data, depth + 1,
                        budget, errors, ocr, pdf_password, style_metadata, allow_pdf_source,
                    )
            except Exception as exc:
                errors.append({
                    "source": name,
                    "error": f"native M10 OfficeArt inspection failed: {type(exc).__name__}: {exc}",
                })
        if suffix == ".doc":
            # Legacy Word comments can hold the margin wording. Convert only a
            # temporary copy to DOCX with macro security high, then reuse the
            # existing DOCX ZIP/XML text path (including word/comments.xml).
            try:
                from h17_doc_lo_fallback import convert_doc_bytes
                converted_docx = convert_doc_bytes(data, name)
                fallback_used = True
                for source, payload in iter_text_streams(
                    f"{name}!/LibreOffice-converted.docx", converted_docx,
                    depth + 1, budget, errors, ocr, pdf_password, style_metadata, allow_pdf_source,
                ):
                    yielded = True
                    yield source, payload
            except Exception as exc:
                errors.append({
                    "source": name,
                    "error": f"LibreOffice legacy .doc fallback failed: {type(exc).__name__}: {exc}",
                })
        if suffix == ".xls":
            # BIFF8 cell strings are stored in structured records inside the
            # OLE Workbook stream; raw ASCII/UTF-16 scanning alone can split a
            # caption across cells. Prefer xlrd when installed; otherwise use
            # the isolated, temporary-copy LibreOffice format adapter.
            try:
                import xlrd
            except ImportError:
                try:
                    from h17_xls_lo_fallback import extract_bytes
                    converted = extract_bytes(
                        data, name,
                        include_image_data=m10_image_workbook,
                        allowed_image_anchors={"M10"} if m10_image_workbook else None,
                    )
                    if m10_image_workbook:
                        xls_image_records = converted.get("embedded_images", [])
                    for style in converted.get("style_metadata", []):
                        style_metadata.append({"source": name, **style})
                    xls_streams = [
                        (
                            f"{name}!/{item['kind']}:{item['source']}",
                            item["text"].encode("utf-8", "replace"),
                        )
                        for item in converted["text_streams"]
                    ]
                    fallback_used = True
                except Exception as exc:
                    errors.append({
                        "source": name,
                        "error": f"xlrd unavailable and LibreOffice BIFF fallback failed: {type(exc).__name__}: {exc}",
                    })
            else:
                try:
                    book = xlrd.open_workbook(file_contents=data, on_demand=False)
                    xls_streams = []
                    cell_budget = 250_000
                    empty_types = {xlrd.XL_CELL_EMPTY, getattr(xlrd, "XL_CELL_BLANK", 6)}
                    for sheet in book.sheets():
                        sheet_rows = []
                        for rowx in range(sheet.nrows):
                            row_values = []
                            for colx in range(sheet.ncols):
                                if cell_budget <= 0:
                                    break
                                cell_budget -= 1
                                cell = sheet.cell(rowx, colx)
                                if cell.ctype in empty_types or cell.value is None:
                                    continue
                                value = str(cell.value)
                                if not value:
                                    continue
                                row_values.append(value)
                                xls_streams.append((
                                    f"{name}!/{sheet.name}!R{rowx + 1}C{colx + 1}",
                                    value.encode("utf-8", "replace"),
                                ))
                            if row_values:
                                row_text = " ".join(row_values)
                                sheet_rows.append(row_text)
                                xls_streams.append((
                                    f"{name}!/{sheet.name}!row{rowx + 1}",
                                    row_text.encode("utf-8", "replace"),
                                ))
                            if cell_budget <= 0:
                                break
                        if sheet_rows:
                            xls_streams.append((
                                f"{name}!/{sheet.name}!sheet",
                                "\n".join(sheet_rows).encode("utf-8", "replace"),
                            ))
                        if cell_budget <= 0:
                            errors.append({"source": name, "error": "legacy .xls cell scan stopped at 250000 cells"})
                            break
                    book.release_resources()
                except Exception as exc:
                    xls_streams = None
                    errors.append({"source": name, "error": f"legacy .xls BIFF extraction failed: {exc}"})
                if m10_image_workbook:
                    try:
                        from h17_xls_lo_fallback import extract_bytes
                        converted_images = extract_bytes(
                            data, name, include_image_data=True,
                            allowed_image_anchors={"M10"},
                        )
                        xls_image_records = converted_images.get("embedded_images", [])
                    except Exception as exc:
                        errors.append({
                            "source": name,
                            "error": f"M10 image extraction failed: {type(exc).__name__}: {exc}",
                        })
        if xls_streams is not None:
            for source, payload in xls_streams:
                yielded = True
                yield source, payload
        # The source-linked mug-stock workbook may contain a photograph or a
        # text-bearing drawing anchored at M10. Only this named workbook and
        # this one original cell anchor may yield embedded image bytes.
        for item in xls_image_records:
            if not item.get("data_included"):
                continue
            if str(item.get("anchor", "")).upper() != "M10":
                errors.append({"source": name, "error": "unexpected non-M10 image emission"})
                continue
            try:
                image_data = base64.b64decode(item["data_base64"], validate=True)
                image_digest = hashlib.sha256(image_data).hexdigest()
                if image_digest != str(item["sha256"]).lower():
                    raise ValueError("embedded image digest mismatch")
            except (KeyError, ValueError, binascii.Error) as exc:
                errors.append({"source": name, "error": f"invalid M10 image: {exc}"})
                continue
            if image_digest in m10_seen_image_digests:
                continue
            m10_seen_image_digests.add(image_digest)
            image_format = str(item.get("format") or "png").lower()
            image_source = f"{name}!/<image:{item['sheet']}!M10>.{image_format}"
            yielded = True
            # Keep the source-literal M10 bit-plane read independent of
            # generic image metadata parsing.
            yield from iter_m10_teal_bit_text(image_source, image_data, errors)
            yield from iter_text_streams(
                image_source, image_data, depth + 1, budget, errors,
                ocr, pdf_password, style_metadata, allow_pdf_source,
            )
        try:
            import olefile
            with olefile.OleFileIO(io.BytesIO(data)) as compound:
                for stream_path in compound.listdir(streams=True, storages=False):
                    stream_name = "/".join(stream_path)
                    # Keep the raw BIFF Workbook/Book stream too: xlrd does not
                    # expose every NOTE/OBJ/comment or embedded-object record.
                    payload = compound.openstream(stream_path).read()
                    if (suffix == ".msg"
                            and stream_path[-1].casefold() == "__substg1.0_10090102"):
                        yield from iter_msg_rtf_text(
                            f"{name}!/{stream_name}", payload, errors,
                        )
                    yielded = True
                    yield from iter_text_streams(f"{name}!/{stream_name}", payload, depth + 1, budget, errors, ocr, pdf_password, style_metadata, allow_pdf_source)
        except ImportError:
            if not yielded or fallback_used:
                errors.append({"source": name, "error": "olefile unavailable; non-Office embedded OLE streams may not be decoded"})
        except Exception as exc:
            errors.append({"source": name, "error": f"OLE extraction failed: {exc}"})
        if not yielded or fallback_used:
            yield name, data
    elif kind == "pdf":
        content_yielded = False
        try:
            from pypdf import PdfReader
            reader = PdfReader(io.BytesIO(data), strict=False)
            if reader.is_encrypted:
                if pdf_password is None:
                    raise ValueError("encrypted PDF; supply --pdf-password if authorized (no guessing)")
                if not reader.decrypt(pdf_password):
                    raise ValueError("supplied --pdf-password did not decrypt PDF")
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
                            yield from iter_text_streams(f"{name}!/<page-{index + 1}-image-{image_index}>", image.data, depth + 1, budget, errors, ocr, pdf_password, style_metadata, allow_pdf_source)
                except Exception:
                    pass
                if ocr and index < 20:
                    try:
                        import fitz
                        import pytesseract
                        from PIL import Image
                        document = fitz.open(stream=data, filetype="pdf", password=pdf_password or "")
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
                        yield from iter_text_streams(f"{name}!/{filename}[{index}]", payload, depth + 1, budget, errors, ocr, pdf_password, style_metadata, allow_pdf_source)
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
                    from PIL import ImageOps

                    frame_count = int(getattr(image, "n_frames", 1))
                    for frame_index in range(frame_count):
                        try:
                            image.seek(frame_index)
                            frame = ImageOps.exif_transpose(image.copy()).convert("RGB")
                            frame.thumbnail((3000, 3000))
                            ocr_text = pytesseract.image_to_string(frame)
                            if ocr_text.strip():
                                frame_suffix = f"#frame={frame_index}" if frame_count > 1 else ""
                                yield f"{name}!/<ocr-text>{frame_suffix}", ocr_text.encode("utf-8", "replace")
                        except Exception as frame_exc:
                            errors.append({
                                "source": f"{name}#frame={frame_index}",
                                "error": f"image-ocr:{type(frame_exc).__name__}:{frame_exc}",
                            })
                else:
                    errors.append({"source": name, "error": "image present; OCR disabled"})
        except Exception as exc:
            errors.append({"source": name, "error": f"image metadata/OCR unavailable: {exc}"})
        # Image bytes themselves are not useful phrase text unless metadata/OCR is present.
    elif data.startswith(b"EMFSPOOL") or b" EMF" in data or name.casefold().endswith(".emf"):
        # EMFSPOOL can wrap one or more EMF pages. Keep the raw member as well
        # as validated Unicode text; glyph-index/bitmap/outline-only content
        # remains outside this reader's coverage.
        emf_stream_count = 0
        try:
            from h17_emf_text import extract_emf_text
            for label, payload in extract_emf_text(data):
                if budget[0] + len(payload) > intake.MAX_TOTAL:
                    errors.append({"source": name, "error": "EMF text output exceeds total scan budget"})
                    break
                budget[0] += len(payload)
                emf_stream_count += 1
                yield f"{name}!/{label}", payload
        except Exception as exc:
            errors.append({"source": name, "error": f"emf-text:{type(exc).__name__}:{exc}"})
        if emf_stream_count == 0:
            errors.append({
                "source": name,
                "error": "EMF/EMFSPOOL candidate produced no validated Unicode text; glyph-index, bitmap or outline content may remain",
            })
        yield name, data
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
            if len(phrase) > 96:
                break
            if len(phrase) < 8:
                continue
            tested += 1
            component = k08_component(nonce, phrase)
            if hashlib.sha256(component).digest() == target:
                hits.append({"source": source, "word_start": start,
                             "word_end_exclusive": end + 1,
                             "word_count": len(phrase_words),
                             "normalized_phrase": phrase,
                             "component_hex": component.hex().upper()})
    return tested



def scan_authored_text_units(text: str, nonce: bytes, target: bytes, source: str,
                             hits: list[dict], max_chars: int = 512) -> int:
    """Check intact long source-authored captions, including labeled fields.

    Preserve whole lines and blank-line-delimited paragraphs. For explicitly
    labeled fields, also test the exact value after the first colon or equals
    sign. This permits a long original caption whose written heading shares
    its line, without generating or paraphrasing candidate wording.
    """
    source_lines = text.replace("\r\n", "\n").replace("\r", "\n")
    units = [("line", line) for line in source_lines.split("\n")]
    units.extend(
        ("paragraph", paragraph)
        for paragraph in re.split(r"\n[ \t]*\n+", source_lines)
    )
    tested = 0
    seen: set[str] = set()
    for kind, unit in units:
        views = [("whole", unit)]
        for delimiter in (":", "="):
            if delimiter in unit:
                views.append((f"value-after-{delimiter}", unit.split(delimiter, 1)[1]))
        for field, value in views:
            phrase = normalize(value)
            if not 96 < len(phrase) <= max_chars or phrase in seen:
                continue
            seen.add(phrase)
            tested += 1
            component = k08_component(nonce, phrase)
            if hashlib.sha256(component).digest() == target:
                hits.append({
                    "source": f"{source} [{kind}-{field}]",
                    "word_start": 0,
                    "word_end_exclusive": len(phrase.split()),
                    "word_count": len(phrase.split()),
                    "normalized_phrase": phrase,
                    "component_hex": component.hex().upper(),
                    "whole_text_unit": kind,
                    "source_field": field,
                })
    return tested


@redact_by_default
def inspect_object(path: Path, resources: Path, transfer_id: str = "AX-7782",
                   ocr: bool = False, max_phrase_words: int = 48,
                   pdf_password: str | None = None,
                   allow_pdf_source: bool = False) -> dict:
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
    workbook_style_metadata: list[dict] = []
    budget = [0]
    streams = 0
    spans_tested = 0
    authored_units_tested = 0
    for source, stream_data in iter_text_streams(path.name, data, 0, budget, errors, ocr, pdf_password, workbook_style_metadata, allow_pdf_source):
        streams += 1
        seen_normalized: set[str] = set()
        for label, text in decode_text_variants(stream_data, source):
            normalized = normalize(text)
            if not normalized or normalized in seen_normalized:
                continue
            seen_normalized.add(normalized)
            spans_tested += scan_phrase_spans(text, nonce, target,
                                              f"{source} [{label}]", max_phrase_words, hits)
            authored_units_tested += scan_authored_text_units(
                text, nonce, target, f"{source} [{label}]", hits)
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
                       "authored_lines_and_paragraphs_tested": authored_units_tested,
                       "max_phrase_words": max_phrase_words,
                       "original_commitment_hits": hits,
                       "ocr_enabled": ocr,
                       "pdf_password_supplied": pdf_password is not None,
                       "pdf_source_authorized": allow_pdf_source},
        "workbook_style_metadata": workbook_style_metadata,
        "errors_or_unavailable_decoders": errors,
        "limits": [
            "Only exact contiguous normalized phrase spans are tested; no paraphrase or word-edit search is performed.",
            "PDF members are skipped unless --allow-pdf-source explicitly attests independent provenance; the pinned BX25-08 source and path-preserving derivatives remain blocked regardless.",
            "OCR is optional and may not reliably transcribe handwritten marginalia; visually inspect original images when needed.",
            "7z/RAR and SQLite databases other than named Windows Sticky Notes plum.sqlite members are not decoded by this path; the joint runner adds a read-only plum.sqlite/WAL bridge. EMF/EMFSPOOL Unicode text and XPS/OXPS UnicodeString plus complete glyph-index-only runs use bounded dedicated readers; incomplete XPS glyph coverage and empty EMF/XPS text extraction are reported, and bitmap/outline-only text may remain. Legacy Excel .xls BIFF cells and legacy Word .doc content/comments are decoded with the isolated LibreOffice fallbacks; other OLE streams are decoded when olefile is installed.",
            "The K04 payload is handled by work/h17_k04_binary_window_intake.py, not by this phrase scanner.",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--object", required=True, type=Path, help="authorized local AX-7782 8 MiB object")
    parser.add_argument("--resources", type=Path, default=Path("resources"))
    parser.add_argument("--transfer", default="AX-7782")
    parser.add_argument("--ocr", action="store_true", help="optional OCR for images; PDFs require --allow-pdf-source")
    parser.add_argument("--pdf-password", help="password for an independently authorized PDF; never guessed")
    parser.add_argument("--allow-pdf-source", action="store_true", help="attest independent provenance for non-quarantined PDFs; never use for BX25-08 or derivatives")
    parser.add_argument("--max-phrase-words", type=int, default=48)
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
                                args.ocr, args.max_phrase_words, args.pdf_password, args.allow_pdf_source)
    except Exception as exc:
        parser.error(str(exc))
    result = redact_sensitive(result)
    output = json.dumps(result, indent=2, sort_keys=True)
    if args.json_out:
        args.json_out.write_text(output + "\n", encoding="utf-8")
    print(output)


if __name__ == "__main__":
    main()
