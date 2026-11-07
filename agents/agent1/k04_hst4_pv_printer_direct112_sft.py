"""H-17 direct PV-to-printer-payload bridge test. Read-only single-file test.

Runs on Windows 11 with Python standard library. Selected 18:02 ACK2
excluded completely; only intact jobs 0300..0411 enter this test.
"""
from __future__ import annotations

import hashlib
import json
import re
import sys
import zipfile
from pathlib import Path

SPOOL_SHA = "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"
HST_SHA = "3787dbd6bab3930ea5293c25a995175161a1c0d7683daad29f498026e057639f"
ROOT = Path(__file__).resolve().parents[2]


def load_sources() -> tuple[bytes, bytes]:
    if len(sys.argv) == 2:
        with zipfile.ZipFile(sys.argv[1]) as archive:
            return (archive.read("evidence/print/spool-reconstruction.log"),
                    archive.read("evidence/telemetry/freeze-export.jsonl"))
    base = ROOT / "resources" / "evidence"
    return ((base / "print" / "spool-reconstruction.log").read_bytes(),
            (base / "telemetry" / "freeze-export.jsonl").read_bytes())


def ranks(values: list[float]) -> list[float]:
    order = sorted(range(len(values)), key=lambda i: (values[i], i))
    output = [0.0] * len(values)
    for rank, index in enumerate(order):
        output[index] = float(rank)
    return output


def correlation(a: list[float], b: list[float]) -> float:
    mean_a = sum(a) / len(a)
    mean_b = sum(b) / len(b)
    centered_a = [v - mean_a for v in a]
    centered_b = [v - mean_b for v in b]
    return (sum(x * y for x, y in zip(centered_a, centered_b)) /
            (sum(x*x for x in centered_a) * sum(y*y for y in centered_b)) ** 0.5)


def main() -> None:
    printer, historian = load_sources()
    assert hashlib.sha256(printer).hexdigest() == SPOOL_SHA
    assert hashlib.sha256(historian).hexdigest() == HST_SHA
    ps = {int(n): bytes.fromhex(payload.decode("ascii")) for n, payload in re.findall(
        rb"JOB=PS-261003-(\d{4}) ATTEMPT=1 STATE=ACK CLASS=\w+ PAYLOAD=([0-9A-F]{32})", printer
    )}
    pv = {record["seq"]: record["value"] for line in historian.splitlines()
          for record in [json.loads(line)] if record["field"] == "PV"}
    assert set(pv) == set(range(100, 212))
    packets = [ps[300 + i] for i in range(112)]
    values = [pv[100 + i] for i in range(112)]
    models = []
    integer_channels = []
    for byteorder in ("big", "little"):
        for lane in range(4):
            words = [int.from_bytes(packet[4*lane:4*lane+4], byteorder)
                     for packet in packets]
            integer_channels.append((f"{byteorder}/{lane}", words))
            for minimum, spread in ((12, 76), (0, 100), (10, 80)):
                predicted = [round(minimum + spread * word / 2**32, 3)
                             for word in words]
                models.append((f"{byteorder}/{lane} {minimum}+{spread}u32", predicted))
        for start in range(3):
            predicted = []
            for packet in packets:
                a = int.from_bytes(packet[4*start:4*start+4], byteorder) >> 5
                b = int.from_bytes(packet[4*(start+1):4*(start+2)], byteorder) >> 6
                u = (a * (2**26) + b) / (2**53)
                predicted.append(round(12 + 76 * u, 3))
            models.append((f"{byteorder}/{start} 12+76u53", predicted))
    exact = [(label, sum(a == b for a, b in zip(predicted, values)))
             for label, predicted in models]
    assert len(models) == 30
    assert max(hits for _, hits in exact) == 0
    synthetic = [round(12 + 76 * v / 2**32, 3) for _, channel in integer_channels[:1]
                 for v in channel]
    assert synthetic == models[0][1]
    assert sum(a == b for a, b in zip(synthetic, models[0][1])) == 112

    pv_rank = ranks(values)
    correlations = [(name, correlation(ranks(channel), pv_rank))
                    for name, channel in integer_channels]
    observed = max(abs(score) for _, score in correlations)
    null_max = []
    for shift in range(112):
        shifted = pv_rank[-shift:] + pv_rank[:-shift] if shift else pv_rank
        null_max.append(max(abs(correlation(ranks(channel), shifted))
                            for _, channel in integer_channels))
    global_p = sum(v >= observed - 1e-12 for v in null_max) / len(null_max)
    print("original PV/printer matched 112 of 112 row identities; 30 integer/float quantizers")
    print(f"exact PV pairs across all 30 models: max={max(h for _, h in exact)} of 112")
    print("best rank correlations", sorted(correlations, key=lambda x: abs(x[1]), reverse=True)[:3])
    print(f"max absolute rank correlation={observed:.9f}, cyclic-lag familywise p={global_p:.6f}")
    print("planted 112/112 quantizer positive PASS; original direct bridge NEGATIVE")


if __name__ == "__main__":
    main()
