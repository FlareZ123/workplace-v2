"""Source-only H-17 p951 AX chunk-batch jump target-independence certificate.

Reproduce from workplace-v2 checkout with Python 3 and g++:
python agents/agent31/k04_ax_batch_jump_sft.py

Uses no selected printer ACK or original K04/K08 commitment. This is a
conditional shared-MT source model, not a historical producer assertion.
"""
import hashlib
import json
import os
import struct
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "agents" / "agent49"))
from k04_p951_symbolic_basis import Basis, get, source, temper, untemper

NODE50 = {
    7: -810, 9: -793, 12: -775, 13: -769, 14: -759,
    24: -683, 25: -677, 41: -568, 43: -552, 44: -545,
    45: -540, 61: -417, 63: -397, 64: -390, 70: -339,
}

def sha_check(path, expected):
    data = path.read_bytes()
    assert hashlib.sha256(data).hexdigest() == expected, str(path)
    return data

def source_basis():
    root = ROOT / "resources"
    base, states = source(root)
    assert base.rank == 15365
    basis = Basis()
    basis.rows = dict(base.rows)
    basis.rank = base.rank

    data = sha_check(
        root / "evidence/transfers/transfer-audit.jsonl",
        "32970ad4431a9d610cc12dcca2813f39dd8fd2e396f9e748dc94b5932cb69adf",
    )
    all_rows = [json.loads(line) for line in data.splitlines()]
    ax = sorted(
        (item for item in all_rows
         if item.get("kind") == "CHUNK" and item.get("transfer") == "AX-7778"),
        key=lambda item: (item["seq"], item["attempt"]),
    )
    assert len(ax) == 16
    for i, row in enumerate(ax):
        value = int.from_bytes(bytes.fromhex(row["checkpoint"]), "little")
        for bit, expr in enumerate(temper(get(states, -157 + i))[16:]):
            basis.insert(expr, (value >> bit) & 1)
    assert basis.rank == 15495

    rec = sha_check(
        root / "evidence/recorder/trip-recorder.raw",
        "5ebc6204ed773102237dd287772de96d19740e163b49b4075537d937888657ba",
    )
    assert rec[:8] == b"TRP2DUMP" and len(rec) == 16 + 88 * 24
    counts = {"node49": 0, "node50": 0}
    for i in range(88):
        packet = rec[16 + 24 * i:16 + 24 * (i + 1)]
        _, node, _, latch, seq = struct.unpack_from("<IHBBI", packet)
        stage = None
        if node == 49 and 200 <= seq <= 203:
            stage = -324 + 3 * latch
        elif node == 49 and 900 <= seq <= 903:
            stage = -323 + 3 * latch  # CRC-invalid, conditional raw source words.
        elif node == 49 and 990 <= seq <= 993:
            stage = -322 + 3 * latch
        elif node == 50:
            stage = NODE50.get(seq)
        if stage is None:
            continue
        native = untemper(int.from_bytes(packet[12:16], "little"))
        for bit, expr in enumerate(get(states, stage)):
            basis.insert(expr, (native >> bit) & 1)
        counts["node49" if node == 49 else "node50"] += 1
    assert counts == {"node49": 12, "node50": 15}, counts
    assert basis.rank == 15632, basis.rank
    return basis

def write_matrix(path, basis):
    with path.open("wb") as out:
        out.write(struct.pack("<II", basis.rank, 624 * 32))
        for pivot, (equation, rhs) in sorted(basis.rows.items()):
            # RHS intentionally omitted: this is the homogeneous source kernel.
            out.write(struct.pack("<I", pivot))
            out.write(equation.to_bytes(624 * 4, "little"))
        out.flush()
        os.fsync(out.fileno())
    assert path.stat().st_size == 8 + basis.rank * 2500

def rank(samples, data, offset, width):
    pivot_rows = {}
    for i in range(samples):
        value = int.from_bytes(data[i * 112 + offset:i * 112 + offset + width], "little")
        while value:
            pivot = value.bit_length() - 1
            if pivot not in pivot_rows:
                pivot_rows[pivot] = value
                break
            value ^= pivot_rows[pivot]
    return len(pivot_rows)

def main():
    basis = source_basis()
    with tempfile.TemporaryDirectory(prefix="h17-ax-long-jump-") as temporary:
        directory = Path(temporary)
        matrix = directory / "basis.bin"
        executable = directory / "projection"
        output = directory / "projected.bin"
        write_matrix(matrix, basis)
        subprocess.run([
            "g++", "-std=c++17", "-O3", "-mpopcnt",
            str(ROOT / "agents/agent31/k04_ax_batch_jump_rank.cpp"),
            "-o", str(executable),
        ], check=True)
        samples = 992
        subprocess.run([str(executable), str(matrix), str(output), str(samples)], check=True)
        data = output.read_bytes()
        assert len(data) == samples * 112
    ranks = {
        "K04_coupon_128": rank(samples, data, 0, 16),
        "AX_1MiB_jump_256": rank(samples, data, 16, 32),
        "AX_8MiB_jump_256": rank(samples, data, 48, 32),
        "AX_16MiB_jump_256": rank(samples, data, 80, 32),
        "AX_joint_768": rank(samples, data, 16, 96),
        "K04_plus_AX_joint_896": rank(samples, data, 0, 112),
    }
    assert ranks == {
        "K04_coupon_128": 128,
        "AX_1MiB_jump_256": 256,
        "AX_8MiB_jump_256": 256,
        "AX_16MiB_jump_256": 256,
        "AX_joint_768": 768,
        "K04_plus_AX_joint_896": 896,
    }, ranks
    print(json.dumps({
        "conditional_source_rank": basis.rank,
        "joint_source_free_dimension": 19968 - basis.rank,
        "homogeneous_states": samples,
        "native_AX7778_start": -157,
        "batch_jump_words": [1 << 18, 1 << 21, 1 << 22],
        "ranks": ranks,
        "original_K04_bits_recovered": 0,
        "historical_common_generator_proven": False,
        "combined_REC8_complete": False,
    }, sort_keys=True))

if __name__ == "__main__":
    main()
