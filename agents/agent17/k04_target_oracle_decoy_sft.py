"""Exact H-17 K04 whole-packet oracle, conditional p951 MT stage and decoy SFT.

Run: python agents/agent17/k04_target_oracle_decoy_sft.py
Original spool selected attempt2 is excluded before payload parsing. A speculative
p951 stage fixture is inherited from agent49; it is NOT historical authentication.
"""
from collections import Counter, defaultdict
from hashlib import sha256
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
from random import Random
import re

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / 'resources/evidence/print/spool-reconstruction.log'
PIN = '7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083'
MASK = bytes.fromhex('8556C8CB6140A7F9A5123AC7571BEE1C')
TARGET = '930a52a1bab97ca2966332137c99e99298ea6182fb32ab63a3421dfb4fd8c9e0'
spec = spec_from_file_location('h17_p951',
                               ROOT / 'agents/agent49/k04_p951_symbolic_basis.py')
mt = module_from_spec(spec)
spec.loader.exec_module(mt)


def spool():
    raw = SOURCE.read_bytes()
    assert sha256(raw).hexdigest() == PIN
    lines = [s for s in raw.decode('ascii').splitlines() if 'PAYLOAD=' in s]
    assert len(lines) == len(mt.STARTS) == 133
    assert 'JOB=PS-261003-0417 ATTEMPT=2 STATE=ACK CLASS=RECOVER' in lines[129]
    packets = []
    for index, line in enumerate(lines):
        if index == 129:
            packets.append(b'')  # Must exclude selected before PAYLOAD parsing.
            continue
        match = re.search(r'PAYLOAD=([0-9A-F]{32})', line)
        assert match
        packets.append(bytes.fromhex(match[1]))
    assert mt.STARTS[129] == 951
    return packets


def synthetic():
    rng = Random(20261118)
    native_outputs = [rng.getrandbits(32)
                      for _ in range(mt.LAST - mt.ORIGIN + 8)]
    packets = []
    for i, start in enumerate(mt.STARTS):
        if i == 129:
            packets.append(b'')
            continue
        packets.append(b''.join(native_outputs[start - mt.ORIGIN + j]
                                 .to_bytes(4, 'little') for j in range(4)))
    return packets


def basis_for(packets, words, omit):
    basis = mt.Basis()
    for row, (packet, start) in enumerate(zip(packets, mt.STARTS)):
        if row in omit:
            continue
        for lane in range(4):
            native = mt.untemper(int.from_bytes(packet[4*lane:4*lane+4], 'little'))
            for bit, vec in enumerate(mt.get(words, start + lane)):
                basis.insert(vec, (native >> bit) & 1)
    return basis


def predicted_bits(basis, words, start):
    return [basis.predict(vec) for lane in range(4)
            for vec in mt.get(words, start + lane)]


def actual_bits(packet):
    return [(mt.untemper(int.from_bytes(packet[4*lane:4*lane+4], 'little'))
             >> bit) & 1 for lane in range(4) for bit in range(32)]


def serialize(bits):
    assert len(bits) == 128 and None not in bits
    return b''.join(sum(bit << j for j, bit in
                        enumerate(mt.temper(bits[32*k:32*k+32])))
                    .to_bytes(4, 'little') for k in range(4))


def all_heldouts(packets, words, label):
    counts = Counter()
    for row, packet in enumerate(packets):
        if row == 129:
            continue
        # No heldout bytes enter stage fit or reconstruction.
        basis = basis_for(packets, words, {129, row})
        predicted = predicted_bits(basis, words, mt.STARTS[row])
        original = actual_bits(packet)
        assert all(bit == original[i] for i, bit in enumerate(predicted)
                   if bit is not None)
        counts[sum(bit is not None for bit in predicted)] += 1
    expected = Counter({0: 41, 1: 20, 2: 1, 31: 10, 32: 5, 33: 4,
                        63: 16, 64: 12, 65: 6, 95: 10, 96: 2, 127: 5})
    assert counts == expected and counts.get(128, 0) == 0
    print(label, 'whole_packet_predictions', 0,
          'zero_bit_holdouts', counts[0],
          'partial_bit_holdouts', 132-counts[0], 'bitcount_histogram',
          sorted(counts.items()))


def one_bit_commitment_positive(packets, words):
    row = 41
    known = predicted_bits(basis_for(packets, words, {129, row}),
                           words, mt.STARTS[row])
    missing = [i for i, bit in enumerate(known) if bit is None]
    assert len(missing) == 1
    # Digest is an independent test fixture calculated after the holdout fit.
    digest = sha256(packets[row]).hexdigest()
    candidates = []
    for bit in (0, 1):
        bits = known[:]
        bits[missing[0]] = bit
        candidates.append(serialize(bits))
    matching = [p for p in candidates if sha256(p).hexdigest() == digest]
    assert matching == [packets[row]]
    print('original_source_onebit_hash_positive', 'row', row,
          'whole_packet_candidates', 2, 'accepted', 1)


def scan_original_complete_windows(packets, words):
    basis = basis_for(packets, words, {129})
    assert basis.rank == 15365
    selected = predicted_bits(basis, words, mt.STARTS[129])
    assert selected.count(None) == 128
    full_words = []
    for stage in range(mt.ORIGIN, mt.LAST+1):
        bits = [basis.predict(bit) for bit in mt.get(words, stage)]
        full_words.append(None if None in bits else
                          sum(x << j for j, x in
                              enumerate(mt.temper(bits))).to_bytes(4, 'little'))
    intact = set(packets)
    all_windows, unseen = 0, set()
    for stage in range(mt.ORIGIN, mt.LAST - 2):
        block = full_words[stage-mt.ORIGIN:stage-mt.ORIGIN+4]
        if any(w is None for w in block):
            continue
        coupon = b''.join(block)
        all_windows += 1
        if coupon not in intact:
            unseen.add(coupon)
        component = bytes(x ^ y for x, y in zip(coupon, MASK))
        assert sha256(component).hexdigest() != TARGET, stage
    assert sum(w is not None for w in full_words) == 991
    assert all_windows == 284 and len(unseen) == 152
    print('original_source_rank', basis.rank,
          'selected_known_bits', 0, 'selected_unconstrained_bits', 128,
          'source_reconstructed_complete_windows', all_windows,
          'previously_unseen_whole_packets', len(unseen),
          'original_k04_full_commitment_hits', 0)


def links(rows):
    words = [(r, j, x) for r, row in enumerate(rows) for j, x in enumerate(row)]
    by_value = defaultdict(list)
    for r, j, x in words:
        by_value[x].append((r, j))
    found = []
    for row, block in enumerate(rows):
        for j in range(len(block)-1):
            a, b = block[j:j+2]
            z = (a & 0x80000000) | (b & 0x7fffffff)
            mix = (z >> 1) ^ (0x9908b0df if z & 1 else 0)
            for c, cj, value in words:
                for d, dj in by_value.get(mix ^ value, ()):
                    if (c, cj) < (d, dj) and len({row, c, d}) == 3:
                        found.append((row, j, c, cj, d, dj))
    return found


def monotone_stage_feasible(candidates, n):
    edges = []
    for a, j, c, cj, d, dj in candidates:
        for target, position, lag in ((c, cj, 397), (d, dj, 624)):
            step = lag + j - position
            edges.extend(((a, target, step), (target, a, -step)))
    for i in range(n-1):
        edges.append((i+1, i, -4))
    distances = [0] * n
    for _ in range(n):
        changed = False
        for u, v, weight in edges:
            if distances[v] > distances[u] + weight:
                distances[v] = distances[u] + weight
                changed = True
        if not changed:
            return True
    return False


def planted_alias_decoy():
    rng = Random(20261118)
    rows, starts, stage = [], [], 0
    for i in range(132):
        starts.append(stage)
        rows.append([mt.untemper(rng.getrandbits(32)) for _ in range(4)])
        stage += 4
        if i != 131:
            for _ in range(3):
                rng.getrandbits(32)
            stage += 3
    original_links = links(rows)
    assert len(original_links) == 43
    assert monotone_stage_feasible(original_links, 132)
    assert all(starts[c]+cj == starts[a]+j+397 and
               starts[d]+dj == starts[a]+j+624
               for a, j, c, cj, d, dj in original_links)
    modified = [block[:] for block in rows]
    source_word = rows[5][2]
    modified[43][0] = ((source_word & 0x80000000) |
                       ((source_word ^ 0x133721) & 0x7fffffff))
    modified[43][1] = rows[5][3]
    assert modified[43][0] != source_word
    augmented = links(modified)
    false = [link for link in augmented if not (
        starts[link[2]]+link[3] == starts[link[0]]+link[1]+397 and
        starts[link[4]]+link[5] == starts[link[0]]+link[1]+624)]
    assert len(augmented) == 44 and false == [(43, 0, 62, 0, 94, 3)]
    assert not monotone_stage_feasible(augmented, 132)
    # Frozen minimal-deletion model: reject an edge only if the remainder
    # admits monotone stages; check all 44 possible single-edge omissions.
    valid_drops = [i for i in range(len(augmented)) if
                   monotone_stage_feasible(augmented[:i]+augmented[i+1:], 132)]
    assert valid_drops == [43] and augmented[43] == false[0]
    print('seeded_decoy_control', 'genuine_links', 43,
          'forged_same_MSB_ancestor', 1,
          'maximum_consensus_correctly_rejected', false[0])


def main():
    original = spool()
    words = mt.words()
    planted_alias_decoy()
    all_heldouts(synthetic(), words, 'planted_MT_oracle_stage')
    all_heldouts(original, words, 'original_source_oracle_stage')
    one_bit_commitment_positive(original, words)
    scan_original_complete_windows(original, words)
    print('PASS: original evidence and acceptance untouched; no selected coupon recovered')


if __name__ == '__main__':
    main()
