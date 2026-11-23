"""Read structured XMP, IPTC and native TIFF/EXIF caption fields.

This is a source-specific metadata reader, not OCR or a broad text search. It
preserves carrier, property/tag, IFD and encoding labels so every candidate
remains traceable to its original caption field.
"""
from __future__ import annotations

import re
import struct
from collections.abc import Iterator
from xml.etree import ElementTree

NS = {
    "dc": "http://purl.org/dc/elements/1.1/",
    "photoshop": "http://ns.adobe.com/photoshop/1.0/",
    "xmp": "http://ns.adobe.com/xap/1.0/",
    "tiff": "http://ns.adobe.com/tiff/1.0/",
    "exif": "http://ns.adobe.com/exif/1.0/",
    "iptcCore": "http://iptc.org/std/Iptc4xmpCore/1.0/xmlns/",
    "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
}
FIELDS = (
    ("dc:description", "dc", "description"),
    ("dc:title", "dc", "title"),
    ("dc:creator", "dc", "creator"),
    ("dc:subject", "dc", "subject"),
    ("photoshop:Headline", "photoshop", "Headline"),
    ("photoshop:CaptionWriter", "photoshop", "CaptionWriter"),
    ("photoshop:Instructions", "photoshop", "Instructions"),
    ("photoshop:Credit", "photoshop", "Credit"),
    ("xmp:Label", "xmp", "Label"),
    ("xmp:CreateDate", "xmp", "CreateDate"),
    ("xmp:ModifyDate", "xmp", "ModifyDate"),
    ("tiff:DateTime", "tiff", "DateTime"),
    ("exif:DateTimeOriginal", "exif", "DateTimeOriginal"),
    ("iptcCore:Location", "iptcCore", "Location"),
)
XMP_STARTS = (b"<x:xmpmeta", b"<xmpmeta", b"<rdf:RDF")
XMP_ENDS = (b"</x:xmpmeta>", b"</xmpmeta>", b"</rdf:RDF>")


def _extract_packet(name: str, data: bytes) -> bytes | None:
    lower = name.casefold()
    if lower.endswith(".xmp"):
        return data[:4 * 1024 * 1024]
    pairs = (
        (b"<x:xmpmeta", b"</x:xmpmeta>"),
        (b"<xmpmeta", b"</xmpmeta>"),
        (b"<rdf:RDF", b"</rdf:RDF>"),
    )
    found = [(data.find(start_token), start_token, end_token)
             for start_token, end_token in pairs
             if data.find(start_token) >= 0]
    if not found:
        return None
    start, _start_token, end_token = min(found, key=lambda item: item[0])
    end = data.find(end_token, start)
    if end < 0:
        return data[start:start + 4 * 1024 * 1024]
    return data[start:end + len(end_token)]


def _field_values(element):
    li_tag = "{" + NS["rdf"] + "}li"
    items = [node for node in element.iter(li_tag)]
    if items:
        for index, item in enumerate(items):
            value = "".join(item.itertext()).strip()
            if value:
                lang = item.attrib.get("{http://www.w3.org/XML/1998/namespace}lang", "")
                yield index, lang, value
    else:
        value = "".join(element.itertext()).strip()
        if value:
            yield 0, "", value


IPTC_FIELDS = {
    (2, 5): "ObjectName",
    (2, 25): "Keywords",
    (2, 55): "DateCreated",
    (2, 60): "TimeCreated",
    (2, 80): "ByLine",
    (2, 90): "City",
    (2, 101): "CountryName",
    (2, 105): "Headline",
    (2, 116): "CopyrightNotice",
    (2, 120): "CaptionAbstract",
}


def _decode_iptc(value: bytes) -> str:
    for encoding in ("utf-8", "cp1252", "latin-1"):
        try:
            return value.decode(encoding).strip("\x00 \t\r\n")
        except UnicodeDecodeError:
            continue
    return value.decode("utf-8", "replace").strip()


def _parse_iptc_datasets(payload: bytes):
    pos = 0
    item_counts: dict[tuple[int, int], int] = {}
    while pos + 5 <= len(payload):
        if payload[pos] != 0x1C:
            pos += 1
            continue
        record, dataset = payload[pos + 1], payload[pos + 2]
        size_word = int.from_bytes(payload[pos + 3:pos + 5], "big")
        pos += 5
        if size_word & 0x8000:
            count = size_word & 0x7FFF
            if count == 0 or count > 4 or pos + count > len(payload):
                break
            length = int.from_bytes(payload[pos:pos + count], "big")
            pos += count
        else:
            length = size_word
        if length < 0 or pos + length > len(payload):
            break
        key = (record, dataset)
        if key in IPTC_FIELDS:
            index = item_counts.get(key, 0)
            item_counts[key] = index + 1
            text = _decode_iptc(payload[pos:pos + length])
            if text:
                yield f"iptc:{IPTC_FIELDS[key]}:record-{record}:dataset-{dataset}:item-{index}", text
        pos += length


def iter_iptc_caption_units(name: str, data: bytes) -> Iterator[tuple[str, str]]:
    """Extract selected IPTC-IIM caption/catalogue text from Photoshop APP13 blocks."""
    if not data or b"Photoshop 3.0\x00" not in data:
        return
    signature = b"Photoshop 3.0\x00"
    pos = 0
    while True:
        marker = data.find(signature, pos)
        if marker < 0:
            break
        # Advance the outer search before parsing this APP13 block.
        # Otherwise one Photoshop 3.0 signature is rediscovered forever.
        pos = marker + len(signature)
        next_marker = data.find(signature, pos)
        section_end = len(data) if next_marker < 0 else next_marker
        cursor = pos
        while cursor + 12 <= section_end:
            block = data.find(b"8BIM", cursor, section_end)
            if block < 0 or block + 12 > section_end:
                break
            resource_id = int.from_bytes(data[block + 4:block + 6], "big")
            name_length = data[block + 6]
            name_start = block + 7
            name_end = name_start + name_length
            padded_name_end = name_start + (((1 + name_length + 1) // 2) * 2) - 1
            size_pos = padded_name_end
            if size_pos + 4 > section_end:
                break
            resource_size = int.from_bytes(data[size_pos:size_pos + 4], "big")
            resource_start = size_pos + 4
            resource_end = resource_start + resource_size
            if resource_end > section_end:
                break
            if resource_id == 0x0404:
                for label, text in _parse_iptc_datasets(data[resource_start:resource_end]):
                    yield label, text
            cursor = resource_end + (resource_size & 1)


def iter_xmp_caption_units(name: str, data: bytes) -> Iterator[tuple[str, str]]:
    packet = _extract_packet(name, data)
    if not packet:
        return
    try:
        root = ElementTree.fromstring(packet)
    except ElementTree.ParseError:
        # XMP sidecars may carry xpacket processing instructions; ElementTree
        # handles them, but malformed/truncated packets are not repaired.
        return
    for field_label, prefix, local_name in FIELDS:
        tag = "{" + NS[prefix] + "}" + local_name
        for element_index, element in enumerate(root.iter(tag)):
            for item_index, lang, value in _field_values(element):
                safe_lang = re.sub(r"[^A-Za-z0-9_.-]+", "_", lang) or "unspecified"
                label = f"xmp:{field_label}:element-{element_index}:item-{item_index}:lang-{safe_lang}"
                yield label, value
        # RDF/XML permits simple literal properties on rdf:Description
        # as XML attributes. Photoshop commonly serializes Headlines and
        # other caption metadata in this form.
        description_tag = "{" + NS["rdf"] + "}Description"
        for description_index, description in enumerate(root.iter(description_tag)):
            value = description.attrib.get(tag, "").strip()
            if value:
                lang = description.attrib.get(
                    "{http://www.w3.org/XML/1998/namespace}lang", ""
                )
                safe_lang = re.sub(r"[^A-Za-z0-9_.-]+", "_", lang) or "unspecified"
                label = f"xmp:{field_label}:description-{description_index}:attribute:lang-{safe_lang}"
                yield label, value

    # Photoshop's standard TextLayers metadata caches complete text per layer.
    # Keep each layer's name paired with its own text, which can distinguish
    # a final envelope overlay from an earlier generic photograph caption.
    layer_section_tag = "{" + NS["photoshop"] + "}TextLayers"
    list_item_tag = "{" + NS["rdf"] + "}li"
    layer_name_tag = "{" + NS["photoshop"] + "}LayerName"
    layer_text_tag = "{" + NS["photoshop"] + "}LayerText"

    def layer_property(item, tag: str) -> str:
        for node in item.iter():
            if node.tag == tag:
                value = "".join(node.itertext()).strip()
                if value:
                    return value
            value = node.attrib.get(tag, "").strip()
            if value:
                return value
        return ""

    for section_index, section in enumerate(root.iter(layer_section_tag)):
        for layer_index, item in enumerate(section.iter(list_item_tag)):
            text = layer_property(item, layer_text_tag)
            if text:
                name = layer_property(item, layer_name_tag)
                safe_name = re.sub(r"[^A-Za-z0-9_.-]+", "_", name).strip("_")[:120] or "unnamed"
                yield (
                    f"xmp:photoshop:TextLayers:section-{section_index}:"
                    f"layer-{layer_index}:name-{safe_name}",
                    text,
                )


# Native TIFF/EXIF caption fields. These are distinct from XMP and IPTC:
# several camera and Windows photo workflows store the only authored caption
# in ImageDescription, UserComment, or XP* tags.
EXIF_TEXT_TAGS = {
    0x010D: ("DocumentName", "ascii"),
    0x010E: ("ImageDescription", "ascii"),
    0x011D: ("PageName", "ascii"),
    0x013B: ("Artist", "ascii"),
    0x8298: ("Copyright", "ascii"),
    0x9C9B: ("XPTitle", "utf16le"),
    0x9C9C: ("XPComment", "utf16le"),
    0x9C9D: ("XPAuthor", "utf16le"),
    0x9C9E: ("XPKeywords", "utf16le"),
    0x9C9F: ("XPSubject", "utf16le"),
    0x9286: ("UserComment", "usercomment"),
}
_TIFF_TYPE_SIZES = {
    1: 1, 2: 1, 3: 2, 4: 4, 5: 8, 6: 1, 7: 1,
    8: 2, 9: 4, 10: 8, 11: 4, 12: 8, 13: 4,
}
_EXIF_MAX_IFD_ENTRIES = 4096
_EXIF_MAX_TEXT_BYTES = 1024 * 1024


def _strip_utf16_nul_terminator(raw: bytes) -> bytes:
    # Do not use bytes.rstrip(b"\0") on UTF-16LE: it removes the high zero
    # byte of the final ASCII character as well as the two-byte terminator.
    while raw.endswith(b"\x00\x00"):
        raw = raw[:-2]
    return raw


def _decode_exif_text(tag: int, raw: bytes, byteorder: str):
    field_name, kind = EXIF_TEXT_TAGS[tag]
    if kind == "ascii":
        raw = raw.rstrip(b"\x00")
        if not raw:
            return None
        try:
            text = raw.decode("ascii")
            encoding = "ascii"
        except UnicodeDecodeError:
            try:
                text = raw.decode("utf-8")
                encoding = "utf-8"
            except UnicodeDecodeError:
                text = raw.decode("latin-1")
                encoding = "latin-1"
    elif kind == "utf16le":
        raw = _strip_utf16_nul_terminator(raw)
        if raw.startswith(b"\xff\xfe"):
            raw, encoding = raw[2:], "utf-16le-bom"
        elif raw.startswith(b"\xfe\xff"):
            raw, encoding = raw[2:], "utf-16be-bom"
        else:
            encoding = "utf-16le"
        if len(raw) & 1:
            raw = raw[:-1]
        if not raw:
            return None
        codec = encoding.removesuffix("-bom")
        text = raw.decode(codec, errors="replace")
    else:
        # EXIF UserComment has an eight-byte character-code designator.
        if raw.startswith(b"ASCII\x00\x00\x00"):
            body = raw[8:].rstrip(b"\x00")
            if not body:
                return None
            text = body.decode("ascii", errors="replace")
            encoding = "ascii"
        elif raw.startswith(b"UNICODE\x00"):
            body = _strip_utf16_nul_terminator(raw[8:])
            if body.startswith(b"\xff\xfe"):
                body, codec, encoding = body[2:], "utf-16le", "utf-16le-bom"
            elif body.startswith(b"\xfe\xff"):
                body, codec, encoding = body[2:], "utf-16be", "utf-16be-bom"
            else:
                codec = "utf-16le" if byteorder == "little" else "utf-16be"
                encoding = codec
            if len(body) & 1:
                body = body[:-1]
            if not body:
                return None
            text = body.decode(codec, errors="replace")
        elif raw.startswith(b"JIS\x00\x00\x00\x00\x00"):
            body = raw[8:].rstrip(b"\x00")
            if not body:
                return None
            text = body.decode("shift_jis", errors="replace")
            encoding = "shift_jis"
        else:
            # Unknown UserComment encodings may be binary. Fail closed rather
            # than promoting arbitrary bytes into candidate phrase streams.
            return None
    text = text.strip("\x00 \t\r\n")
    if not text:
        return None
    return field_name, encoding, text


def _iter_tiff_exif_caption_units(tiff: bytes, carrier: str) -> Iterator[tuple[str, str]]:
    """Read bounded IFD0 and ExifIFD caption tags from one TIFF header."""
    if len(tiff) < 8:
        return
    if tiff[:2] == b"II":
        endian, byteorder = "<", "little"
    elif tiff[:2] == b"MM":
        endian, byteorder = ">", "big"
    else:
        return
    # Classic TIFF/EXIF only. BigTIFF uses a different header and IFD layout.
    if struct.unpack_from(endian + "H", tiff, 2)[0] != 42:
        return
    ifd0_offset = struct.unpack_from(endian + "I", tiff, 4)[0]
    visited: set[int] = set()

    def parse_ifd(offset: int, ifd_name: str):
        found = []
        if offset in visited or offset < 8 or offset + 2 > len(tiff):
            return found, None
        visited.add(offset)
        entry_count = struct.unpack_from(endian + "H", tiff, offset)[0]
        table_end = offset + 2 + entry_count * 12 + 4
        if entry_count > _EXIF_MAX_IFD_ENTRIES or table_end > len(tiff):
            return found, None
        exif_ifd_offset = None
        for entry_index in range(entry_count):
            entry = offset + 2 + entry_index * 12
            tag, field_type, count = struct.unpack_from(endian + "HHI", tiff, entry)
            value_field = tiff[entry + 8:entry + 12]
            if tag == 0x8769 and field_type in (4, 13) and count == 1:
                exif_ifd_offset = struct.unpack(endian + "I", value_field)[0]
            if tag not in EXIF_TEXT_TAGS:
                continue
            if field_type not in _TIFF_TYPE_SIZES or count == 0:
                continue
            if count > _EXIF_MAX_TEXT_BYTES:
                continue
            if tag in (0x9C9B, 0x9C9C, 0x9C9D, 0x9C9E, 0x9C9F) and field_type not in (1, 7):
                continue
            if tag in (0x010D, 0x010E, 0x011D, 0x013B, 0x8298) and field_type not in (2, 7):
                continue
            if tag == 0x9286 and field_type not in (1, 7):
                continue
            value_size = count * _TIFF_TYPE_SIZES[field_type]
            if value_size > _EXIF_MAX_TEXT_BYTES:
                continue
            if value_size <= 4:
                raw = value_field[:value_size]
            else:
                value_offset = struct.unpack(endian + "I", value_field)[0]
                if value_offset < 8 or value_offset + value_size > len(tiff):
                    continue
                raw = tiff[value_offset:value_offset + value_size]
            decoded = _decode_exif_text(tag, raw, byteorder)
            if decoded:
                field_name, encoding, text = decoded
                label = (
                    f"exif:{carrier}:{field_name}:{ifd_name}:"
                    f"tag-0x{tag:04X}:encoding-{encoding}"
                )
                found.append((label, text))
        return found, exif_ifd_offset

    ifd0_fields, exif_ifd_offset = parse_ifd(ifd0_offset, "ifd0")
    yield from ifd0_fields
    if exif_ifd_offset:
        exif_fields, _unused = parse_ifd(exif_ifd_offset, "exif-ifd")
        yield from exif_fields


def iter_exif_caption_units(name: str, data: bytes) -> Iterator[tuple[str, str]]:
    """Yield authored EXIF caption fields from classic TIFF or JPEG APP1 data.

    Only recognized TIFF/EXIF signatures and bounded IFD fields are read.
    JPEG scanning stops at SOS/EOI; unknown UserComment encodings are ignored.
    """
    if data.startswith((b"II*\x00", b"MM\x00*")):
        yield from _iter_tiff_exif_caption_units(data, "tiff")
        return
    if data.startswith(b"Exif\x00\x00"):
        yield from _iter_tiff_exif_caption_units(data[6:], "exif-prefix")
        return
    if not data.startswith(b"\xff\xd8"):
        return

    position = 2
    app1_index = 0
    while position + 4 <= len(data):
        if data[position] != 0xFF:
            break
        while position < len(data) and data[position] == 0xFF:
            position += 1
        if position >= len(data):
            break
        marker = data[position]
        position += 1
        if marker in (0xD9, 0xDA):  # EOI or start of compressed scan
            break
        if marker == 0x01 or 0xD0 <= marker <= 0xD7:  # standalone markers
            continue
        if position + 2 > len(data):
            break
        segment_length = int.from_bytes(data[position:position + 2], "big")
        if segment_length < 2 or position + segment_length > len(data):
            break
        payload_start = position + 2
        payload_end = position + segment_length
        if marker == 0xE1 and data[payload_start:payload_start + 6] == b"Exif\x00\x00":
            yield from _iter_tiff_exif_caption_units(
                data[payload_start + 6:payload_end], f"jpeg-app1-{app1_index}"
            )
            app1_index += 1
        position = payload_end
