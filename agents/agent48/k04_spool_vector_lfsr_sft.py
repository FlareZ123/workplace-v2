"""H17 printer source-only shared word-vector recurrence, using original ZIP.

Tests an arbitrary unknown GF(2) polynomial whose coefficients XOR prior
32-bit output words. The copied selected ACK2 is excluded from fitting.
"""
from __future__ import annotations
import argparse
import hashlib
import random
import re
import zipfile

SPOOL = "evidence/print/spool-reconstruction.log"
SHA = "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"

def source_packets(z: zipfile.ZipFile) -> list[bytes]:
    raw = z.read(SPOOL)
    assert hashlib.sha256(raw).hexdigest() == SHA
    rows = {}
    for line in raw.decode().splitlines():
        job = re.search(r"JOB=PS-261003-(\d+)", line)
        payload = re.search(r"PAYLOAD=([A-F0-9]{32})", line)
        if not job or not payload:
            continue
        n = int(job.group(1))
        if 300 <= n <= 427 and "STATE=ACK" in line and "ATTEMPT=1" in line:
            rows[n] = bytes.fromhex(payload.group(1))
    assert sorted(rows) == list(range(300, 428))
    return [rows[i] for i in sorted(rows)]

def word_stream(packets: list[bytes], endian: str, reverse: bool) -> list[int]:
    out = []
    for p in packets:
        w = [int.from_bytes(p[i:i + 4], endian) for i in (0, 4, 8, 12)]
        if reverse:
            w.reverse()
        out.extend(w)
    return out

def fit(ws: list[int], degree: int, train: int) -> tuple[int | None, int, int]:
    """Gaussian elimination on 32 lanes; high coefficient is the pivot."""
    basis: dict[int, int] = {}
    low_mask = (1 << degree) - 1
    for i in range(degree, train):
        window = ws[i - degree:i][::-1]
        for bit in range(32):
            x = sum(((w >> bit) & 1) << j for j, w in enumerate(window))
            row = x | (((ws[i] >> bit) & 1) << degree)
            while row:
                left = row & low_mask
                if not left:
                    return None, len(basis), i
                pivot = left.bit_length() - 1
                if pivot not in basis:
                    basis[pivot] = row
                    break
                row ^= basis[pivot]
    solution = 0
    for pivot in sorted(basis):
        row = basis[pivot]
        rhs = (row >> degree) & 1
        lower = row & ((1 << pivot) - 1)
        if rhs ^ ((lower & solution).bit_count() & 1):
            solution |= 1 << pivot
    return solution, len(basis), train

def check_holdout(ws: list[int], degree: int, coeff: int, train: int) -> tuple[int, int]:
    predicted = list(ws[:train])
    hits = 0
    for i in range(train, len(ws)):
        value = 0
        for j in range(degree):
            if (coeff >> j) & 1:
                value ^= predicted[i - j - 1]
        predicted.append(value)
        hits += value == ws[i]
    return hits, len(ws) - train

def synthetic_control() -> None:
    rng = random.Random(1987)
    degree = 128
    poly = 1 | (1 << 17) | (1 << 59) | (1 << 96) | (1 << 127)
    ws = [rng.getrandbits(32) for _ in range(degree)]
    for i in range(degree, 512):
        word = 0
        for j in range(degree):
            if (poly >> j) & 1:
                word ^= ws[i - j - 1]
        ws.append(word)
    fitted, rank, _ = fit(ws, degree, 448)
    assert fitted is not None
    good, total = check_holdout(ws, degree, fitted, 448)
    assert (good, total) == (64, 64)
    print(f"SYNTHETIC degree=128 rank={rank} holdout={good}/{total}: PASS")

def main(zip_path: str) -> None:
    synthetic_control()
    with zipfile.ZipFile(zip_path) as z:
        packets = source_packets(z)
    print(f"ORIGINAL intact packets={len(packets)}; selected ACK2 excluded")
    for endian in ("big", "little"):
        for reverse in (False, True):
            ws = word_stream(packets, endian, reverse)
            for degree in (128, 256, 384, 434, 496):
                train = 448 if degree < 448 else 512
                fitted, rank, where = fit(ws, degree, train)
                tag = f"{endian}, reverse={reverse}, degree={degree}"
                if fitted is None:
                    print(f"ORIGINAL {tag}: INCOMPATIBLE rank={rank} first_word={where}")
                else:
                    good, total = check_holdout(ws, degree, fitted, train)
                    print(f"ORIGINAL {tag}: holdout={good}/{total}")
                    if good == total and total:
                        print("SOURCE PREDICTION: investigate selected-target stage")


def conditional_role_sources(zip_path: str) -> None:
    """Test independent linear emitters selected by original CLASS/DEST labels."""
    import collections
    with zipfile.ZipFile(zip_path) as z:
        raw = z.read(SPOOL)
    assert hashlib.sha256(raw).hexdigest() == SHA
    groups = collections.defaultdict(list)
    for line in raw.decode().splitlines():
        job = re.search(r"JOB=PS-261003-(\\d+)", line)
        payload = re.search(r"PAYLOAD=([A-F0-9]{32})", line)
        cls = re.search(r"CLASS=(\\w+)", line)
        dest = re.search(r"DEST=(\\w+)", line)
        if not all((job, payload, cls, dest)):
            continue
        if not (300 <= int(job.group(1)) <= 427 and "STATE=ACK" in line and "ATTEMPT=1" in line):
            continue
        p = bytes.fromhex(payload.group(1))
        c, d = cls.group(1), dest.group(1)
        for key in [("CLASS", c), ("DEST", d), ("CLASS_DEST", c + "|" + d)]:
            groups[key].append(p)
    evaluated, compatible = 0, 0
    for key, packets in groups.items():
        assert len(packets) >= 11
        fits = []
        for endian in ("big", "little"):
            for reverse in (False, True):
                ws = word_stream(packets, endian, reverse)
                train = len(ws) - 8
                for degree in (8, 16, 24, 32, 48, 64, 96, 128):
                    if degree >= train:
                        continue
                    evaluated += 1
                    coeff, rank, first_failure = fit(ws, degree, train)
                    if coeff is not None:
                        good, total = check_holdout(ws, degree, coeff, train)
                        fits.append((endian, reverse, degree, good, total))
                        if good == total:
                            compatible += 1
        print(f"CONDITIONAL {key} packets={len(packets)} fitted={fits}")
    assert len(groups) == 15
    print(f"CONDITIONAL tested={evaluated} full_source_holdout_passes={compatible}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("archive_zip")
    archive_zip = parser.parse_args().archive_zip
    main(archive_zip)
    conditional_role_sources(archive_zip)
