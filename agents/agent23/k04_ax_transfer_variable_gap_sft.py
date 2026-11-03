"""Conditional K04 cross-transfer MT stage alignment with arbitrary 1..64 draw gaps.

Use: python agents/agent23/k04_ax_transfer_variable_gap_sft.py
Source model is the existing p951 hypothetical producer, NOT historical firmware proof.
Selected printer row129 is omitted by the reused symbolic-source constructor.
"""
from collections import defaultdict, deque
import hashlib
import json
from pathlib import Path
import random
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'agents' / 'agent49'))
from k04_p951_symbolic_basis import ORIGIN, LAST, source, get, temper

AX_SHA256 = '32970ad4431a9d610cc12dcca2813f39dd8fd2e396f9e748dc94b5932cb69adf'
NEG = -10**9


def transfers():
    raw = (ROOT / 'resources/evidence/transfers/transfer-audit.jsonl').read_bytes()
    assert hashlib.sha256(raw).hexdigest() == AX_SHA256
    groups = defaultdict(list)
    for line in raw.splitlines():
        record = json.loads(line)
        if record['kind'] == 'CHUNK':
            groups[record['transfer']].append(record)
    assert sorted(groups) == ['AX-7778', 'AX-7781', 'AX-7782', 'AX-7783']
    assert all(len(group) == 16 for group in groups.values())
    return groups


def predicted_halves():
    basis, symbols = source(ROOT / 'resources')
    assert basis.rank == 15365
    masks, values = [[], []], [[], []]
    for stage in range(ORIGIN, LAST + 1):
        mask = value = 0
        for bit, expr in enumerate(temper(get(symbols, stage))):
            found = basis.predict(expr)
            if found is not None:
                mask |= 1 << bit
                value |= found << bit
        for half, shift in enumerate((16, 0)):
            masks[half].append((mask >> shift) & 65535)
            values[half].append((value >> shift) & 65535)
    assert all(masks[half][stage - ORIGIN] == 0 for half in range(2) for stage in range(951, 955))
    return masks, values


def order_rows(rows, mode):
    if mode == 'file':
        return rows
    if mode == 'seq_asc':
        return sorted(rows, key=lambda x: (x['seq'], x['attempt']))
    if mode == 'seq_desc':
        return sorted(rows, key=lambda x: (-x['seq'], -x['attempt']))
    if mode == 'attempt_asc':
        return sorted(rows, key=lambda x: (x['attempt'], x['seq']))
    if mode == 'attempt_desc':
        return sorted(rows, key=lambda x: (-x['attempt'], -x['seq']))
    raise ValueError(mode)


def best_path(observed, masks, values, max_gap):
    """O(16*N) sliding-maximum dynamic programming, stage gap 1..max_gap."""
    n = len(masks)
    scores = [m.bit_count() if ((v ^ observed[0]) & m) == 0 else NEG
              for m, v in zip(masks, values)]
    backpointers = []
    for target in observed[1:]:
        window = deque()
        following = [NEG] * n
        previous_indices = [-1] * n
        for index in range(n):
            previous = index - 1
            if previous >= 0 and scores[previous] > NEG:
                while window and scores[window[-1]] <= scores[previous]:
                    window.pop()
                window.append(previous)
            while window and window[0] < index - max_gap:
                window.popleft()
            mask = masks[index]
            if window and ((values[index] ^ target) & mask) == 0:
                predecessor = window[0]
                following[index] = scores[predecessor] + mask.bit_count()
                previous_indices[index] = predecessor
        scores = following
        backpointers.append(previous_indices)
    index = max(range(n), key=scores.__getitem__)
    total = scores[index]
    if total == NEG:
        return total, ()
    path = [index + ORIGIN]
    for previous_indices in reversed(backpointers):
        index = previous_indices[index]
        assert index >= 0
        path.append(index + ORIGIN)
    path.reverse()
    return total, tuple(path)


def search_group(group, masks, values):
    best = None
    for ordering in ('seq_asc', 'attempt_asc', 'seq_desc', 'attempt_desc', 'file'):
        rows = order_rows(group, ordering)
        for byte_swap in (False, True):
            observed = [int.from_bytes(bytes.fromhex(row['checkpoint']),
                                       'little' if byte_swap else 'big') for row in rows]
            for half in (0, 1):
                for gap in (4, 8, 16, 32, 64):
                    score, path = best_path(observed, masks[half], values[half], gap)
                    item = (score, ordering, 'upper' if half == 0 else 'lower',
                            byte_swap, gap, path)
                    if best is None or score > best[0]:
                        best = item
    return best


def main():
    masks, values = predicted_halves()
    groups = transfers()
    results = {name: search_group(rows, masks, values)
               for name, rows in sorted(groups.items())}
    a = results['AX-7778']
    assert a[:5] == (122, 'seq_asc', 'upper', True, 4)
    assert a[5] == tuple(range(-157, -141))
    assert {k: results[k][0] for k in ('AX-7781','AX-7782','AX-7783')} == {
        'AX-7781': 51, 'AX-7782': 45, 'AX-7783': 48}
    print('Source fixed rank=15365; 16 checkpoints per AX transfer')
    for name, result in results.items():
        print(name, result)
    rng = random.Random(20261103)
    observed = [int.from_bytes(bytes.fromhex(r['checkpoint']), 'little')
                for r in order_rows(groups['AX-7778'], 'seq_asc')]
    shuffled = []
    for _ in range(100):
        trial = observed[:]
        rng.shuffle(trial)
        shuffled.append(best_path(trial, masks[0], values[0], 64)[0])
    assert max(shuffled) < 122
    print('100 shuffled AX-7778 orders: max', max(shuffled),
          'mean', sum(shuffled) / len(shuffled))
    print('K04 recovered coupon bits: 0/128. No commitment hit.')


if __name__ == '__main__':
    main()
