"""H-17 K04, legacy .NET Framework System.Random source-only hypotheses.

Python 3 standard library. Run from the repo without changing any evidence.
Model A: continuous NextBytes with 0..16 fixed hidden draws/packet and 8
         four-by-four byte packings, across all 128 intact printer packets.
Model B: independent newly seeded NextBytes for first intact job0300;
         exhaust all Int32 seed magnitudes by inverting its first draw.
Neither model reads the disputed selected ESC-N coupon or commitments.
"""
from __future__ import annotations
import hashlib
import json
import math
from pathlib import Path
import re

MOD = 2147483647
EXPECTED_SPOOL = "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"


class ClassicRandom:
    """Original Microsoft reference-source subtractive generator."""
    def __init__(self, seed: int):
        mj = (161803398 - (MOD if seed == -(1 << 31) else abs(seed))) % MOD
        mk = 1
        self.state = [0] * 56
        self.state[55] = mj
        for i in range(1, 55):
            loc = (21 * i) % 55
            self.state[loc] = mk
            mk, mj = (mj - mk) % MOD, self.state[loc]
        for _ in range(4):
            for i in range(1, 56):
                self.state[i] = (
                    self.state[i] - self.state[1 + (i + 30) % 55]
                ) % MOD
        self.i = 0
        self.j = 21

    def draw(self) -> int:
        self.i = 1 if self.i == 55 else self.i + 1
        self.j = 1 if self.j == 55 else self.j + 1
        v = (self.state[self.i] - self.state[self.j]) % MOD
        self.state[self.i] = v
        return v

    def bytes(self, count: int) -> bytes:
        return bytes(self.draw() % 256 for _ in range(count))


def packet_transform(data: bytes, mode: int) -> bytes:
    lanes = [data[i:i + 4] for i in range(0, 16, 4)]
    if mode & 1:
        lanes = [lane[::-1] for lane in lanes]
    if mode & 2:
        lanes.reverse()
    if mode & 4:
        lanes = [bytes(lanes[j][i] for j in range(4)) for i in range(4)]
    return b"".join(lanes)


def packet_inverse(data: bytes, mode: int) -> bytes:
    lookup = packet_transform(bytes(range(16)), mode)
    result = bytearray(16)
    for output_position, input_position in enumerate(lookup):
        result[input_position] = data[output_position]
    return bytes(result)


def intact_rows() -> list[bytes]:
    path = (Path(__file__).resolve().parents[2] / "resources"
            / "evidence" / "print" / "spool-reconstruction.log")
    original = path.read_bytes()
    assert hashlib.sha256(original).hexdigest() == EXPECTED_SPOOL
    rows = {}
    pattern = re.compile(
        r"JOB=PS-261003-(\d{4})\s+ATTEMPT=1\s+STATE=ACK\b"
        r".*?PAYLOAD=([0-9A-F]{32})"
    )
    for line in original.decode().splitlines():
        match = pattern.search(line)
        if match and "+00:00" in line:
            job = int(match.group(1))
            if 300 <= job < 428:
                assert job not in rows
                rows[job] = bytes.fromhex(match.group(2))
    assert list(rows) == list(range(300, 428))
    return list(rows.values())


def lag_test(packets: list[bytes], gap: int, mode: int) -> tuple[int, int]:
    observations = {}
    for row, packet in enumerate(packets):
        for i, b in enumerate(packet_inverse(packet, mode)):
            observations[row * (16 + gap) + i] = b
    hits = tested = 0
    for t, b in observations.items():
        if t >= 55 and t - 55 in observations and t - 34 in observations:
            residue = (b - observations[t - 55] + observations[t - 34]) % 256
            hits += residue == 0 or residue == 255
            tested += 1
    return hits, tested


def inverted_seeds(packet: bytes) -> tuple[list[int], list[int]]:
    first = ClassicRandom(0)
    next_seed = ClassicRandom(1)
    base = [first.draw() for _ in range(16)]
    shifted = [next_seed.draw() for _ in range(16)]
    slopes = [(b - a) % MOD for a, b in zip(base, shifted)]
    assert math.gcd(slopes[0], MOD) == 1
    inv = pow(slopes[0], -1, MOD)
    survivors = [0] * 16
    solutions = []
    # The raw first draw is in [0, MOD), so enumerate exactly the output
    # values with the observed low eight bits, then invert for the seed.
    for raw_first in range(packet[0], MOD, 256):
        seed = ((raw_first - base[0]) * inv) % MOD
        survivors[0] += 1
        for i in range(1, 16):
            if ((slopes[i] * seed + base[i]) % MOD) % 256 != packet[i]:
                break
            survivors[i] += 1
        else:
            solutions.append(seed)
    return survivors, solutions


def run() -> None:
    assert ClassicRandom(0).draw() == 1559595546
    assert ClassicRandom(42).draw() == 1434747710
    for seed in (0, 1, 42, 20261103, 2147483646):
        trial = ClassicRandom(seed)
        r0, r1 = ClassicRandom(0), ClassicRandom(1)
        for _ in range(16):
            a, b = r0.draw(), r1.draw()
            assert trial.draw() == (a + (b - a) * seed) % MOD

    packets = intact_rows()
    for mode in range(8):
        gap = mode * 2
        rng = ClassicRandom(20261103 + mode)
        synthetic = []
        for _ in range(128):
            synthetic.append(packet_transform(rng.bytes(16), mode))
            rng.bytes(gap)
        count, applicable = lag_test(synthetic, gap, mode)
        assert applicable and count == applicable

    planted = 20261103
    planted_wire = packet_transform(ClassicRandom(planted).bytes(16), 7)
    planted_counts, planted_matches = inverted_seeds(packet_inverse(planted_wire, 7))
    assert planted in planted_matches and planted_counts[-1] > 0

    models = []
    for mode in range(8):
        for gap in range(17):
            hit, tested = lag_test(packets, gap, mode)
            assert hit < tested
            models.append((hit / tested, hit, tested, mode, gap))
    models.sort(reverse=True)

    reset_models = []
    for mode in range(8):
        counts, seeds = inverted_seeds(packet_inverse(packets[0], mode))
        assert counts[0] == (1 << 23) and not seeds
        reset_models.append({"geometry": mode, "survivors_after_bytes_1_to_5": counts[:5]})

    print(json.dumps({
        "source_sha256": EXPECTED_SPOOL,
        "intact_packets": len(packets),
        "continuous_models": len(models),
        "best_continuous": models[:8],
        "continuous_exact_matches": 0,
        "seed_magnitudes_per_packet_geometry": 1 << 31,
        "packet_geometries": 8,
        "first_packet_seed_inversion": reset_models,
        "seeded_inverse_positive": planted,
        "eight_seeded_continuous_positive_controls": "PASS",
        "selected_physical_coupon_used": False
    }, indent=2))


if __name__ == "__main__":
    run()
