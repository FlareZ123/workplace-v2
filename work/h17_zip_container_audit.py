"""Read-only H-17 ZIP container audit; Python 3 standard library.

Usage: python work/h17_zip_container_audit.py /path/to/h17-archive-dump.zip
Checks ordinary ZIP framing/headers/descriptors/streams, not steganography.
"""
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
import hashlib
import struct
import sys
import zipfile
import zlib


def fields(value):
    entries = []
    offset = 0
    while offset < len(value):
        assert offset + 4 <= len(value)
        tag, size = struct.unpack_from("<HH", value, offset)
        offset += 4
        assert offset + size <= len(value)
        entries.append((tag, value[offset:offset + size]))
        offset += size
    return entries


def audit(path):
    data = Path(path).read_bytes()
    counts = Counter()
    stamps = Counter()
    with zipfile.ZipFile(path) as archive:
        members = archive.infolist()
        assert archive.testzip() is None
        assert not archive.comment
        assert len({x.filename for x in members}) == len(members)
        offset = 0
        for member in sorted(members, key=lambda x: x.header_offset):
            assert member.header_offset == offset
            assert data[offset:offset + 4] == b"PK\x03\x04"
            flags, method = struct.unpack_from("<HH", data, offset + 6)
            name_len, extra_len = struct.unpack_from("<HH", data, offset + 26)
            name = data[offset + 30:offset + 30 + name_len].decode("utf-8")
            extra = data[offset + 30 + name_len:offset + 30 + name_len + extra_len]
            assert name == member.filename and method == member.compress_type
            assert flags == member.flag_bits and flags in (0, 8)
            assert not member.comment
            parts = fields(extra)
            assert {tag for tag, _ in parts} == {0x5455, 0x7875}
            for tag, value in parts:
                if tag == 0x7875:
                    assert value == bytes.fromhex("0104000000000400000000")
                else:
                    assert len(value) == 13 and value[0] == 7
                    for pos, label in ((1, "mtime"), (5, "atime"), (9, "ctime")):
                        t = int.from_bytes(value[pos:pos + 4], "little")
                        stamps[(label, datetime.fromtimestamp(t, timezone.utc).isoformat())] += 1
            counts["local_extra_fields"] += len(parts)
            offset += 30 + name_len + extra_len
            compressed = data[offset:offset + member.compress_size]
            original = archive.read(member.filename)
            if method == zipfile.ZIP_DEFLATED:
                decoder = zlib.decompressobj(-zlib.MAX_WBITS)
                result = decoder.decompress(compressed) + decoder.flush()
                assert decoder.eof and not decoder.unused_data and not decoder.unconsumed_tail
                assert result == original
                counts["deflated"] += 1
            else:
                assert method == zipfile.ZIP_STORED and compressed == original
                counts["stored"] += 1
            offset += member.compress_size
            if flags & 8:
                assert data[offset:offset + 4] == b"PK\x07\x08"
                assert struct.unpack_from("<III", data, offset + 4) == (
                    member.CRC, member.compress_size, member.file_size)
                offset += 16
                counts["data_descriptors"] += 1
            counts["directories" if member.is_dir() else "files"] += 1
        assert offset == archive.start_dir
        for member in members:
            assert data[offset:offset + 4] == b"PK\x01\x02"
            name_len, extra_len, comment_len = struct.unpack_from("<HHH", data, offset + 28)
            name = data[offset + 46:offset + 46 + name_len].decode("utf-8")
            extra = data[offset + 46 + name_len:offset + 46 + name_len + extra_len]
            assert name == member.filename and comment_len == 0
            assert fields(extra) == fields(member.extra)
            assert {tag for tag, _ in fields(extra)} == {0x5455, 0x7875}
            for tag, value in fields(extra):
                if tag == 0x5455:
                    assert len(value) == 5 and value[0] == 1
                else:
                    assert value == bytes.fromhex("0104000000000400000000")
            offset += 46 + name_len + extra_len
        assert data[offset:offset + 4] == b"PK\x05\x06"
        assert struct.unpack_from("<HH", data, offset + 8) == (len(members), len(members))
        assert struct.unpack_from("<H", data, offset + 20)[0] == 0
        assert offset + 22 == len(data)
    print("zip_sha256:", hashlib.sha256(data).hexdigest())
    print("entries/files/dirs:", len(members), counts["files"], counts["directories"])
    print("deflated/stored/descriptors:", counts["deflated"], counts["stored"], counts["data_descriptors"])
    print("local_extra_fields:", counts["local_extra_fields"])
    print("timestamp_fields:", dict(stamps))
    print("unaccounted_bytes: 0, unused_deflate_bytes: 0, comments: 0, duplicate_names: 0")


if __name__ == "__main__":
    audit(sys.argv[1])
