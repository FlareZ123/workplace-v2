"""H-17 SFT: invert RomuDuo and RomuDuoJr from one intact 16-byte packet.

Original printer evidence pinned by SHA256. The disputed ESC-N ACK2 is excluded.
Three independent complete historical printer holdouts and authentic synthetic
controls. Runs with Python 3 standard library, on repository or attached ZIP.
"""
from __future__ import annotations
import hashlib
import pathlib
import zipfile

M = (1 << 64) - 1
C = 15241094284759029579
C_INV = pow(C, -1, 1 << 64)
SOURCE_SHA = "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"


def rotl(x: int, bits: int) -> int:
    return ((x << bits) | (x >> (64 - bits))) & M


def step(x: int, y: int, model: str) -> tuple[int, int]:
    xn = C * y & M
    if model == "RomuDuoJr":
        return xn, rotl((y - x) & M, 27)
    return xn, (rotl(y, 36) + rotl(y, 15) - x) & M


def words(payload: bytes, endian: str, reverse: bool) -> list[int]:
    seq = [int.from_bytes(payload[i : i + 8], endian) for i in (0, 8)]
    return seq[::-1] if reverse else seq


def serialize(seq: list[int], endian: str, reverse: bool) -> bytes:
    return b"".join(v.to_bytes(8, endian) for v in (seq[::-1] if reverse else seq))


def after_first(payload: bytes, model: str, endian: str, reverse: bool) -> tuple[int, int]:
    x0, x1 = words(payload, endian, reverse)
    y0 = x1 * C_INV & M
    x, y = step(x0, y0, model)
    assert x == x1
    return step(x, y, model)


def scan(first: bytes, withheld: bytes, model: str, endian: str, reverse: bool,
         max_gap: int) -> tuple[int, list[int]]:
    x, y = after_first(first, model, endian, reverse)
    left, right = words(withheld, endian, reverse)
    first_word_hits = 0
    exact_gap_hits = []
    for gap in range(max_gap + 1):
        if x == left:
            first_word_hits += 1
            nx, _ = step(x, y, model)
            if nx == right:
                exact_gap_hits.append(gap)
        x, y = step(x, y, model)
    return first_word_hits, exact_gap_hits


def load_source() -> dict[str, tuple[dict[str, str], bytes]]:
    root = pathlib.Path(__file__).resolve().parents[2]
    source = root / "resources/evidence/print/spool-reconstruction.log"
    if source.exists():
        raw = source.read_bytes()
    else:
        archive = pathlib.Path("/mnt/data/h17-archive-dump.zip")
        with zipfile.ZipFile(archive) as z:
            raw = z.read("evidence/print/spool-reconstruction.log")
    assert hashlib.sha256(raw).hexdigest() == SOURCE_SHA
    rows = {}
    retained = 0
    for line in raw.decode().splitlines():
        if "JOB=" not in line:
            continue
        parts = dict(t.split("=", 1) for t in line.split() if "=" in t)
        if parts["JOB"] == "PS-261003-0417" and parts["ATTEMPT"] == "2":
            continue  # selected physical/copy-stage row excluded before fit
        retained += 1
        key = parts["JOB"].split("-")[-1] + "#" + parts["ATTEMPT"]
        rows[key] = parts, bytes.fromhex(parts["PAYLOAD"])
    assert retained == 132
    for key in ("0407#1", "0416#1", "0420#2"):
        p = rows[key][0]
        assert p["CLASS"] == "RECOVER" and p["DEST"] == "bench"
    return rows


def plant(model: str, endian: str, reverse: bool) -> None:
    x, y = 0x3243F6A8885A308D, 0x13198A2E03707344
    original = []
    for _ in range(2):
        original.append(x)
        x, y = step(x, y, model)
    for _ in range(17):
        x, y = step(x, y, model)
    future = []
    for _ in range(2):
        future.append(x)
        x, y = step(x, y, model)
    n, gaps = scan(serialize(original, endian, reverse),
                   serialize(future, endian, reverse), model, endian, reverse, 23)
    assert (n, gaps) == (1, [17])


def main() -> None:
    rows = load_source()
    pairs = [
        ("0300#1", "0301#1", "ordinary-next"),
        ("0407#1", "0416#1", "same-role-early"),
        ("0416#1", "0420#2", "same-role-selected-bracket"),
    ]
    for model in ("RomuDuoJr", "RomuDuo"):
        for endian in ("little", "big"):
            for reverse in (False, True):
                plant(model, endian, reverse)
                for a, b, role in pairs:
                    n, gaps = scan(rows[a][1], rows[b][1], model, endian,
                                   reverse, 1_000_000)
                    print(f"ORIGINAL model={model} endian={endian} reverse={reverse} "
                          f"pair={role} gaps=1000001 first64_hits={n} full128_hits={len(gaps)}")
                    assert not gaps
    print("PLANTED=8/8 PASS; ORIGINAL=24/24 full-coupon holdouts 0 matches; "
          "ESC-N selected ACK2 excluded; no K04 target consulted")


if __name__ == "__main__":
    main()
