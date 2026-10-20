"""Read-only K08 native photograph caption, EXIF/IPTC/XMP and sidecar inventory.

An extracted caption is a candidate witness only. It needs an independent
historical link to Emily's *final incident-envelope inscription* before K08
can be reported recovered. All source files are hashed without modification.
"""

from __future__ import annotations

import argparse
import hashlib
import hmac
import json
import re
import tempfile
from pathlib import Path
from typing import Any, Iterator

from defusedxml import ElementTree
from PIL import Image, IptcImagePlugin

CAPTION_FIELDS = {"ImageDescription", "XPTitle", "XPComment", "XPSubject"}
EXIF_FIELDS = {270: "ImageDescription", 40091: "XPTitle", 40092: "XPComment", 40095: "XPSubject"}
IPTC_FIELDS = {(2, 120): "CaptionAbstract", (2, 105): "Headline", (2, 5): "ObjectName"}


def source_hash(path: Path) -> str:
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def normalize(text: str) -> str:
    return " ".join(re.sub(r"[^a-z0-9\s]", " ", text.lower()).split())


def text_value(value: str | bytes) -> str:
    if isinstance(value, str):
        return value.strip()
    if value.startswith(b"ASCII\x00\x00\x00"):
        return value[8:].decode("ascii", errors="replace").strip("\x00 ")
    if len(value) >= 2 and value[1] == 0:
        return value.decode("utf-16le", errors="replace").strip("\x00 ")
    return value.decode("utf-8", errors="replace").strip("\x00 ")


def flatten(value: Any, trail: str = "XMP") -> Iterator[tuple[str, str]]:
    if isinstance(value, dict):
        for key, child in value.items():
            yield from flatten(child, trail + "." + str(key))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            yield from flatten(child, trail + f"[{index}]")
    elif isinstance(value, (str, bytes)):
        content = text_value(value)
        if content:
            yield trail, content


def xmp_sidecar(path: Path) -> Iterator[tuple[str, str]]:
    root = ElementTree.parse(path).getroot()
    def visit(element: Any, trail: str) -> Iterator[tuple[str, str]]:
        tag = element.tag.rsplit("}", 1)[-1]
        new_path = trail + "." + tag
        if element.text and element.text.strip():
            yield new_path, element.text.strip()
        for child in element:
            yield from visit(child, new_path)
    yield from visit(root, "XMP_SIDE_CAR")


def photo_fields(path: Path) -> tuple[list[tuple[str, str]], dict[str, str]]:
    fields: list[tuple[str, str]] = []
    facts: dict[str, str] = {}
    with Image.open(path) as im:
        facts["format"] = im.format or "unknown"
        exif = im.getexif()
        for tag, label in EXIF_FIELDS.items():
            value = exif.get(tag)
            if isinstance(value, (str, bytes)):
                fields.append(("EXIF." + label, text_value(value)))
        for tag, label in ((306, "DateTime"), (315, "Artist"), (33432, "Copyright")):
            value = exif.get(tag)
            if isinstance(value, (str, bytes)):
                facts["EXIF." + label] = text_value(value)
        iptc = IptcImagePlugin.getiptcinfo(im) or {}
        for tag, label in IPTC_FIELDS.items():
            value = iptc.get(tag)
            if isinstance(value, list):
                fields.extend(("IPTC." + label, text_value(x)) for x in value)
            elif isinstance(value, bytes):
                fields.append(("IPTC." + label, text_value(value)))
        fields.extend(flatten(im.getxmp()))
    sidecar = path.with_suffix(".xmp")
    if sidecar.is_file():
        fields.extend(xmp_sidecar(sidecar))
        facts["sidecar_sha256"] = source_hash(sidecar)
    return [(field, value) for field, value in fields if value], facts


def assess(photos: list[Path], resources: Path) -> dict[str, Any]:
    route = json.loads((resources / "evidence/recovery-routing.json").read_text(encoding="utf-8"))
    accepted = json.loads((resources / "acceptance.json").read_text(encoding="utf-8"))
    nonce = bytes.fromhex(route["K08"]["desk_nonce"])
    target = accepted["slot_sha256"]["K08"]
    out: list[dict[str, Any]] = []
    matches = 0
    for path in photos:
        fields, facts = photo_fields(path)
        entries = []
        for origin, text in fields:
            normalized = normalize(text)
            if not normalized:
                continue
            candidate = hmac.new(nonce, normalized.encode("utf-8"), "sha256").digest()[:16]
            hit = hashlib.sha256(candidate).hexdigest() == target
            matches += bool(hit)
            entries.append({"field": origin, "exact_metadata_text": text, "normalized": normalized,
                            "k08_component": candidate.hex().upper(), "commitment_match": hit})
        out.append({"path": str(path), "original_sha256": source_hash(path),
                    "metadata": facts, "caption_fields": entries})
    return {"records": out, "cryptographic_matches": matches,
            "final_margin_provenance": "NOT ESTABLISHED BY METADATA ALONE"}


def self_test(resources: Path) -> None:
    first = "A good watch leaves the room ready for the next pair of hands."
    nonce = bytes.fromhex(json.loads((resources / "evidence/recovery-routing.json").read_text())["K08"]["desk_nonce"])
    assert hmac.new(nonce, normalize(first).encode(), "sha256").digest()[:16].hex().upper() == "BF889359B0303F2B2B2FD96AE841210B"
    with tempfile.TemporaryDirectory() as folder:
        photo = Path(folder) / "crew-original.jpg"
        im = Image.new("RGB", (2, 2), (1, 1, 1))
        exif = Image.Exif()
        exif[270] = first
        im.save(photo, exif=exif)
        photo.with_suffix(".xmp").write_text('''<?xml version="1.0"?>
<x:xmpmeta xmlns:x="adobe:ns:meta/" xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#" xmlns:dc="http://purl.org/dc/elements/1.1/">
<rdf:RDF><rdf:Description><dc:description><rdf:Alt><rdf:li>The little lamp stays on until the corridor has gone quiet.</rdf:li></rdf:Alt></dc:description></rdf:Description></rdf:RDF>
</x:xmpmeta>''' , encoding="utf-8")
        original_sha = source_hash(photo)
        result = assess([photo], resources)
        fields = result["records"][0]["caption_fields"]
        assert any(x["field"] == "EXIF.ImageDescription" and x["exact_metadata_text"] == first for x in fields)
        assert any(x["field"].startswith("XMP_SIDE_CAR") and "little lamp" in x["exact_metadata_text"] for x in fields)
        assert all(not x["commitment_match"] for x in fields)
        assert source_hash(photo) == original_sha
        assert result["records"][0]["metadata"]["sidecar_sha256"]
    print("PASS: literal EXIF and XMP sidecar captions, HMAC normalization, unchanged source hash")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("photos", nargs="*", type=Path)
    parser.add_argument("--resources", type=Path, required=True)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        self_test(args.resources)
    if args.photos:
        print(json.dumps(assess(args.photos, args.resources), ensure_ascii=False, indent=2))
    elif not args.self_test:
        parser.error("supply at least one native photograph or use --self-test")


if __name__ == "__main__":
    main()
