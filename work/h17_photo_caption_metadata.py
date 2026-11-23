"""Read structured XMP caption/description fields from original photo files/sidecars.

This is a source-specific metadata reader, not OCR or a broad text search. It
preserves the XMP property and language label so a candidate remains traceable
to its original caption field.
"""
from __future__ import annotations

import re
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
            return value.decode(encoding).strip("\\x00 \\t\\r\\n")
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
    if not data or b"Photoshop 3.0\\x00" not in data:
        return
    signature = b"Photoshop 3.0\\x00"
    pos = 0
    while True:
        marker = data.find(signature, pos)
        if marker < 0:
            break
        # Advance the outer search before parsing this APP13 block.
        # Otherwise one Photoshop 3.0 signature is rediscovered forever.
        pos = marker + len(signature)
        cursor = pos
        while cursor + 12 <= len(data):
            block = data.find(b"8BIM", cursor)
            if block < 0 or block + 12 > len(data):
                break
            resource_id = int.from_bytes(data[block + 4:block + 6], "big")
            name_length = data[block + 6]
            name_start = block + 7
            name_end = name_start + name_length
            padded_name_end = name_start + (((1 + name_length + 1) // 2) * 2) - 1
            size_pos = padded_name_end
            if size_pos + 4 > len(data):
                break
            resource_size = int.from_bytes(data[size_pos:size_pos + 4], "big")
            resource_start = size_pos + 4
            resource_end = resource_start + resource_size
            if resource_end > len(data):
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
