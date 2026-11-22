"""Read-only original 128-packet low-bit gate for xoshiro128+ 32bit fullword emitter."""
import hashlib
import json
import re
import sys
from pathlib import Path
from zipfile import ZipFile

SPOOL_SHA = "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"
if len(sys.argv) > 1:
    with ZipFile(sys.argv[1]) as archive:
        raw = archive.read("evidence/print/spool-reconstruction.log")
else:
    raw = (Path(__file__).resolve().parents[2]
           / "resources/evidence/print/spool-reconstruction.log").read_bytes()
assert hashlib.sha256(raw).hexdigest() == SPOOL_SHA
packets = {}
for line in raw.decode("ascii").splitlines():
    match = re.search(
        r"JOB=PS-261003-(\d+) ATTEMPT=1 STATE=ACK .*?PAYLOAD=([0-9A-F]{32})",
        line,
    )
    if match and 300 <= int(match.group(1)) <= 427:
        packets[int(match.group(1))] = bytes.fromhex(match.group(2))
assert len(packets) == 128
original = [packets[i] for i in range(300, 428)]
M32 = (1 << 32) - 1


def symbolic_step(state):
    a, b, c, d = state
    t = [0] * 9 + b[:23]
    c = [c[i] ^ a[i] for i in range(32)]
    d = [d[i] ^ b[i] for i in range(32)]
    b = [b[i] ^ c[i] for i in range(32)]
    a = [a[i] ^ d[i] for i in range(32)]
    c = [c[i] ^ t[i] for i in range(32)]
    d = [d[(i - 11) % 32] for i in range(32)]
    return a, b, c, d


def source_consistency(packet_bits, gap):
    state = tuple([
        1 << (j * 32 + i) for i in range(32)
    ] for j in range(4))
    basis = {}
    train_rank = 0
    first_conflict = None
    for packet_idx, word_bits in enumerate(packet_bits):
        if packet_idx == 32:
            train_rank = len(basis)
        for bit in word_bits:
            row = state[0][0] ^ state[3][0]
            rhs = bit
            while row:
                index = row.bit_length() - 1
                if index not in basis:
                    basis[index] = row, rhs
                    break
                prior, value = basis[index]
                row ^= prior
                rhs ^= value
            else:
                if rhs and first_conflict is None:
                    first_conflict = packet_idx
            state = symbolic_step(state)
        for _ in range(gap):
            state = symbolic_step(state)
    return len(basis), train_rank, first_conflict


def forward(state):
    a, b, c, d = state
    value = (a + d) & M32
    temp = (b << 9) & M32
    c ^= a
    d ^= b
    b ^= c
    a ^= d
    c ^= temp
    d = ((d << 11) | (d >> 21)) & M32
    return value, (a, b, c, d)


def unpack_bits(payload, endian, reversed_words):
    words = [int.from_bytes(payload[j:j+4], endian) for j in range(0, 16, 4)]
    return [value & 1 for value in (words[::-1] if reversed_words else words)]


# Full 128-packet synthetic controls for the exact same emission/serializer family.
for gap, endian, reversed_words in [(3, "little", False), (9, "big", True)]:
    state = (0x12345678, 0x9ABCDEF0, 0xFEDCBA98, 0x76543210)
    bits = []
    for _ in range(128):
        outputs = []
        for _ in range(4):
            value, state = forward(state)
            outputs.append(value)
        words = outputs[::-1] if reversed_words else outputs
        encoded = b"".join(word.to_bytes(4, endian) for word in words)
        bits.append(unpack_bits(encoded, endian, reversed_words))
        for _ in range(gap):
            _, state = forward(state)
    rank, training_rank, conflict = source_consistency(bits, gap)
    assert rank == 128 and conflict is None
    print("PLANTED_PASS", gap, endian, reversed_words, rank, training_rank)

results = []
for endian in ("little", "big"):
    for reversed_words in (False, True):
        bits = [unpack_bits(p, endian, reversed_words) for p in original]
        for gap in range(17):
            rank, training_rank, conflict = source_consistency(bits, gap)
            results.append((endian, reversed_words, gap,
                            rank, training_rank, conflict))
assert len(results) == 68
assert all(conflict is not None for *_, conflict in results)
print(json.dumps({
    "original_models_checked": len(results),
    "original_source_compatible": 0,
    "first_conflict_latest_row_0based": max(r[-1] for r in results),
    "first_conflict_earliest_row_0based": min(r[-1] for r in results),
    "max_rank": max(r[-3] for r in results),
}, sort_keys=True))
