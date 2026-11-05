"""Cross-packet false-native-MT adjacency controls, no selected ACK bytes.

Source-only exhaustive all-future-pair scan, a negative-cycle witness, and
a clearly labeled conditional existing p951 native-stage interpretation.
"""
from __future__ import annotations

import ast
import re
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import k04_stagefree_mt_packet_graph_sft as g


def prior_map() -> list[int]:
    path = Path(__file__).resolve().parents[1] / "agent49" / "k04_p951_symbolic_basis.py"
    text = path.read_text(encoding="utf-8")
    match = re.search(r"^STARTS\s*=\s*(\[[^\n]+\])", text, re.M)
    assert match is not None
    starts = ast.literal_eval(match.group(1))
    assert len(starts) == 133 and starts[129] == 951
    return starts


def main(path: str):
    rows = g.source_rows(path)
    flat, inside = g.discover(rows)
    assert len(inside) == 25
    row_words = dict(rows)
    values = [x[2] for x in flat]
    index = defaultdict(list)
    for k in range(len(values)):
        for l in range(k + 1, len(values)):
            index[values[k] ^ values[l]].append((k, l))
    cross = []
    possible = 0
    for i in range(len(values) - 1):
        a, ai, _ = flat[i]
        b, bj, _ = flat[i + 1]
        if ai != 3 or bj != 0 or b != a + 1:
            continue
        possible += 1
        for k, l in index.get(g.twist_mix(values[i], values[i + 1]), ()):
            if (k > i + 1 and flat[k][0] > b
                    and flat[l][0] > flat[k][0]):
                cross.append((i, i + 1, k, l))
    groups = [
        tuple(flat[t][0] for t in relation) for relation in cross
    ]
    expected = [
        (3, 4, 57, 87), (12, 13, 67, 97),
        (13, 14, 68, 98), (33, 34, 86, 116),
        (40, 41, 94, 125), (43, 44, 97, 130)
    ]
    assert possible == 130 and groups == expected, (possible, groups)

    # This source-only graph excludes the candidate cross-boundary equalities.
    # A proposed exact s13-s12=4 would contradict its established lower bound 5.
    chronology = g.directed_constraints(flat, inside)
    lower_gap = -g.shortest(133, chronology, 13)[12]
    assert lower_gap == 5

    # Retrospective, explicitly conditional p951 explanation of all six.
    starts = prior_map()
    by_stage = {
        starts[r] + j: (r, j, x)
        for r, words in rows for j, x in enumerate(words)
    }
    donor_eligible, leading_bit_matches = 0, 0
    donor_stages = []
    for b in range(1, 133):
        if b == 129 or b - 1 == 129:
            continue
        if b not in row_words or b - 1 not in row_words:
            continue
        stage = starts[b]
        k = by_stage.get(stage + 396)
        l = by_stage.get(stage + 623)
        if k is None or l is None:
            continue
        donor_eligible += 1
        prev = row_words[b-1][3]
        first = row_words[b][0]
        encoded_twist = k[2] ^ l[2]
        # Infer the MSB of the hidden native predecessor at stage-1 from
        # the two intact future source words and the intact current word.
        match_0 = g.twist_mix(0, first) == encoded_twist
        match_1 = g.twist_mix(0x80000000, first) == encoded_twist
        assert match_0 != match_1
        hidden_msb = int(match_1)
        if int(bool(prev & 0x80000000)) == hidden_msb:
            leading_bit_matches += 1
        donor_stages.append(stage - 1)
    assert (donor_eligible, leading_bit_matches) == (17, 6)

    for i, j, k, l in cross:
        a, ai, _ = flat[i]
        b, bj, _ = flat[j]
        c, ck, _ = flat[k]
        d, dl, _ = flat[l]
        assert starts[b] - starts[a] > 4
        assert starts[c] + ck == starts[b] + 396
        assert starts[d] + dl == starts[b] + 623
        assert g.twist_mix(values[i], values[j]) == values[k] ^ values[l]
    assert not (set(donor_stages) & {
        328, 329, 330, 331, 724, 725, 726, 727
    })
    # Real seeded CPython output streams: source geometry identical, no
    # historical target/hash inputs. False fullword matches remain common.
    import random
    eligible = [b for b in range(1, 133)
                if b in row_words and b - 1 in row_words
                and starts[b] + 396 in by_stage
                and starts[b] + 623 in by_stage]
    assert len(eligible) == 17
    synthetic_counts = []
    for seed in range(200):
        rng = random.Random(seed)
        native = [g.untemper(rng.getrandbits(32)) for _ in range(967)]
        synthetic_counts.append(sum(
            g.twist_mix(native[starts[b-1] + 3], native[starts[b]])
            == (native[starts[b] + 396] ^ native[starts[b] + 623])
            for b in eligible))
    assert (min(synthetic_counts), max(synthetic_counts),
            sum(synthetic_counts), sum(v <= 6 for v in synthetic_counts)) \
        == (3, 14, 1665, 41)
    print("GENUINE_SYNTHETIC_MT_SEED_COUNT", len(synthetic_counts))
    print("GENUINE_SYNTHETIC_FALSE_FULLWORD_MEAN",
          sum(synthetic_counts) / len(synthetic_counts))
    print("GENUINE_SYNTHETIC_COUNTS_LE_ORIGINAL6",
          sum(v <= 6 for v in synthetic_counts))
    print("ORIGINAL_SPOOL_SHA256", g.SPOOL_SHA256)
    print("TRUE_INTRA_PACKET_RELATIONS", len(inside))
    print("ADJACENT_INTACT_PACKET_BOUNDARIES", possible)
    print("EXACT_APPARENT_CROSS_PACKET_RELATIONS", len(cross))
    print("SOURCE_ONLY_ROW12_TO13_GAP_MIN", int(lower_gap))
    print("CONDITIONAL_P951_DONOR_ELIGIBLE", donor_eligible)
    print("CONDITIONAL_P951_MATCHED_PREV_MSB", leading_bit_matches)
    print("CONDITIONAL_NATIVE_GAP_EXPLANATION", "SIX_OF_SIX")
    print("TARGET_CAUSAL_EIGHT_NATIVE_DONOR_OVERLAP", 0)
    print("PHYSICAL_K04_BITS_AUTHENTICATED", 0)


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1
         else "resources/evidence/print/spool-reconstruction.log")
