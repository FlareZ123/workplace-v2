"""H-17: MT11213b complete source-only 351-phase / fixed-gap producer check.

Source: original SHA256-pinned spool; 128 ordinary historical packets only.
Selected PS-261003-0417 RECOVER ACK2 is never parsed into the model.
Genuine C++ std::mersenne_twister_engine seed42 controls verify recurrence.
Standard library only. Run from repository root (allow several minutes).

Model: Boost/std MT11213b (351x32 state, m175, r19, tempering),
all 351 starting block phases, fixed 0/1/2/3/4/8 discarded native words
after each 4-output printer packet, two uint32 byte orders and both word orders.
Training: first 120 original intact ordinary packets, last 8 held out.
"""
from __future__ import annotations

import hashlib
import os
from pathlib import Path

N, M, R = 351, 175, 19
A, B, C = 0xCCAB8EE7, 0x31B6AB00, 0xFFE50000
U32 = (1 << 32) - 1
LOW = (1 << R) - 1
HIGH = U32 ^ LOW
SOURCE_SHA = "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"
TRAIN = 120
GAPS = (0, 1, 2, 3, 4, 8)


def temper(x: int) -> int:
    x ^= x >> 11
    x ^= (x << 7) & B
    x ^= (x << 15) & C
    x ^= x >> 17
    return x & U32


def invert_shift(y: int, shift: int, mask: int, left: bool) -> int:
    x = y
    for _ in range(6):
        x = y ^ (((x << shift) if left else (x >> shift)) & mask)
    return x & U32


def untemper(x: int) -> int:
    x = invert_shift(x, 17, U32, False)
    x = invert_shift(x, 15, C, True)
    x = invert_shift(x, 7, B, True)
    return invert_shift(x, 11, U32, False)


def twist_numeric(state: list[int]) -> list[int]:
    s = state.copy()
    for i in range(N):
        y = (s[i] & HIGH) | (s[(i + 1) % N] & LOW)
        s[i] = (s[(i + M) % N] ^ (y >> 1) ^ (A if y & 1 else 0)) & U32
    return s


def twist_symbolic(state: list[list[int]]) -> list[list[int]]:
    s = [w.copy() for w in state]
    for i in range(N):
        old, nextword, companion = s[i], s[(i + 1) % N], s[(i + M) % N]
        y0 = nextword[0]
        new = []
        for bit in range(32):
            shifted = ((old[bit + 1] if bit + 1 >= R else nextword[bit + 1])
                       if bit < 31 else 0)
            new.append(companion[bit] ^ shifted ^ (y0 if (A >> bit) & 1 else 0))
        s[i] = new
    return s


def seed_reference(seed: int, number: int) -> list[int]:
    state = [seed & U32]
    for i in range(1, N):
        previous = state[-1]
        state.append((1812433253 * (previous ^ (previous >> 30)) + i) & U32)
    sequence = []
    while len(sequence) < number:
        state = twist_numeric(state)
        sequence.extend(temper(v) for v in state)
    return sequence[:number]


def bytes_from_words(words: list[int], endian: str, reverse: bool) -> bytes:
    ordered = list(reversed(words)) if reverse else words
    return b"".join(w.to_bytes(4, endian) for w in ordered)


def words_from_bytes(packet: bytes, endian: str, reverse: bool) -> list[int]:
    words = [int.from_bytes(packet[i:i+4], endian) for i in (0, 4, 8, 12)]
    return list(reversed(words)) if reverse else words


def original_packets() -> list[bytes]:
    root = Path(__file__).resolve().parents[2]
    raw = (root / "resources/evidence/print/spool-reconstruction.log").read_bytes()
    assert hashlib.sha256(raw).hexdigest() == SOURCE_SHA
    rows = {}
    for line in raw.decode("utf-8").splitlines():
        if "JOB=" not in line:
            continue
        fields = dict(field.split("=", 1) for field in line.split() if "=" in field)
        job = int(fields["JOB"].split("-")[-1])
        if (fields["ATTEMPT"] == "1" and fields["STATE"] == "ACK"
                and 300 <= job <= 427):
            rows[job] = bytes.fromhex(fields["PAYLOAD"])
    assert sorted(rows) == list(range(300, 428))
    return [rows[i] for i in range(300, 428)]


class EqSystem:
    def __init__(self, n: int) -> None:
        self.n = n
        self.coeff_mask = (1 << n) - 1
        self.pivots: dict[int, int] = {}

    def add(self, equation: int) -> bool:
        while True:
            vars_left = equation & self.coeff_mask
            if not vars_left:
                return equation >> self.n == 0
            pivot = vars_left.bit_length() - 1
            old = self.pivots.get(pivot)
            if old is not None:
                equation ^= old
            else:
                self.pivots[pivot] = equation
                return True

    def solve_unique(self) -> int | None:
        if len(self.pivots) != self.n:
            return None
        sol = 0
        for pivot in range(self.n):
            equation = self.pivots[pivot]
            lower = equation & ((1 << pivot) - 1)
            bit = ((equation >> self.n) & 1) ^ ((lower & sol).bit_count() & 1)
            sol |= bit << pivot
        return sol


def infer(packets: list[bytes], gap: int, endian: str, reverse: bool,
          phase: int, train: int = TRAIN) -> tuple[int, int, int, int | None, int | None]:
    words = [words_from_bytes(pkt, endian, reverse) for pkt in packets]
    positions = {phase + r*(4+gap) + j: words[r][j]
                 for r in range(train) for j in range(4)}
    known = {i: untemper(v) for i, v in positions.items() if i < N}
    missing = [i for i in range(N) if i not in known]
    nvars = 32 * len(missing)
    rhs_bit = 1 << nvars
    variable_word = {word: order for order, word in enumerate(missing)}
    state = []
    for i in range(N):
        if i in known:
            state.append([rhs_bit if (known[i] >> j) & 1 else 0 for j in range(32)])
        else:
            pos = variable_word[i] * 32
            state.append([1 << (pos+j) for j in range(32)])
    eq = EqSystem(nvars)
    current_block = 0
    for output_pos, actual in sorted(positions.items()):
        while output_pos >= (current_block + 1) * N:
            state = twist_symbolic(state)
            current_block += 1
        if current_block == 0:
            continue
        observed = untemper(actual)
        row = state[output_pos % N]
        for bit in range(32):
            if not eq.add(row[bit] ^ (rhs_bit if (observed >> bit) & 1 else 0)):
                return nvars, len(eq.pivots), output_pos, None, None
    solution = eq.solve_unique()
    if solution is None:
        return nvars, len(eq.pivots), -1, None, None
    recovered = [known.get(i, 0) for i in range(N)]
    for pos, ordinal in variable_word.items():
        recovered[pos] = (solution >> (32*ordinal)) & U32
    blocks = [recovered]
    word_matches = 0
    packet_matches = 0
    for r in range(train, len(words)):
        predicted = []
        for j in range(4):
            index = phase + r*(4+gap) + j
            while index // N >= len(blocks):
                blocks.append(twist_numeric(blocks[-1]))
            predicted.append(temper(blocks[index // N][index % N]))
        word_matches += sum(a == b for a, b in zip(predicted, words[r]))
        packet_matches += predicted == words[r]
    return nvars, len(eq.pivots), -1, word_matches, packet_matches


def main() -> None:
    assert seed_reference(42, 5) == [
        1518079045, 208983500, 812239652, 4170938572, 3525382634
    ], "native std::mersenne_twister_engine reference vector mismatch"
    print("GENUINE_CXX17_SEED42_VECTOR_PASS", flush=True)
    for gap in GAPS:
        for phase in (0, 175, 350):
            native = seed_reference(42, phase + 127*(4+gap) + 4)
            for endian in ("little", "big"):
                for reverse in (False, True):
                    synthetic = [
                        bytes_from_words(native[phase+r*(4+gap):phase+r*(4+gap)+4],
                                         endian, reverse)
                        for r in range(128)
                    ]
                    n, rank, conflict, w, p = infer(
                        synthetic, gap, endian, reverse, phase
                    )
                    assert conflict == -1, (gap, phase, endian, reverse)
                    if w is not None:
                        assert (w, p) == (32, 8), (gap, phase, endian, reverse, w, p)
        print(f"GENUINE_SYNTHETIC_PHASE_AND_GAP_PASS gap={gap} checks=12", flush=True)

    original = original_packets()
    gaps = GAPS
    if os.environ.get("H17_GAP"):
        selected = int(os.environ["H17_GAP"])
        assert selected in GAPS
        gaps = (selected,)

    for gap in gaps:
        contradictions = 0
        survivors = []
        for phase in range(N):
            for endian in ("little", "big"):
                for reverse in (False, True):
                    n, rank, conflict, w, p = infer(
                        original, gap, endian, reverse, phase
                    )
                    if conflict >= 0:
                        contradictions += 1
                    else:
                        survivors.append((phase, endian, reverse, n, rank, w, p))
        print(f"ORIGINAL gap={gap} assignments={N*4} "
              f"contradictions={contradictions} survivors={len(survivors)} "
              f"survivor_examples={survivors[:3]}", flush=True)
    print("selected_18:02_ACK2_not_used original_commitments_not_queried", flush=True)


if __name__ == "__main__":
    main()
