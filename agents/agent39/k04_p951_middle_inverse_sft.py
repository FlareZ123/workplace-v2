"""K04 p951 source-only CPython key-array CENTRAL-word inversion.

Run from repository root:
    python agents/agent39/k04_p951_middle_inverse_sft.py

Reads the same original intact spool as Agent45. The disputed selected row129,
K04/K08 acceptance oracles, routing mask and candidate are never read.
"""
import hashlib
import importlib.util
import random
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "agents/agent45/k04_p951_seed_residue_inverse_sft.py"
spec = importlib.util.spec_from_file_location("agent45_inverse", SOURCE)
prior = importlib.util.module_from_spec(spec)
spec.loader.exec_module(prior)
MASK = prior.MASK


def inverse_middle(i, a, c, key):
    """Exact b solutions for T[i-1]=key; 32-bit low-bit lifting.

    The upper two bits of b and b+i-1 are guessed (4x4).
    Each low-bit prefix is kept only when it matches the key-term low bits.
    Truncated prefixes use their independently guessed high bits while the
    omitted middle bits cannot affect the tested low bits. Every surviving
    full word is independently checked by the forward key equation.
    """
    a_mix = prior.mix(a, 1566083941)
    ci = (c + i) & MASK
    reference = prior.BASE[i]
    result = set()
    for b_high in range(4):
        for predecessor_high in range(4):
            prefixes = [0]
            for bit_length in range(1, 31):
                limit = (1 << bit_length) - 1
                next_prefixes = []
                for prefix in prefixes:
                    for candidate in (prefix, prefix | (1 << (bit_length - 1))):
                        b = candidate | (b_high << 30)
                        predecessor = (
                            ((candidate + i - 1) & 0x3fffffff)
                            | (predecessor_high << 30)
                        ) ^ a_mix
                        predicted = (
                            (ci ^ prior.mix(b, 1566083941))
                            - (reference ^ prior.mix(predecessor, 1664525))
                        ) & limit
                        if predicted == (key & limit):
                            next_prefixes.append(candidate)
                prefixes = next_prefixes
                if not prefixes:
                    break
                assert len(prefixes) <= 20000, "unexpected inverse branch explosion"
            for prefix in prefixes:
                b = prefix | (b_high << 30)
                if (((b + i - 1) & MASK) >> 30) != predecessor_high:
                    continue
                if prior.key_term(i, a, b, c) == key:
                    result.add(b)
    return result


def residue_domains(n, values, masks):
    domains = {}
    for j, choices in prior.source_terms(values, masks).items():
        residue = j % n
        domains[residue] = (
            domains[residue] & choices if residue in domains else set(choices)
        )
        assert domains[residue], f"baseline inconsistent n={n}"
    return domains


def central_constraints(n, values, masks):
    """Conservative central-state candidate union; no guess ever discarded."""
    domains = residue_domains(n, values, masks)
    fixes = []
    attempted = []
    for i in range(4, 624):
        keys = domains.get((i - 1) % n)
        if not keys or masks[i - 1] == MASK:
            continue
        first = prior.near_complete_domain(values[i - 2], masks[i - 2])
        third = prior.near_complete_domain(values[i], masks[i])
        if not first or not third:
            continue
        options = set()
        for key in keys:
            for a in first:
                for c in third:
                    options.update(inverse_middle(i, a, c, key))
        options = {
            b for b in options
            if not ((b ^ values[i - 1]) & masks[i - 1])
        }
        attempted.append((i, len(options)))
        if not options:
            return False, [], attempted
        exemplar = next(iter(options))
        consensus = MASK
        for b in options:
            consensus &= ~(b ^ exemplar) & MASK
        extra_mask = consensus & ~masks[i - 1]
        if extra_mask:
            fixes.append((i - 1, exemplar, extra_mask))
    return True, fixes, attempted


def source_sieve(payloads):
    source, known, offset = prior.close(payloads)
    initial = source[offset - 624:offset]
    masks = known[offset - 624:offset]
    first = prior.source_terms(initial, masks)
    baseline_lengths = []
    for n in range(1, 624):
        seen = {}
        for j, options in first.items():
            residue = j % n
            seen[residue] = (
                seen[residue] & options if residue in seen else options
            )
            if not seen[residue]:
                break
        else:
            baseline_lengths.append(n)
    assert len(baseline_lengths) == 144

    near_survivors = []
    for n in baseline_lengths:
        ok, inferred, inferred_masks, _ = prior.infer_near(n, initial, masks)
        if not ok:
            continue
        extras = [
            (i, inferred[i], inferred_masks[i] & ~masks[i])
            for i in range(624) if inferred_masks[i] & ~masks[i]
        ]
        try:
            prior.close(payloads, extras)
        except ValueError:
            continue
        near_survivors.append((n, inferred, inferred_masks))
    assert len(near_survivors) == 71
    excluded = {}
    remaining = []
    for n, inferred, inferred_masks in near_survivors:
        ok, fixes, attempts = central_constraints(n, inferred, inferred_masks)
        if not ok:
            excluded[n] = attempts
            continue
        extras = [
            (i, inferred[i], inferred_masks[i] & ~masks[i])
            for i in range(624) if inferred_masks[i] & ~masks[i]
        ]
        extras.extend(fixes)
        try:
            prior.close(payloads, extras)
        except ValueError as error:
            excluded[n] = str(error)
            continue
        remaining.append(n)
    return excluded, remaining


def positive_controls():
    rng = random.Random(47217)
    for _ in range(250):
        i = rng.randrange(4, 624)
        a, b, c = (rng.getrandbits(32) for _ in range(3))
        key = prior.key_term(i, a, b, c)
        assert b in inverse_middle(i, a, c, key)

    positives = 0
    for n in (364, 394, 512, 522, 573):
        for variant in (0, 1):
            seed = sum(
                ((0x71a5024d + variant * 0xd13 + j * 0x12537) & MASK) << (32 * j)
                for j in range(n)
            )
            mt = random.Random(seed)
            true_register = list(mt.getstate()[1][:624])
            draws = [mt.getrandbits(32) for _ in range(967)]
            payloads = [
                b"".join(draws[start + lane].to_bytes(4, "little")
                         for lane in range(4))
                for start in prior.STARTS
            ]
            source, masks, offset = prior.close(payloads)
            baseline, baseline_mask = (
                source[offset - 624:offset], masks[offset - 624:offset]
            )
            ok, inferred, inferred_mask, _ = prior.infer_near(
                n, baseline, baseline_mask
            )
            assert ok
            assert all(
                not ((true ^ proposed) & mask)
                for true, proposed, mask in
                zip(true_register, inferred, inferred_mask)
            )
            valid, fixes, tested = central_constraints(
                n, inferred, inferred_mask
            )
            assert valid and tested
            assert all(
                not ((true_register[i] ^ val) & mask)
                for i, val, mask in fixes
            )
            positives += 1
    assert positives == 10
    print("250/250 random exact inverses; 10/10 seeded full-spool controls PASS")


def main():
    positive_controls()
    spool = ROOT / "resources/evidence/print/spool-reconstruction.log"
    raw = spool.read_bytes()
    assert hashlib.sha256(raw).hexdigest() == prior.SPOOL_SHA
    payloads = [
        bytes.fromhex(hex_text.decode())
        for hex_text in re.findall(rb"PAYLOAD=([0-9A-F]{32})", raw)
    ]
    assert len(payloads) == len(prior.STARTS) == 133
    assert prior.STARTS[129] == 951
    excluded, surviving = source_sieve(payloads)
    assert set(excluded) == {364, 394, 512, 522, 573}, excluded
    assert len(surviving) == 66
    print("Original 71 -> 66 conditional CPython seed-array lengths")
    print("New excluded length: first/third terms and middle index")
    for n in sorted(excluded):
        print(n, excluded[n])
    print("Selected K04 original payload bits authenticated: 0/128")
    print("No original K04 or K08 acceptance data examined")


if __name__ == "__main__":
    main()
