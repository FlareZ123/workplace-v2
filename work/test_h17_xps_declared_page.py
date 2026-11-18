"""SFT: OPC FixedPage declarations and spatial glyph order reach both reducers.

Two synthetic targets are intentionally distinct from original H-17 commitments.
"""
import hashlib
import hmac
import io
import zipfile
from h17_xps_text import extract_xps_text, _spatial_texts

CT = 'http://schemas.openxmlformats.org/package/2006/content-types'
NS = 'http://schemas.microsoft.com/xps/2005/06'
MIME = 'application/vnd.ms-package.xps-fixedpage+xml'
MASK = bytes.fromhex('8556C8CB6140A7F9A5123AC7571BEE1C')
NONCE = bytes.fromhex('5F933DA6A1BD03C32DA5CBC25344F497')
COUPON = bytes.fromhex('102132435465768798A9BACBDCEDFE0F')
PHRASE = 'the water held the last light around the table'


def fixed_page(left, right):
    # XML order is deliberately right-to-left, while visual coordinates are left-to-right.
    return (f'<FixedPage xmlns="{NS}">'
            f'<Glyphs OriginX="400" OriginY="40" UnicodeString="{right}"/>'
            f'<Glyphs OriginX="10" OriginY="40" UnicodeString="{left}"/>'
            '</FixedPage>').encode('utf-8')


def package(declaration='override', reverse=False):
    parts = [('Documents/1/Pages/1.xml', fixed_page(COUPON.hex().upper()[:16], COUPON.hex().upper()[16:])),
             ('Documents/1/Pages/2.xml', fixed_page('the water held the ', 'last light around the table'))]
    if declaration == 'override':
        entries = ''.join(f'<Override PartName="/{name}" ContentType="{MIME}"/>' for name, _ in parts)
    elif declaration == 'default':
        entries = f'<Default Extension="xml" ContentType="{MIME}"/>'
    else:
        entries = '<Default Extension="xml" ContentType="application/xml"/>'
    manifest = f'<Types xmlns="{CT}">{entries}</Types>'
    out = io.BytesIO()
    with zipfile.ZipFile(out, 'w', compression=zipfile.ZIP_DEFLATED) as archive:
        archive.writestr('[Content_Types].xml', manifest)
        for name, page in parts:
            archive.writestr(name, page)
    data = out.getvalue()
    return (b'NATIVE-SPOOL-PREFIX' + data) if reverse else data


def test():
    expected = bytes(x ^ y for x, y in zip(COUPON, MASK))
    expected_k04 = hashlib.sha256(expected).digest()
    expected_k08 = hashlib.sha256(hmac.new(NONCE, PHRASE.encode(), hashlib.sha256).digest()[:16]).digest()
    for kind in ('override', 'default'):
        for wrapped in (False, True):
            data = package(kind, wrapped)
            before = hashlib.sha256(data).digest()
            streams = dict(extract_xps_text(data))
            actual_coupon = bytes.fromhex(streams['xps-page-1-spatial-joined'].decode())
            actual_k04 = bytes(x ^ y for x, y in zip(actual_coupon, MASK))
            assert hashlib.sha256(actual_k04).digest() == expected_k04
            phrase = streams['xps-page-2-spatial-joined'].decode()
            assert phrase == PHRASE
            actual_k08 = hmac.new(NONCE, phrase.encode(), hashlib.sha256).digest()[:16]
            assert hashlib.sha256(actual_k08).digest() == expected_k08
            assert hashlib.sha256(data).digest() == before
            print(f'PASS: {kind} OPC declaration wrapped={wrapped}, visual K04 and K08 synthetic complete candidates')
    assert not list(extract_xps_text(package('unsupported')))
    print('PASS: unrelated declared content types ignored')
    assert _spatial_texts(fixed_page('one', 'two').replace(b'OriginX="400"', b'OriginX="NaN"')) == []
    print('PASS: nonfinite position does not emit spatial candidate')


if __name__ == '__main__':
    test()
