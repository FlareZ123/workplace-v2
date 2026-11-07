"""Source-only SFT: native std::mt19937(uint32) at p951 / 2496 prior outputs.

Run from repository root:
    python agents/agent1/k04_native_mt2496_seed_sft.py

The selected row129 is withheld before basis construction. The K04 mask,
acceptance commitment, K08 nonce, candidate and verifier are never read.
"""
from __future__ import annotations

import configparser
import hashlib
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
U32 = 0xFFFFFFFF
MAG = 0x9908B0DF
MULT = 1812433253
MULT_INV = pow(MULT, -1, 1 << 32)
OFFSET = 2496
SPOOL_SHA = "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"
LABEL_SHA = "146fa698f44bc9b9fa7a443d8dc71a2e23ff0f883dabd01512f8ade82d3666ad"

# Exact p951 packet-start schedule used by the existing original-source basis.
STARTS = [
    0,7,16,22,30,37,45,54,64,72,80,88,95,108,116,122,130,136,142,148,
    154,164,170,176,182,188,194,203,209,218,224,230,237,244,250,257,265,
    272,284,294,301,307,314,324,335,342,348,354,360,366,372,378,384,394,
    401,408,416,423,429,435,446,454,460,470,477,485,491,503,511,518,524,
    531,539,556,562,568,576,582,588,595,602,608,617,624,632,638,644,650,
    658,666,672,678,686,693,701,710,717,729,736,743,755,762,770,776,782,
    788,795,801,813,819,825,831,837,846,853,861,870,876,884,891,899,905,
    912,918,924,930,936,942,947,951,955,959,963,
]
SELECTED_ROW = 129


class Basis:
    def __init__(self) -> None:
        self.rows: dict[int, tuple[int, int]] = {}
        self.rank = 0

    def insert(self, expression: int, value: int) -> None:
        while expression:
            pivot = expression.bit_length() - 1
            if pivot not in self.rows:
                self.rows[pivot] = (expression, value)
                self.rank += 1
                return
            prior, prior_value = self.rows[pivot]
            expression ^= prior
            value ^= prior_value
        assert value == 0, "original source contradicts p951/offset model"

    def predict(self, expression: int) -> int | None:
        value = 0
        while expression:
            pivot = expression.bit_length() - 1
            if pivot not in self.rows:
                return None
            prior, prior_value = self.rows[pivot]
            expression ^= prior
            value ^= prior_value
        return value


def source_packets() -> tuple[list[bytes | None], int]:
    evidence = ROOT / "resources" / "evidence"
    spool_path = evidence / "print" / "spool-reconstruction.log"
    labels_path = evidence / "archive-labels.ini"
    spool = spool_path.read_bytes()
    labels = labels_path.read_bytes()
    assert hashlib.sha256(spool).hexdigest() == SPOOL_SHA
    assert hashlib.sha256(labels).hexdigest() == LABEL_SHA

    config = configparser.ConfigParser(interpolation=None)
    config.read_string(labels.decode("utf-8"))
    route = config["printer_routes_2026-09-01_to_2026-10-03"]["esc-n"]

    lines = [line for line in spool.decode("ascii").splitlines()
             if line.startswith("2026-")]
    assert len(lines) == len(STARTS) == 133
    metadata = [
        dict(re.findall(r"(JOB|ATTEMPT|STATE|CLASS)=([^\s]+)", line))
        for line in lines
    ]
    acknowledgements = [
        (index, int(fields["ATTEMPT"]))
        for index, fields in enumerate(metadata)
        if fields.get("JOB") == route
        and fields.get("STATE") == "ACK"
        and fields.get("CLASS") == "RECOVER"
    ]
    assert acknowledgements
    last_index, last_attempt = max(acknowledgements, key=lambda item: item[1])
    assert (last_index, last_attempt) == (SELECTED_ROW, 2)

    packets: list[bytes | None] = []
    for index, line in enumerate(lines):
        if index == SELECTED_ROW:
            # The selected ACK line is retained only as metadata; its payload
            # field is not extracted, decoded, or used in any equation.
            packets.append(None)
        else:
            match = re.search(r"(?:^|\s)PAYLOAD=([0-9A-F]{32})(?=\s|$)", line)
            assert match is not None
            packets.append(bytes.fromhex(match.group(1)))
    return packets, last_index


def untemper(value: int) -> int:
    for shift, left, mask in (
        (18, False, U32),
        (15, True, 0xEFC60000),
        (7, True, 0x9D2C5680),
        (11, False, U32),
    ):
        previous = value
        for _ in range(6):
            previous = value ^ (
                ((previous << shift) & mask) if left else (previous >> shift)
            )
        value = previous & U32
    return value


def source_basis(packets: list[bytes | None], selected_index: int) -> Basis:
    assert len(packets) == len(STARTS) == 133
    assert selected_index == SELECTED_ROW and packets[selected_index] is None

    observations: dict[int, int] = {}
    for row, (packet, start) in enumerate(zip(packets, STARTS)):
        if row == selected_index:
            continue
        assert packet is not None and len(packet) == 16
        for lane in range(4):
            stage = 624 + OFFSET + start + lane
            assert stage not in observations
            value = int.from_bytes(packet[4 * lane:4 * lane + 4], "little")
            observations[stage] = untemper(value)
    assert len(observations) == 132 * 4

    # Ring-buffer form of the exact MT19937 linear recurrence. It retains only
    # the current 624 words while projecting observations at output 2496+STARTS.
    ring = [
        [1 << (32 * word + bit) for bit in range(32)]
        for word in range(624)
    ]
    basis = Basis()
    for index in range(max(observations) + 1):
        if index < 624:
            word = ring[index]
        else:
            prior = index - 624
            x = ring[prior % 624]
            y = ring[(prior + 1) % 624]
            z = ring[(prior + 397) % 624]
            word = [
                z[bit]
                ^ (x[31] if bit == 30 else (y[bit + 1] if bit < 30 else 0))
                ^ (y[0] if (MAG >> bit) & 1 else 0)
                for bit in range(32)
            ]
            ring[index % 624] = word

        observed = observations.get(index)
        if observed is not None:
            for bit, expression in enumerate(word):
                basis.insert(expression, (observed >> bit) & 1)

    assert basis.rank == 15365
    return basis


def project_initial_register(basis: Basis) -> list[tuple[int, int]]:
    projected = []
    for word in range(624):
        mask = value = 0
        for bit in range(32):
            known = basis.predict(1 << (32 * word + bit))
            if known is not None:
                mask |= 1 << bit
                value |= known << bit
        projected.append((mask, value))
    return projected


def seed_step(previous: int, index: int) -> int:
    return (MULT * (previous ^ (previous >> 30)) + index) & U32


def invert_seed_step(current: int, index: int) -> int:
    transformed = ((current - index) * MULT_INV) & U32
    return transformed ^ (transformed >> 30)


def seed_from_initial_word(value: int, index: int) -> int:
    seed = value
    for position in range(index, 0, -1):
        seed = invert_seed_step(seed, position)
    return seed


def native_initial_state(seed: int) -> list[int]:
    state = [seed]
    for index in range(1, 624):
        state.append(seed_step(state[-1], index))
    return state


def native_next_word(state: list[int], index: int) -> int:
    prior = index - 624
    joined = (state[prior] & 0x80000000) | (state[prior + 1] & 0x7FFFFFFF)
    return (
        state[prior + 397]
        ^ (joined >> 1)
        ^ (MAG if joined & 1 else 0)
    ) & U32


def temper(value: int) -> int:
    value ^= value >> 11
    value ^= (value << 7) & 0x9D2C5680
    value ^= (value << 15) & 0xEFC60000
    value ^= value >> 18
    return value & U32


def synthetic_packets(seed: int) -> tuple[list[bytes | None], list[int]]:
    state = native_initial_state(seed)
    last = 624 + OFFSET + max(STARTS) + 3
    for index in range(624, last + 1):
        state.append(native_next_word(state, index))
    packets = []
    for start in STARTS:
        packet = b"".join(
            temper(state[624 + OFFSET + start + lane]).to_bytes(4, "little")
            for lane in range(4)
        )
        packets.append(packet)
    packets[SELECTED_ROW] = None
    return packets, state[:624]


def check_synthetic_controls() -> None:
    controls = (0, 1, 5489, 0x12345678, 0xDEADBEEF, 0xFFFFFFFF)
    assert temper(native_next_word(native_initial_state(5489), 624)) == 3499211612
    for seed in controls:
        packets, expected_state = synthetic_packets(seed)
        basis = source_basis(packets, SELECTED_ROW)
        projected = project_initial_register(basis)
        assert basis.rank == 15365
        assert sum(mask.bit_count() for mask, _ in projected) == 711
        assert all(
            ((actual ^ value) & mask) == 0
            for actual, (mask, value) in zip(expected_state, projected)
        )
        full_words = [
            (index, value)
            for index, (mask, value) in enumerate(projected)
            if mask == U32
        ]
        assert len(full_words) == 4
        assert {seed_from_initial_word(value, index)
                for index, value in full_words} == {seed}
    print("SYNTHETIC: 6/6 native std::mt19937(uint32) offset-2496 controls PASS")
    print("REFERENCE: std::mt19937(5489) first output = 3499211612 PASS")


def check_original() -> None:
    packets, selected_index = source_packets()
    basis = source_basis(packets, selected_index)
    projected = project_initial_register(basis)
    fixed_bits = sum(mask.bit_count() for mask, _ in projected)
    full_words = [
        (index, value)
        for index, (mask, value) in enumerate(projected)
        if mask == U32
    ]
    assert fixed_bits == 711
    assert [(index, value) for index, value in full_words] == [
        (6, 0xE403BB7D),
        (7, 0x1F7B301F),
        (170, 0x664F8F37),
        (605, 0x0D8EFC5D),
    ]

    candidate_rows = []
    for index, value in full_words:
        seed = seed_from_initial_word(value, index)
        initial = native_initial_state(seed)
        mismatch_bits = sum(
            ((actual ^ expected) & mask).bit_count()
            for actual, (mask, expected) in zip(initial, projected)
        )
        candidate_rows.append((index, value, seed, mismatch_bits))

    seeds = [seed for _, _, seed, _ in candidate_rows]
    assert seeds == [0xF848BA70, 0xA5571EA3, 0xE5FD2AAC, 0xE2E0B436]
    assert len(set(seeds)) == 4
    assert [mismatch for _, _, _, mismatch in candidate_rows] == [314, 351, 327, 333]

    print("ORIGINAL: selected ACK row129 withheld; 132 intact packets")
    print(f"ORIGINAL: source rank {basis.rank}/19968; fixed initial bits {fixed_bits}")
    print("ORIGINAL: fully fixed initial words:")
    for index, value, seed, mismatch in candidate_rows:
        print(
            f"  S[{index}]={value:08X} -> unique seed {seed:08X}; "
            f"{mismatch}/711 projected bits disagree"
        )
    print("RESULT: NO native std::mt19937(uint32_seed) at p951 / 2496 outputs")
    print("SCOPE: this does not identify the historical printer or recover K04")


if __name__ == "__main__":
    check_synthetic_controls()
    check_original()
