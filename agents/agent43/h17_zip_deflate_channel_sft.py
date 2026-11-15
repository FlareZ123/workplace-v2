"""H-17 source ZIP DEFLATE-padding candidate search; no original file changes."""
import argparse
import hashlib
import json
import struct
import zipfile
import zlib
from pathlib import Path

EXPECTED_ZIP = 'e778552c555fac652e24fd09e1c4f31bd066b4686e624b91f6e94e1d64342bf7'
MASK = bytes.fromhex('8556C8CB6140A7F9A5123AC7571BEE1C')
TARGETS = {
    'K04': '930a52a1bab97ca2966332137c99e99298ea6182fb32ab63a3421dfb4fd8c9e0',
    'K08': '285eb6b4196d21eaf47e251449e61e0bce28749881ccc5a065ca733b0c3fd747',
}


def deflate_padding(stream: bytes, original: bytes) -> tuple[int, int]:
    assert zlib.decompress(stream, -15) == original
    slack = 0
    for bit in range(7, -1, -1):
        modified = stream[:-1] + bytes((stream[-1] ^ (1 << bit),))
        try:
            same = zlib.decompress(modified, -15) == original
        except zlib.error:
            same = False
        if not same:
            break
        slack += 1
    value = stream[-1] >> (8 - slack) if slack else 0
    if slack:
        synthetic = stream[:-1] + bytes((stream[-1] | (255 << (8 - slack) & 255),))
        assert zlib.decompress(synthetic, -15) == original
    return slack, value


def silent_interior_bits(stream: bytes, original: bytes) -> list[tuple[int, int, int]]:
    """Locate single-bit changes outside terminal padding that preserve raw decoded bytes."""
    silent = []
    for index in range(len(stream) - 1):
        for bit in range(8):
            altered = stream[:index] + bytes((stream[index] ^ (1 << bit),)) + stream[index + 1:]
            try:
                same = zlib.decompress(altered, -15) == original
            except zlib.error:
                same = False
            if same:
                silent.append((index, bit, (stream[index] >> bit) & 1))
    return silent


def candidate_blocks(lengths: list[int]):
    for reverse_entries in (False, True):
        ordered = lengths[::-1] if reverse_entries else lengths
        for reverse_bits in (False, True):
            bit_string = ''.join((f'{n:03b}'[::-1] if reverse_bits else f'{n:03b}') for n in ordered)
            for offset in range(len(bit_string) - 127):
                word = int(bit_string[offset:offset + 128], 2).to_bytes(16, 'big')
                for reverse_bytes in (False, True):
                    datum = word[::-1] if reverse_bytes else word
                    yield (reverse_entries, reverse_bits, offset, reverse_bytes, 'direct'), datum
                    yield (reverse_entries, reverse_bits, offset, reverse_bytes, 'xor-mask'), bytes(a ^ b for a, b in zip(datum, MASK))


def run(source: Path):
    binary = source.read_bytes()
    assert hashlib.sha256(binary).hexdigest() == EXPECTED_ZIP, 'Source ZIP SHA256 mismatch'
    lengths = []
    padding = []
    interior = []
    compressed_bits = 0
    stock_zlib_exact = 0
    with zipfile.ZipFile(source) as archive:
        for item in archive.infolist():
            if item.compress_type != zipfile.ZIP_DEFLATED:
                continue
            header = binary[item.header_offset:item.header_offset + 30]
            signature, *_fields, name_len, extra_len = struct.unpack('<IHHHHHIIIHH', header)
            assert signature == 0x04034B50
            start = item.header_offset + 30 + name_len + extra_len
            stream = binary[start:start + item.compress_size]
            assert len(stream) == item.compress_size
            original = archive.read(item)
            compressor = zlib.compressobj(6, zlib.DEFLATED, -15, 8, zlib.Z_DEFAULT_STRATEGY)
            if compressor.compress(original) + compressor.flush() == stream:
                stock_zlib_exact += 1
            count, value = deflate_padding(stream, original)
            compressed_bits += len(stream) * 8
            interior.extend((item.filename, *entry) for entry in silent_interior_bits(stream, original))
            lengths.append(count)
            padding.append(value)
    assert len(lengths) == 46 and sum(lengths) == 170
    assert all(v == 0 for v in padding)
    assert compressed_bits == 314288
    assert stock_zlib_exact == 46
    assert len(interior) == 17
    assert ''.join(str(entry[3]) for entry in interior) == '00000000111000010'

    # Independently planted 128-bit message, carried in 46 three-bit length symbols.
    plant = bytes.fromhex('00112233445566778899AABBCCDDEEFF')
    bits = ''.join(f'{b:08b}' for b in plant) + '0' * 10
    planted_lengths = [int(bits[i:i + 3], 2) for i in range(0, len(bits), 3)]
    planted = list(candidate_blocks(planted_lengths))
    assert any(candidate == plant for _layout, candidate in planted)
    assert any(hashlib.sha256(candidate).digest() == hashlib.sha256(plant).digest() for _layout, candidate in planted)

    trials = list(candidate_blocks(lengths))
    matches = [(layout, target, word.hex().upper()) for layout, word in trials
               for target, digest in TARGETS.items() if hashlib.sha256(word).hexdigest() == digest]
    assert len(trials) == 176 and not matches
    return {'source_sha256': EXPECTED_ZIP, 'deflate_members': len(lengths),
            'slack_bits': sum(lengths), 'nonzero_padding_members': sum(v != 0 for v in padding),
            'slack_bit_counts': lengths, 'compressed_bits': compressed_bits,
            'stock_zlib_level6_memlevel8_exact_members': stock_zlib_exact,
            'individually_decode_inert_interior_bits': interior,
            'length_channel_bits': len(lengths) * 3,
            'complete_candidate_layouts': len(trials),
            'full_sha256_target_checks': len(trials) * len(TARGETS),
            'original_commitment_hits': matches, 'synthetic_128bit_length_control': 'PASS'}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('archive', type=Path, help='Exact supplied h17-archive-dump.zip')
    print(json.dumps(run(parser.parse_args().archive), indent=2))
