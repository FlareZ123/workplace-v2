"""H-17 K04: global GF(2) printer-source screen of CPython seed inversions.

Uses Agent45 exact/onebit inverse term SFT and Agent8 source-basis algebra.
Selected original row129, route mask, K04/K08 acceptance and verifier excluded.
Run: python agents/agent45/k04_p951_seed_fullsource_gf2_sft.py resources
"""
import hashlib
import importlib.util
import random
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def import_file(name, path):
    spec = importlib.util.spec_from_file_location(name, ROOT / path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


m = import_file('agent45_inverse', 'agents/agent45/k04_p951_seed_residue_inverse_sft.py')
g = import_file('agent8_gf2', 'agents/agent8/k04_p951_witness_target_projection_sft.py')


def add_source_bits(basis, expr, extras):
    """Exact affine source constraints; false when any relation contradicts."""
    new = basis.copy()
    for index, value, mask in extras:
        for bit in range(32):
            if not (mask >> bit) & 1:
                continue
            raw = expr[1100 - 624 + index][bit]
            row = g.reduce_affine(raw, (value >> bit) & 1, new)
            if row == 1:
                return None
            if row > 1:
                new[row.bit_length() - 1] = row
    return new


def target_rank(affine, targets):
    linear = {position - 1: row >> 1 for position, row in affine.items()}
    return g.quotient(linear, targets)


def source_row_basis(expr, packets):
    basis = g.source_basis(expr, packets)
    assert len(basis) == 15365
    return basis


def added_state_bits(initial_values, initial_masks, inferred_values, inferred_masks):
    return [(i, inferred_values[i], inferred_masks[i] & ~initial_masks[i])
            for i in range(624) if inferred_masks[i] & ~initial_masks[i]]


def main(resources):
    raw = (resources / 'evidence/print/spool-reconstruction.log').read_bytes()
    assert hashlib.sha256(raw).hexdigest() == m.SPOOL_SHA
    packets = [bytes.fromhex(part.decode()) for part in re.findall(
        rb'PAYLOAD=([0-9A-F]{32})', raw)]
    assert len(packets) == len(m.STARTS) == 133 and m.STARTS[129] == 951
    packets[129] = b''
    expr = g.states()
    target = [bit for j in range(4) for bit in g.temper_expr(expr[1100+951+j])]
    original_basis = source_row_basis(expr, packets)
    assert target_rank(original_basis, target) == 128
    source, masks, origin = m.close(packets)
    initial, initial_masks = source[origin-624:origin], masks[origin-624:origin]
    prior, first, after, _, _, _ = m.screen(packets)
    assert len(prior) == 144 and len(first) == 118 and len(after) == 85

    near_survivors = []
    for n in after:
        ok, values, known, why = m.infer_near(n, initial, initial_masks)
        if not ok:
            continue
        extras = added_state_bits(initial, initial_masks, values, known)
        try:
            m.close(packets, extras)
        except ValueError:
            continue
        near_survivors.append((n, extras))
    assert len(near_survivors) == 71

    contradictions = []
    survivors = []
    for n, extras in near_survivors:
        augmented = add_source_bits(original_basis, expr, extras)
        if augmented is None:
            contradictions.append(n)
            continue
        rank = target_rank(augmented, target)
        assert rank == 128, (n, rank)
        survivors.append(n)
    assert len(contradictions) == 24 and len(survivors) == 47
    assert min(survivors) == 393 and 364 in contradictions and 512 in contradictions
    print('Original source-only rank', len(original_basis),
          'selected K04 quotient rank', target_rank(original_basis,target))
    print('Seed lengths among 1..623: 144 → 118 → 85 → 71 → 47')
    print('New global affine source contradictions:',len(contradictions))
    print('Full-source surviving first-cycle lengths:',survivors)
    print('First surviving length',min(survivors),
          'all K04 target quotient ranks exactly 128')

    # Independent genuine seeded controls. Source index geometry is held fixed.
    for n in (364,374,407,512,623):
        for variant in (0,1):
            seed = sum((((0x50fa7d89+variant*31337+i*98177)&m.MASK) << (32*i))
                       for i in range(n))
            generator = random.Random(seed)
            true_register = list(generator.getstate()[1][:624])
            draws = [generator.getrandbits(32) for _ in range(967)]
            synthetic = [b''.join(draws[start+j].to_bytes(4,'little')
                                  for j in range(4)) for start in m.STARTS]
            synthetic[129] = b''
            words, known, offset = m.close(synthetic)
            register = words[offset-624:offset]
            register_masks = known[offset-624:offset]
            valid, inferred, inferred_masks, reason = m.infer_near(
                n, register, register_masks)
            assert valid, (n,variant,reason)
            assert all(not ((inferred[i] ^ true_register[i]) & inferred_masks[i])
                       for i in range(624))
            original = source_row_basis(expr, synthetic)
            extras = added_state_bits(register, register_masks, inferred, inferred_masks)
            new = add_source_bits(original, expr, extras)
            assert new is not None, (n,variant)
            assert target_rank(new,target) == 128
            observed, updated_masks, off = m.close(synthetic, extras)
            selected = [m.untemper(draws[951+j]) for j in range(4)]
            assert all(not ((observed[off+951+j] ^ selected[j])
                            & updated_masks[off+951+j]) for j in range(4))
            print('Genuine seeded full-source GF2 positive control',
                  n,variant,'PASS',flush=True)
    print('10/10 genuine seeded full-source positives PASS; K04 still missing')


if __name__ == '__main__':
    main(Path(sys.argv[1]) if len(sys.argv)>1 else ROOT / 'resources')
