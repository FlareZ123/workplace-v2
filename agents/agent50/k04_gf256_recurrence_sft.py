"""K04: source-only GF(256) low-complexity linear recurrence holdout.

Run from repository root with: python agents/agent50/k04_gf256_recurrence_sft.py
No original acceptance target, selected coupon, or K04 mask is read.
"""
import hashlib
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "resources/evidence/print/spool-reconstruction.log"
PIN = "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"


def mul(a, b):
    value = 0
    while b:
        if b & 1:
            value ^= a
        a <<= 1
        if a & 256:
            a ^= 0x11B
        b >>= 1
    return value


def power(a, exponent):
    value = 1
    while exponent:
        if exponent & 1:
            value = mul(value, a)
        a = mul(a, a)
        exponent >>= 1
    return value


def berlekamp_massey(seq):
    coeff, previous = [1], [1]
    length, shift, last = 0, 1, 1
    for index, symbol in enumerate(seq):
        discrepancy = symbol
        for k in range(1, length + 1):
            discrepancy ^= mul(coeff[k], seq[index - k])
        if not discrepancy:
            shift += 1
            continue
        old = coeff[:]
        scale = mul(discrepancy, power(last, 254))
        coeff.extend([0] * max(0, len(previous) + shift - len(coeff)))
        for j, val in enumerate(previous):
            coeff[j + shift] ^= mul(scale, val)
        if 2 * length <= index:
            length = index + 1 - length
            previous, last, shift = old, discrepancy, 1
        else:
            shift += 1
    return coeff[:length + 1], length


def predict(prefix, coeff, count):
    series = list(prefix)
    for _ in range(count):
        value = 0
        for k in range(1, len(coeff)):
            value ^= mul(coeff[k], series[-k])
        series.append(value)
    return bytes(series[-count:])


def layouts(packet):
    return {
        "raw": packet,
        "reverse-byte": packet[::-1],
        "word4-reverse": b"".join(packet[k:k+4] for k in (12, 8, 4, 0)),
        "word4-byte-swap": b"".join(packet[k:k+4][::-1] for k in (0, 4, 8, 12)),
    }


def run():
    raw = SOURCE.read_bytes()
    assert hashlib.sha256(raw).hexdigest() == PIN
    rows = []
    for line in raw.decode("ascii").splitlines():
        match = re.search(
            r"JOB=PS-261003-(\d+) ATTEMPT=(\d+) STATE=(\w+) .*? PAYLOAD=([0-9A-F]{32}) ",
            line,
        )
        if match and 300 <= int(match[1]) <= 427 and match[2] == "1" and match[3] == "ACK":
            rows.append((int(match[1]), bytes.fromhex(match[4])))
    rows.sort()
    assert len(rows) == 128 and [i for i, _ in rows] == list(range(300, 428))
    print("original_sha256", PIN, "intact_routine_packets", len(rows))

    # Genuine five-tap linear generator with 64 blind withheld symbols.
    samples = list(range(1, 6))
    taps = (1, 0x83, 0x71, 0xD1, 0x4F, 0xE5)
    for _ in range(1000):
        value = 0
        for k in range(1, 6):
            value ^= mul(taps[k], samples[-k])
        samples.append(value)
    learned, order = berlekamp_massey(samples[:320])
    assert order == 5
    assert predict(samples[:320], learned, 64) == bytes(samples[320:384])
    print("synthetic_positive PASS, order", order, "withheld", 64)

    heldout_packets = 0
    for name in layouts(rows[0][1]):
        packets = [layouts(packet)[name] for _, packet in rows]
        for train_rows in (24, 48, 80, 96):
            training = b"".join(packets[:train_rows])
            coeff, order = berlekamp_massey(training)
            actual = b"".join(packets[train_rows:train_rows+8])
            guess = predict(training, coeff, len(actual))
            matching_bytes = sum(a == b for a, b in zip(actual, guess))
            matching_packets = sum(actual[k:k+16] == guess[k:k+16]
                                   for k in range(0, len(actual), 16))
            assert matching_packets == 0
            heldout_packets += 8
            print(name, "train_rows", train_rows, "GF_order", order,
                  "byte_matches", matching_bytes, "/128; whole_packets",
                  matching_packets, "/8")
    for train_rows in (32, 64, 96):
        matched, complete_lanes = 0, 0
        for column in range(16):
            training = bytes(p[column] for _, p in rows[:train_rows])
            actual = bytes(p[column] for _, p in rows[train_rows:train_rows+16])
            coeff, order = berlekamp_massey(training)
            guess = predict(training, coeff, len(actual))
            matched += sum(a == b for a, b in zip(actual, guess))
            complete_lanes += guess == actual
        assert complete_lanes == 0
        print("byte-lane train_rows", train_rows, "matching_bytes", matched,
              "/256; complete_lanes", complete_lanes, "/16")
    print("original complete heldout predictions", heldout_packets,
          "correct complete packets 0")


if __name__ == "__main__":
    run()
