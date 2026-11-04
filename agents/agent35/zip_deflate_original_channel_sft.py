"""Check whether the supplied H-17 ZIP contains noncanonical DEFLATE coding.

SFT: python zip_deflate_original_channel_sft.py h17-archive-dump.zip
Read-only. The original bundle SHA256 and all 46 compressed original members
are authenticated before evaluating byte-for-byte compression equality.
"""
import hashlib
import struct
import sys
import zipfile
import zlib
from pathlib import Path

BUNDLE_SHA256 = "e778552c555fac652e24fd09e1c4f31bd066b4686e624b91f6e94e1d64342bf7"
HEADER = struct.Struct("<IHHHHHIIIHH")


def check(archive: Path) -> None:
    assert hashlib.sha256(archive.read_bytes()).hexdigest() == BUNDLE_SHA256
    regular = 0
    directories = 0
    noncanonical = []
    with zipfile.ZipFile(archive) as zipped, archive.open("rb") as raw:
        for info in zipped.infolist():
            raw.seek(info.header_offset)
            header = raw.read(HEADER.size)
            magic, _, _, compression, _, _, _, _, _, name_len, extra_len = HEADER.unpack(header)
            assert magic == 0x04034B50
            assert compression == info.compress_type
            assert raw.read(name_len).decode("utf-8") == info.filename
            raw.read(extra_len)
            compressed = raw.read(info.compress_size)
            clear = zipped.read(info.filename)
            assert zlib.crc32(clear) == info.CRC
            if info.is_dir():
                assert compression == 0 and clear == compressed == b""
                directories += 1
                continue
            assert compression == 8
            packer = zlib.compressobj(level=6, method=zlib.DEFLATED, wbits=-15)
            canonical = packer.compress(clear) + packer.flush()
            if compressed != canonical:
                noncanonical.append(info.filename)
            regular += 1

        # Genuine counterexample: another valid DEFLATE encoding is distinguishable.
        sample_info = zipped.getinfo("evidence/print/spool-reconstruction.log")
        raw.seek(sample_info.header_offset)
        _, _, _, _, _, _, _, _, _, name_len, extra_len = HEADER.unpack(raw.read(HEADER.size))
        raw.read(name_len + extra_len)
        stored = raw.read(sample_info.compress_size)
        original = zipped.read(sample_info.filename)
        alternate = zlib.compressobj(level=1, method=zlib.DEFLATED, wbits=-15)
        different = alternate.compress(original) + alternate.flush()
        assert different != stored
        assert zlib.decompress(different, wbits=-15) == original

    assert regular == 46 and directories == 10 and not noncanonical
    print(f"PASS: 46/46 original DEFLATE streams identical to zlib-{zlib.ZLIB_VERSION} level 6")
    print("PASS: 10/10 directory entries are empty STORED objects")
    print("PASS: distinct but valid DEFLATE positive control is detected")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("Usage: python zip_deflate_original_channel_sft.py original.zip")
    check(Path(sys.argv[1]))
