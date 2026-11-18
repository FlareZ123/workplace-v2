"""Single-file bounded XPS/OXPS text extractor regression."""
import hashlib
import hmac
import io
import sys
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from h17_xps_text import extract_xps_text

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
    assert list(extract_xps_text(b"not an xps")) == []
    print("PASS: reject nonpackage input")


if __name__ == "__main__":
    test()
