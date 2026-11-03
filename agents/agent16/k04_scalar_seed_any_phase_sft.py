"""SFT: source-constrained scalar MT19937 seed-register placement across native phases.

Run from repository root: python agents/agent16/k04_scalar_seed_any_phase_sft.py
Original disputed ACK row129, route mask and K04 acceptance commitment are excluded.
"""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'agents' / 'agent49'))
from k04_p951_symbolic_basis import Basis, LAST, ORIGIN, STARTS, get, source

MULTIPLIER = 1812433253
MOD_MASK = 0xFFFFFFFF
TWIST = 0x9908B0DF


def seed_step(previous, i):
    return (MULTIPLIER * (previous ^ (previous >> 30)) + i) & MOD_MASK


def seeded_native(seed, phase):
    states = {phase: seed}
    for i in range(1, 624):
        states[phase + i] = seed_step(states[phase + i - 1], i)
    for i in range(phase + 624, LAST + 1):
        before = states[i - 624]
        following = states[i - 623]
        twist = (((before & 0x80000000) | (following & 0x7FFFFFFF)) >> 1)
        states[i] = states[i - 227] ^ twist ^ (TWIST if following & 1 else 0)
    return states


def fully_known_native(basis, symbolic):
    fixed = {}
    for i in range(ORIGIN, LAST + 1):
        bits = [basis.predict(expression) for expression in get(symbolic, i)]
        if all(value is not None for value in bits):
            fixed[i] = sum(value << bit for bit, value in enumerate(bits))
    return fixed


def phase_result(fixed, start):
    matching = 0
    contradictions = 0
    first_mismatch = None
    for native_index in range(start + 1, start + 624):
        if native_index - 1 not in fixed or native_index not in fixed:
            continue
        expected = seed_step(fixed[native_index - 1], native_index - start)
        actual = fixed[native_index]
        if expected == actual:
            matching += 1
        else:
            contradictions += 1
            if first_mismatch is None:
                first_mismatch = (native_index, expected, actual)
    return matching, contradictions, first_mismatch


def sparse_positive(symbolic, seed, phase):
    states = seeded_native(seed, phase)
    basis = Basis()
    for row, start in enumerate(STARTS):
        if row == 129:
            continue
        for lane in range(4):
            native = states[start + lane]
            for bit, expression in enumerate(get(symbolic, start + lane)):
                basis.insert(expression, (native >> bit) & 1)
    assert basis.rank == 15365
    fixed = fully_known_native(basis, symbolic)
    matched, mismatched, _ = phase_result(fixed, phase)
    assert mismatched == 0 and matched >= 90
    print(f'SYNTHETIC scalar seed={seed} phase={phase}: '
          f'{matched} source-fixed initializer pairs, 0 contradictions, PASS')


def main():
    original_basis, symbolic = source(ROOT / 'resources')
    assert original_basis.rank == 15365
    fixed = fully_known_native(original_basis, symbolic)
    assert len(fixed) == 991
    print(f'ORIGINAL source: {original_basis.rank} rank, {len(fixed)} fully determined native words')

    phases = range(ORIGIN - 622, LAST + 1)
    tested = [(phase, phase_result(fixed, phase)) for phase in phases]
    excluded = [phase for phase, (hits, misses, _) in tested if misses]
    untestable = [phase for phase, (hits, misses, _) in tested if not hits and not misses]
    assert len(tested) == 2763
    assert len(excluded) == 2732
    assert len(untestable) == 31
    assert all(hits == 0 for _, (hits, _, _) in tested)
    print(f'ORIGINAL overlap phases: {len(tested)}, contradicted={len(excluded)}, '
          f'no fully source-fixed adjacent witness={len(untestable)}')
    assert untestable == list(range(-1722, -1703)) + list(range(1029, 1041))

    forward = [(phase, result) for phase, result in tested if phase + 624 <= 0]
    assert len(forward) == 1099
    assert sum(result[1] > 0 for _, result in forward) == 1080
    print('FORWARD-ONLY first printer packet at native 0: '
          '1099 candidate seed epochs, 1080 contradicted, 19 untestable at left edge')
    for phase in (-1703, -1100, -900, -800, -624):
        matched, mismatched, first = phase_result(fixed, phase)
        assert mismatched > 0
        print(f'  phase={phase}: known_pairs={matched + mismatched}, '
              f'mismatches={mismatched}, first={first}')

    # True scalar-seeded producers, sampled at the exact 132 intact printer positions.
    sparse_positive(symbolic, 5489, -1100)
    sparse_positive(symbolic, 0xDEADBEEF, -800)
    for seed, phase in ((1, -1100), (5489, -777), (0xDEADBEEF, -497)):
        states = seeded_native(seed, phase)
        matched, mismatched, _ = phase_result(states, phase)
        assert (matched, mismatched) == (623, 0)
        print(f'SYNTHETIC full native seed={seed} phase={phase}: 623/623 PASS')

    print('RESULT: original scalar initializer excluded at all 2732 testable '
          'native register starts in this conditional p951 window; K04 still MISSING')


if __name__ == '__main__':
    main()
