"""Positive-control SFT for the read-only H-17 ZIP container auditor.

Pass the original uploaded H-17 ZIP path. The only modifications are to
separate disposable copies inside a temporary directory.
"""
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path
from tempfile import TemporaryDirectory
import hashlib
import struct
import sys
import zipfile

from h17_zip_container_audit import audit


def main(original_path: Path) -> None:
    raw = original_path.read_bytes()
    with zipfile.ZipFile(original_path) as archive:
        first = archive.infolist()[0]
        first_start = first.header_offset
        central_start = archive.start_dir
        assert first.flag_bits & 8
        assert first.compress_type == zipfile.ZIP_DEFLATED
        assert archive.testzip() is None

    filename_length, extra_length = struct.unpack_from('<HH', raw, first_start + 26)
    extra_start = first_start + 30 + filename_length
    assert raw[extra_start:extra_start + 4] == bytes.fromhex('75780b00')
    assert raw[extra_start + 15:extra_start + 19] == bytes.fromhex('55540d00')
    first_descriptor = extra_start + extra_length + first.compress_size
    assert raw[first_descriptor:first_descriptor + 4] == b'PK\x07\x08'
    assert raw[central_start:central_start + 4] == b'PK\x01\x02'

    with redirect_stdout(StringIO()) as original_log:
        audit(original_path)
    print('ORIGINAL PASS', len(raw), hashlib.sha256(raw).hexdigest())
    print('ORIGINAL LOG TAIL', original_log.getvalue().splitlines()[-1])

    mutations = {
        'nonzero_trailer': (None, b'K08_FALSE_TRAILER'),
        'local_uid': (extra_start + 7, None),
        'local_ut_mtime': (extra_start + 15 + 5, None),
        'local_dos_time': (first_start + 10, None),
        'local_crc_placeholder': (first_start + 14, None),
        'data_descriptor_signature': (first_descriptor, None),
        'central_creator_version': (central_start + 4, None),
        'central_permission_bits': (central_start + 38, None),
    }
    with TemporaryDirectory(prefix='h17_zip_audit_') as scratch:
        for label, (position, trailer) in mutations.items():
            modified = bytearray(raw)
            if position is None:
                modified.extend(trailer)
            else:
                modified[position] ^= 1
            copy = Path(scratch) / (label + '.zip')
            copy.write_bytes(modified)
            try:
                with redirect_stdout(StringIO()):
                    audit(copy)
            except (AssertionError, zipfile.BadZipFile, EOFError, struct.error) as error:
                print('CONTROL DETECTED', label, type(error).__name__, str(error)[:140])
            else:
                raise AssertionError('Undetected tamper: ' + label)
    assert original_path.read_bytes() == raw
    print('PASS: 8/8 mutated copies rejected, original unchanged.')


if __name__ == '__main__':
    main(Path(sys.argv[1]))
