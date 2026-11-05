"""Read-only original-source SFT for ZIP representation and spool join keys.

Usage: python agent13_zip_and_spool_source_boundary_sft.py h17-archive-dump.zip
Standard library only. Never modifies original evidence or acceptance.
"""
import collections
import hashlib
import io
import re
import struct
import sys
import zipfile
import zlib
from pathlib import Path

ZIP_SHA256 = "e778552c555fac652e24fd09e1c4f31bd066b4686e624b91f6e94e1d64342bf7"
SPOOL_SHA256 = "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"


def zip_representation(data):
    assert hashlib.sha256(data).hexdigest() == ZIP_SHA256
    with zipfile.ZipFile(io.BytesIO(data)) as archive:
        members = archive.infolist()
        assert len(members) == 56
        local_extras = collections.Counter()
        deflated = descriptors = 0
        for index, member in enumerate(members):
            offset = member.header_offset
            header = struct.unpack_from("<IHHHHHIIIHH", data, offset)
            assert header[0] == 0x04034B50
            name_size, extra_size = header[-2:]
            name = data[offset + 30:offset + 30 + name_size]
            assert name.decode("utf-8") == member.filename
            local = data[offset + 30 + name_size:offset + 30 + name_size + extra_size]
            assert extra_size == 32 and len(member.extra) == 24
            local_extras[local] += 1
            position = offset + 30 + name_size + extra_size
            compressed = data[position:position + member.compress_size]
            end = position + member.compress_size
            if member.compress_type == zipfile.ZIP_DEFLATED:
                compressor = zlib.compressobj(6, zlib.DEFLATED, -15)
                assert compressor.compress(archive.read(member)) + compressor.flush() == compressed
                deflated += 1
                signature, crc, packed_len, raw_len = struct.unpack_from("<IIII", data, end)
                assert signature == 0x08074B50
                assert (crc, packed_len, raw_len) == (member.CRC, member.compress_size, member.file_size)
                end += 16
                descriptors += 1
            else:
                assert member.is_dir() and member.compress_type == zipfile.ZIP_STORED and not compressed
            next_offset = members[index + 1].header_offset if index + 1 < len(members) else archive.start_dir
            assert end == next_offset
        assert (deflated, descriptors, len(local_extras)) == (46, 46, 6)
        assert archive.comment == b"" and all(member.comment == b"" for member in members)
        assert data.rfind(b"PK\x05\x06") == len(data) - 22
        print("ZIP: 56 contiguous entries, 46 byte-exact zlib-6 raw-deflate streams,")
        print("     46 exact descriptors, 6 local timestamp-extra variants; no ZIP comments or tail")


def spool_collisions(data):
    assert hashlib.sha256(data).hexdigest() == SPOOL_SHA256
    records = []
    for line in data.decode("ascii").splitlines():
        if line.startswith("2026-"):
            fields = dict(re.findall(r"([A-Z]+)=([^ ]+)", line))
            fields["UTC"] = line.split()[0]
            records.append(fields)
    assert len(records) == 133
    expectations = {
        ("JOB",): (2, 4),
        ("JOB", "ATTEMPT"): (1, 1),
        ("JOB", "CLASS", "ATTEMPT"): (0, 0),
        ("JOB", "STATE", "ATTEMPT"): (0, 0),
    }
    for key, expected in expectations.items():
        bins = collections.defaultdict(list)
        for record in records:
            bins[tuple(record[field] for field in key)].append(record)
        duplicates = [group for group in bins.values() if len(group) > 1]
        actual = (len(duplicates), sum(len(group) - 1 for group in duplicates))
        assert actual == expected
        print("SPOOL:", key, "collision groups", actual[0], "extra rows", actual[1])
    selected = [record for record in records if
                (record["JOB"], record["CLASS"], record["ATTEMPT"], record["STATE"]) ==
                ("PS-261003-0417", "RECOVER", "2", "ACK")]
    assert len(selected) == 1
    assert selected[0]["PAYLOAD"] == "A9A9DC5731A5E2AE879C47215C2559D5"
    key = lambda record: (record["JOB"], record["ATTEMPT"])
    assert sum(key(r) == key(selected[0]) for r in records) == 1
    assert sum(key(r) == key(selected[0]) for r in records + [dict(selected[0])]) == 2
    print("SPOOL: selected 0417 RECOVER ACK2 uniquely keyed by JOB+ATTEMPT;")
    print("       synthetic selected-row duplicate detected correctly")


def main(path):
    data = path.read_bytes()
    zip_representation(data)
    with zipfile.ZipFile(path) as archive:
        spool_collisions(archive.read("evidence/print/spool-reconstruction.log"))
    print("SFT PASS; no original missing components recovered")


if __name__ == "__main__":
    main(Path(sys.argv[1]) if len(sys.argv) > 1 else Path("h17-archive-dump.zip"))
