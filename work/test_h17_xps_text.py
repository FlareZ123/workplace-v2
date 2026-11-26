"""Single-file bounded XPS/OXPS text extractor regression."""
import hashlib
import hmac
import io
import sys
import zipfile
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).parent))
from h17_xps_text import extract_xps_text
import h17_k04_binary_window_intake as k04

NS = "http://schemas.microsoft.com/xps/2005/06"
NONCE = bytes.fromhex("5F933DA6A1BD03C32DA5CBC25344F497")
MASK = bytes.fromhex("8556C8CB6140A7F9A5123AC7571BEE1C")


def package(pages, *, opc=True):
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        if opc:
            archive.writestr("[Content_Types].xml", '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"/>')
        for i, text in enumerate(pages, 1):
            archive.writestr(f"Documents/1/Pages/{i}.fpage", text)
    return buffer.getvalue()


def page(*parts):
    runs = "".join(f'<Glyphs UnicodeString="{part}"/>' for part in parts)
    return f'<FixedPage xmlns="{NS}">{runs}</FixedPage>'.encode()


def test():
    coupon = bytes.fromhex("102132435465768798A9BACBDCEDFE0F")
    encoded = coupon.hex().upper()
    phrase = "the water held the last light around the table"
    source = package([page(encoded[:16], encoded[16:]), page(phrase[:19], phrase[19:])])
    original_hash = hashlib.sha256(source).hexdigest()
    streams = list(extract_xps_text(source))
    assert any(value.decode() == encoded for name, value in streams if name.endswith("-joined"))
    assert any(value.decode() == phrase for name, value in streams if name.endswith("-joined"))
    recovered = next(value for name, value in streams if name == "xps-page-1-joined")
    restored_coupon = bytes.fromhex(recovered.decode())
    recovered_component = bytes(a ^ b for a, b in zip(restored_coupon, MASK))
    assert hashlib.sha256(recovered_component).digest() == hashlib.sha256(bytes(a ^ b for a, b in zip(coupon, MASK))).digest()
    normalized = " ".join(phrase.split()).lower()
    expected_k08 = hmac.new(NONCE, normalized.encode(), hashlib.sha256).digest()[:16]
    assembled = next(value for name, value in streams if name == "xps-page-2-joined")
    assert hmac.new(NONCE, assembled.lower(), hashlib.sha256).digest()[:16] == expected_k08
    assert hashlib.sha256(source).hexdigest() == original_hash
    print("PASS: synthetic 2-page package, split 16-byte K04 and split whole-phrase K08")

    # The quarantined BX25-08 source is never opened. Exercise the hash-only
    # branch with synthetic PDF-magic bytes and a stubbed pinned-hash match.
    opaque_path = Path("BX25-08.pdf")
    opaque_pdf = b"%PDF-1.7 synthetic hash-only fixture"
    opaque_sha = hashlib.sha256(opaque_pdf).hexdigest()
    target_digest = bytes.fromhex(k04.DEFAULT_TARGET)
    with patch.object(k04.intake, "OPAQUE_PDF_SHA256", opaque_sha), \
         patch.object(k04, "magic", side_effect=AssertionError("opaque PDF reached magic")), \
         patch.object(k04, "scan_bytes", side_effect=AssertionError("opaque PDF reached raw-window scan")):
        opaque_result = k04.scan_member(
            str(opaque_path), opaque_pdf, 0,
            [0, k04.DEFAULT_MAX_TOTAL, 0, k04.DEFAULT_MAX_MEMBERS],
            target_digest, bytes.fromhex(k04.DEFAULT_MASK), 1,
            k04.DEFAULT_MAX_MEMBER, k04.DEFAULT_MAX_DEPTH
        )
    assert opaque_result == {
        "name": str(opaque_path), "size": len(opaque_pdf), "sha256": opaque_sha,
        "status": "skipped_opaque_pdf",
    }

    bundle = io.BytesIO()
    with zipfile.ZipFile(bundle, "w", compression=zipfile.ZIP_STORED) as archive:
        archive.writestr("BX25-08.pdf", opaque_pdf)
    with patch.object(k04.intake, "OPAQUE_PDF_SHA256", opaque_sha), \
         patch.object(k04, "scan_bytes", side_effect=AssertionError("container raw scan could inspect opaque member")):
        bundle_result = k04.scan_member(
            "bundle.zip", bundle.getvalue(), 0,
            [0, k04.DEFAULT_MAX_TOTAL, 0, k04.DEFAULT_MAX_MEMBERS],
            target_digest, bytes.fromhex(k04.DEFAULT_MASK), 1,
            k04.DEFAULT_MAX_MEMBER, k04.DEFAULT_MAX_DEPTH
        )
    assert bundle_result["hits"] == []
    assert bundle_result["members"][0]["status"] == "skipped_opaque_pdf"
    assert bundle_result["members"][0]["sha256"] == opaque_sha
    print("PASS: synthetic PDF fixture remains hash-only without reading BX25-08")

    # Actual archival scanner integration: whole coupon in joined XPS glyph runs.
    from h17_k04_binary_window_intake import scan_member
    expected_component = bytes(a ^ b for a, b in zip(coupon, MASK))
    source_result = scan_member(
        "synthetic.xps", source, 0, [0, 16 * 1024 * 1024, 0, 100],
        hashlib.sha256(expected_component).digest(), MASK, 1, 8 * 1024 * 1024, 3
    )
    assert any(
        item["kind"] == "payload_xor_route_mask"
        and item["component_hex"] == expected_component.hex().upper()
        and "xps-page-1-joined" in item["source"]
        for item in source_result["hits"]
    ), source_result["hits"]
    print("PASS: K04 native archive scanner recovers a planted whole XPS coupon")

    # An authorized profile scan can check the exact original K08 HMAC rule.
    from h17_profile_k08_phrase_scan import scan_inventory
    import json
    import tempfile
    with tempfile.TemporaryDirectory() as folder:
        source_root = Path(folder) / "source"
        source_root.mkdir()
        original = source_root / "synthetic.xps"
        original.write_bytes(source)
        manifest = Path(folder) / "inventory.json"
        manifest.write_text(json.dumps({
            "schema": "h17-profile-inventory/v1",
            "source_root": str(source_root),
            "files": [{
                "path": "synthetic.xps",
                "size": len(source),
                "sha256": original_hash,
                "categories": ["printer"],
            }],
        }), encoding="utf-8")
        report = scan_inventory(
            manifest, NONCE, hashlib.sha256(expected_k08).digest(),
            max_phrase_words=16, max_file_bytes=8 * 1024 * 1024,
            max_total_bytes=16 * 1024 * 1024
        )
        assert any("xps-page-2-joined" in hit["source"] for hit in report["hits"]), report["hits"]
        assert original.read_bytes() == source
    print("PASS: K08 profile phrase scanner recovers planted final caption; source unchanged")

    open_ns = "http://schemas.openxps.org/oxps/v1.0"
    open_page = f'<FixedPage xmlns="{open_ns}"><Glyphs UnicodeString="watch &amp; water"/></FixedPage>'.encode()
    assert ("xps-page-1-joined", b"watch & water") in list(extract_xps_text(package([open_page])))
    print("PASS: ECMA OpenXPS namespace and escaped UnicodeString")

    assert list(extract_xps_text(package([page("abc")], opc=False))) == []
    print("PASS: reject ordinary ZIP lacking OPC [Content_Types].xml")
    assert list(extract_xps_text(package([b'<FixedPage><Glyphs UnicodeString="x"/></FixedPage>']))) == []
    print("PASS: reject fake XML FixedPage without XPS namespace")
    assert list(extract_xps_text(package([b'<FixedPage xmlns="'+NS.encode()+b'"><Glyphs UnicodeString="x">']))) == []
    print("PASS: skip truncated XML")
    assert list(extract_xps_text(package([b'<FixedPage xmlns="'+NS.encode()+b'"><!DOCTYPE foo><Glyphs UnicodeString="x"/></FixedPage>']))) == []
    print("PASS: reject XML DTD")
    giant = package([page("X" * (4*1024*1024))])
    assert list(extract_xps_text(giant)) == []
    print("PASS: reject over-limit inflated page")
    wrapped = b"NATIVE-SPOOL-PREFIX" + source
    assert any(
        value.decode() == encoded
        for name, value in extract_xps_text(wrapped)
        if name == "xps-page-1-joined"
    )
    wrapped_result = scan_member(
        "synthetic.spl", wrapped, 0, [0, 16 * 1024 * 1024, 0, 100],
        hashlib.sha256(expected_component).digest(), MASK, 1,
        8 * 1024 * 1024, 3
    )
    assert any(
        "xps-page-1-joined" in hit["source"]
        and hit["component_hex"] == expected_component.hex().upper()
        for hit in wrapped_result["hits"]
    ), wrapped_result["hits"]
    print("PASS: prefix-wrapped spool package reaches original K04 acceptance")

    assert list(extract_xps_text(b"not an xps")) == []
    print("PASS: reject nonpackage input")


if __name__ == "__main__":
    test()
