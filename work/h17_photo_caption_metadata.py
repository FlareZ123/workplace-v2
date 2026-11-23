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
    start = min((data.find(token) for token in XMP_STARTS if data.find(token) >= 0), default=-1)
    if start < 0:
        return None
    ends = [(data.find(token, start), token) for token in XMP_ENDS]
    ends = [(pos, token) for pos, token in ends if pos >= 0]
    if not ends:
        return data[start:start + 4 * 1024 * 1024]
    pos, token = min(ends, key=lambda item: item[0])
    return data[start:pos + len(token)]


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
