"""Original-source exact two-packet withholding discriminator for the conditional p951 printer model.

The authentic selected ACK2 row129 is entirely excluded from source fitting and inference.
Prints the rank and degree of exact whole-packet reconstruction after withholding
historical complete packets *jointly* rather than one at a time.
"""
from __future__ import annotations

from itertools import combinations
from pathlib import Path
import hashlib
import re
import sys
import random

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'agents/agent49'))
from k04_p951_symbolic_basis import STARTS, ORIGIN, Basis, get, untemper, words

SPOOL_SHA = '7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083'
FIVE = (12, 41, 66, 95, 125)
EXPECTED_PAIR_LOSS = {(12, 66): 129, (41, 125): 129}


def temper(y: int) -> int:
    y ^= y >> 11
    y ^= (y << 7) & 0x9D2C5680
    y ^= (y << 15) & 0xEFC60000
    y ^= y >> 18
    return y & 0xFFFFFFFF


def rows_from_packets(packets: list[bytes], symbolic: list[list[int]]) -> dict[int, list[tuple[int, int]]]:
    assert len(packets) == len(STARTS) == 133
    result = {}
    for row, (payload, start) in enumerate(zip(packets, STARTS)):
        if row == 129:
            continue
        assert len(payload) == 16
        data = []
        for lane in range(4):
            native = untemper(int.from_bytes(payload[4 * lane: 4 * lane + 4], 'little'))
            data.extend((vector, (native >> pos) & 1) for pos, vector in enumerate(get(symbolic, start + lane)))
        assert len(data) == 128
        result[row] = data
    return result


def fit(rows: dict[int, list[tuple[int, int]]], excluded: set[int]) -> Basis:
    basis = Basis()
    for row, data in rows.items():
        if row in excluded:
            continue
        for vector, bit in data:
            basis.insert(vector, bit)
    return basis


def source_experiment(rows: dict[int, list[tuple[int, int]]]) -> None:
    full = fit(rows, set())
    assert full.rank == 15365, full.rank
    table = []
    for a, b in combinations(FIVE, 2):
        withheld = (a, b)
        basis = fit(rows, set(withheld))
        loss = full.rank - basis.rank
        predicted = [sum(basis.predict(v) is not None for v, _ in rows[row]) for row in withheld]
        expected = EXPECTED_PAIR_LOSS.get(withheld, 2)
        assert (loss, predicted) == (expected, [0, 0] if expected == 129 else [127, 127]), (withheld, loss, predicted)
        table.append((a, b, loss, *predicted))
        print(f'WHOLE_PACKET_PAIR a={a} b={b} rank_loss={loss} fixed_native={predicted}')

    late = fit(rows, {131, 132})
    late_fixed = [sum(late.predict(v) is not None for v, _ in rows[row]) for row in (131, 132)]
    assert (full.rank - late.rank, late_fixed) == (129, [64, 63])
    print(f'LATE_RECOVER_ACK_PAIR rows=131,132 rank_loss=129 native_fixed={late_fixed}')

    batch = fit(rows, set(FIVE))
    batch_fixed = [sum(batch.predict(v) is not None for v, _ in rows[row]) for row in FIVE]
    assert full.rank - batch.rank == 259
    # The exact full source enforces 127/128 original native bits of row95 in this case.
    assert batch_fixed == [0, 0, 0, 127, 0], batch_fixed
    print(f'FIVE_WHOLE_PACKET_JOINT rows={FIVE} rank_loss=259 native_fixed={batch_fixed}')

    # Calibrate the source's complete original payloads only after each withheld prediction was frozen.
    # Every original observed bit must be consistent with the full basis.
    for row in FIVE + (131, 132):
        assert all(full.predict(v) == bit for v, bit in rows[row])
    print('ORIGINAL_FULL_PACKET_DATA_POSITIVE_CONTROL_PASS')


def synthetic_experiment(symbolic: list[list[int]]) -> None:
    # Genuinely construct a 624-word MT source state and sample every native stage.
    rng = random.Random(20261106)
    initial = sum(rng.getrandbits(32) << (32 * word) for word in range(624))
    synthetic = []
    for start in STARTS:
        packet = bytearray()
        for lane in range(4):
            native = sum(((v & initial).bit_count() & 1) << bit for bit, v in enumerate(get(symbolic, start + lane)))
            packet.extend(temper(native).to_bytes(4, 'little'))
        synthetic.append(bytes(packet))
    synthetic[129] = b''
    rows = rows_from_packets(synthetic, symbolic)
    source_experiment(rows)
    print('SYNTHETIC_GENUINE_MT_FULL_PACKET_SOURCE_CONTROL_PASS')


def main() -> None:
    raw = (ROOT / 'resources/evidence/print/spool-reconstruction.log').read_bytes()
    assert hashlib.sha256(raw).hexdigest() == SPOOL_SHA
    original = [bytes.fromhex(s.decode()) for s in re.findall(rb'PAYLOAD=([0-9A-F]{32})', raw)]
    assert len(original) == 133
    original[129] = b''
    symbolic = words()
    source_experiment(rows_from_packets(original, symbolic))
    # Original and synthetic control use the same inference path, no target hash.
    synthetic_experiment(symbolic)
    print('ORIGINAL_AND_SYNTHETIC_JOINT_WITHHOLDOUT_PASS')


if __name__ == '__main__':
    main()
